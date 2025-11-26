"""
Database Models for Time Capsule Application

This module defines all SQLAlchemy ORM models for the application including:
- User: Account owners who create and manage time capsules
- Recipient: People who will receive capsules (e.g., children, friends)
- Guardian: Trusted verifiers for event-based capsule releases
- Capsule: Core entity containing encrypted messages and metadata
- CapsuleRecipient: Junction table for Capsule-Recipient many-to-many relationship
- CapsuleGuardian: Junction table for Capsule-Guardian many-to-many relationship
- Attachment: Files (photos, videos, documents) linked to capsules
- DeliveryLog: Records of capsule delivery attempts
- HeartbeatCheck: Periodic "still alive?" pings for inactivity-based triggers
"""

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(db.Model):
    """
    User model representing account owners.
    
    Users can create time capsules, manage recipients and guardians,
    and configure delivery settings for their digital legacy.
    
    Attributes:
        id: Primary key
        name: User's display name
        email: Unique email address for authentication
        password_hash: Securely hashed password
        role: User role ('user' or 'admin')
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")  # 'user', 'admin'
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    capsules = db.relationship("Capsule", back_populates="owner", cascade="all, delete-orphan")
    recipients = db.relationship("Recipient", back_populates="owner", cascade="all, delete-orphan")
    guardians = db.relationship("Guardian", back_populates="owner", cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", back_populates="owner", cascade="all, delete-orphan")
    heartbeat_checks = db.relationship("HeartbeatCheck", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """Hash and store the user's password securely."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excludes sensitive data)."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<User {self.email}>'


