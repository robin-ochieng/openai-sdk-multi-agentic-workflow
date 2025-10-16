"""
Email Agent
Converts report to HTML and sends via Gmail SMTP with guardrails
"""

import os
from openai import OpenAI
from openai.lib._agents import Agent, function_tool
from typing import Dict
from ...email_sender import EmailConfig, GmailSender
from ...email_sender.guardrails_email import EmailGuardrails


# Instructions for the email agent
INSTRUCTIONS = (
    "You are able to send a nicely formatted HTML email based on a detailed report. "
    "You will be provided with a detailed report. You should use your tool to send one email, providing the "
    "report converted into clean, well presented HTML with an appropriate subject line."
)


@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    """
    Send out an email with the given subject and HTML body
    
    Args:
        subject: Email subject line
        html_body: HTML content of the email
        
    Returns:
        Dict with status and message
    """
    try:
        # Get email configuration from environment
        config = EmailConfig(
            gmail_email=os.environ.get('GMAIL_EMAIL'),
            gmail_app_password=os.environ.get('GMAIL_APP_PASSWORD')
        )
        
        recipient = os.environ.get('RECIPIENT_EMAIL')
        
        # Initialize Gmail sender and guardrails
        sender = GmailSender(config)
        guardrails = EmailGuardrails()
        
        # Run guardrail checks
        validation = guardrails.run_all_checks(
            subject=subject,
            body=html_body,
            recipient_email=recipient
        )
        
        # Check if email passes guardrails
        if not validation['passed']:
            return {
                "status": "blocked",
                "message": f"Email blocked by guardrails: {', '.join(validation['blocking_issues'])}"
            }
        
        # Send email via Gmail SMTP
        result = sender.send_html_email(
            to_email=recipient,
            subject=subject,
            html_body=html_body
        )
        
        if result.get('success'):
            # Record send for rate limiting
            guardrails.record_send()
            
            return {
                "status": "success",
                "message": f"Email sent successfully to {recipient}"
            }
        else:
            return {
                "status": "error",
                "message": f"Failed to send email: {result.get('message', 'Unknown error')}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Exception while sending email: {str(e)}"
        }


def create_email_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent:
    """
    Create the Email Agent
    
    This agent converts the markdown report to clean HTML and sends it via
    Gmail SMTP with full guardrails protection.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o-mini)
        
    Returns:
        Configured Agent instance with send_email tool
        
    Example:
        >>> email_agent = create_email_agent(api_key)
        >>> result = Runner.run(email_agent, {"report": report_data})
        >>> print(result.final_output)
    """
    client = OpenAI(api_key=api_key)
    
    email_agent = Agent(
        name="EmailAgent",
        instructions=INSTRUCTIONS,
        tools=[send_email],
        model=model,
    )
    
    return email_agent
