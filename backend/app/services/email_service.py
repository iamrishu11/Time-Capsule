"""
Email Service Module

Provides email functionality for the Time Capsule application.
Handles sending emails for capsule delivery, notifications, and user communications.
"""

import os
from threading import Thread
from flask import current_app, render_template_string
from flask_mail import Message

from app.extensions import mail


def send_async_email(app, msg):
    """Send email asynchronously in a separate thread."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            app.logger.error(f"Failed to send email: {e}")


def send_email(subject, recipients, text_body=None, html_body=None, sender=None, async_send=True):
    """
    Send an email to specified recipients.
    
    Args:
        subject: Email subject line
        recipients: List of recipient email addresses
        text_body: Plain text email body
        html_body: HTML email body (optional)
        sender: Sender email address (uses default if not specified)
        async_send: Whether to send asynchronously (default: True)
    
    Returns:
        True if email was queued/sent successfully, False otherwise
    """
    try:
        app = current_app._get_current_object()
        
        # Get sender from config if not provided
        if sender is None:
            sender_name = app.config.get('MAIL_SENDER_NAME', 'Time Capsule')
            sender_email = app.config.get('MAIL_DEFAULT_SENDER')
            sender = f"{sender_name} <{sender_email}>" if sender_email else None
        
        if not sender:
            app.logger.error("No email sender configured")
            return False
        
        msg = Message(
            subject=subject,
            sender=sender,
            recipients=recipients if isinstance(recipients, list) else [recipients]
        )
        
        msg.body = text_body
        if html_body:
            msg.html = html_body
        
        if async_send:
            # Send in background thread
            Thread(target=send_async_email, args=(app, msg)).start()
        else:
            mail.send(msg)
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error preparing email: {e}")
        return False


def send_welcome_email(user):
    """
    Send welcome email to a newly registered user.
    
    Args:
        user: User model instance
    """
    subject = "Welcome to Time Capsule!"
    
    text_body = f"""
Hello {user.name},

Welcome to Time Capsule! Your account has been successfully created.

Time Capsule allows you to create messages that will be delivered to your loved ones at a future date. 
You can:
- Create time capsules with personal messages
- Add photos, videos, and documents
- Schedule delivery for specific dates
- Set up event-based delivery

Start creating your first time capsule today!

