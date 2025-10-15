# Gmail SMTP Email Sender

A simple, reliable Gmail SMTP email sender for Python projects. Free alternative to SendGrid for development and testing.

## Features

- ✅ **Simple API** - Easy-to-use interface for sending emails
- ✅ **HTML & Plain Text** - Support for both email formats
- ✅ **Email Templates** - Pre-built templates for common use cases
- ✅ **Retry Logic** - Automatic retry with exponential backoff
- ✅ **Error Handling** - Comprehensive exception handling
- ✅ **Type Safety** - Full type hints for better IDE support
- ✅ **Validation** - Email address and configuration validation
- ✅ **Free** - Uses Gmail's free SMTP service (500 emails/day)

## Quick Start

### 1. Prerequisites

- Gmail account with 2-factor authentication enabled
- Gmail App Password (see [Setup Guide](SETUP_GUIDE.md))

### 2. Installation

No additional packages needed beyond standard library! The module uses only built-in Python modules:
- `smtplib` - SMTP protocol
- `email` - Email construction
- `dotenv` - Environment variables (already installed in main project)

### 3. Configuration

Add to your `.env` file:

```env
# Gmail SMTP Configuration
GMAIL_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# Default recipient (optional)
RECIPIENT_EMAIL=robinochieng74@gmail.com
```

### 4. Basic Usage

```python
from email_sender import EmailConfig, GmailSender

# Load configuration
config = EmailConfig.from_env()

# Create sender
sender = GmailSender(config)

# Send plain text email
result = sender.send_text_email(
    subject="Hello from Python!",
    body="This is a test email.",
    to_email="recipient@example.com"
)

print(result)  # {'success': True, 'message': '...', 'recipients': [...]}
```

## Examples

### Send HTML Email

```python
html_body = """
<html>
<body>
    <h1>Welcome!</h1>
    <p>This is an HTML email.</p>
</body>
</html>
"""

sender.send_html_email(
    subject="HTML Email Test",
    html_body=html_body,
    to_email="recipient@example.com"
)
```

### Using Templates

```python
from email_sender.email_templates import create_sales_email

# Create sales email
plain_text, html = create_sales_email(
    recipient_name="John",
    product_name="AI Platform",
    value_proposition="Save 10+ hours per week",
    call_to_action="Book a demo today!",
    sender_name="Jane Smith",
    sender_title="Sales Engineer",
    company_name="Tech Corp"
)

# Send it
sender.send_html_email(
    subject="Transform Your Workflow",
    html_body=html,
    plain_body=plain_text
)
```

### Send to Multiple Recipients

```python
recipients = [
    "person1@example.com",
    "person2@example.com",
    "person3@example.com"
]

sender.send_text_email(
    subject="Team Update",
    body="Hello team!",
    to_emails=recipients
)
```

### Test Connection

```python
result = sender.test_connection()
if result['success']:
    print("✅ Gmail SMTP connection working!")
else:
    print(f"❌ Connection failed: {result['message']}")
```

## API Reference

### `EmailConfig`

Configuration class for Gmail SMTP settings.

**Class Methods:**
- `from_env(env_file=None)` - Load configuration from environment variables

**Properties:**
- `gmail_email` (str) - Your Gmail address
- `gmail_app_password` (str) - Your Gmail App Password
- `recipient_email` (str) - Default recipient
- `smtp_server` (str) - SMTP server (default: "smtp.gmail.com")
- `smtp_port` (int) - SMTP port (default: 587)
- `timeout` (int) - Connection timeout in seconds (default: 30)
- `max_retries` (int) - Maximum retry attempts (default: 3)
- `use_tls` (bool) - Use TLS encryption (default: True)

### `GmailSender`

Main email sender class.

**Methods:**

#### `send_text_email(subject, body, to_email=None, to_emails=None, from_email=None)`

Send plain text email.

**Parameters:**
- `subject` (str) - Email subject
- `body` (str) - Plain text body
- `to_email` (str, optional) - Single recipient
- `to_emails` (List[str], optional) - Multiple recipients
- `from_email` (str, optional) - Sender email (defaults to config)

**Returns:** `dict` with keys: `success`, `message`, `recipients`, `subject`

