"""
OpenAI SDK Sales Agent System with Guardrails
An automated cold email generation and delivery system using multiple AI agents
NOW WITH COMPREHENSIVE GUARDRAILS & STRUCTURED OUTPUTS
"""

# Core imports
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Dict, Optional
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

# NOTE: Update these imports based on your OpenAI SDK version
# The 'agents' module import needs to be corrected - see documentation
try:
    from openai import OpenAI
    from openai.types.responses import ResponseTextDeltaEvent
    client = OpenAI()
except ImportError:
    print("⚠️  OpenAI SDK not properly installed or 'agents' module not available")
    print("Please check your OpenAI SDK version and documentation")

# Load environment variables from .env file
load_dotenv(override=True)

# Import guardrail system
from email_sender.guardrails_email import EmailGuardrails


# ============================================================================
# STRUCTURED OUTPUT MODELS - For Robust AI Responses
# ============================================================================

class NameCheckOutput(BaseModel):
    """Structured output for name validation guardrail"""
    is_name_in_message: bool = Field(
        description="True if the user is including someone's personal name"
    )
    name: str = Field(
        description="The name found in the message, or empty string if no name found"
    )


class EmailDraft(BaseModel):
    """Structured model for email drafts"""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    tone: str = Field(description="Tone used (professional/engaging/concise)")
    confidence_score: float = Field(
        description="Confidence in quality (0-1)",
        ge=0.0,
        le=1.0
    )


class EmailSelectionOutput(BaseModel):
    """Structured output for email selection"""
    selected_email: str = Field(description="The selected best email")
    selection_reason: str = Field(description="Why this email was chosen")
    estimated_response_rate: float = Field(
        description="Estimated response rate (0-1)",
        ge=0.0,
        le=1.0
    )


# ============================================================================
# GUARDRAIL IMPLEMENTATION - Input & Output Validation
# ============================================================================

class GuardrailAgent:
    """
    Guardrail agent that checks inputs before processing
    Based on the OpenAI Agents framework pattern
    """
    
    def __init__(self):
        self.email_guardrails = EmailGuardrails()
    
    async def check_name_in_message(self, message: str) -> NameCheckOutput:
        """
        Check if the user is including someone's personal name
        This prevents inappropriate use of personal information
        
        Args:
            message: The input message to check
            
        Returns:
            NameCheckOutput with check results
        """
        # Simple name detection logic
        # In production, use NER or AI model
        common_salutations = ['dear', 'hi', 'hello', 'hey']
        words = message.lower().split()
        
        found_name = ""
        is_name_present = False
        
        for i, word in enumerate(words):
            if word in common_salutations and i + 1 < len(words):
                potential_name = words[i + 1].strip(',')
                # Check if it's likely a name (capitalized, not common words)
                if potential_name.capitalize() == potential_name and \
                   potential_name.lower() not in ['sir', 'madam', 'ceo', 'team']:
                    found_name = potential_name
                    is_name_present = True
                    break
        
        return NameCheckOutput(
            is_name_in_message=is_name_present,
            name=found_name
        )
    
    async def validate_email_before_send(
        self,
        subject: str,
        body: str,
        recipient_email: str,
        recipient_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Run all email guardrails before sending
        
        Args:
            subject: Email subject
            body: Email body
            recipient_email: Recipient email address
            recipient_name: Optional recipient name
            
        Returns:
            Dict with validation results
        """
        return self.email_guardrails.run_all_checks(
            subject=subject,
            body=body,
            recipient_email=recipient_email,
            recipient_name=recipient_name
        )


# ============================================================================
# INITIALIZE GUARDRAILS
# ============================================================================

guardrail_system = GuardrailAgent()


# ============================================================================
# EMAIL TESTING
# ============================================================================

def send_test_email():
    """Test SendGrid email functionality - use this first to verify setup"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDER_EMAIL', 'your_email@example.com'))
    to_email = To(os.environ.get('RECIPIENT_EMAIL', 'recipient@example.com'))
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"SendGrid response status: {response.status_code}")
    return response.status_code


# ============================================================================
# AGENT INSTRUCTIONS - Customize these for your company
# ============================================================================

# Agent 1: Professional and formal tone
instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

# Agent 2: Engaging and witty tone
instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

# Agent 3: Brief and concise tone
instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."


# ============================================================================
# PROTECTED EMAIL SENDING WITH GUARDRAILS
# ============================================================================

