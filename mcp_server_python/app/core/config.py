"""
Settings and configuration for the MCP server
"""

import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings and configuration
    """
    # Server settings
    API_VERSION: str = "v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    PROJECT_NAME: str = "Azure DevOps Integration Agent MCP"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Rate limiting
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_MAX: int = 100
    
    # Authentication
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    API_KEY_HEADER: str = "X-API-Key"
    VALID_API_KEYS: List[str] = []
    DISABLE_AUTH: bool = False
    
    # Database
    DATABASE_URL: PostgresDsn
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PREFIX: str = "azdevops_mcp:"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_ORGANIZATION: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4"
    
    # Azure OpenAI
    USE_AZURE_OPENAI: bool = False
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = None
    
    # Azure DevOps
    AZURE_DEVOPS_PAT: Optional[str] = None
    AZURE_DEVOPS_ORGANIZATION: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = "logs/server.log"
    STRUCTURED_LOGGING: bool = True
    
    # Timeouts (seconds)
    TASK_PROCESSING_TIMEOUT: int = 3600
    CODE_GENERATION_TIMEOUT: int = 600
    REPOSITORY_OPERATION_TIMEOUT: int = 300
    
    # Feature flags
    ENABLE_AUDIT_LOGGING: bool = True
    ENABLE_CACHING: bool = True
    
    # Parse CORS origins
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], List[AnyHttpUrl]]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Parse API keys list
    @validator("VALID_API_KEYS", pre=True)
    def assemble_api_keys(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        return []

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()