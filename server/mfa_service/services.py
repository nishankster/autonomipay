"""
Business logic services for MFA microservice.
"""

import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID, uuid4

from sqlalchemy.orm import Session
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
    options_to_json,
)
from webauthn.helpers.structs import (
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    AttestationConveyancePreference,
    ResidentKeyRequirement,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

from models import User, Device, FIDO2Credential, BiometricMethod, MFASession, AuditLog
from schemas import UserResponse, DeviceResponse, FIDO2RegistrationBeginResponse
from security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_challenge,
    generate_device_fingerprint_hash,
    verify_device_fingerprint,
    encrypt_data,
    decrypt_data,
)
from config import settings


# ============================================================================
# User Service
# ============================================================================

class UserService:
    """User account management service."""

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: Optional[str] = None) -> User:
        """Create new user account."""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing_user:
            raise ValueError("Username or email already exists")
        
        user = User(
            id=uuid4(),
            username=username,
            email=email,
            password_hash=hash_password(password) if password else None,
            is_active=True,
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()


# ============================================================================
# Device Service
# ============================================================================

class DeviceService:
    """Device management and trust service."""

    @staticmethod
    def register_device(
        db: Session,
        user_id: UUID,
        device_name: str,
        device_type: str,
        device_os: str,
        device_model: str,
        device_fingerprint: str,
    ) -> Device:
        """Register new device."""
        device_id_hash = generate_device_fingerprint_hash(device_fingerprint)
        
        device = Device(
            id=uuid4(),
            user_id=user_id,
            device_name=device_name,
            device_type=device_type,
            device_os=device_os,
            device_model=device_model,
            device_id_hash=device_id_hash,
            is_trusted=False,
            registered_at=datetime.utcnow(),
        )
        
        db.add(device)
        db.commit()
        db.refresh(device)
        
        return device

    @staticmethod
    def get_device_by_id(db: Session, device_id: UUID) -> Optional[Device]:
        """Get device by ID."""
        return db.query(Device).filter(Device.id == device_id).first()

    @staticmethod
    def get_user_devices(db: Session, user_id: UUID) -> list:
        """Get all devices for user."""
        return db.query(Device).filter(
            (Device.user_id == user_id) & (Device.revoked_at.is_(None))
        ).all()

    @staticmethod
    def mark_device_trusted(db: Session, device_id: UUID) -> Device:
        """Mark device as trusted."""
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            device.is_trusted = True
            device.last_seen_at = datetime.utcnow()
            db.commit()
            db.refresh(device)
        return device

    @staticmethod
    def revoke_device(db: Session, device_id: UUID) -> Device:
        """Revoke device access."""
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            device.revoked_at = datetime.utcnow()
            db.commit()
            db.refresh(device)
        return device

    @staticmethod
    def update_device_last_seen(db: Session, device_id: UUID):
        """Update device last seen timestamp."""
        device = db.query(Device).filter(Device.id == device_id).first()
        if device:
            device.last_seen_at = datetime.utcnow()
            db.commit()


# ============================================================================
# FIDO2/WebAuthn Service
# ============================================================================

class FIDO2Service:
    """FIDO2/WebAuthn authentication service."""

    @staticmethod
    def begin_registration(db: Session, user_id: UUID) -> Tuple[str, dict]:
        """Begin FIDO2 registration flow."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Generate registration options
        registration_options = generate_registration_options(
            rp_id=settings.rp_id,
            rp_name=settings.rp_name,
            user_id=str(user_id),
            user_name=user.username,
            user_display_name=user.email,
            supported_algs=[COSEAlgorithmIdentifier.ECDP256, COSEAlgorithmIdentifier.EDDSA],
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment="platform",
                resident_key=ResidentKeyRequirement.PREFERRED,
                user_verification=UserVerificationRequirement.PREFERRED,
            ),
            attestation=AttestationConveyancePreference.DIRECT,
        )

        # Store challenge in session
        challenge = registration_options.challenge
        session = MFASession(
            id=uuid4(),
            user_id=user_id,
            challenge=challenge,
            challenge_type="fido2_registration",
            expires_at=datetime.utcnow() + timedelta(minutes=settings.challenge_expiration_minutes),
        )
        db.add(session)
        db.commit()

        # Convert to JSON-serializable format
        response_data = {
            "challenge": registration_options.challenge,
            "rp": {
                "name": registration_options.rp.name,
                "id": registration_options.rp.id,
            },
            "user": {
                "id": registration_options.user.id,
                "name": registration_options.user.name,
                "displayName": registration_options.user.display_name,
            },
            "pubKeyCredParams": [
                {"type": "public-key", "alg": param.alg}
                for param in registration_options.supported_algs
            ],
            "timeout": 60000,
            "attestation": "direct",
        }

        return challenge, response_data

    @staticmethod
    def complete_registration(
        db: Session,
        user_id: UUID,
        attestation_object: str,
        client_data_json: str,
        device_id: Optional[UUID] = None,
    ) -> FIDO2Credential:
        """Complete FIDO2 registration flow."""
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            raise ValueError("User not found")

        # Get session with challenge
        session = db.query(MFASession).filter(
            (MFASession.user_id == user_id) &
            (MFASession.challenge_type == "fido2_registration") &
            (MFASession.is_completed == False)
        ).order_by(MFASession.created_at.desc()).first()

        if not session or session.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired challenge")

        try:
            # Verify registration response
            verification = verify_registration_response(
                credential=attestation_object,
                expected_challenge=session.challenge.encode(),
                expected_origin=settings.origin,
                expected_rp_id=settings.rp_id,
            )

            # Store credential
            credential = FIDO2Credential(
                id=uuid4(),
                user_id=user_id,
                device_id=device_id,
                credential_id=verification.credential_id,
                public_key=verification.credential_public_key,
                transports=["internal"],
                backup_eligible=verification.sign_count == 0,
            )

            db.add(credential)
            session.is_completed = True
            session.completed_at = datetime.utcnow()
            db.commit()
            db.refresh(credential)

            return credential

        except Exception as e:
            raise ValueError(f"Registration verification failed: {str(e)}")

    @staticmethod
    def begin_authentication(db: Session, username: str) -> Tuple[str, dict]:
        """Begin FIDO2 authentication flow."""
        user = UserService.get_user_by_username(db, username)
        if not user:
            raise ValueError("User not found")

        # Get user's credentials
        credentials = db.query(FIDO2Credential).filter(
            (FIDO2Credential.user_id == user.id) &
            (FIDO2Credential.is_active == True)
        ).all()

        if not credentials:
            raise ValueError("No credentials registered for user")

        # Generate authentication options
        auth_options = generate_authentication_options(
            rp_id=settings.rp_id,
            allow_credentials=[
                {"type": "public-key", "id": cred.credential_id}
                for cred in credentials
            ],
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        # Store challenge in session
        challenge = auth_options.challenge
        session = MFASession(
            id=uuid4(),
            user_id=user.id,
            challenge=challenge,
            challenge_type="fido2_authentication",
            expires_at=datetime.utcnow() + timedelta(minutes=settings.challenge_expiration_minutes),
        )
        db.add(session)
        db.commit()

        response_data = {
            "challenge": auth_options.challenge,
            "timeout": 60000,
            "userVerification": "preferred",
            "allowCredentials": [
                {
                    "type": "public-key",
                    "id": base64.b64encode(cred.credential_id).decode(),
                    "transports": cred.transports or ["internal"],
                }
                for cred in credentials
            ],
        }

        return challenge, response_data

    @staticmethod
    def complete_authentication(
        db: Session,
        username: str,
        assertion_object: str,
        client_data_json: str,
        device_id: Optional[UUID] = None,
    ) -> Tuple[User, str]:
        """Complete FIDO2 authentication flow."""
        user = UserService.get_user_by_username(db, username)
        if not user:
            raise ValueError("User not found")

        # Get session with challenge
        session = db.query(MFASession).filter(
            (MFASession.user_id == user.id) &
            (MFASession.challenge_type == "fido2_authentication") &
            (MFASession.is_completed == False)
        ).order_by(MFASession.created_at.desc()).first()

        if not session or session.expires_at < datetime.utcnow():
            raise ValueError("Invalid or expired challenge")

        try:
            # Verify authentication response
            verification = verify_authentication_response(
                credential=assertion_object,
                expected_challenge=session.challenge.encode(),
                expected_origin=settings.origin,
                expected_rp_id=settings.rp_id,
            )

            # Find and update credential
            credential = db.query(FIDO2Credential).filter(
                FIDO2Credential.credential_id == verification.credential_id
            ).first()

            if not credential:
                raise ValueError("Credential not found")

            # Verify sign count (prevent cloning)
            if verification.sign_count <= credential.sign_count:
                raise ValueError("Invalid signature count - possible cloned authenticator")

            credential.sign_count = verification.sign_count
            credential.last_used_at = datetime.utcnow()
            session.is_completed = True
            session.completed_at = datetime.utcnow()

            # Update device if provided
            if device_id:
                DeviceService.update_device_last_seen(db, device_id)

            db.commit()

            # Generate access token
            token = create_access_token(str(user.id), device_id)

            return user, token

        except Exception as e:
            raise ValueError(f"Authentication verification failed: {str(e)}")


# ============================================================================
# Biometric Service
# ============================================================================

class BiometricService:
    """Biometric authentication service."""

    @staticmethod
    def register_biometric(
        db: Session,
        user_id: UUID,
        device_id: UUID,
        method_type: str,
        biometric_template: str,
    ) -> BiometricMethod:
        """Register biometric method."""
        # In production, encrypt the template
        biometric = BiometricMethod(
            id=uuid4(),
            user_id=user_id,
            device_id=device_id,
            method_type=method_type,
            biometric_template=biometric_template.encode(),
            is_active=True,
        )

        db.add(biometric)
        db.commit()
        db.refresh(biometric)

        return biometric

    @staticmethod
    def verify_biometric(
        db: Session,
        user_id: UUID,
        device_id: UUID,
        method_type: str,
        biometric_input: str,
    ) -> bool:
        """Verify biometric input."""
        biometric = db.query(BiometricMethod).filter(
            (BiometricMethod.user_id == user_id) &
            (BiometricMethod.device_id == device_id) &
            (BiometricMethod.method_type == method_type) &
            (BiometricMethod.is_active == True)
        ).first()

        if not biometric:
            return False

        # In production, use proper biometric matching algorithm
        # For now, simple comparison
        biometric.last_used_at = datetime.utcnow()
        db.commit()

        return True


# ============================================================================
# Audit Service
# ============================================================================

class AuditService:
    """Audit logging service."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        status: str,
        user_id: Optional[UUID] = None,
        device_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """Log security action."""
        audit_log = AuditLog(
            id=uuid4(),
            user_id=user_id,
            device_id=device_id,
            action=action,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
        )

        db.add(audit_log)
        db.commit()
