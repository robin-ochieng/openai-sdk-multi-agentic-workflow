"""
Sales email example: Send a sales email using templates
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from email_sender import EmailConfig, GmailSender
from email_sender.email_templates import create_sales_email


def main():
    """Send a sales email example"""
    print("📧 Sales Email Sender Example")
    print("=" * 50)
    
    try:
        # Load configuration
        print("\n1. Loading configuration...")
        config = EmailConfig.from_env()
        print(f"   ✅ Config loaded")
        
        # Create sender
        sender = GmailSender(config)
        
        # Create sales email
        print("\n2. Creating sales email...")
        plain_text, html_body = create_sales_email(
            recipient_name="Robin",
            product_name="AI Sales Automation Platform",
            value_proposition=(
                "Our platform uses advanced AI to automate your sales outreach, "
                "saving you 10+ hours per week while increasing response rates by 40%."
            ),
            call_to_action=(
                "🚀 Book a free demo today and see how we can transform your sales process!"
            ),
            sender_name="John Smith",
            sender_title="Senior Sales Engineer",
            company_name="AI Solutions Inc.",
            tone="friendly"
        )
        print("   ✅ Sales email created")
        
        # Send HTML email
        print("\n3. Sending sales email...")
        result = sender.send_html_email(
            subject="🚀 Transform Your Sales Process with AI",
            html_body=html_body,
            plain_body=plain_text,
            to_email=config.recipient_email
        )
        print(f"   ✅ {result['message']}")
        print(f"   📬 Sent to: {', '.join(result['recipients'])}")
        
        print("\n" + "=" * 50)
        print("✅ Sales email sent successfully!")
        print(f"📬 Check your inbox at: {config.recipient_email}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
