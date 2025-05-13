"""
Security utilities for the MCP server
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Union

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.utils.exceptions import UnauthorizedException
from app.utils.logger import get_logger

# Initialize logger
logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# API key security scheme
api_key_header = APIKeyHeader(name=settings.API_KEY_HEADER)


def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a JWT access token
    
    Args:
        subject: Subject claim (usually user ID)
        expires_delta: Optional expiration time
        
    Returns:
        JWT token string
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Get password hash
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    return pwd_context.hash(password)


async def verify_api_key(
    request: Request,
    api_key: str = Depends(api_key_header),
) -> Dict[str, Any]:
    """
    Verify API key from request
    
    Args:
        request: FastAPI request
        api_key: API key from header
        
    Returns:
        Auth info dictionary
        
    Raises:
        UnauthorizedException: If API key is invalid
    """
    if settings.DISABLE_AUTH:
        logger.warning("Authentication is disabled")
        return {"type": "api_key", "id": "development"}
        
    # In development, allow a special key
    if settings.ENVIRONMENT == "development" and api_key == "dev-api-key":
        logger.debug("Using development API key")
        return {"type": "api_key", "id": "development"}
        
    if not api_key:
        logger.warning("API key not provided")
        raise UnauthorizedException("API key is required")
        
    # Check against valid API keys
    if api_key not in settings.VALID_API_KEYS:
        logger.warning(f"Invalid API key: {api_key[:5]}...")
        raise UnauthorizedException("Invalid API key")
        
    logger.debug(f"API key verified: {api_key[:5]}...")
    return {"type": "api_key", "id": api_key}