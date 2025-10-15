"""
Configuration management for Gmail SMTP sender
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from .exceptions import ConfigurationError
from .validators import validate_smtp_config


@dataclass
class EmailConfig:
    """Email configuration settings"""
    
    # Gmail credentials
    gmail_email: str
    gmail_app_password: str
    
    # Default recipient
    recipient_email: str = "robinochieng74@gmail.com"
    
    # SMTP settings
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    
    # Optional settings
    timeout: int = 30
    max_retries: int = 3
    use_tls: bool = True
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        try:
            validate_smtp_config(
                self.smtp_server,
                self.smtp_port,
                self.gmail_email,
                self.gmail_app_password
            )
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")
    
    @classmethod
    def from_env(cls, env_file: Optional[str] = None) -> 'EmailConfig':
        """
        Load configuration from environment variables
        
        Args:
            env_file: Optional path to .env file
            
        Returns:
            EmailConfig instance
            
        Raises:
            ConfigurationError: If required variables are missing
        """
        if env_file:
            load_dotenv(env_file, override=True)
        else:
            load_dotenv(override=True)
        
        # Required variables
        gmail_email = os.getenv('GMAIL_EMAIL')
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
        
        if not gmail_email:
            raise ConfigurationError(
                "GMAIL_EMAIL environment variable is required. "
                "Please set it in your .env file."
            )
        
        if not gmail_app_password:
            raise ConfigurationError(
                "GMAIL_APP_PASSWORD environment variable is required. "
                "Please set it in your .env file. "
                "Note: Use Gmail App Password, not regular password."
            )
        
        # Optional variables with defaults
        recipient_email = os.getenv('RECIPIENT_EMAIL', 'robinochieng74@gmail.com')
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        timeout = int(os.getenv('EMAIL_TIMEOUT', '30'))
        max_retries = int(os.getenv('MAX_RETRIES', '3'))
        use_tls = os.getenv('USE_TLS', 'true').lower() == 'true'
        
        return cls(
            gmail_email=gmail_email,
            gmail_app_password=gmail_app_password,
            recipient_email=recipient_email,
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            timeout=timeout,
            max_retries=max_retries,
            use_tls=use_tls
        )
    
    def __repr__(self) -> str:
        """String representation (hiding password)"""
        return (
            f"EmailConfig("
            f"gmail_email={self.gmail_email}, "
            f"recipient={self.recipient_email}, "
            f"smtp_server={self.smtp_server}:{self.smtp_port}, "
            f"password=***hidden***)"
        )
