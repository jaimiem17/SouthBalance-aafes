"""
JWT Authentication Module for AAFES Order Management MVP

This module provides JWT-based authentication functions including:
- Password verification using PBKDF2
- User authentication
- JWT token creation and verification

Requirements: 1.1, 1.3, 1.4
"""

from __future__ import annotations

import base64
import hashlib
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from sqlmodel import Session, select

from models import UserAccount


# JWT Configuration
SECRET_KEY = "your-secret-key-here-change-in-production"  # TODO: Move to environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

# Password hashing configuration (matching main.py)
PASSWORD_HASH_ITERATIONS = 600_000


def verify_password(plain_password: str, password_hash: str) -> bool:
    """
    Verify a plain password against a PBKDF2 password hash.
    
    Args:
        plain_password: The plain text password to verify
        password_hash: The stored password hash in format:
                      pbkdf2_sha256$iterations$salt$digest
    
    Returns:
        True if password matches, False otherwise
    
    Validates: Requirements 1.1, 1.3
    """
    try:
        # Parse the stored hash format: pbkdf2_sha256$iterations$salt$digest
        parts = password_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2].encode("ascii"))
        stored_digest = base64.b64decode(parts[3].encode("ascii"))
        
        # Hash the provided password with the same salt and iterations
        computed_digest = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            iterations,
        )
        
        # Compare digests using constant-time comparison
        return computed_digest == stored_digest
    
    except (ValueError, IndexError):
        return False


def authenticate_user(
    username: str, 
    password: str, 
    session: Session
) -> Optional[UserAccount]:
    """
    Authenticate a user by username and password.
    
    Args:
        username: The username to authenticate
        password: The plain text password
        session: Database session
    
    Returns:
        UserAccount object if authentication succeeds, None otherwise
    
    Validates: Requirements 1.1, 1.3
    """
    # Query user by username
    statement = select(UserAccount).where(UserAccount.username == username)
    user = session.exec(statement).first()
    
    if not user:
        return None
    
    # Check if user is active
    if not user.is_active:
        return None
    
    # Verify password
    if not verify_password(password, user.password_hash):
        return None
    
    return user


def create_jwt_token(user: UserAccount) -> str:
    """
    Create a JWT token for an authenticated user with 8-hour expiration.
    
    Args:
        user: The authenticated UserAccount object
    
    Returns:
        JWT token string
    
    Validates: Requirements 1.1, 1.4
    """
    # Calculate expiration time (8 hours from now)
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    # Create JWT payload
    payload = {
        "sub": user.account_id,  # Subject: user account ID
        "username": user.username,
        "role": user.role,
        "exp": expire,  # Expiration time
        "iat": datetime.utcnow(),  # Issued at time
    }
    
    # Encode and return JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token string to verify
    
    Returns:
        Decoded token payload as dict if valid, None otherwise
    
    Validates: Requirements 1.1, 1.4
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check if token has required fields
        if "sub" not in payload or "role" not in payload:
            return None
        
        return payload
    
    except JWTError:
        # Token is invalid, expired, or malformed
        return None
