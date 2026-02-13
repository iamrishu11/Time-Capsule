"""
Services package for Time Capsule application.

Contains business logic services including:
- email_service: Email sending functionality
- scheduler_service: Capsule delivery scheduling
"""

from app.services.email_service import (
    send_email,
    send_welcome_email,
    send_capsule_delivery_email,
    send_capsule_reminder_email,
    send_heartbeat_ping_email,
    send_test_email,
)
