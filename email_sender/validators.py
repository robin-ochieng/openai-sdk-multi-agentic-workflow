"""
Email validation utilities
"""
import re
from typing import List
from .exceptions import InvalidEmailError


def validate_email_format(email: str) -> bool:
    """
    Validate email format using regex
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        InvalidEmailError: If email format is invalid
    """
    if not email or not isinstance(email, str):
        raise InvalidEmailError("Email must be a non-empty string")
    
    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise InvalidEmailError(f"Invalid email format: {email}")
    
    return True


def validate_email_list(emails: List[str]) -> bool:
    """
    Validate a list of email addresses
    
    Args:
        emails: List of email addresses
        
    Returns:
        True if all valid
        
    Raises:
        InvalidEmailError: If any email is invalid
    """
    if not emails:
        raise InvalidEmailError("Email list cannot be empty")
    
    for email in emails:
        validate_email_format(email)
    
    return True


def sanitize_email_content(content: str, max_length: int = 100000) -> str:
    """
    Sanitize email content
    
    Args:
        content: Email content to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized content
        
    Raises:
        ValueError: If content exceeds max length
    """
    if not content:
        return ""
    
    if len(content) > max_length:
        raise ValueError(f"Email content exceeds maximum length of {max_length} characters")
    
    # Remove any null bytes
    content = content.replace('\x00', '')
    
    return content


def validate_smtp_config(server: str, port: int, email: str, password: str) -> bool:
    """
    Validate SMTP configuration
    
    Args:
        server: SMTP server address
        port: SMTP port number
        email: Gmail email address
        password: Gmail app password
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    if not server:
        raise ValueError("SMTP server is required")
    
    if not isinstance(port, int) or port < 1 or port > 65535:
        raise ValueError(f"Invalid port number: {port}")
    
    if not email:
        raise ValueError("Email address is required")
    
    validate_email_format(email)
    
    if not password:
        raise ValueError("Password is required")
    
    # Gmail app passwords should be 16 characters (with or without spaces)
    clean_password = password.replace(' ', '')
    if len(clean_password) < 8:
        raise ValueError("Password appears to be too short (use Gmail App Password)")
    
    return True
