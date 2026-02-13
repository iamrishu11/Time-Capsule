"""
Scheduler Service Module

Handles scheduled tasks for the Time Capsule application including:
- Capsule delivery processing
- Heartbeat ping scheduling
- Reminder emails
"""

from datetime import datetime, timedelta
from flask import current_app

from app.extensions import db
from app.models import Capsule, CapsuleRecipient, DeliveryLog, HeartbeatCheck, User
from app.security.encryption import decrypt_text
from app.services.email_service import (
    send_capsule_delivery_email,
    send_capsule_reminder_email,
    send_heartbeat_ping_email,
)


def process_scheduled_capsules():
    """
    Process all capsules that are due for delivery.
    
    This function should be called periodically (e.g., every hour) by a scheduler
    like cron, APScheduler, or Celery.
    
    Returns:
        dict: Summary of processed capsules
    """
    now = datetime.utcnow()
    summary = {
        'processed': 0,
        'delivered': 0,
        'failed': 0,
        'errors': []
    }
    
    try:
        # Find all scheduled capsules that are due
        due_capsules = Capsule.query.filter(
            Capsule.status == 'SCHEDULED',
            Capsule.release_type == 'TIME',
            Capsule.release_at <= now
        ).all()
        
        for capsule in due_capsules:
            summary['processed'] += 1
            
            try:
                # Decrypt the message
                decrypted_message = decrypt_text(capsule.message_encrypted)
                
                # Send to all recipients
                delivery_success = True
                for cr in capsule.recipients:
                    recipient = cr.recipient
                    
                    # Create delivery log
                    delivery_log = DeliveryLog(
                        capsule_id=capsule.id,
                        recipient_id=recipient.id,
                        scheduled_for=capsule.release_at,
                        status='PENDING'
                    )
                    db.session.add(delivery_log)
                    
                    # Send the email
                    if send_capsule_delivery_email(capsule, recipient, decrypted_message):
                        delivery_log.status = 'SENT'
                        delivery_log.delivered_at = datetime.utcnow()
                    else:
                        delivery_log.status = 'FAILED'
                        delivery_log.error_message = 'Failed to send email'
                        delivery_success = False
                
                # Update capsule status
                if delivery_success:
                    capsule.status = 'SENT'
                    summary['delivered'] += 1
                else:
                    summary['failed'] += 1
                
                db.session.commit()
                
            except Exception as e:
                db.session.rollback()
                summary['failed'] += 1
                summary['errors'].append(f"Capsule {capsule.id}: {str(e)}")
                current_app.logger.error(f"Error processing capsule {capsule.id}: {e}")
        
    except Exception as e:
        current_app.logger.error(f"Error in process_scheduled_capsules: {e}")
        summary['errors'].append(str(e))
    
    return summary


def send_delivery_reminders(days_before=[7, 1]):
    """
    Send reminder emails to users about upcoming capsule deliveries.
    
    Args:
        days_before: List of days before delivery to send reminders
    
    Returns:
        dict: Summary of reminders sent
    """
    now = datetime.utcnow()
    summary = {
        'reminders_sent': 0,
        'errors': []
    }
    
    try:
        for days in days_before:
            target_date = now + timedelta(days=days)
            
            # Find capsules due in exactly 'days' days
            upcoming_capsules = Capsule.query.filter(
                Capsule.status == 'SCHEDULED',
                Capsule.release_type == 'TIME',
                db.func.date(Capsule.release_at) == target_date.date()
            ).all()
            
            for capsule in upcoming_capsules:
                try:
                    if send_capsule_reminder_email(capsule, days):
                        summary['reminders_sent'] += 1
                except Exception as e:
                    summary['errors'].append(f"Capsule {capsule.id}: {str(e)}")
                    
    except Exception as e:
        current_app.logger.error(f"Error in send_delivery_reminders: {e}")
        summary['errors'].append(str(e))
    
    return summary


