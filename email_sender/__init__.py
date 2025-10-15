"""
Gmail SMTP Email Sender Module
A modular, standalone email sender using Gmail SMTP
"""

from .config import EmailConfig
from .gmail_sender import GmailSender
from .email_templates import (
    create_plain_text_email,
    create_html_email,
    create_sales_email
)
from .exceptions import (
    EmailSenderException,
    SMTPConnectionError,
    InvalidEmailError,
    AuthenticationError,
    SendFailureError
)

__version__ = "1.0.0"
__all__ = [
    "EmailConfig",
    "GmailSender",
    "create_plain_text_email",
    "create_html_email",
    "create_sales_email",
    "EmailSenderException",
    "SMTPConnectionError",
    "InvalidEmailError",
    "AuthenticationError",
    "SendFailureError",
]
