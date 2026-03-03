"""
Security utilities for encryption, hashing, and JWT token management.
"""

import os
import secrets
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID

import bcrypt
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend

from config import settings


# ============================================================================
# Password Hashing
# ============================================================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), password_hash.encode())


# ============================================================================
# Encryption/Decryption
# ============================================================================

def derive_key_from_password(password: str, salt: bytes = None) -> tuple:
    """Derive encryption key from password using PBKDF2."""
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_data(data: bytes, key: bytes) -> bytes:
    """Encrypt data using Fernet (AES-128-CBC)."""
    f = Fernet(key)
    return f.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """Decrypt data using Fernet."""
    f = Fernet(key)
    return f.decrypt(encrypted_data)


def encrypt_string(data: str, key: bytes) -> str:
    """Encrypt string and return base64 encoded result."""
    encrypted = encrypt_data(data.encode(), key)
    return base64.b64encode(encrypted).decode()


def decrypt_string(encrypted_data: str, key: bytes) -> str:
    """Decrypt base64 encoded string."""
    encrypted = base64.b64decode(encrypted_data.encode())
    decrypted = decrypt_data(encrypted, key)
    return decrypted.decode()


# ============================================================================
# JWT Token Management
# ============================================================================

def create_access_token(
    subject: str,
    device_id: Optional[UUID] = None,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token."""
    if expires_delta is None:
        expires_delta = timedelta(hours=settings.jwt_expiration_hours)
    
    expire = datetime.utcnow() + expires_delta
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": settings.rp_id,
    }
    
    if device_id:
        to_encode["device_id"] = str(device_id)
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_subject(token: str) -> Optional[str]:
    """Extract subject from token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


# ============================================================================
# Challenge Generation
# ============================================================================

def generate_challenge(length: int = 32) -> str:
    """Generate cryptographically secure random challenge."""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode().rstrip("=")


def generate_device_fingerprint_hash(fingerprint: str) -> str:
    """Hash device fingerprint."""
    salt = os.urandom(16)
    kdf = PBKDF2(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    hash_value = kdf.derive(fingerprint.encode())
    return base64.b64encode(salt + hash_value).decode()


def verify_device_fingerprint(fingerprint: str, fingerprint_hash: str) -> bool:
    """Verify device fingerprint against hash."""
    try:
        decoded = base64.b64decode(fingerprint_hash.encode())
        salt = decoded[:16]
        stored_hash = decoded[16:]
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        computed_hash = kdf.derive(fingerprint.encode())
        
        return computed_hash == stored_hash
    except Exception:
        return False


# ============================================================================
# Utility Functions
# ============================================================================

def generate_random_string(length: int = 32) -> str:
    """Generate random string."""
    return secrets.token_urlsafe(length)


def constant_time_compare(a: str, b: str) -> bool:
    """Constant time string comparison to prevent timing attacks."""
    return secrets.compare_digest(a, b)