Best regards,
The Time Capsule Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .feature {{ margin: 15px 0; padding: 10px; background: white; border-radius: 5px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Time Capsule!</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{user.name}</strong>,</p>
            <p>Your account has been successfully created. Time Capsule allows you to preserve memories and messages for your loved ones.</p>
            
            <h3>What you can do:</h3>
            <div class="feature">📝 Create time capsules with personal messages</div>
            <div class="feature">📷 Add photos, videos, and documents</div>
            <div class="feature">📅 Schedule delivery for specific dates</div>
            <div class="feature">🔐 Your messages are encrypted for privacy</div>
            
            <p>Start creating your first time capsule today!</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Time Capsule Team</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, [user.email], text_body, html_body)


def send_capsule_delivery_email(capsule, recipient, decrypted_message):
    """
    Send a time capsule to a recipient.
    
    Args:
        capsule: Capsule model instance
        recipient: Recipient model instance
        decrypted_message: Decrypted message content
    """
    subject = f"Time Capsule: {capsule.title}"
    owner_name = capsule.owner.name if capsule.owner else "Someone special"
    
    text_body = f"""
Dear {recipient.name},

You have received a Time Capsule from {owner_name}.

Title: {capsule.title}

Message:
{decrypted_message}

---
This message was created on {capsule.created_at.strftime('%B %d, %Y')} and scheduled to be delivered to you on this date.

With love and memories,
The Time Capsule Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .capsule-content {{ background: #fff; padding: 30px; border: 2px solid #667eea; border-radius: 10px; margin: 20px 0; }}
        .message {{ background: #f9f9f9; padding: 20px; border-left: 4px solid #667eea; margin: 15px 0; white-space: pre-wrap; }}
        .meta {{ color: #666; font-size: 14px; margin-top: 20px; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>You've Received a Time Capsule!</h1>
            <p>A message from the past, delivered to your present</p>
        </div>
        <div class="capsule-content">
            <p>Dear <strong>{recipient.name}</strong>,</p>
            <p>You have received a Time Capsule from <strong>{owner_name}</strong>.</p>
            
            <h2 style="color: #667eea;">{capsule.title}</h2>
            
            <div class="message">{decrypted_message}</div>
            
            <div class="meta">
                <p>📅 Created on: {capsule.created_at.strftime('%B %d, %Y')}</p>
                <p>⏰ Delivered on: {capsule.release_at.strftime('%B %d, %Y') if capsule.release_at else 'Now'}</p>
            </div>
        </div>
        <div class="footer">
            <p>With love and memories,<br>The Time Capsule Team</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, [recipient.email], text_body, html_body)


def send_capsule_reminder_email(capsule, days_until_release):
    """
    Send a reminder to the capsule owner about upcoming delivery.
    
    Args:
        capsule: Capsule model instance
        days_until_release: Number of days until the capsule is released
    """
    subject = f"Reminder: Your Time Capsule will be delivered in {days_until_release} days"
    
    text_body = f"""
Hello {capsule.owner.name},

This is a reminder that your time capsule "{capsule.title}" is scheduled to be delivered in {days_until_release} days.

Delivery Date: {capsule.release_at.strftime('%B %d, %Y')}
Recipients: {', '.join([r.recipient.name for r in capsule.recipients])}

If you need to make any changes, please log in to your Time Capsule account.

Best regards,
The Time Capsule Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .info-box {{ background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⏰ Delivery Reminder</h1>
            <p>Your time capsule will be delivered soon!</p>
        </div>
        <div class="content">
            <p>Hello <strong>{capsule.owner.name}</strong>,</p>
            <p>This is a reminder that your time capsule is scheduled to be delivered in <strong>{days_until_release} days</strong>.</p>
            
            <div class="info-box">
                <h3>{capsule.title}</h3>
                <p>📅 Delivery Date: {capsule.release_at.strftime('%B %d, %Y')}</p>
                <p>👥 Recipients: {', '.join([r.recipient.name for r in capsule.recipients])}</p>
            </div>
            
            <p>If you need to make any changes, please log in to your account.</p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Time Capsule Team</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, [capsule.owner.email], text_body, html_body)


def send_heartbeat_ping_email(user, confirmation_link):
    """
    Send a heartbeat check ("Are you still there?") email to a user.
    
    Args:
        user: User model instance
        confirmation_link: URL to confirm the user is still active
    """
    subject = "Time Capsule: Are you still there?"
    
    text_body = f"""
Hello {user.name},

This is a periodic check from Time Capsule to confirm you're still active.

Please click the link below to confirm you're still with us:
{confirmation_link}

If you don't respond within 30 days, your event-based time capsules may be released to your designated recipients.

Best regards,
The Time Capsule Team
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; text-align: center; }}
        .btn {{ display: inline-block; padding: 15px 30px; background: #11998e; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
        .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 14px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👋 Are You Still There?</h1>
        </div>
        <div class="content">
            <p>Hello <strong>{user.name}</strong>,</p>
            <p>This is a periodic check from Time Capsule to confirm you're still active.</p>
            
            <a href="{confirmation_link}" class="btn">Yes, I'm Still Here!</a>
            
            <div class="warning">
                <strong>⚠️ Important:</strong> If you don't respond within 30 days, your event-based time capsules may be released to your designated recipients.
            </div>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Time Capsule Team</p>
        </div>
    </div>
</body>
</html>
"""
    
    return send_email(subject, [user.email], text_body, html_body)


def send_guardian_verification_email(guardian, capsule, verify_url):
    """
    Send a guardian verification request email.

    The email contains confirm/deny links that route the guardian to the
    public GuardianVerify page in the frontend.

    Args:
        guardian: Guardian model instance
        capsule: Capsule model instance
        verify_url: Full URL to the frontend GuardianVerify page (includes token)
    """
    owner_name = capsule.owner.name if capsule.owner else 'Someone'
    subject = f"Action Required: Guardian Verification for \"{capsule.title}\""

    text_body = f"""
Hello {guardian.name},

{owner_name} has designated you as a trusted guardian for their Time Capsule.

You have been asked to verify a capsule release request:

  Capsule: {capsule.title}
  Created by: {owner_name}

Please visit the link below to confirm or deny this release:
{verify_url}

This link is unique to you. Please do not share it.

If you were not expecting this email, you can safely ignore it.

Best regards,
The Time Capsule Team
"""

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
    .capsule-box {{ background: white; border: 2px solid #667eea; border-radius: 8px; padding: 20px; margin: 20px 0; }}
    .btn-confirm {{ display: inline-block; padding: 14px 32px; background: #22c55e; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 8px 6px 8px 0; }}
    .btn-deny   {{ display: inline-block; padding: 14px 32px; background: #ef4444; color: white; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 8px 0; }}
    .note {{ font-size: 13px; color: #666; margin-top: 20px; }}
    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🛡️ Guardian Verification Request</h1>
      <p>Your trusted decision is needed</p>
    </div>
    <div class="content">
      <p>Hello <strong>{guardian.name}</strong>,</p>
      <p><strong>{owner_name}</strong> has designated you as a trusted guardian for their Time Capsule and is requesting your verification to release the following capsule:</p>

      <div class="capsule-box">
        <h3 style="color:#667eea; margin-top:0;">{capsule.title}</h3>
        <p>Created by: <strong>{owner_name}</strong></p>
      </div>

      <p>Please click one of the buttons below to record your decision:</p>

      <a href="{verify_url}" class="btn-confirm">Review &amp; Respond</a>

      <p class="note">
        ⚠️ This link is unique to you — please do not share it.<br>
        If you were not expecting this email, you can safely ignore it.
      </p>
    </div>
    <div class="footer">
      <p>Best regards,<br>The Time Capsule Team</p>
    </div>
  </div>
</body>
</html>
"""

    return send_email(subject, [guardian.email], text_body, html_body)


def send_guardian_response_notification(capsule, guardian, status, notes=''):
    """
    Notify the capsule owner that a guardian has responded.

    Args:
        capsule: Capsule model instance
        guardian: Guardian model instance
        status: 'CONFIRMED' or 'DENIED'
        notes: Optional notes from the guardian
    """
    owner = capsule.owner
    if not owner:
        return False

    action_word = 'confirmed' if status == 'CONFIRMED' else 'denied'
    action_emoji = '✅' if status == 'CONFIRMED' else '❌'
    subject = f"Guardian {action_word.capitalize()}: {capsule.title}"

    text_body = f"""
Hello {owner.name},

Your guardian {guardian.name} has {action_word} the release of your time capsule "{capsule.title}".

Guardian: {guardian.name} ({guardian.email})
Decision: {status}
{f'Notes: {notes}' if notes else ''}

Log in to your Time Capsule account to view the full audit log.

Best regards,
The Time Capsule Team
"""

    status_color = '#22c55e' if status == 'CONFIRMED' else '#ef4444'

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <style>
    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
    .header {{ background: {status_color}; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
    .decision-box {{ background: white; border-left: 4px solid {status_color}; padding: 15px 20px; margin: 15px 0; border-radius: 0 8px 8px 0; }}
    .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 13px; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{action_emoji} Guardian Response Received</h1>
    </div>
    <div class="content">
      <p>Hello <strong>{owner.name}</strong>,</p>
      <p>Your guardian <strong>{guardian.name}</strong> has responded to the verification request for <strong>"{capsule.title}"</strong>.</p>

      <div class="decision-box">
        <p><strong>Guardian:</strong> {guardian.name} ({guardian.email})</p>
        <p><strong>Decision:</strong> <span style="color:{status_color}; font-weight:bold;">{status}</span></p>
        {f'<p><strong>Notes:</strong> {notes}</p>' if notes else ''}
      </div>

      <p>Log in to your account to view the full audit trail and current verification status.</p>
    </div>
    <div class="footer">
      <p>Best regards,<br>The Time Capsule Team</p>
    </div>
  </div>
</body>
</html>
"""

    return send_email(subject, [owner.email], text_body, html_body)


def send_test_email(recipient_email):
    """
    Send a test email to verify email configuration.
    
    Args:
        recipient_email: Email address to send test to
    """
    subject = "Time Capsule - Test Email"
    
    text_body = """
Hello!

This is a test email from Time Capsule to verify that email configuration is working correctly.

If you received this email, your email setup is complete!

Best regards,
The Time Capsule Team
"""
    
    return send_email(subject, [recipient_email], text_body, async_send=False)
