"""
Main entry point for Azure DevOps Integration Agent.

This module provides the command-line interface and entry point for the agent.
"""

import argparse
import logging
import os
import sys
import yaml
from typing import Dict, Any, Optional

from azure_devops_agent.core.orchestrator import Orchestrator
from azure_devops_agent.security.credential_manager import CredentialManager
from azure_devops_agent.security.audit_logger import AuditLogger

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from a YAML file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        Configuration dictionary.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {str(e)}")
        return {}

def main() -> None:
    """Main entry point for the Azure DevOps Integration Agent."""
    parser = argparse.ArgumentParser(description="Azure DevOps Integration Agent")
    
    parser.add_argument(
        "--config", 
        type=str, 
        default="config/agent_config.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--task-id", 
        type=str, 
        help="ID of the task to process"
    )
    
    parser.add_argument(
        "--poll", 
        action="store_true", 
        help="Poll for tasks continuously"
    )
    
    parser.add_argument(
        "--log-level", 
        type=str, 
        default=os.environ.get("LOG_LEVEL", "INFO"),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Load configuration
    config = load_config(args.config)
    
    # Set up audit logger
    audit_config = config.get("logging", {})
    audit_log_path = audit_config.get("audit_log", "logs/audit.log")
    
    audit_logger = AuditLogger(
        log_file=audit_log_path,
        log_to_console=audit_config.get("log_to_console", False),
        log_to_azure=audit_config.get("log_to_azure", False),
        structured_format=audit_config.get("format", "structured") == "structured"
    )
    
    # Get credentials
    security_config = config.get("security", {})
    credential_store = security_config.get("credential_store", "env")
    
    credential_manager = CredentialManager(credential_store=credential_store)
    
    # Get Azure DevOps credentials
    azure_devops_config = config.get("azure_devops", {})
    organization = azure_devops_config.get("organization") or os.environ.get("AZURE_DEVOPS_ORG")
    project = azure_devops_config.get("project") or os.environ.get("AZURE_DEVOPS_PROJECT")
    
    if not organization:
        logger.error("Azure DevOps organization not specified")
        sys.exit(1)
    
    # Get PAT from credential manager
    pat = credential_manager.get_azure_devops_credentials(organization)
    
    if not pat:
        logger.error("Azure DevOps PAT not found")
        sys.exit(1)
    
    # Get repository settings
    repo_config = config.get("repository", {})
    work_dir = repo_config.get("work_dir")
    
    # Set up orchestrator
    orchestrator = Orchestrator(
        organization_url=f"https://dev.azure.com/{organization}",
        personal_access_token=pat,
        project=project,
        work_dir=work_dir
    )
    
    # Log agent start
    audit_logger.log_event(
        event_type=audit_logger.EVENT_CONFIGURATION,
        severity=audit_logger.SEVERITY_INFO,
        message="Azure DevOps Integration Agent started",
        details={
            "organization": organization,
            "project": project,
            "polling_enabled": args.poll
        }
    )
    
    if args.task_id:
        # Process a specific task
        logger.info(f"Processing task {args.task_id}")
        
        audit_logger.log_task_access(
            task_id=args.task_id,
            user="agent",
            action="process"
        )
        
        result = orchestrator.process_task(args.task_id)
        
        if result.get("status") == "completed":
            logger.info(f"Task {args.task_id} processed successfully")
            logger.info(f"PR created: {result.get('pull_request', {}).get('pr_url', 'N/A')}")
        else:
            logger.error(f"Failed to process task {args.task_id}: {result.get('message', 'Unknown error')}")
    
    elif args.poll:
        # Poll for tasks
        logger.info("Starting to poll for tasks")
        
        # This would be implemented to continuously poll for tasks
        # For simplicity, this is not implemented in this example
        logger.error("Polling not implemented yet")
    
    else:
        # No action specified
        parser.print_help()

if __name__ == "__main__":
    main()