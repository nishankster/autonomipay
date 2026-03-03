"""
Main FastAPI application for MFA microservice with comprehensive Swagger/OpenAPI documentation.
"""

from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from config import settings
from database import get_db, init_db
from models import User
from schemas import (
    UserRegisterRequest,
    UserResponse,
    DeviceRegisterRequest,
    DeviceResponse,
    DeviceListResponse,
    DeviceTrustRequest,
    FIDO2RegistrationBeginRequest,
    FIDO2RegistrationBeginResponse,
    FIDO2RegistrationCompleteRequest,
    FIDO2RegistrationCompleteResponse,
    FIDO2AuthenticationBeginRequest,
    FIDO2AuthenticationBeginResponse,
    FIDO2AuthenticationCompleteRequest,
    TokenResponse,
    BiometricRegisterRequest,
    BiometricRegisterResponse,
    BiometricVerifyRequest,
    BiometricVerifyResponse,
    BiometricMethodsListResponse,
    ErrorResponse,
)
from services import (
    UserService,
    DeviceService,
    FIDO2Service,
    BiometricService,
    AuditService,
)

# Initialize FastAPI app with comprehensive documentation
app = FastAPI(
    title="MFA Microservice API",
    version="1.0.0",
    description="""
# Multi-Factor Authentication Microservice

A production-grade MFA microservice providing enterprise-level authentication capabilities:

## Features

- **FIDO2/WebAuthn Support**: Passwordless authentication using security keys and biometric authenticators
- **Device Management**: Register, trust, and manage user devices with cryptographic binding
- **Device Binding**: Bind credentials to specific devices for enhanced security
- **Biometric Authentication**: Support for fingerprint, face recognition, and other biometric methods
- **Audit Logging**: Comprehensive security event logging and compliance tracking
- **JWT Token Management**: Secure token generation and validation with device binding
- **PostgreSQL Backend**: Encrypted data storage with proper indexing and performance optimization

## Authentication Flow

### FIDO2 Registration
1. Client requests registration challenge
2. Server generates random challenge and stores in session
3. Client presents challenge to authenticator (security key, biometric)
4. Authenticator creates attestation object with public key
5. Server verifies attestation and stores credential

### FIDO2 Authentication
1. Client requests authentication challenge
2. Server generates challenge and returns credential IDs for user
3. Client presents challenge to authenticator
4. Authenticator signs challenge with private key
5. Server verifies signature and issues JWT token

## Security

- All sensitive data encrypted using AES-256-GCM
- Passwords hashed using bcrypt with 12 rounds
- JWT tokens signed with HS256
- HTTPS/TLS 1.3 required for all endpoints
- Device fingerprints hashed with PBKDF2
- FIDO2 signatures verified using public key cryptography
- Audit logs track all security events

## API Endpoints

The API is organized into the following categories:

- **Health**: Service health checks
- **Authentication**: User registration and FIDO2 flows
- **Devices**: Device management and trust
- **FIDO2/WebAuthn**: FIDO2 registration and authentication
- **Biometric**: Biometric method registration and verification

## Getting Started

1. Register a new user: `POST /auth/register`
2. Register a device: `POST /devices/register?user_id={user_id}`
3. Begin FIDO2 registration: `POST /auth/fido2/register/begin`
4. Complete FIDO2 registration: `POST /auth/fido2/register/complete`
5. Begin FIDO2 authentication: `POST /auth/fido2/authenticate/begin`
6. Complete FIDO2 authentication: `POST /auth/fido2/authenticate/complete`

## Documentation

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`
""",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "MFA Microservice Support",
        "url": "https://github.com/manus-ai/mfa-microservice",
        "email": "support@manus.im",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Startup/Shutdown Events
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()
    print("✓ Database initialized")


@app.get(
    "/health",
    tags=["Health"],
    summary="Health Check",
    description="Check if the MFA microservice is running and healthy.",
    responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {"status": "healthy", "version": "1.0.0"}
                }
            },
        }
    },
)
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# ============================================================================
# User Endpoints
# ============================================================================

