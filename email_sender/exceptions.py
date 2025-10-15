"""
Custom exceptions for email sender module
"""


class EmailSenderException(Exception):
    """Base exception for all email sender errors"""
    pass


class SMTPConnectionError(EmailSenderException):
    """Raised when SMTP connection fails"""
    pass


class InvalidEmailError(EmailSenderException):
    """Raised when email format is invalid"""
    pass


class AuthenticationError(EmailSenderException):
    """Raised when Gmail authentication fails"""
    pass


class SendFailureError(EmailSenderException):
    """Raised when email sending fails"""
    pass


class ConfigurationError(EmailSenderException):
    """Raised when configuration is invalid or missing"""
    pass
