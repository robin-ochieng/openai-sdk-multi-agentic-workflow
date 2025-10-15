"""
Integration example: Using Gmail sender with OpenAI SDK Agents
Shows how to integrate the email sender with your main agent
"""
import sys
import os

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from email_sender import EmailConfig, GmailSender
from email_sender.email_templates import create_sales_email

# Initialize Gmail sender once (at module level)
print("🔧 Initializing Gmail SMTP sender...")
gmail_config = EmailConfig.from_env()
gmail_sender = GmailSender(gmail_config)
print(f"✅ Gmail sender ready for: {gmail_config.gmail_email}\n")

# Example 1: Simple email function for agents
def send_agent_email(subject: str, body: str, recipient: str) -> str:
    """
    Simple email function that agents can call
    Returns success message or error
    """
    try:
        result = gmail_sender.send_html_email(
            subject=subject,
            html_body=body,
            to_email=recipient
        )
        return f"✅ Email sent successfully to {recipient}"
    except Exception as e:
        return f"❌ Failed to send email: {str(e)}"

# Example 2: Sales email function using templates
def send_sales_email(
    recipient_name: str,
    recipient_email: str,
    product: str,
    value_prop: str
) -> str:
    """
    Send a formatted sales email using templates
    """
    try:
        plain, html = create_sales_email(
            recipient_name=recipient_name,
            product_name=product,
            value_proposition=value_prop,
            call_to_action="Let's schedule a quick call to discuss!",
            sender_name="AI Sales Agent",
            sender_title="Automated Sales Assistant",
            company_name="Your Company",
            tone="friendly"
        )
        
        result = gmail_sender.send_html_email(
            subject=f"Introducing {product}",
            html_body=html,
            plain_body=plain,
            to_email=recipient_email
        )
        
        return f"✅ Sales email sent to {recipient_name} at {recipient_email}"
    except Exception as e:
        return f"❌ Failed: {str(e)}"

# Demo the functions
if __name__ == "__main__":
    print("=" * 60)
    print("📧 Gmail Integration Demo - Ready for Agent Use")
    print("=" * 60)
    
    print("\n1️⃣ Testing simple email function...")
    result1 = send_agent_email(
        subject="Test from AI Agent",
        body="<h1>Hello!</h1><p>This email was sent by an AI agent using Gmail SMTP.</p>",
        recipient=gmail_config.recipient_email
    )
    print(f"   {result1}")
    
    print("\n2️⃣ Testing sales email function with template...")
    result2 = send_sales_email(
        recipient_name="Robin",
        recipient_email=gmail_config.recipient_email,
        product="Multi-Agent AI System",
        value_prop="Automate complex workflows with multiple specialized AI agents working together"
    )
    print(f"   {result2}")
    
    print("\n" + "=" * 60)
    print("✅ Integration demo complete!")
    print("\n📝 To integrate with openai_sdk_agent.py:")
    print("   1. Import: from email_sender import EmailConfig, GmailSender")
    print("   2. Initialize: gmail_sender = GmailSender(EmailConfig.from_env())")
    print("   3. Replace send_email() function with gmail_sender.send_html_email()")
    print("\n📬 Check inbox at:", gmail_config.recipient_email)
