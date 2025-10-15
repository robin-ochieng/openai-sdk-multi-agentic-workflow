"""
Simple example: Send a test email using Gmail SMTP
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_sender import EmailConfig, GmailSender
from email_sender.email_templates import create_test_email


def main():
    """Send a simple test email"""
    print("📧 Gmail SMTP Test Email Sender")
    print("=" * 50)
    
    try:
        # Load configuration from .env file
        print("\n1. Loading configuration...")
        config = EmailConfig.from_env()
        print(f"   ✅ Loaded config for: {config.gmail_email}")
        print(f"   ✅ Default recipient: {config.recipient_email}")
        
        # Create sender instance
        print("\n2. Creating Gmail sender...")
        sender = GmailSender(config)
        print("   ✅ Gmail sender created")
        
        # Test connection
        print("\n3. Testing SMTP connection...")
        result = sender.test_connection()
        if result['success']:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ {result['message']}")
            return
        
        # Create test email
        print("\n4. Creating test email...")
        plain_text, html_body = create_test_email()
        print("   ✅ Test email created")
        
        # Send plain text version
        print("\n5. Sending plain text email...")
        result = sender.send_text_email(
            subject="Test Email - Plain Text",
            body=plain_text
        )
        print(f"   ✅ {result['message']}")
        print(f"   📬 Recipients: {', '.join(result['recipients'])}")
        
        # Send HTML version
        print("\n6. Sending HTML email...")
        result = sender.send_html_email(
            subject="Test Email - HTML",
            html_body=html_body,
            plain_body=plain_text
        )
        print(f"   ✅ {result['message']}")
        print(f"   📬 Recipients: {', '.join(result['recipients'])}")
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        print(f"📬 Check your inbox at: {config.recipient_email}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure GMAIL_EMAIL and GMAIL_APP_PASSWORD are set in .env")
        print("2. Use Gmail App Password, not regular password")
        print("3. Enable 2-factor authentication and generate App Password")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