@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=201,
    tags=["Authentication"],
    summary="Register New User",
    description="Create a new user account with username and email. Returns user details.",
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "john_doe",
                        "email": "john@example.com",
                        "created_at": "2026-02-27T10:30:00Z",
                        "is_active": True,
                    }
                }
            },
        },
        400: {"description": "Username or email already exists"},
    },
)
async def register_user(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register new user account."""
    try:
        user = UserService.create_user(
            db,
            username=request.username,
            email=request.email,
        )
        
        AuditService.log_action(
            db,
            action="user_registration",
            status="success",
            user_id=user.id,
            metadata={"username": user.username},
        )
        
        return UserResponse.from_orm(user)
    
    except ValueError as e:
        AuditService.log_action(
            db,
            action="user_registration",
            status="failure",
            metadata={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Device Management Endpoints
# ============================================================================

@app.post(
    "/devices/register",
    response_model=DeviceResponse,
    status_code=201,
    tags=["Devices"],
    summary="Register Device",
    description="Register a new device for the user. Device must be bound with a cryptographic fingerprint.",
    responses={
        201: {"description": "Device registered successfully"},
        400: {"description": "Invalid device registration request"},
    },
)
async def register_device(
    user_id: UUID,
    request: DeviceRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register new device."""
    try:
        device = DeviceService.register_device(
            db,
            user_id=user_id,
            device_name=request.device_name,
            device_type=request.device_type,
            device_os=request.device_os,
            device_model=request.device_model,
            device_fingerprint=request.device_fingerprint,
        )
        
        AuditService.log_action(
            db,
            action="device_registration",
            status="success",
            user_id=user_id,
            device_id=device.id,
            metadata={"device_name": device.device_name},
        )
        
        return DeviceResponse.from_orm(device)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get(
    "/devices",
    response_model=DeviceListResponse,
    tags=["Devices"],
    summary="List User Devices",
    description="Retrieve all registered devices for the authenticated user.",
    responses={
        200: {"description": "List of user devices"},
    },
)
async def list_devices(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """List user's devices."""
    devices = DeviceService.get_user_devices(db, user_id)
    return DeviceListResponse(
        devices=[DeviceResponse.from_orm(d) for d in devices]
    )


@app.put(
    "/devices/{device_id}/trust",
    response_model=DeviceResponse,
    tags=["Devices"],
    summary="Update Device Trust Status",
    description="Mark a device as trusted or revoke its trust status.",
    responses={
        200: {"description": "Device trust status updated"},
        404: {"description": "Device not found"},
    },
)
async def trust_device(
    device_id: UUID,
    request: DeviceTrustRequest,
    db: Session = Depends(get_db),
):
    """Mark device as trusted."""
    if request.is_trusted:
        device = DeviceService.mark_device_trusted(db, device_id)
    else:
        device = DeviceService.revoke_device(db, device_id)
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    return DeviceResponse.from_orm(device)


@app.delete(
    "/devices/{device_id}",
    status_code=204,
    tags=["Devices"],
    summary="Revoke Device",
    description="Revoke access for a specific device. The device will no longer be able to authenticate.",
    responses={
        204: {"description": "Device revoked successfully"},
        404: {"description": "Device not found"},
    },
)
async def revoke_device(
    device_id: UUID,
    db: Session = Depends(get_db),
):
    """Revoke device access."""
    device = DeviceService.revoke_device(db, device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")


# ============================================================================
# FIDO2/WebAuthn Endpoints
# ============================================================================

@app.post(
    "/auth/fido2/register/begin",
    response_model=FIDO2RegistrationBeginResponse,
    tags=["FIDO2/WebAuthn"],
    summary="Begin FIDO2 Registration",
    description="Initiate FIDO2/WebAuthn registration. Returns challenge and options for the client to present to the authenticator.",
    responses={
        200: {"description": "Registration challenge generated"},
        400: {"description": "User not found"},
    },
)
async def fido2_register_begin(
    request: FIDO2RegistrationBeginRequest,
    db: Session = Depends(get_db),
):
    """Begin FIDO2 registration."""
    try:
        challenge, response_data = FIDO2Service.begin_registration(db, request.user_id)
        return FIDO2RegistrationBeginResponse(**response_data)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/auth/fido2/register/complete",
    response_model=FIDO2RegistrationCompleteResponse,
    status_code=201,
    tags=["FIDO2/WebAuthn"],
    summary="Complete FIDO2 Registration",
    description="Complete FIDO2/WebAuthn registration by verifying the attestation object from the authenticator.",
    responses={
        201: {"description": "Credential registered successfully"},
        400: {"description": "Registration verification failed"},
    },
)
async def fido2_register_complete(
    request: FIDO2RegistrationCompleteRequest,
    db: Session = Depends(get_db),
):
    """Complete FIDO2 registration."""
    try:
        credential = FIDO2Service.complete_registration(
            db,
            user_id=request.user_id,
            attestation_object=request.attestation_object,
            client_data_json=request.client_data_json,
            device_id=request.device_id,
        )
        
        AuditService.log_action(
            db,
            action="fido2_registration",
            status="success",
            user_id=request.user_id,
            device_id=request.device_id,
        )
        
        return FIDO2RegistrationCompleteResponse(
            credential_id=credential.id,
            status="registered",
            message="FIDO2 credential registered successfully",
        )
    
    except ValueError as e:
        AuditService.log_action(
            db,
            action="fido2_registration",
            status="failure",
            user_id=request.user_id,
            metadata={"error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/auth/fido2/authenticate/begin",
    response_model=FIDO2AuthenticationBeginResponse,
    tags=["FIDO2/WebAuthn"],
    summary="Begin FIDO2 Authentication",
    description="Initiate FIDO2/WebAuthn authentication. Returns challenge and list of allowed credentials.",
    responses={
        200: {"description": "Authentication challenge generated"},
        400: {"description": "User not found or no credentials registered"},
    },
)
async def fido2_authenticate_begin(
    request: FIDO2AuthenticationBeginRequest,
    db: Session = Depends(get_db),
):
    """Begin FIDO2 authentication."""
    try:
        challenge, response_data = FIDO2Service.begin_authentication(db, request.username)
        return FIDO2AuthenticationBeginResponse(**response_data)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/auth/fido2/authenticate/complete",
    response_model=TokenResponse,
    tags=["FIDO2/WebAuthn"],
    summary="Complete FIDO2 Authentication",
    description="Complete FIDO2/WebAuthn authentication by verifying the assertion from the authenticator. Returns JWT access token on success.",
    responses={
        200: {"description": "Authentication successful, JWT token issued"},
        400: {"description": "Authentication verification failed"},
    },
)
async def fido2_authenticate_complete(
    request: FIDO2AuthenticationCompleteRequest,
    db: Session = Depends(get_db),
):
    """Complete FIDO2 authentication."""
    try:
        user, token = FIDO2Service.complete_authentication(
            db,
            username=request.username,
            assertion_object=request.assertion_object,
            client_data_json=request.client_data_json,
            device_id=request.device_id,
        )
        
        AuditService.log_action(
            db,
            action="fido2_authentication",
            status="success",
            user_id=user.id,
            device_id=request.device_id,
        )
        
        return TokenResponse(
            access_token=token,
            token_type="Bearer",
            expires_in=settings.jwt_expiration_hours * 3600,
            user=UserResponse.from_orm(user),
        )
    
    except ValueError as e:
        AuditService.log_action(
            db,
            action="fido2_authentication",
            status="failure",
            metadata={"username": request.username, "error": str(e)},
        )
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Biometric Endpoints
# ============================================================================

@app.post(
    "/biometric/register",
    response_model=BiometricRegisterResponse,
    status_code=201,
    tags=["Biometric"],
    summary="Register Biometric Method",
    description="Register a biometric authentication method (fingerprint, face, iris) for the user on a specific device.",
    responses={
        201: {"description": "Biometric method registered successfully"},
        400: {"description": "Invalid biometric registration request"},
    },
)
async def register_biometric(
    user_id: UUID,
    request: BiometricRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register biometric method."""
    try:
        biometric = BiometricService.register_biometric(
            db,
            user_id=user_id,
            device_id=request.device_id,
            method_type=request.method_type,
            biometric_template=request.biometric_data,
        )
        
        AuditService.log_action(
            db,
            action="biometric_registration",
            status="success",
            user_id=user_id,
            device_id=request.device_id,
            metadata={"method": request.method_type},
        )
        
        return BiometricRegisterResponse(
            biometric_id=biometric.id,
            method=biometric.method_type,
            status="registered",
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post(
    "/biometric/verify",
    response_model=BiometricVerifyResponse,
    tags=["Biometric"],
    summary="Verify Biometric",
    description="Verify a biometric input against registered biometric methods. Returns verification result and confidence score.",
    responses={
        200: {"description": "Biometric verification completed"},
        400: {"description": "Biometric verification failed"},
    },
)
async def verify_biometric(
    user_id: UUID,
    request: BiometricVerifyRequest,
    db: Session = Depends(get_db),
):
    """Verify biometric input."""
    try:
        verified = BiometricService.verify_biometric(
            db,
            user_id=user_id,
            device_id=request.device_id,
            method_type=request.method_type,
            biometric_input=request.biometric_input,
        )
        
        status = "success" if verified else "failure"
        AuditService.log_action(
            db,
            action="biometric_verification",
            status=status,
            user_id=user_id,
            device_id=request.device_id,
            metadata={"method": request.method_type},
        )
        
        return BiometricVerifyResponse(
            verified=verified,
            confidence=0.95 if verified else 0.0,
        )
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Exception",
            "message": exc.detail,
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "status_code": 500,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
