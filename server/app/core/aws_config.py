"""
AWS Configuration Manager for Parameter Store and Secrets Manager integration.
"""

import logging
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

logger = logging.getLogger(__name__)


class AWSConfigManager:
    """Manages configuration values from AWS Parameter Store and Secrets Manager."""
    
    def __init__(self, region_name: str = "ap-southeast-2", profile_name: Optional[str] = None):
        self.region_name = region_name
        self.profile_name = profile_name
        self._secrets_cache: Dict[str, str] = {}
        self._parameters_cache: Dict[str, str] = {}
        
        # Initialize AWS clients
        try:
            session_kwargs = {'region_name': region_name}
            if profile_name:
                session_kwargs['profile_name'] = profile_name
                logger.info(f"Using AWS profile: {profile_name}")
            
            session = boto3.Session(**session_kwargs)
            self.secrets_client = session.client('secretsmanager')
            self.ssm_client = session.client('ssm')
        except NoCredentialsError:
            logger.warning("AWS credentials not found. Using environment variables as fallback.")
            self.secrets_client = None
            self.ssm_client = None
    
    def get_secret(self, secret_name: str, fallback_env_var: Optional[str] = None) -> str:
        """Get secret from AWS Secrets Manager with fallback to environment variable."""
        if secret_name in self._secrets_cache:
            return self._secrets_cache[secret_name]
        
        if self.secrets_client is None:
            if fallback_env_var:
                import os
                value = os.getenv(fallback_env_var)
                if value:
                    logger.info(f"Using environment variable {fallback_env_var} as fallback for {secret_name}")
                    return value
            raise ValueError(f"AWS Secrets Manager not available and no fallback for {secret_name}")
        
        try:
            response = self.secrets_client.get_secret_value(SecretId=secret_name)
            secret_value = response['SecretString']
            self._secrets_cache[secret_name] = secret_value
            logger.info(f"Successfully retrieved secret: {secret_name}")
            return secret_value
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ResourceNotFoundException':
                logger.error(f"Secret {secret_name} not found in AWS Secrets Manager")
            elif error_code == 'AccessDeniedException':
                logger.error(f"Access denied to secret {secret_name}")
            else:
                logger.error(f"Error retrieving secret {secret_name}: {e}")
            
            # Try fallback to environment variable
            if fallback_env_var:
                import os
                value = os.getenv(fallback_env_var)
                if value:
                    logger.info(f"Using environment variable {fallback_env_var} as fallback for {secret_name}")
                    return value
            
            raise ValueError(f"Failed to retrieve secret {secret_name}: {e}")
    
    def get_parameter(self, parameter_name: str, fallback_env_var: Optional[str] = None) -> str:
        """Get parameter from AWS Parameter Store with fallback to environment variable."""
        if parameter_name in self._parameters_cache:
            return self._parameters_cache[parameter_name]
        
        if self.ssm_client is None:
            if fallback_env_var:
                import os
                value = os.getenv(fallback_env_var)
                if value:
                    logger.info(f"Using environment variable {fallback_env_var} as fallback for {parameter_name}")
                    return value
            raise ValueError(f"AWS Parameter Store not available and no fallback for {parameter_name}")
        
        try:
            response = self.ssm_client.get_parameter(
                Name=parameter_name,
                WithDecryption=True
            )
            parameter_value = response['Parameter']['Value']
            self._parameters_cache[parameter_name] = parameter_value
            logger.info(f"Successfully retrieved parameter: {parameter_name}")
            return parameter_value
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'ParameterNotFound':
                logger.error(f"Parameter {parameter_name} not found in AWS Parameter Store")
            elif error_code == 'AccessDeniedException':
                logger.error(f"Access denied to parameter {parameter_name}")
            else:
                logger.error(f"Error retrieving parameter {parameter_name}: {e}")
            
            # Try fallback to environment variable
            if fallback_env_var:
                import os
                value = os.getenv(fallback_env_var)
                if value:
                    logger.info(f"Using environment variable {fallback_env_var} as fallback for {parameter_name}")
                    return value
            
            raise ValueError(f"Failed to retrieve parameter {parameter_name}: {e}")
