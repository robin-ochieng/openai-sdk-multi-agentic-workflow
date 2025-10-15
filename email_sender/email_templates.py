"""
Email Templates
Pre-built templates for common email types
"""
from typing import Optional


def create_plain_text_email(
    greeting: str,
    body: str,
    closing: str = "Best regards",
    signature: Optional[str] = None
) -> str:
    """
    Create plain text email with standard formatting
    
    Args:
        greeting: Email greeting (e.g., "Hi John,")
        body: Main email content
        closing: Closing phrase (default: "Best regards")
        signature: Optional signature block
        
    Returns:
        Formatted plain text email
    """
    parts = [greeting, "", body, "", closing]
    
    if signature:
        parts.extend(["", signature])
    
    return "\n".join(parts)


def create_html_email(
    greeting: str,
    body: str,
    closing: str = "Best regards",
    signature: Optional[str] = None,
    header_color: str = "#4A90E2",
    font_family: str = "Arial, sans-serif"
) -> str:
    """
    Create HTML email with professional styling
    
    Args:
        greeting: Email greeting
        body: Main email content (can include HTML)
        closing: Closing phrase
        signature: Optional signature block
        header_color: Header background color (hex)
        font_family: Font family for email
        
    Returns:
        Formatted HTML email
    """
    signature_html = f"<p><strong>{signature}</strong></p>" if signature else ""
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: {font_family};
            line-height: 1.6;
            color: #333333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: {header_color};
            color: white;
            padding: 20px;
            border-radius: 5px 5px 0 0;
            text-align: center;
        }}
        .content {{
            background-color: #f9f9f9;
            padding: 30px;
            border-radius: 0 0 5px 5px;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
        }}
        .body {{
            margin-bottom: 30px;
        }}
        .closing {{
            margin-top: 30px;
            font-style: italic;
        }}
        .signature {{
            margin-top: 10px;
            color: #666666;
        }}
    </style>
</head>
<body>
    <div class="content">
        <p class="greeting">{greeting}</p>
        <div class="body">
            {body}
        </div>
        <p class="closing">{closing}</p>
        {signature_html}
    </div>
</body>
</html>
    """
    return html.strip()


def create_sales_email(
    recipient_name: str,
    product_name: str,
    value_proposition: str,
    call_to_action: str,
    sender_name: str,
    sender_title: str = "Sales Representative",
    company_name: str = "Our Company",
    tone: str = "professional"
) -> tuple[str, str]:
    """
    Create sales email in both plain text and HTML formats
    
    Args:
        recipient_name: Name of recipient
        product_name: Product or service name
        value_proposition: Main selling point
        call_to_action: What you want recipient to do
        sender_name: Sender's name
        sender_title: Sender's job title
        company_name: Company name
        tone: Email tone ("professional", "friendly", "casual")
        
    Returns:
        tuple: (plain_text_version, html_version)
    """
    # Adjust greeting based on tone
    greetings = {
        "professional": f"Dear {recipient_name},",
        "friendly": f"Hi {recipient_name},",
        "casual": f"Hey {recipient_name}!"
    }
    greeting = greetings.get(tone, greetings["professional"])
    
    # Build body content
    body_text = f"""I wanted to reach out to introduce you to {product_name}.

{value_proposition}

{call_to_action}

I'd love to discuss how {product_name} can benefit you. Would you be available for a brief call this week?"""
    
    body_html = f"""
        <p>I wanted to reach out to introduce you to <strong>{product_name}</strong>.</p>
        
        <p>{value_proposition}</p>
        
        <p style="background-color: #fffacd; padding: 15px; border-left: 4px solid #4A90E2;">
            {call_to_action}
        </p>
        
        <p>I'd love to discuss how <strong>{product_name}</strong> can benefit you. 
        Would you be available for a brief call this week?</p>
    """
    
    # Build signature
    signature = f"{sender_name}\n{sender_title}\n{company_name}"
    signature_html = f"{sender_name}<br/>{sender_title}<br/>{company_name}"
    
    # Create both versions
    plain_text = create_plain_text_email(
        greeting=greeting,
        body=body_text,
        closing="Looking forward to hearing from you!",
        signature=signature
    )
    
    html_version = create_html_email(
        greeting=greeting,
        body=body_html,
        closing="Looking forward to hearing from you!",
        signature=signature_html
    )
    
    return plain_text, html_version


def create_followup_email(
    recipient_name: str,
    previous_subject: str,
    days_since: int,
    additional_info: str,
    sender_name: str,
    tone: str = "friendly"
) -> tuple[str, str]:
    """
    Create follow-up email after no response
    
    Args:
        recipient_name: Name of recipient
        previous_subject: Subject of previous email
        days_since: Days since last email
        additional_info: Additional information to share
        sender_name: Sender's name
        tone: Email tone
        
    Returns:
        tuple: (plain_text_version, html_version)
    """
    greetings = {
        "professional": f"Dear {recipient_name},",
        "friendly": f"Hi {recipient_name},",
        "casual": f"Hey {recipient_name}!"
    }
    greeting = greetings.get(tone, greetings["friendly"])
    
    body_text = f"""I wanted to follow up on my previous email about "{previous_subject}" from {days_since} days ago.

I understand you're busy, but I thought you might be interested in this additional information:

{additional_info}

If you have any questions or would like to learn more, I'm happy to chat!"""
    
    body_html = f"""
        <p>I wanted to follow up on my previous email about 
        <strong>"{previous_subject}"</strong> from {days_since} days ago.</p>
        
        <p>I understand you're busy, but I thought you might be interested in this 
        additional information:</p>
        
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
            {additional_info}
        </div>
        
        <p>If you have any questions or would like to learn more, I'm happy to chat!</p>
    """
    
    plain_text = create_plain_text_email(
        greeting=greeting,
        body=body_text,
        closing="Best regards",
        signature=sender_name
    )
    
    html_version = create_html_email(
        greeting=greeting,
        body=body_html,
        closing="Best regards",
        signature=sender_name
    )
    
    return plain_text, html_version


def create_test_email() -> tuple[str, str]:
    """
    Create simple test email for connection testing
    
    Returns:
        tuple: (plain_text_version, html_version)
    """
    plain_text = create_plain_text_email(
        greeting="Hello!",
        body="This is a test email from the Gmail SMTP sender.\n\nIf you're reading this, the email system is working correctly! 🎉",
        closing="Test email sent by OpenAI SDK Agents",
        signature="Automated Email System"
    )
    
    html_version = create_html_email(
        greeting="Hello!",
        body="""
            <p>This is a test email from the Gmail SMTP sender.</p>
            <p>If you're reading this, the email system is working correctly! 🎉</p>
            <div style="background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 5px; margin-top: 20px;">
                <strong>✅ Status:</strong> Email delivery is operational
            </div>
        """,
        closing="Test email sent by OpenAI SDK Agents",
        signature="Automated Email System"
    )
    
    return plain_text, html_version
