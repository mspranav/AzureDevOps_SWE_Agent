"""
Credential Manager module for Azure DevOps Integration Agent.

This module provides secure credential storage and retrieval using keyring
and Azure identity libraries.
"""

import os
import logging
import json
import base64
from typing import Dict, Optional, Any, Union, Tuple
import keyring
import keyring.errors
from azure.identity import DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential

logger = logging.getLogger(__name__)

class CredentialManager:
    """
    Manage credentials for Azure DevOps and other services.
    
    This class provides secure storage and retrieval of credentials using
    the system keyring, environment variables, or Azure identity services.
    """
    
    # Service names for keyring storage
    KEYRING_SERVICE_AZURE_DEVOPS = "AzureDevOpsAgent-AzureDevOps"
    KEYRING_SERVICE_GITHUB = "AzureDevOpsAgent-GitHub"
    KEYRING_SERVICE_CONFIG = "AzureDevOpsAgent-Config"
    
    def __init__(self, credential_store: str = "keyring"):
        """
        Initialize the credential manager.
        
        Args:
            credential_store: Type of credential store to use ("keyring", "env", "azure").
        """
        self.credential_store = credential_store
        logger.info(f"Credential manager initialized using {credential_store} store")
    
    def store_azure_devops_credentials(self, 
                                    organization: str,
                                    personal_access_token: str) -> bool:
        """
        Store Azure DevOps credentials.
        
        Args:
            organization: Azure DevOps organization name.
            personal_access_token: Personal access token.
            
        Returns:
            True if credentials were stored successfully.
        """
        if self.credential_store != "keyring":
            logger.warning("Storing credentials is only supported with keyring store")
            return False
            
        try:
            # Store the PAT in the keyring
            keyring.set_password(
                self.KEYRING_SERVICE_AZURE_DEVOPS,
                organization,
                personal_access_token
            )
            logger.info(f"Stored Azure DevOps PAT for organization {organization}")
            return True
        except keyring.errors.KeyringError as e:
            logger.error(f"Failed to store Azure DevOps PAT: {str(e)}")
            return False
    
    def get_azure_devops_credentials(self, organization: str) -> Optional[str]:
        """
        Get Azure DevOps credentials.
        
        Args:
            organization: Azure DevOps organization name.
            
        Returns:
            Personal access token or None if not found.
        """
        # Try to get from keyring if using keyring store
        if self.credential_store == "keyring":
            try:
                pat = keyring.get_password(self.KEYRING_SERVICE_AZURE_DEVOPS, organization)
                if pat:
                    logger.info(f"Retrieved Azure DevOps PAT for organization {organization} from keyring")
                    return pat
            except keyring.errors.KeyringError as e:
                logger.warning(f"Failed to get Azure DevOps PAT from keyring: {str(e)}")
        
        # Try to get from environment variables
        env_var_name = f"AZURE_DEVOPS_PAT_{organization.upper()}"
        pat = os.environ.get(env_var_name)
        if not pat:
            # Try a generic PAT environment variable
            pat = os.environ.get("AZURE_DEVOPS_PAT")
            
        if pat:
            logger.info(f"Retrieved Azure DevOps PAT from environment variable")
            return pat
            
        # Try to get from Azure identity if using Azure store
        if self.credential_store == "azure":
            # This is a simplified placeholder - in a real implementation,
            # this would use Azure Key Vault or a similar service
            logger.info("Attempting to get Azure DevOps PAT from Azure identity")
            # In a real implementation, this would be implemented
            
        logger.warning(f"No Azure DevOps PAT found for organization {organization}")
        return None
    
    def store_github_credentials(self, username: str, token: str) -> bool:
        """
        Store GitHub credentials.
        
        Args:
            username: GitHub username.
            token: GitHub personal access token.
            
        Returns:
            True if credentials were stored successfully.
        """
        if self.credential_store != "keyring":
            logger.warning("Storing credentials is only supported with keyring store")
            return False
            
        try:
            # Store the token in the keyring
            keyring.set_password(
                self.KEYRING_SERVICE_GITHUB,
                username,
                token
            )
            logger.info(f"Stored GitHub token for user {username}")
            return True
        except keyring.errors.KeyringError as e:
            logger.error(f"Failed to store GitHub token: {str(e)}")
            return False
    
    def get_github_credentials(self, username: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Get GitHub credentials.
        
        Args:
            username: GitHub username (optional).
            
        Returns:
            Tuple of (username, token) or (None, None) if not found.
        """
        token = None
        
        # If username is provided, try to get from keyring
        if username and self.credential_store == "keyring":
            try:
                token = keyring.get_password(self.KEYRING_SERVICE_GITHUB, username)
                if token:
                    logger.info(f"Retrieved GitHub token for user {username} from keyring")
                    return username, token
            except keyring.errors.KeyringError as e:
                logger.warning(f"Failed to get GitHub token from keyring: {str(e)}")
        
        # Try to get from environment variables
        env_username = os.environ.get("GITHUB_USERNAME")
        env_token = os.environ.get("GITHUB_TOKEN")
        
        if env_token:
            logger.info("Retrieved GitHub token from environment variable")
            return env_username or username, env_token
            
        logger.warning("No GitHub credentials found")
        return None, None
    
    def store_configuration(self, config_name: str, config_data: Dict[str, Any]) -> bool:
        """
        Store configuration securely.
        
        Args:
            config_name: Name of the configuration.
            config_data: Configuration data to store.
            
        Returns:
            True if configuration was stored successfully.
        """
        if self.credential_store != "keyring":
            logger.warning("Storing configuration is only supported with keyring store")
            return False
            
        try:
            # Convert dictionary to JSON string
            config_json = json.dumps(config_data)
            
            # Store in keyring
            keyring.set_password(
                self.KEYRING_SERVICE_CONFIG,
                config_name,
                config_json
            )
            logger.info(f"Stored configuration {config_name}")
            return True
        except (keyring.errors.KeyringError, TypeError, ValueError) as e:
            logger.error(f"Failed to store configuration: {str(e)}")
            return False
    
    def get_configuration(self, config_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration.
        
        Args:
            config_name: Name of the configuration.
            
        Returns:
            Configuration dictionary or None if not found.
        """
        if self.credential_store == "keyring":
            try:
                # Get JSON string from keyring
                config_json = keyring.get_password(self.KEYRING_SERVICE_CONFIG, config_name)
                
                if config_json:
                    # Parse JSON to dictionary
                    config_data = json.loads(config_json)
                    logger.info(f"Retrieved configuration {config_name} from keyring")
                    return config_data
            except (keyring.errors.KeyringError, json.JSONDecodeError) as e:
                logger.warning(f"Failed to get configuration from keyring: {str(e)}")
        
        # Try to get from environment variables
        env_var_name = f"CONFIG_{config_name.upper()}"
        config_json = os.environ.get(env_var_name)
        
        if config_json:
            try:
                config_data = json.loads(config_json)
                logger.info(f"Retrieved configuration {config_name} from environment variable")
                return config_data
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse configuration from environment variable: {str(e)}")
        
        logger.warning(f"No configuration found for {config_name}")
        return None
    
    def get_azure_credential(self) -> Optional[Union[DefaultAzureCredential, ClientSecretCredential, ManagedIdentityCredential]]:
        """
        Get Azure credential for authentication.
        
        Returns:
            Azure credential object or None if not available.
        """
        try:
            # Try to use DefaultAzureCredential, which tries various methods
            logger.info("Attempting to get Azure credential")
            return DefaultAzureCredential()
        except Exception as e:
            logger.warning(f"Failed to get Azure credential: {str(e)}")
            
            # Try to use client secret if environment variables are set
            client_id = os.environ.get("AZURE_CLIENT_ID")
            client_secret = os.environ.get("AZURE_CLIENT_SECRET")
            tenant_id = os.environ.get("AZURE_TENANT_ID")
            
            if client_id and client_secret and tenant_id:
                try:
                    logger.info("Attempting to get Azure credential using client secret")
                    return ClientSecretCredential(
                        tenant_id=tenant_id,
                        client_id=client_id,
                        client_secret=client_secret
                    )
                except Exception as e:
                    logger.warning(f"Failed to get Azure credential using client secret: {str(e)}")
            
            # Try to use managed identity if running in Azure
            try:
                logger.info("Attempting to get Azure credential using managed identity")
                return ManagedIdentityCredential()
            except Exception as e:
                logger.warning(f"Failed to get Azure credential using managed identity: {str(e)}")
            
            return None
    
    def clear_credentials(self, service: str = "all") -> bool:
        """
        Clear stored credentials.
        
        Args:
            service: Service to clear credentials for ("all", "azure_devops", "github", "config").
            
        Returns:
            True if credentials were cleared successfully.
        """
        if self.credential_store != "keyring":
            logger.warning("Clearing credentials is only supported with keyring store")
            return False
            
        try:
            if service in ["all", "azure_devops"]:
                # This is a simplified approach - in a real implementation,
                # we would enumerate all organizations
                for org in ["dummy_org"]:  # Placeholder
                    try:
                        keyring.delete_password(self.KEYRING_SERVICE_AZURE_DEVOPS, org)
                    except keyring.errors.PasswordDeleteError:
                        pass
                logger.info("Cleared Azure DevOps credentials")
                
            if service in ["all", "github"]:
                # This is a simplified approach - in a real implementation,
                # we would enumerate all usernames
                for username in ["dummy_user"]:  # Placeholder
                    try:
                        keyring.delete_password(self.KEYRING_SERVICE_GITHUB, username)
                    except keyring.errors.PasswordDeleteError:
                        pass
                logger.info("Cleared GitHub credentials")
                
            if service in ["all", "config"]:
                # This is a simplified approach - in a real implementation,
                # we would enumerate all configs
                for config in ["dummy_config"]:  # Placeholder
                    try:
                        keyring.delete_password(self.KEYRING_SERVICE_CONFIG, config)
                    except keyring.errors.PasswordDeleteError:
                        pass
                logger.info("Cleared configuration data")
                
            return True
        except Exception as e:
            logger.error(f"Failed to clear credentials: {str(e)}")
            return False