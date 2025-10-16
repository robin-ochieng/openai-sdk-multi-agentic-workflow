"""
Tests for Gmail SMTP sender
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_sender.gmail_sender import GmailSender
from email_sender.config import EmailConfig
from email_sender.exceptions import (
    SMTPConnectionError,
    AuthenticationError,
    SendFailureError,
    InvalidEmailError
)


class TestGmailSender(unittest.TestCase):
    """Test cases for GmailSender class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = EmailConfig(
            gmail_email="test@gmail.com",
            gmail_app_password="test_app_password_16chars",
            recipient_email="recipient@gmail.com"
        )
        self.sender = GmailSender(self.config)
    
    def test_initialization(self):
        """Test GmailSender initialization"""
        self.assertIsNotNone(self.sender)
        self.assertEqual(self.sender.config, self.config)
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_connect_success(self, mock_smtp):
        """Test successful SMTP connection"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test connection
        server = self.sender._connect()
        
        # Verify calls
        mock_smtp.assert_called_once_with(
            self.config.smtp_server,
            self.config.smtp_port,
            timeout=self.config.timeout
        )
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with(
            self.config.gmail_email,
            self.config.gmail_app_password
        )
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_send_text_email_success(self, mock_smtp):
        """Test successful text email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Send email
        result = self.sender.send_text_email(
            subject="Test Subject",
            body="Test Body",
            to_email="test@example.com"
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('test@example.com', result['recipients'])
        self.assertEqual(result['subject'], "Test Subject")
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_send_html_email_success(self, mock_smtp):
        """Test successful HTML email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Send email
        result = self.sender.send_html_email(
            subject="Test HTML",
            html_body="<h1>Test</h1>",
            to_email="test@example.com"
        )
        
        # Verify result
        self.assertTrue(result['success'])
        self.assertIn('test@example.com', result['recipients'])
    
    def test_invalid_email_format(self):
        """Test sending to invalid email address"""
        with self.assertRaises(InvalidEmailError):
            self.sender.send_text_email(
                subject="Test",
                body="Test",
                to_email="invalid-email"
            )
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_multiple_recipients(self, mock_smtp):
        """Test sending to multiple recipients"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Send to multiple recipients
        recipients = ["test1@example.com", "test2@example.com"]
        result = self.sender.send_text_email(
            subject="Test",
            body="Test",
            to_emails=recipients
        )
        
        # Verify
        self.assertTrue(result['success'])
        self.assertEqual(len(result['recipients']), 2)
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_test_connection_success(self, mock_smtp):
        """Test connection testing"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test connection
        result = self.sender.test_connection()
        
        # Verify
        self.assertTrue(result['success'])
        self.assertIn('Successfully connected', result['message'])
    
    @patch('email_sender.gmail_sender.smtplib.SMTP')
    def test_context_manager(self, mock_smtp):
        """Test using GmailSender as context manager"""
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        with GmailSender(self.config) as sender:
            self.assertIsNotNone(sender)


class TestEmailConfig(unittest.TestCase):
    """Test cases for EmailConfig class"""
    
    def test_valid_config(self):
        """Test valid configuration"""
        config = EmailConfig(
            gmail_email="test@gmail.com",
            gmail_app_password="test_password_1234567",
            recipient_email="recipient@gmail.com"
        )
        self.assertEqual(config.gmail_email, "test@gmail.com")
        self.assertEqual(config.smtp_server, "smtp.gmail.com")
        self.assertEqual(config.smtp_port, 587)
    
    def test_config_repr(self):
        """Test config string representation hides password"""
        config = EmailConfig(
            gmail_email="test@gmail.com",
            gmail_app_password="secret_password_12345",
            recipient_email="recipient@gmail.com"
        )
        repr_str = repr(config)
        
        # Verify password is hidden
        self.assertNotIn("secret_password", repr_str)
        self.assertIn("***hidden***", repr_str)
        self.assertIn("test@gmail.com", repr_str)


if __name__ == '__main__':
    unittest.main()