async def send_email_with_guardrails(subject: str, body: str, recipient_email: str) -> Dict[str, any]:
    """
    Send email with comprehensive guardrail checks
    
    Args:
        subject: Email subject
        body: Email body
        recipient_email: Recipient email
        
    Returns:
        Dict with sending result
    """
    print("\n" + "=" * 60)
    print("🛡️  RUNNING GUARDRAIL CHECKS")
    print("=" * 60)
    
    # Run all guardrail checks
    validation_result = await guardrail_system.validate_email_before_send(
        subject=subject,
        body=body,
        recipient_email=recipient_email
    )
    
    # Display results
    print(f"\n📊 Guardrail Results:")
    print(f"   Passed: {validation_result['passed']}")
    
    if validation_result['blocking_issues']:
        print(f"\n❌ BLOCKING ISSUES:")
        for issue in validation_result['blocking_issues']:
            print(f"   - {issue}")
    
    if validation_result['warnings']:
        print(f"\n⚠️  WARNINGS:")
        for warning in validation_result['warnings']:
            print(f"   - {warning}")
    
    # Check spam score
    spam_info = validation_result['checks']['spam']
    print(f"\n📈 Spam Score: {spam_info['spam_score']}/100 ({spam_info['severity']} severity)")
    
    # Show statistics
    stats = guardrail_system.email_guardrails.get_statistics()
    print(f"\n📧 Sending Statistics:")
    print(f"   Last hour: {stats['sent_last_hour']}/{stats['hourly_limit']}")
    print(f"   Last 24h: {stats['sent_last_24h']}/{stats['daily_limit']}")
    
    # Decide whether to send
    if not validation_result['passed']:
        print(f"\n🚫 EMAIL BLOCKED BY GUARDRAILS")
        print("=" * 60)
        return {
            "status": "blocked",
            "reason": validation_result['blocking_issues'],
            "validation": validation_result
        }
    
    # Send the email
    print(f"\n✅ All guardrails passed - sending email...")
    
    try:
        sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        from_email = Email(os.environ.get('SENDER_EMAIL', 'your_email@example.com'))
        to_email = To(recipient_email)
        content = Content("text/html", body)
        mail = Mail(from_email, to_email, subject, content).get()
        response = sg.client.mail.send.post(request_body=mail)
        
        # Record the send for rate limiting
        guardrail_system.email_guardrails.record_send()
        
        print(f"📬 Email sent! Status: {response.status_code}")
        print("=" * 60)
        
        return {
            "status": "success",
            "status_code": response.status_code,
            "validation": validation_result
        }
    except Exception as e:
        print(f"❌ Error sending email: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "validation": validation_result
        }


# ============================================================================
# INPUT GUARDRAIL - Check for Personal Names
# ============================================================================

async def check_input_guardrails(message: str) -> Dict[str, any]:
    """
    Check input message with guardrails before processing
    
    Args:
        message: The user input to check
        
    Returns:
        Dict with guardrail check results
    """
    print("\n" + "=" * 60)
    print("🛡️  INPUT GUARDRAIL CHECK")
    print("=" * 60)
    
    # Check for personal names
    name_check = await guardrail_system.check_name_in_message(message)
    
    print(f"\n📝 Message: {message}")
    print(f"\n🔍 Name detected: {name_check.is_name_in_message}")
    
    if name_check.is_name_in_message:
        print(f"   Found name: '{name_check.name}'")
        print(f"\n⚠️  WARNING: Personal name detected in input!")
        print(f"   This may require special handling for privacy/compliance")
    
    print("=" * 60)
    
    return {
        "passed": True,  # We allow it but flag it
        "name_detected": name_check.is_name_in_message,
        "name": name_check.name,
        "requires_review": name_check.is_name_in_message
    }


# ============================================================================
# EXAMPLE: Full Workflow with Guardrails
# ============================================================================

async def run_protected_email_workflow():
    """
    Complete email workflow with comprehensive guardrails
    Demonstrates input validation, output validation, and safe sending
    """
    print("\n" + "=" * 60)
    print("🚀 PROTECTED EMAIL WORKFLOW")
    print("=" * 60)
    
    # Step 1: Check input with guardrails
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    input_check = await check_input_guardrails(message)
    
    if input_check['requires_review']:
        print(f"\n⚠️  Input requires manual review due to personal name: {input_check['name']}")
        # In production, you might pause here for approval
    
    # Step 2: Generate email (simulated - replace with actual agent)
    print(f"\n📝 Generating email draft...")
    
    # Simulated email content
    email_subject = "Quick question about your compliance needs"
    email_body = """
<html>
<body>
<p>Hi,</p>

<p>I noticed your company is in the fintech space and thought you might be 
interested in our AI-powered compliance solution for SOC2 preparation.</p>

<p>Our tool has helped over 100 companies achieve compliance 50% faster.</p>

<p>Would you be open to a quick 15-minute call next week to discuss?</p>

<p>Best regards,<br>
Alice<br>
ComplAI Sales Team</p>
</body>
</html>
"""
    
    recipient_email = os.environ.get('RECIPIENT_EMAIL', 'test@example.com')
    
    print(f"   Subject: {email_subject}")
    print(f"   Recipient: {recipient_email}")
    
    # Step 3: Send with guardrails
    result = await send_email_with_guardrails(
        subject=email_subject,
        body=email_body,
        recipient_email=recipient_email
    )
    
    # Step 4: Report final status
    print(f"\n📊 FINAL RESULT:")
    print(f"   Status: {result['status']}")
    
    if result['status'] == 'success':
        print(f"   ✅ Email sent successfully!")
        print(f"   HTTP Status: {result['status_code']}")
    elif result['status'] == 'blocked':
        print(f"   🚫 Email blocked by guardrails")
        print(f"   Reasons: {', '.join(result['reason'])}")
    else:
        print(f"   ❌ Error: {result.get('error')}")
    
    return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function to run the sales automation system with guardrails"""
    print("=" * 60)
    print("OpenAI SDK Sales Agent System WITH GUARDRAILS")
    print("=" * 60)
    
    # 📝 INSTRUCTIONS: Choose one option
    
    # Option 1: Test guardrails with protected workflow
    await run_protected_email_workflow()
    
    # Option 2: Test SendGrid connection
    # send_test_email()
    
    print("\n" + "=" * 60)
    print("Execution complete!")
    print("=" * 60)


# Program entry point
if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
