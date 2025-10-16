"""
Quick test script for Gmail SMTP sender
Run from project root directory
"""
import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("📧 Gmail SMTP Test Email Sender")
print("=" * 50)

try:
    # Import from email_sender package
    from email_sender import EmailConfig, GmailSender
    from email_sender.email_templates import create_test_email
    
    print("\n✅ Modules imported successfully")
    
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
        print("\nTroubleshooting:")
        print("1. Make sure GMAIL_EMAIL and GMAIL_APP_PASSWORD are set in .env")
        print("2. Use Gmail App Password, not regular password")
        print("3. Enable 2-factor authentication and generate App Password")
        sys.exit(1)
    
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
    print("\nNext steps:")
    print("1. Check your Gmail inbox")
    print("2. Look for 2 test emails")
    print("3. If emails are in spam, mark as 'Not spam'")
    
except FileNotFoundError as e:
    print(f"\n❌ Error: .env file not found")
    print(f"   {str(e)}")
    print("\nPlease create a .env file in the project root with:")
    print("   GMAIL_EMAIL=your.email@gmail.com")
    print("   GMAIL_APP_PASSWORD=your_16_char_app_password")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Make sure GMAIL_EMAIL and GMAIL_APP_PASSWORD are set in .env")
    print("2. Use Gmail App Password, not regular password")
    print("3. Enable 2-factor authentication on Gmail")
    print("4. Generate App Password at: https://myaccount.google.com/apppasswords")
    print("5. Remove all spaces from the App Password")
    print("\nFor detailed setup, see: email_sender/SETUP_GUIDE.md")
    sys.exit(1)
