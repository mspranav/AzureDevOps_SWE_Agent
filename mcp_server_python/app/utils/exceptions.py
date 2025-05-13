"""
Custom exceptions for the MCP server
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, status


class APIException(HTTPException):
    """Base API exception class"""
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        self.errors = errors
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestException(APIException):
    """400 Bad Request Exception"""
    def __init__(
        self,
        detail: str = "Bad Request",
        headers: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
            errors=errors,
        )


class UnauthorizedException(APIException):
    """401 Unauthorized Exception"""
    def __init__(
        self,
        detail: str = "Unauthorized",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class ForbiddenException(APIException):
    """403 Forbidden Exception"""
    def __init__(
        self,
        detail: str = "Forbidden",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class NotFoundException(APIException):
    """404 Not Found Exception"""
    def __init__(
        self,
        detail: str = "Resource not found",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )


class ConflictException(APIException):
    """409 Conflict Exception"""
    def __init__(
        self,
        detail: str = "Resource conflict",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            headers=headers,
        )


class UnprocessableEntityException(APIException):
    """422 Unprocessable Entity Exception"""
    def __init__(
        self,
        detail: str = "Unprocessable entity",
        headers: Optional[Dict[str, Any]] = None,
        errors: Optional[List[Dict[str, Any]]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers,
            errors=errors,
        )


class TooManyRequestsException(APIException):
    """429 Too Many Requests Exception"""
    def __init__(
        self,
        detail: str = "Too many requests",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers,
        )


class InternalServerException(APIException):
    """500 Internal Server Exception"""
    def __init__(
        self,
        detail: str = "Internal server error",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            headers=headers,
        )


class BadGatewayException(APIException):
    """502 Bad Gateway Exception"""
    def __init__(
        self,
        detail: str = "Bad gateway",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            headers=headers,
        )


class ServiceUnavailableException(APIException):
    """503 Service Unavailable Exception"""
    def __init__(
        self,
        detail: str = "Service unavailable",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers,
        )


class GatewayTimeoutException(APIException):
    """504 Gateway Timeout Exception"""
    def __init__(
        self,
        detail: str = "Gateway timeout",
        headers: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=detail,
            headers=headers,
        )