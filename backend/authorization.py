"""
Role-Based Access Control Module for AAFES Order Management MVP

This module provides authorization functions including:
- JWT token extraction and user retrieval
- Role-based access control decorator
- Unauthorized access logging

Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6
"""

from __future__ import annotations

from typing import List

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session

from auth import verify_jwt_token
from database import get_session
from models import UserAccount, AuditLog


# OAuth2 scheme for JWT token extraction
oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
) -> UserAccount:
    """
    Extract and validate JWT token, then retrieve the current user.
    
    Args:
        credentials: HTTP Bearer token credentials
        session: Database session
    
    Returns:
        UserAccount object for the authenticated user
    
    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    
    Validates: Requirements 2.1, 2.6
    """
    # Extract token from credentials
    token = credentials.credentials
    
    # Verify and decode JWT token
    payload = verify_jwt_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
        )
    
    # Extract account_id from token payload
    account_id = payload.get("sub")
    if not account_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload",
        )
    
    # Retrieve user from database
    user = session.get(UserAccount, account_id)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found",
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User account is inactive",
        )
    
    return user


def require_role(allowed_roles: List[str]):
    """
    Decorator factory that creates a dependency to check user role.
    
    Args:
        allowed_roles: List of role names that are allowed to access the endpoint
    
    Returns:
        Dependency function that validates user role
    
    Usage:
        @app.get("/admin-only")
        def admin_endpoint(user: UserAccount = Depends(require_role(["Admin"]))):
            return {"message": "Admin access granted"}
    
    Validates: Requirements 2.2, 2.3, 2.4, 2.5, 2.6
    """
    def role_checker(
        request: Request,
        user: UserAccount = Depends(get_current_user),
        session: Session = Depends(get_session),
    ) -> UserAccount:
        """
        Check if the current user has one of the allowed roles.
        
        Args:
            request: FastAPI request object (for IP address logging)
            user: Current authenticated user
            session: Database session
        
        Returns:
            UserAccount object if role is allowed
        
        Raises:
            HTTPException: 403 if user role is not in allowed_roles
        """
        # Check if user's role is in the allowed roles list
        if user.role not in allowed_roles:
            # Get client IP address for audit logging
            ip_address = request.client.host if request.client else None
            
            # Log unauthorized access attempt
            unauthorized_log = AuditLog(
                event_type="unauthorized_access",
                account_id=user.account_id,
                ip_address=ip_address,
                details=(
                    f"User {user.username} (role: {user.role}) attempted to access "
                    f"endpoint requiring roles: {', '.join(allowed_roles)}"
                ),
            )
            session.add(unauthorized_log)
            session.commit()
            
            # Return 403 Forbidden
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )
        
        return user
    
    return role_checker
