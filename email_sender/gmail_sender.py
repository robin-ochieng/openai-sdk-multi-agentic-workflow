"""
Gmail SMTP Email Sender
Provides simple interface for sending emails via Gmail
"""
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from .config import EmailConfig
from .exceptions import (
    SMTPConnectionError,
    AuthenticationError,
    SendFailureError,
    InvalidEmailError
)
from .validators import validate_email_format, validate_email_list


class GmailSender:
    """Gmail SMTP Email Sender with retry logic and error handling"""
    
    def __init__(self, config: EmailConfig):
        """
        Initialize Gmail sender
        
        Args:
            config: EmailConfig instance with Gmail credentials
        """
        self.config = config
        self._server: Optional[smtplib.SMTP] = None
    
    def _connect(self) -> smtplib.SMTP:
        """
        Establish connection to Gmail SMTP server
        
        Returns:
            SMTP server instance
            
        Raises:
            SMTPConnectionError: If connection fails
            AuthenticationError: If authentication fails
        """
        try:
            # Create server instance
            server = smtplib.SMTP(
                self.config.smtp_server,
                self.config.smtp_port,
                timeout=self.config.timeout
            )
            
            # Enable debug output (optional, for troubleshooting)
            # server.set_debuglevel(1)
            
            # Start TLS encryption
            if self.config.use_tls:
                server.starttls()
            
            # Authenticate
            try:
                server.login(
                    self.config.gmail_email,
                    self.config.gmail_app_password
                )
            except smtplib.SMTPAuthenticationError as e:
                raise AuthenticationError(
                    f"Gmail authentication failed. Please check your credentials. "
                    f"Make sure you're using an App Password, not your regular password. "
                    f"Error: {str(e)}"
                )
            
            return server
            
        except smtplib.SMTPConnectError as e:
            raise SMTPConnectionError(f"Failed to connect to Gmail SMTP server: {str(e)}")
        except smtplib.SMTPServerDisconnected as e:
            raise SMTPConnectionError(f"Server disconnected unexpectedly: {str(e)}")
        except Exception as e:
            raise SMTPConnectionError(f"Unexpected connection error: {str(e)}")
    
    def _send_with_retry(
        self,
        msg: MIMEMultipart,
        from_email: str,
        to_emails: List[str]
    ) -> None:
        """
        Send email with retry logic
        
        Args:
            msg: MIME message to send
            from_email: Sender email address
            to_emails: List of recipient email addresses
            
        Raises:
            SendFailureError: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(1, self.config.max_retries + 1):
            try:
                # Connect to server
                server = self._connect()
                
                # Send email
                server.send_message(msg, from_email, to_emails)
                
                # Close connection
                server.quit()
                
                # Success!
                return
                
            except Exception as e:
                last_error = e
                
                if attempt < self.config.max_retries:
                    # Wait before retry (exponential backoff)
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    # All retries exhausted
                    raise SendFailureError(
                        f"Failed to send email after {self.config.max_retries} attempts. "
                        f"Last error: {str(last_error)}"
                    )
    
    def send_text_email(
        self,
        subject: str,
        body: str,
        to_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None,
        from_email: Optional[str] = None
    ) -> dict:
        """
        Send plain text email
        
        Args:
            subject: Email subject
            body: Plain text email body
            to_email: Single recipient (optional if to_emails provided)
            to_emails: Multiple recipients (optional if to_email provided)
            from_email: Sender email (defaults to config gmail_email)
            
        Returns:
            dict: Result with status and message
            
        Raises:
            InvalidEmailError: If email addresses are invalid
            SendFailureError: If sending fails
        """
        # Determine recipients
        if to_emails:
            recipients = to_emails
        elif to_email:
            recipients = [to_email]
        else:
            recipients = [self.config.recipient_email]
        
        # Validate recipients
        validate_email_list(recipients)
        
        # Set sender
        sender = from_email or self.config.gmail_email
        validate_email_format(sender)
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Send with retry
        self._send_with_retry(msg, sender, recipients)
        
        return {
            'success': True,
            'message': f'Email sent successfully to {len(recipients)} recipient(s)',
            'recipients': recipients,
            'subject': subject
        }
    
    def send_html_email(
        self,
        subject: str,
        html_body: str,
        plain_body: Optional[str] = None,
        to_email: Optional[str] = None,
        to_emails: Optional[List[str]] = None,
        from_email: Optional[str] = None
    ) -> dict:
        """
        Send HTML email with optional plain text fallback
        
        Args:
            subject: Email subject
            html_body: HTML email body
            plain_body: Plain text fallback (optional)
            to_email: Single recipient (optional if to_emails provided)
            to_emails: Multiple recipients (optional if to_email provided)
            from_email: Sender email (defaults to config gmail_email)
            
        Returns:
            dict: Result with status and message
            
        Raises:
            InvalidEmailError: If email addresses are invalid
            SendFailureError: If sending fails
        """
        # Determine recipients
        if to_emails:
            recipients = to_emails
        elif to_email:
            recipients = [to_email]
        else:
            recipients = [self.config.recipient_email]
        
        # Validate recipients
        validate_email_list(recipients)
        
        # Set sender
        sender = from_email or self.config.gmail_email
        validate_email_format(sender)
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        # Attach plain text fallback (if provided)
        if plain_body:
            msg.attach(MIMEText(plain_body, 'plain'))
        
        # Attach HTML body
        msg.attach(MIMEText(html_body, 'html'))
        
        # Send with retry
        self._send_with_retry(msg, sender, recipients)
        
        return {
            'success': True,
            'message': f'HTML email sent successfully to {len(recipients)} recipient(s)',
            'recipients': recipients,
            'subject': subject
        }
    
    def test_connection(self) -> dict:
        """
        Test Gmail SMTP connection and authentication
        
        Returns:
            dict: Result with connection status
        """
        try:
            server = self._connect()
            server.quit()
            
            return {
                'success': True,
                'message': 'Successfully connected to Gmail SMTP',
                'server': self.config.smtp_server,
                'port': self.config.smtp_port,
                'email': self.config.gmail_email
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}',
                'server': self.config.smtp_server,
                'port': self.config.smtp_port,
                'email': self.config.gmail_email
            }
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self._server:
            try:
                self._server.quit()
            except:
                pass
        return False
