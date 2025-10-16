"""
Test sales email template
Run from project root directory
"""
import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

print("📧 Sales Email Template Test")
print("=" * 50)

try:
    from email_sender import EmailConfig, GmailSender
    from email_sender.email_templates import create_sales_email
    
    # Load configuration
    print("\n1. Loading configuration...")
    config = EmailConfig.from_env()
    print(f"   ✅ Config loaded for: {config.gmail_email}")
    
    # Create sender
    print("\n2. Creating Gmail sender...")
    sender = GmailSender(config)
    print("   ✅ Sender created")
    
    # Create sales email with your name
    print("\n3. Creating sales email...")
    plain_text, html_body = create_sales_email(
        recipient_name="Robin",
        product_name="AI Sales Automation Platform",
        value_proposition=(
            "Our platform uses advanced AI agents to automate your sales outreach, "
            "saving you 10+ hours per week while increasing response rates by 40%. "
            "The multi-agent system handles everything from email generation to follow-ups."
        ),
        call_to_action=(
            "🚀 Book a free demo today and see how we can transform your sales process!"
        ),
        sender_name="Sales Team",
        sender_title="Senior Sales Engineer",
        company_name="AI Solutions Inc.",
        tone="friendly"
    )
    print("   ✅ Sales email created with professional formatting")
    
    # Send HTML email
    print("\n4. Sending sales email...")
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
    print("\nThis email demonstrates:")
    print("  • Professional HTML formatting")
    print("  • Custom styling and colors")
    print("  • Call-to-action highlighting")
    print("  • Friendly tone customization")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    sys.exit(1)
