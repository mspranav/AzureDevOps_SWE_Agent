"""
API dependencies for the MCP server
"""

from typing import Any, Dict, Optional

from fastapi import Depends, Request
from fastapi.security import APIKeyHeader

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_api_key
from app.utils.exceptions import UnauthorizedException
from app.utils.logger import Logger


async def get_auth_info(
    request: Request,
    auth_info: Dict[str, Any] = Depends(verify_api_key),
) -> Dict[str, Any]:
    """
    Get authentication information from request
    
    Args:
        request: FastAPI request
        auth_info: Auth info from API key verification
        
    Returns:
        Auth info dictionary
    """
    return auth_info


async def get_current_user(
    auth_info: Dict[str, Any] = Depends(get_auth_info),
) -> Dict[str, Any]:
    """
    Get current user info from auth info
    
    Args:
        auth_info: Auth info from verification
        
    Returns:
        User info dictionary
        
    Raises:
        UnauthorizedException: If user cannot be determined
    """
    if not auth_info:
        raise UnauthorizedException("Could not validate credentials")
        
    # For now, just return the auth info as user info
    # In a real implementation, this would look up the user in a database
    user_info = {
        "id": auth_info.get("id", "anonymous"),
        "type": auth_info.get("type", "unknown"),
    }
    
    return user_info


def get_logger(context: Optional[Dict[str, Any]] = None) -> Logger:
    """
    Get a logger with context
    
    Args:
        context: Optional logging context
        
    Returns:
        Logger instance
    """
    return Logger(context)