class Recipient(db.Model):
    """
    Recipient model for people who will receive time capsules.
    
    Recipients are managed by users and can be assigned to multiple capsules.
    They do not have accounts in the system - they receive content via email
    or other delivery methods.
    
    Attributes:
        id: Primary key
        owner_id: Foreign key to the user who created this recipient
        name: Recipient's name
        email: Recipient's email address for delivery
        relation: Relationship to the owner (e.g., 'daughter', 'friend')
    """
    __tablename__ = "recipients"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    relation = db.Column(db.String(100))  # e.g., 'daughter', 'friend', 'colleague'
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship("User", back_populates="recipients")
    capsules = db.relationship("CapsuleRecipient", back_populates="recipient", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert recipient to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'relation': self.relation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Recipient {self.name} ({self.email})>'


class Guardian(db.Model):
    """
    Guardian model for trusted verifiers.
    
    Guardians can confirm events (like the owner's death or incapacity)
    that trigger event-based capsule releases. They serve as trusted
    third parties in the delivery verification process.
    
    Attributes:
        id: Primary key
        owner_id: Foreign key to the user who designated this guardian
        name: Guardian's name
        email: Guardian's email address
        relation: Relationship to the owner (e.g., 'brother', 'lawyer')
    """
    __tablename__ = "guardians"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    relation = db.Column(db.String(100))  # e.g., 'brother', 'lawyer', 'executor'
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship("User", back_populates="guardians")
    capsules = db.relationship("CapsuleGuardian", back_populates="guardian", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert guardian to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'relation': self.relation,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Guardian {self.name} ({self.email})>'


class Capsule(db.Model):
    """
    Capsule model - the core entity of the application.
    
    A capsule contains encrypted messages, letters, or other content
    that will be delivered to recipients at a specified future date
    or upon certain events (like owner's death or prolonged inactivity).
    
    Attributes:
        id: Primary key
        owner_id: Foreign key to the user who created this capsule
        title: Capsule title/name
        message_encrypted: AES-encrypted message content
        release_type: 'TIME' for date-based, 'EVENT' for event-based release
        release_at: Scheduled release datetime (for TIME-based capsules)
        status: Current status (DRAFT, SCHEDULED, SENT, CANCELLED)
        requires_guardian: Whether guardian confirmation is needed for release
    """
    __tablename__ = "capsules"
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    title = db.Column(db.String(255), nullable=False)
    
    # Encrypted text content (AES encryption handled in business logic)
    message_encrypted = db.Column(db.Text, nullable=False)
    
    # Release type: 'TIME' = date-based, 'EVENT' = event-based (death/inactivity)
    release_type = db.Column(db.String(20), nullable=False, default="TIME")
    
    # For TIME-based capsules (nullable for EVENT-based)
    release_at = db.Column(db.DateTime, nullable=True)
    
    # Status: DRAFT, SCHEDULED, SENT, CANCELLED
    status = db.Column(db.String(20), nullable=False, default="DRAFT")
    
    # Whether guardian confirmation is required before release
    requires_guardian = db.Column(db.Boolean, nullable=False, default=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = db.relationship("User", back_populates="capsules")
    recipients = db.relationship("CapsuleRecipient", back_populates="capsule", cascade="all, delete-orphan")
    guardians = db.relationship("CapsuleGuardian", back_populates="capsule", cascade="all, delete-orphan")
    attachments = db.relationship("Attachment", back_populates="capsule", cascade="all, delete-orphan")
    delivery_logs = db.relationship("DeliveryLog", back_populates="capsule", cascade="all, delete-orphan")
    
    # Indexes for optimizing scheduling queries
    __table_args__ = (
        db.Index("ix_capsule_owner_status", "owner_id", "status"),
        db.Index("ix_capsule_release", "release_type", "release_at"),
    )
    
    def to_dict(self):
        """Convert capsule to dictionary (excludes encrypted content)."""
        return {
            'id': self.id,
            'title': self.title,
            'release_type': self.release_type,
            'release_at': self.release_at.isoformat() if self.release_at else None,
            'status': self.status,
            'requires_guardian': self.requires_guardian,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Capsule {self.id}: {self.title}>'


class CapsuleRecipient(db.Model):
    """
    Junction table for many-to-many relationship between Capsule and Recipient.
    
    Allows a capsule to be sent to multiple recipients and a recipient
    to receive multiple capsules from the same owner.
    """
    __tablename__ = "capsule_recipients"
    
    id = db.Column(db.Integer, primary_key=True)
    
    capsule_id = db.Column(db.Integer, db.ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipients.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    capsule = db.relationship("Capsule", back_populates="recipients")
    recipient = db.relationship("Recipient", back_populates="capsules")
    
    __table_args__ = (
        db.UniqueConstraint("capsule_id", "recipient_id", name="uq_capsule_recipient"),
    )
    
    def __repr__(self):
        return f'<CapsuleRecipient capsule={self.capsule_id} recipient={self.recipient_id}>'


class CapsuleGuardian(db.Model):
    """
    Junction table for many-to-many relationship between Capsule and Guardian.
    
    Allows a capsule to have multiple guardians who can verify release
    conditions, and a guardian to oversee multiple capsules.
    """
    __tablename__ = "capsule_guardians"
    
    id = db.Column(db.Integer, primary_key=True)
    
    capsule_id = db.Column(db.Integer, db.ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False)
    guardian_id = db.Column(db.Integer, db.ForeignKey("guardians.id", ondelete="CASCADE"), nullable=False)
    
    # Relationships
    capsule = db.relationship("Capsule", back_populates="guardians")
    guardian = db.relationship("Guardian", back_populates="capsules")
    
    __table_args__ = (
        db.UniqueConstraint("capsule_id", "guardian_id", name="uq_capsule_guardian"),
    )
    
    def __repr__(self):
        return f'<CapsuleGuardian capsule={self.capsule_id} guardian={self.guardian_id}>'


class Attachment(db.Model):
    """
    Attachment model for files linked to capsules.
    
    Supports photos, videos, documents, and other file types.
    Files are stored separately (local filesystem or cloud storage)
    with metadata tracked in the database.
    
    Attributes:
        id: Primary key
        capsule_id: Foreign key to the associated capsule
        owner_id: Foreign key to the user who uploaded the attachment
        original_filename: Original name of the uploaded file
        storage_path: Path/URL where the file is stored
        mime_type: MIME type of the file
        size_bytes: File size in bytes
    """
    __tablename__ = "attachments"
    
    id = db.Column(db.Integer, primary_key=True)
    
    capsule_id = db.Column(db.Integer, db.ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    original_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)  # Local path or cloud URL
    mime_type = db.Column(db.String(100))
    size_bytes = db.Column(db.BigInteger)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    capsule = db.relationship("Capsule", back_populates="attachments")
    owner = db.relationship("User", back_populates="attachments")
    
    def to_dict(self):
        """Convert attachment to dictionary."""
        return {
            'id': self.id,
            'original_filename': self.original_filename,
            'mime_type': self.mime_type,
            'size_bytes': self.size_bytes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Attachment {self.id}: {self.original_filename}>'


class DeliveryLog(db.Model):
    """
    DeliveryLog model for tracking capsule delivery attempts.
    
    Records all attempts to deliver capsules to recipients, including
    successful deliveries and failures with error messages.
    
    Attributes:
        id: Primary key
        capsule_id: Foreign key to the capsule being delivered
        recipient_id: Foreign key to the recipient (nullable if recipient deleted)
        scheduled_for: When delivery was scheduled
        delivered_at: When delivery was completed (null if pending/failed)
        status: PENDING, SENT, or FAILED
        error_message: Error details if delivery failed
    """
    __tablename__ = "delivery_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    
    capsule_id = db.Column(db.Integer, db.ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey("recipients.id", ondelete="SET NULL"), nullable=True)
    
    scheduled_for = db.Column(db.DateTime, nullable=False)
    delivered_at = db.Column(db.DateTime, nullable=True)
    
    # Status: PENDING, SENT, FAILED
    status = db.Column(db.String(20), nullable=False, default="PENDING")
    
    error_message = db.Column(db.Text, nullable=True)
    
    # Relationships
    capsule = db.relationship("Capsule", back_populates="delivery_logs")
    recipient = db.relationship("Recipient")
    
    __table_args__ = (
        db.Index("ix_delivery_status_scheduled", "status", "scheduled_for"),
    )
    
    def to_dict(self):
        """Convert delivery log to dictionary."""
        return {
            'id': self.id,
            'capsule_id': self.capsule_id,
            'recipient_id': self.recipient_id,
            'scheduled_for': self.scheduled_for.isoformat() if self.scheduled_for else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'status': self.status,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<DeliveryLog {self.id}: capsule={self.capsule_id} status={self.status}>'


class HeartbeatCheck(db.Model):
    """
    HeartbeatCheck model for "still alive?" verification.
    
    Used for inactivity-based triggers where capsules are released
    if the owner doesn't respond to periodic ping checks.
    
    Attributes:
        id: Primary key
        user_id: Foreign key to the user being checked
        ping_sent_at: When the check ping was sent
        ping_confirmed_at: When the user confirmed they're active (null if not confirmed)
        status: AWAITING, CONFIRMED, or EXPIRED
    """
    __tablename__ = "heartbeat_checks"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    ping_sent_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ping_confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Status: AWAITING, CONFIRMED, EXPIRED
    status = db.Column(db.String(20), nullable=False, default="AWAITING")
    
    # Relationship
    user = db.relationship("User", back_populates="heartbeat_checks")
    
    __table_args__ = (
        db.Index("ix_heartbeat_status", "status"),
    )
    
    def to_dict(self):
        """Convert heartbeat check to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ping_sent_at': self.ping_sent_at.isoformat() if self.ping_sent_at else None,
            'ping_confirmed_at': self.ping_confirmed_at.isoformat() if self.ping_confirmed_at else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<HeartbeatCheck {self.id}: user={self.user_id} status={self.status}>'