def process_heartbeat_checks():
    """
    Process heartbeat checks for event-based capsules.
    
    - Send pings to users who haven't confirmed recently
    - Expire old unconfirmed pings
    - Trigger event-based capsule delivery for expired users
    
    Returns:
        dict: Summary of heartbeat processing
    """
    now = datetime.utcnow()
    summary = {
        'pings_sent': 0,
        'expired': 0,
        'capsules_triggered': 0,
        'errors': []
    }
    
    try:
        # Find users with event-based capsules who haven't been pinged recently
        users_with_event_capsules = db.session.query(User).join(
            Capsule, User.id == Capsule.owner_id
        ).filter(
            Capsule.release_type == 'EVENT',
            Capsule.status == 'SCHEDULED'
        ).distinct().all()
        
        for user in users_with_event_capsules:
            # Check if there's a recent pending heartbeat
            recent_ping = HeartbeatCheck.query.filter(
                HeartbeatCheck.user_id == user.id,
                HeartbeatCheck.status == 'AWAITING',
                HeartbeatCheck.ping_sent_at > now - timedelta(days=30)
            ).first()
            
            if not recent_ping:
                # Check last confirmed heartbeat
                last_confirmed = HeartbeatCheck.query.filter(
                    HeartbeatCheck.user_id == user.id,
                    HeartbeatCheck.status == 'CONFIRMED'
                ).order_by(HeartbeatCheck.ping_confirmed_at.desc()).first()
                
                # If no confirmation in last 60 days, send ping
                if not last_confirmed or last_confirmed.ping_confirmed_at < now - timedelta(days=60):
                    # Create new heartbeat check
                    heartbeat = HeartbeatCheck(
                        user_id=user.id,
                        ping_sent_at=now,
                        status='AWAITING'
                    )
                    db.session.add(heartbeat)
                    db.session.commit()
                    
                    # Generate confirmation link (this would need a proper route)
                    confirmation_link = f"/api/heartbeat/confirm/{heartbeat.id}"
                    
                    if send_heartbeat_ping_email(user, confirmation_link):
                        summary['pings_sent'] += 1
        
        # Expire old unconfirmed pings and trigger capsule delivery
        expired_pings = HeartbeatCheck.query.filter(
            HeartbeatCheck.status == 'AWAITING',
            HeartbeatCheck.ping_sent_at < now - timedelta(days=30)
        ).all()
        
        for ping in expired_pings:
            ping.status = 'EXPIRED'
            summary['expired'] += 1
            
            # Check if this is the second consecutive expired ping
            previous_expired = HeartbeatCheck.query.filter(
                HeartbeatCheck.user_id == ping.user_id,
                HeartbeatCheck.status == 'EXPIRED',
                HeartbeatCheck.id != ping.id
            ).order_by(HeartbeatCheck.ping_sent_at.desc()).first()
            
            if previous_expired:
                # Two consecutive expired pings - trigger event-based capsules
                event_capsules = Capsule.query.filter(
                    Capsule.owner_id == ping.user_id,
                    Capsule.release_type == 'EVENT',
                    Capsule.status == 'SCHEDULED'
                ).all()
                
                for capsule in event_capsules:
                    capsule.status = 'TRIGGERED'
                    summary['capsules_triggered'] += 1
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in process_heartbeat_checks: {e}")
        summary['errors'].append(str(e))
    
    return summary


def get_delivery_stats():
    """
    Get statistics about capsule deliveries.
    
    Returns:
        dict: Delivery statistics
    """
    now = datetime.utcnow()
    
    return {
        'total_capsules': Capsule.query.count(),
        'scheduled': Capsule.query.filter_by(status='SCHEDULED').count(),
        'sent': Capsule.query.filter_by(status='SENT').count(),
        'due_today': Capsule.query.filter(
            Capsule.status == 'SCHEDULED',
            db.func.date(Capsule.release_at) == now.date()
        ).count(),
        'pending_deliveries': DeliveryLog.query.filter_by(status='PENDING').count(),
        'successful_deliveries': DeliveryLog.query.filter_by(status='SENT').count(),
        'failed_deliveries': DeliveryLog.query.filter_by(status='FAILED').count(),
    }
