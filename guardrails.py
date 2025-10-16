"""
Guardrails & Structured Outputs for Robust AI Agent Systems
Implements input validation, output validation, and safety checks
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from agents import Agent, Runner, function_tool
import re


# ============================================================================
# STRUCTURED OUTPUT MODELS
# ============================================================================

class NameCheckOutput(BaseModel):
    """Structured output for name validation guardrail"""
    is_name_in_message: bool = Field(
        description="True if the user is including someone's personal name in what they want you to do"
    )
    name: str = Field(
        description="The name found in the message, or empty string if no name found"
    )


class GuardrailFunctionOutput(BaseModel):
    """Structured output for guardrail function results"""
    output_info: dict = Field(
        description="Information about the guardrail check"
    )
    tripwire_triggered: bool = Field(
        description="True if the guardrail was triggered (potential issue detected)"
    )


class EmailValidationOutput(BaseModel):
    """Structured output for email content validation"""
    is_valid: bool = Field(description="Whether the email content is valid")
    contains_spam_indicators: bool = Field(description="Whether spam indicators detected")
    tone_appropriate: bool = Field(description="Whether the tone is professional")
    has_personalization: bool = Field(description="Whether email has personalization")
    issues: List[str] = Field(default_factory=list, description="List of issues found")


class EmailContent(BaseModel):
    """Structured model for email content"""
    subject: str = Field(description="Email subject line")
    body: str = Field(description="Email body content")
    recipient_email: str = Field(description="Recipient email address")
    
    @validator('recipient_email')
    def validate_email(cls, v):
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError(f"Invalid email format: {v}")
        return v


# ============================================================================
# NAME CHECKING GUARDRAIL
# ============================================================================

guardrail_agent = Agent(
    name="Name Check",
    instructions="Check if the user is including someone's personal name in what they want you to do.",
    output_type=NameCheckOutput,
    model="gpt-4o-mini"
)


@function_tool
async def guardrail_against_name(ctx, agent, message) -> GuardrailFunctionOutput:
    """
    Input guardrail that checks if message contains personal names
    Prevents agents from using real names inappropriately
    
    Args:
        ctx: Context object
        agent: The agent being protected
        message: The input message to check
    
    Returns:
        GuardrailFunctionOutput with check results
    """
    # Run the guardrail agent to check for names
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    
    # Extract structured output
    is_name_in_message = result.final_output.is_name_in_message
    
    # Return structured result
    return GuardrailFunctionOutput(
        output_info={"found_name": result.final_output.name},
        tripwire_triggered=is_name_in_message
    )


# ============================================================================
# CONTENT SAFETY GUARDRAIL
# ============================================================================

content_safety_agent = Agent(
    name="Content Safety",
    instructions="""Check if the content contains any inappropriate, offensive, or unsafe material.
    Flag content that contains: profanity, hate speech, threats, personal attacks, or 
    content that violates professional communication standards.""",
    model="gpt-4o-mini"
)


@function_tool
async def guardrail_content_safety(content: str) -> dict:
    """
    Content safety guardrail for output validation
    Checks generated content for inappropriate material
    
    Args:
        content: The content to check
    
    Returns:
        dict with safety check results
    """
    result = await Runner.run(
        content_safety_agent,
        f"Check this content for safety issues: {content}"
    )
    
    # Check if any issues were flagged
    has_issues = "unsafe" in result.final_output.lower() or "inappropriate" in result.final_output.lower()
    
    return {
        "is_safe": not has_issues,
        "details": result.final_output,
        "tripwire_triggered": has_issues
    }


# ============================================================================
# EMAIL CONTENT VALIDATION GUARDRAIL
# ============================================================================

email_validation_agent = Agent(
    name="Email Validator",
    instructions="""Validate email content for quality and appropriateness.
    Check for:
    1. Spam indicators (excessive caps, too many exclamation marks, suspicious links)
    2. Professional tone and language
    3. Personalization elements (uses recipient info appropriately)
    4. Clear call-to-action
    5. Proper business communication standards
    
    Return a structured assessment.""",
    output_type=EmailValidationOutput,
    model="gpt-4o-mini"
)


async def validate_email_content(email_body: str, subject: str = "") -> EmailValidationOutput:
    """
    Comprehensive email content validation
    
    Args:
        email_body: The email body text
        subject: The email subject line
    
    Returns:
        EmailValidationOutput with validation results
    """
    validation_prompt = f"""
    Validate this email:
    Subject: {subject}
    Body: {email_body}
    """
    
    result = await Runner.run(email_validation_agent, validation_prompt)
    return result.final_output


# ============================================================================
# RATE LIMITING GUARDRAIL
# ============================================================================

class RateLimiter:
    """Simple rate limiter for email sending"""
    
    def __init__(self, max_emails_per_hour: int = 50):
        self.max_emails_per_hour = max_emails_per_hour
        self.sent_timestamps: List[float] = []
    
    def can_send(self) -> tuple[bool, str]:
        """
        Check if we can send another email
        
        Returns:
            Tuple of (can_send: bool, message: str)
        """
        import time
        current_time = time.time()
        one_hour_ago = current_time - 3600
        
        # Remove timestamps older than 1 hour
        self.sent_timestamps = [ts for ts in self.sent_timestamps if ts > one_hour_ago]
        
        if len(self.sent_timestamps) >= self.max_emails_per_hour:
            return False, f"Rate limit exceeded: {self.max_emails_per_hour} emails/hour"
        
        return True, "OK"
    
    def record_send(self):
        """Record that an email was sent"""
        import time
        self.sent_timestamps.append(time.time())


# ============================================================================
# COMBINED GUARDRAIL SYSTEM
# ============================================================================

class GuardrailSystem:
    """
    Centralized guardrail management system
    Coordinates all guardrails and provides unified interface
    """
    
    def __init__(self):
        self.rate_limiter = RateLimiter(max_emails_per_hour=50)
        self.guardrails_enabled = True
    
    async def check_input(self, message: str, agent=None, ctx=None) -> dict:
        """
        Run all input guardrails on incoming message
        
        Returns:
            dict with all guardrail results
        """
        results = {
            "passed": True,
            "checks": {}
        }
        
        if not self.guardrails_enabled:
            return results
        
        # Check for personal names
        if agent and ctx:
            name_check = await guardrail_against_name(ctx, agent, message)
            results["checks"]["name_check"] = name_check
            if name_check.tripwire_triggered:
                results["passed"] = False
                results["blocked_reason"] = f"Personal name detected: {name_check.output_info.get('found_name')}"
        
        return results
    
    async def check_output(self, content: str, subject: str = "") -> dict:
        """
        Run all output guardrails on generated content
        
        Returns:
            dict with all guardrail results
        """
        results = {
            "passed": True,
            "checks": {}
        }
        
        if not self.guardrails_enabled:
            return results
        
        # Check content safety
        safety_check = await guardrail_content_safety(content)
        results["checks"]["safety"] = safety_check
        if safety_check["tripwire_triggered"]:
            results["passed"] = False
            results["blocked_reason"] = "Content safety violation"
        
        # Check email quality
        email_validation = await validate_email_content(content, subject)
        results["checks"]["email_validation"] = email_validation
        if not email_validation.is_valid:
            results["passed"] = False
            results["blocked_reason"] = f"Email validation failed: {', '.join(email_validation.issues)}"
        
        return results
    
    def check_rate_limit(self) -> dict:
        """
        Check rate limiting guardrail
        
        Returns:
            dict with rate limit check results
        """
        can_send, message = self.rate_limiter.can_send()
        return {
            "passed": can_send,
            "message": message,
            "emails_sent_this_hour": len(self.rate_limiter.sent_timestamps)
        }
    
    def record_email_sent(self):
        """Record that an email was sent for rate limiting"""
        self.rate_limiter.record_send()
    
    def disable_guardrails(self):
        """Disable all guardrails (use with caution!)"""
        self.guardrails_enabled = False
    
    def enable_guardrails(self):
        """Enable all guardrails"""
        self.guardrails_enabled = True


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def example_with_guardrails():
    """
    Example showing how to use the guardrail system
    """
    system = GuardrailSystem()
    
    # Example 1: Check input with name guardrail
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    input_result = await system.check_input(message)
    
    if not input_result["passed"]:
        print(f"❌ Input blocked: {input_result.get('blocked_reason')}")
        return
    
    print("✅ Input passed all guardrails")
    
    # Example 2: Check output content
    email_content = """
    Dear CEO,
    
    I'm reaching out to introduce our AI-powered compliance solution...
    """
    
    output_result = await system.check_output(email_content, "Transform Your Compliance")
    
    if not output_result["passed"]:
        print(f"❌ Output blocked: {output_result.get('blocked_reason')}")
        return
    
    print("✅ Output passed all guardrails")
    
    # Example 3: Check rate limiting
    rate_limit_result = system.check_rate_limit()
    
    if not rate_limit_result["passed"]:
        print(f"❌ Rate limit: {rate_limit_result['message']}")
        return
    
    print("✅ Rate limit check passed")
    
    # Record the send
    system.record_email_sent()
    print(f"📧 Email sent! Total this hour: {rate_limit_result['emails_sent_this_hour'] + 1}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_with_guardrails())
