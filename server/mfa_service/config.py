"""
Configuration management for MFA microservice.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = "postgresql://mfa_user:mfa_password@localhost:5432/mfa_db"
    
    # JWT
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # FIDO2/WebAuthn
    rp_id: str = "localhost"
    rp_name: str = "MFA Service"
    origin: str = "http://localhost:8000"
    
    # Security
    bcrypt_rounds: int = 12
    token_expiration_minutes: int = 60
    challenge_expiration_minutes: int = 5
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15
    
    # Device Trust
    device_trust_window_days: int = 30
    
    # API
    api_title: str = "MFA Microservice API"
    api_version: str = "1.0.0"
    api_description: str = "Multi-Factor Authentication microservice with FIDO2/WebAuthn support"
    debug: bool = False
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8081", "http://localhost:19000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