#### `send_html_email(subject, html_body, plain_body=None, to_email=None, to_emails=None, from_email=None)`

Send HTML email with optional plain text fallback.

**Parameters:**
- `subject` (str) - Email subject
- `html_body` (str) - HTML body content
- `plain_body` (str, optional) - Plain text fallback
- `to_email` (str, optional) - Single recipient
- `to_emails` (List[str], optional) - Multiple recipients
- `from_email` (str, optional) - Sender email

**Returns:** `dict` with result information

#### `test_connection()`

Test Gmail SMTP connection.

**Returns:** `dict` with connection status

### Email Templates

Pre-built templates in `email_templates.py`:

- `create_plain_text_email()` - Standard plain text format
- `create_html_email()` - Professional HTML format
- `create_sales_email()` - Sales outreach template
- `create_followup_email()` - Follow-up email template
- `create_test_email()` - Simple test email

## Error Handling

The module provides custom exceptions:

```python
from email_sender.exceptions import (
    EmailSenderException,      # Base exception
    SMTPConnectionError,       # Connection failures
    AuthenticationError,       # Login failures
    SendFailureError,          # Send failures
    InvalidEmailError,         # Invalid email format
    ConfigurationError         # Config issues
)

try:
    sender.send_text_email(...)
except AuthenticationError:
    print("Invalid Gmail credentials")
except SMTPConnectionError:
    print("Cannot connect to Gmail SMTP")
except SendFailureError:
    print("Failed to send email")
```

## Limitations

### Gmail Free Tier Limits:
- **500 emails per day** (rolling 24-hour period)
- **500 recipients per email** (To, Cc, Bcc combined)
- **25 MB attachment size** (not implemented in this module)

### Best Practices:
- Use App Passwords, not regular passwords
- Enable 2-factor authentication
- Monitor your daily sending quota
- Implement rate limiting for bulk sends
- Add delays between emails (use `time.sleep()`)

## Running Examples

### Simple Test Email
```bash
cd email_sender
python examples/simple_send.py
```

### Sales Email Example
```bash
python examples/sales_email.py
```

## Running Tests

```bash
cd email_sender
python -m unittest tests/test_gmail_sender.py -v
```

Or with pytest:
```bash
pytest tests/ -v
```

## Troubleshooting

### "Authentication failed"
- Make sure you're using a Gmail **App Password**, not your regular password
- Enable 2-factor authentication in your Google account
- Generate a new App Password in Google Account settings

### "Connection timeout"
- Check your internet connection
- Verify firewall isn't blocking port 587
- Try port 465 with SSL (update config)

### "Invalid email address"
- Verify email format is correct
- Check for typos in email addresses
- Ensure no extra spaces or special characters

### "Send failure after retries"
- Check Gmail sending limits (500/day)
- Verify recipient email addresses are valid
- Check if emails are being marked as spam

## Integration with Main Project

This module is designed to integrate with `openai_sdk_agent.py`:

```python
# In your main script
from email_sender import EmailConfig, GmailSender

# Configure
config = EmailConfig.from_env()
gmail_sender = GmailSender(config)

# Use in your agent tools
@function_tool
def send_email(subject: str, body: str, to_email: str) -> str:
    """Send email via Gmail SMTP"""
    try:
        result = gmail_sender.send_html_email(
            subject=subject,
            html_body=body,
            to_email=to_email
        )
        return f"Email sent to {to_email}"
    except Exception as e:
        return f"Failed to send: {str(e)}"
```

## Additional Resources

- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [Google App Passwords](https://support.google.com/accounts/answer/185833)
- [SMTP RFC Documentation](https://tools.ietf.org/html/rfc5321)

## License

Part of OpenAI SDK Multi-Agentic Workflow project.

## Support

For issues or questions:
1. Check the [Setup Guide](SETUP_GUIDE.md)
2. Review [Troubleshooting](#troubleshooting) section
3. Check Gmail SMTP settings in your Google account
4. Verify environment variables are set correctly

## Changelog

### v1.0.0 (2024)
- Initial release
- Gmail SMTP integration
- Email templates
- Retry logic
- Comprehensive error handling
