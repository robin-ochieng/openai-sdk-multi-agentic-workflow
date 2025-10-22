"""
Enhanced Email Agent
Converts report to HTML and sends via Gmail SMTP with advanced features and guardrails
"""

import os
import json
import logging
from openai import OpenAI
from agents import Agent, function_tool
from typing import Dict, List, Optional, Union, Any
from email_sender import EmailConfig, GmailSender
from email_sender.guardrails_email import EmailGuardrails
from datetime import datetime
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced instructions for the email agent
INSTRUCTIONS = (
    "You are an advanced email composition and delivery agent capable of sending "
    "professionally formatted HTML emails based on detailed reports. "
    "You will be provided with a detailed report and optional parameters. "
    "Your responsibilities include:\n"
    "1. Converting markdown/text reports to clean, responsive HTML\n"
    "2. Creating appropriate subject lines if not provided\n"
    "3. Adding proper formatting with tables, headers, and styling\n"
    "4. Including executive summaries when appropriate\n"
    "5. Handling multiple recipients and CC/BCC if needed\n"
    "6. Adding attachments when specified\n"
    "Use your tools to compose and send emails with professional formatting."
)


@function_tool
def send_email(
    subject: str, 
    html_body: str,
    recipients: Optional[Union[str, List[str]]] = None,
    cc: Optional[Union[str, List[str]]] = None,
    bcc: Optional[Union[str, List[str]]] = None,
    priority: str = "normal",
    include_timestamp: bool = True,
    add_footer: bool = True
) -> str:
    """
    Send an enhanced email with multiple recipients and advanced options
    
    Args:
        subject: Email subject line
        html_body: HTML content of the email
        recipients: Single email or list of recipient emails (optional, uses env default if not provided)
        cc: Single email or list of CC recipients (optional)
        bcc: Single email or list of BCC recipients (optional)
        priority: Email priority - "high", "normal", or "low" (default: "normal")
        include_timestamp: Add timestamp to email (default: True)
        add_footer: Add professional footer (default: True)
        
    Returns:
        Dict with status, message, and additional metadata
    """
    try:
        # Get email configuration from environment
        config = EmailConfig(
            gmail_email=os.environ.get('GMAIL_EMAIL'),
            gmail_app_password=os.environ.get('GMAIL_APP_PASSWORD')
        )
        
        # Handle recipients
        if recipients is None:
            recipients = os.environ.get('RECIPIENT_EMAIL')
        
        if isinstance(recipients, str):
            recipients = [recipients]
        
        # Process CC and BCC
        cc_list = [cc] if isinstance(cc, str) else cc or []
        bcc_list = [bcc] if isinstance(bcc, str) else bcc or []
        
        # Initialize Gmail sender and guardrails
        sender = GmailSender(config)
        guardrails = EmailGuardrails()
        
        # Enhance HTML body
        enhanced_body = _enhance_html_body(
            html_body, 
            include_timestamp, 
            add_footer,
            priority
        )
        
        # Validate all recipients
        all_recipients = recipients + cc_list + bcc_list
        for recipient in all_recipients:
            validation = guardrails.run_all_checks(
                subject=subject,
                body=enhanced_body,
                recipient_email=recipient
            )
            
            if not validation['passed']:
                logger.warning(f"Guardrail check failed for {recipient}: {validation['blocking_issues']}")
                return {
                    "status": "blocked",
                    "message": f"Email blocked by guardrails for {recipient}: {', '.join(validation['blocking_issues'])}",
                    "details": validation
                }
        
        # Send emails
        results = []
        for recipient in recipients:
            result = sender.send_html_email(
                to_email=recipient,
                subject=subject,
                html_body=enhanced_body,
                cc=cc_list,
                bcc=bcc_list,
                priority=priority
            )
            results.append({
                "recipient": recipient,
                "success": result.get('success'),
                "message": result.get('message')
            })
            
            if result.get('success'):
                guardrails.record_send()
                logger.info(f"Email sent successfully to {recipient}")
            else:
                logger.error(f"Failed to send email to {recipient}: {result.get('message')}")
        
        # Aggregate results
        all_success = all(r['success'] for r in results)
        
        result_data = {
            "status": "success" if all_success else "partial",
            "message": f"Email sent to {len([r for r in results if r['success']])} of {len(results)} recipients",
            "details": results,
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "subject": subject,
                "priority": priority,
                "total_recipients": len(all_recipients)
            }
        }
        return json.dumps(result_data)
            
    except Exception as e:
        logger.error(f"Exception while sending email: {str(e)}", exc_info=True)
        error_data = {
            "status": "error",
            "message": f"Exception while sending email: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_data)


@function_tool
def preview_email(subject: str, html_body: str, format_type: str = "html") -> str:
    """
    Preview the email before sending
    
    Args:
        subject: Email subject line
        html_body: HTML content of the email
        format_type: "html" or "text" for preview format
        
    Returns:
        JSON string with preview content
    """
    try:
        if format_type == "text":
            # Convert HTML to plain text
            text_body = re.sub('<[^<]+?>', '', html_body)
            result = {
                "status": "success",
                "subject": subject,
                "body": text_body,
                "format": "text"
            }
        else:
            result = {
                "status": "success",
                "subject": subject,
                "body": html_body,
                "format": "html"
            }
        return json.dumps(result)
    except Exception as e:
        error = {
            "status": "error",
            "message": f"Failed to preview email: {str(e)}"
        }
        return json.dumps(error)


@function_tool
def save_draft(subject: str, html_body: str, metadata: Optional[str] = None) -> str:
    """
    Save email as draft for later sending
    
    Args:
        subject: Email subject line
        html_body: HTML content of the email
        metadata: Additional metadata as JSON string (optional)
        
    Returns:
        JSON string with draft ID and status
    """
    try:
        draft_dir = os.environ.get('DRAFT_DIR', './email_drafts')
        os.makedirs(draft_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        draft_id = f"draft_{timestamp}"
        
        # Parse metadata if provided
        metadata_dict = {}
        if metadata:
            try:
                metadata_dict = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in metadata, using empty dict")
        
        draft_data = {
            "id": draft_id,
            "subject": subject,
            "html_body": html_body,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata_dict
        }
        
        draft_path = os.path.join(draft_dir, f"{draft_id}.json")
        with open(draft_path, 'w') as f:
            json.dump(draft_data, f, indent=2)
        
        logger.info(f"Draft saved with ID: {draft_id}")
        
        result = {
            "status": "success",
            "draft_id": draft_id,
            "path": draft_path,
            "message": f"Draft saved successfully with ID: {draft_id}"
        }
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed to save draft: {str(e)}")
        error = {
            "status": "error",
            "message": f"Failed to save draft: {str(e)}"
        }
        return json.dumps(error)


def _enhance_html_body(
    html_body: str, 
    include_timestamp: bool = True,
    add_footer: bool = True,
    priority: str = "normal"
) -> str:
    """
    Enhance HTML body with professional styling and optional elements
    
    Args:
        html_body: Original HTML content
        include_timestamp: Add timestamp to email
        add_footer: Add professional footer
        priority: Email priority level
        
    Returns:
        Enhanced HTML string
    """
    # Professional CSS styling
    css_style = """
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }
        h1, h2, h3 { color: #2c3e50; }
        table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: 600; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 2px solid #e9ecef; font-size: 0.9em; color: #6c757d; }
        .priority-high { border-left: 4px solid #dc3545; padding-left: 10px; }
        .priority-normal { border-left: 4px solid #007bff; padding-left: 10px; }
        .priority-low { border-left: 4px solid #28a745; padding-left: 10px; }
        .timestamp { font-size: 0.85em; color: #6c757d; margin-bottom: 20px; }
        .summary-box { background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }
    </style>
    """
    
    # Build enhanced HTML
    enhanced = f"<html><head>{css_style}</head><body>"
    
    # Add priority indicator
    if priority != "normal":
        enhanced += f'<div class="priority-{priority}">'
    
    # Add timestamp if requested
    if include_timestamp:
        timestamp = datetime.now().strftime('%B %d, %Y at %I:%M %p')
        enhanced += f'<div class="timestamp">Generated on {timestamp}</div>'
    
    # Add main content
    enhanced += html_body
    
    # Close priority div if needed
    if priority != "normal":
        enhanced += '</div>'
    
    # Add footer if requested
    if add_footer:
        footer = """
        <div class="footer">
            <p>This email was automatically generated by the Research Agent System.</p>
            <p style="font-size: 0.8em;">Please do not reply to this email. For questions, contact your administrator.</p>
        </div>
        """
        enhanced += footer
    
    enhanced += "</body></html>"
    
    return enhanced


def create_email_agent(
    api_key: str, 
    model: str = "gpt-4o",
    enable_drafts: bool = True,
    enable_preview: bool = True
) -> Agent:
    """
    Create an enhanced Email Agent with advanced capabilities
    
    This agent converts markdown reports to professional HTML and sends them via
    Gmail SMTP with full guardrails protection, multi-recipient support, and
    additional features like drafts and previews.
    
    Args:
        api_key: OpenAI API key
        model: Model to use (default: gpt-4o)
        enable_drafts: Enable draft saving functionality (default: True)
        enable_preview: Enable email preview functionality (default: True)
        
    Returns:
        Configured Agent instance with enhanced email tools
        
    Example:
        >>> email_agent = create_email_agent(api_key, enable_drafts=True)
        >>> result = Runner.run(email_agent, {
        ...     "report": report_data,
        ...     "recipients": ["user1@example.com", "user2@example.com"],
        ...     "priority": "high"
        ... })
        >>> print(result.final_output)
    """
    client = OpenAI(api_key=api_key)
    
    # Build tool list based on configuration
    tools = [send_email]
    
    if enable_preview:
        tools.append(preview_email)
        logger.info("Email preview functionality enabled")
    
    if enable_drafts:
        tools.append(save_draft)
        logger.info("Email draft functionality enabled")
    
    email_agent = Agent(
        name="EnhancedEmailAgent",
        instructions=INSTRUCTIONS,
        tools=tools,
        model=model,
    )
    
    logger.info(f"Enhanced Email Agent created with {len(tools)} tools")
    
    return email_agent
