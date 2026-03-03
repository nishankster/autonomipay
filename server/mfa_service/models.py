"""
Database models for MFA microservice using SQLAlchemy ORM.
"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, String, Boolean, DateTime, Integer, LargeBinary, ForeignKey, ARRAY, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

Base = declarative_base()


class User(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # For backup/recovery only
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    credentials = relationship("FIDO2Credential", back_populates="user", cascade="all, delete-orphan")
    biometric_methods = relationship("BiometricMethod", back_populates="user", cascade="all, delete-orphan")
    mfa_sessions = relationship("MFASession", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )


class Device(Base):
    """Device registration and trust management model."""
    __tablename__ = "devices"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # iOS, Android, Web
    device_os = Column(String(255), nullable=True)
    device_model = Column(String(255), nullable=True)
    device_id_hash = Column(String(255), unique=True, nullable=False, index=True)
    is_trusted = Column(Boolean, default=False, nullable=False)
    last_seen_at = Column(DateTime, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="devices")
    credentials = relationship("FIDO2Credential", back_populates="device", cascade="all, delete-orphan")
    biometric_methods = relationship("BiometricMethod", back_populates="device", cascade="all, delete-orphan")
    mfa_sessions = relationship("MFASession", back_populates="device", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="device", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_device_user_id', 'user_id'),
        Index('idx_device_id_hash', 'device_id_hash'),
    )


class FIDO2Credential(Base):
    """FIDO2/WebAuthn credential storage model."""
    __tablename__ = "fido2_credentials"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(PG_UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    credential_id = Column(LargeBinary, unique=True, nullable=False, index=True)
    public_key = Column(LargeBinary, nullable=False)  # Encrypted
    sign_count = Column(Integer, default=0, nullable=False)
    transports = Column(ARRAY(String), nullable=True)  # usb, nfc, ble, internal
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    backup_eligible = Column(Boolean, default=False, nullable=False)
    backup_state = Column(Boolean, default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="credentials")
    device = relationship("Device", back_populates="credentials")

    __table_args__ = (
        Index('idx_credential_user_id', 'user_id'),
        Index('idx_credential_id', 'credential_id'),
    )


class BiometricMethod(Base):
    """Biometric authentication methods model."""
    __tablename__ = "biometric_methods"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(PG_UUID(as_uuid=True), ForeignKey("devices.id"), nullable=False)
    method_type = Column(String(50), nullable=False)  # fingerprint, face, iris
    biometric_template = Column(LargeBinary, nullable=False)  # Encrypted
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="biometric_methods")
    device = relationship("Device", back_populates="biometric_methods")

    __table_args__ = (
        Index('idx_biometric_user_id', 'user_id'),
        Index('idx_biometric_device_id', 'device_id'),
    )


class MFASession(Base):
    """MFA session and challenge management model."""
    __tablename__ = "mfa_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    device_id = Column(PG_UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    challenge = Column(String(255), unique=True, nullable=False, index=True)
    challenge_type = Column(String(50), nullable=False)  # fido2, biometric, backup
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="mfa_sessions")
    device = relationship("Device", back_populates="mfa_sessions")

    __table_args__ = (
        Index('idx_mfa_session_user_id', 'user_id'),
        Index('idx_mfa_session_challenge', 'challenge'),
    )


class AuditLog(Base):
    """Audit logging for security events."""
    __tablename__ = "audit_logs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    device_id = Column(PG_UUID(as_uuid=True), ForeignKey("devices.id"), nullable=True)
    action = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)  # success, failure
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="audit_logs")
    device = relationship("Device", back_populates="audit_logs")

    __table_args__ = (
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_device_id', 'device_id'),
        Index('idx_audit_created_at', 'created_at'),
    )
