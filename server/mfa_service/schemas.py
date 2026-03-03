"""
Pydantic schemas for request/response validation.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ============================================================================
# User Schemas
# ============================================================================

class UserRegisterRequest(BaseModel):
    """User registration request."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    device_name: Optional[str] = None


class UserResponse(BaseModel):
    """User response."""
    id: UUID
    username: str
    email: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# Device Schemas
# ============================================================================

class DeviceRegisterRequest(BaseModel):
    """Device registration request."""
    device_name: str
    device_type: str  # iOS, Android, Web
    device_os: str
    device_model: str
    device_fingerprint: str


class DeviceResponse(BaseModel):
    """Device response."""
    id: UUID
    device_name: str
    device_type: str
    device_os: str
    device_model: str
    is_trusted: bool
    last_seen_at: Optional[datetime]
    registered_at: datetime

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    """Device list response."""
    devices: List[DeviceResponse]


class DeviceTrustRequest(BaseModel):
    """Device trust update request."""
    is_trusted: bool


# ============================================================================
# FIDO2/WebAuthn Schemas
# ============================================================================

class FIDO2RegistrationBeginRequest(BaseModel):
    """FIDO2 registration begin request."""
    user_id: UUID


class FIDO2RegistrationBeginResponse(BaseModel):
    """FIDO2 registration begin response."""
    challenge: str
    rp: dict
    user: dict
    pubKeyCredParams: list
    timeout: int
    attestation: str


class FIDO2RegistrationCompleteRequest(BaseModel):
    """FIDO2 registration complete request."""
    user_id: UUID
    attestation_object: str
    client_data_json: str
    device_id: Optional[UUID] = None


class FIDO2RegistrationCompleteResponse(BaseModel):
    """FIDO2 registration complete response."""
    credential_id: UUID
    status: str
    message: str


class FIDO2AuthenticationBeginRequest(BaseModel):
    """FIDO2 authentication begin request."""
    username: str


class FIDO2AuthenticationBeginResponse(BaseModel):
    """FIDO2 authentication begin response."""
    challenge: str
    timeout: int
    userVerification: str
    allowCredentials: list


class FIDO2AuthenticationCompleteRequest(BaseModel):
    """FIDO2 authentication complete request."""
    username: str
    assertion_object: str
    client_data_json: str
    device_id: Optional[UUID] = None


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


# ============================================================================
# Biometric Schemas
# ============================================================================

class BiometricRegisterRequest(BaseModel):
    """Biometric method registration request."""
    device_id: UUID
    method_type: str  # fingerprint, face, iris
    biometric_data: str  # Encrypted template


class BiometricRegisterResponse(BaseModel):
    """Biometric method registration response."""
    biometric_id: UUID
    method: str
    status: str


class BiometricVerifyRequest(BaseModel):
    """Biometric verification request."""
    device_id: UUID
    method_type: str
    biometric_input: str  # Encrypted template


class BiometricVerifyResponse(BaseModel):
    """Biometric verification response."""
    verified: bool
    confidence: float


class BiometricMethodResponse(BaseModel):
    """Biometric method response."""
    id: UUID
    method_type: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


class BiometricMethodsListResponse(BaseModel):
    """Biometric methods list response."""
    methods: List[BiometricMethodResponse]


# ============================================================================
# MFA Session Schemas
# ============================================================================

class MFAVerifyRequest(BaseModel):
    """MFA verification request."""
    challenge: str
    verification_data: str


class MFAVerifyResponse(BaseModel):
    """MFA verification response."""
    verified: bool
    message: str


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response."""
    error: str
    message: str
    status_code: int


# ============================================================================
# Audit Log Schemas
# ============================================================================

class AuditLogResponse(BaseModel):
    """Audit log response."""
    id: UUID
    user_id: Optional[UUID]
    device_id: Optional[UUID]
    action: str
    status: str
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class AuditLogsListResponse(BaseModel):
    """Audit logs list response."""
    logs: List[AuditLogResponse]
    total: int
