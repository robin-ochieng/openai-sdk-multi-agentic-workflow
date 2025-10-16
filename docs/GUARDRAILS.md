# 🛡️ Guardrails & Structured Outputs Implementation

## Overview

This project now implements comprehensive **guardrails** and **structured outputs** for robust AI agent systems, following OpenAI best practices for production-grade AI applications.

---

## 📋 Table of Contents

1. [What are Guardrails?](#what-are-guardrails)
2. [Implementation Overview](#implementation-overview)
3. [Guardrail Types](#guardrail-types)
4. [Structured Outputs](#structured-outputs)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Testing Guardrails](#testing-guardrails)

---

## What are Guardrails?

**Guardrails** are safety mechanisms that validate inputs and outputs of AI systems to ensure:

- ✅ **Safety**: Prevent harmful or inappropriate content
- ✅ **Compliance**: Enforce business rules and regulations
- ✅ **Quality**: Maintain high standards for generated content
- ✅ **Reliability**: Catch errors before they reach users

### Types of Guardrails

1. **Input Guardrails** - Validate user inputs before processing
2. **Output Guardrails** - Validate AI-generated content before use
3. **Operational Guardrails** - Rate limiting, quotas, resource management

---

## Implementation Overview

### Files Added

```
OpenAI SDK Agents/
│
├── guardrails.py                          # Main guardrail system
├── openai_sdk_agent_with_guardrails.py   # Protected agent workflow
└── email_sender/
    └── guardrails_email.py                # Email-specific guardrails
```

### Architecture

```
User Input
    ↓
[Input Guardrails] ← Check for names, content safety
    ↓
AI Agent Processing
    ↓
[Output Guardrails] ← Validate quality, safety, spam score
    ↓
[Rate Limit Check] ← Ensure within sending limits
    ↓
Send Email / Take Action
```

---

## Guardrail Types

### 1. Name Checking Guardrail

**Purpose**: Detect and flag personal names in user inputs for privacy/compliance

**Implementation**: `guardrails.py` → `guardrail_against_name()`

**Example**:
```python
from guardrails import GuardrailSystem

system = GuardrailSystem()

# Check input
message = "Send email to CEO from Alice"
result = await system.check_input(message)

if not result["passed"]:
    print(f"❌ Blocked: {result['blocked_reason']}")
```

**Output**:
```python
{
    "passed": False,
    "checks": {
        "name_check": {
            "output_info": {"found_name": "Alice"},
            "tripwire_triggered": True
        }
    },
    "blocked_reason": "Personal name detected: Alice"
}
```

---

### 2. Content Safety Guardrail

**Purpose**: Prevent inappropriate, offensive, or unsafe content

**Implementation**: `guardrails.py` → `guardrail_content_safety()`

**Checks for**:
- Profanity
- Hate speech
- Threats
- Personal attacks
- Unprofessional language

**Example**:
```python
content = "Your product is terrible!!!"
safety_result = await system.check_output(content)

if not safety_result["passed"]:
    print(f"❌ Content blocked: {safety_result['blocked_reason']}")
```

---

### 3. Spam Detection Guardrail

**Purpose**: Prevent emails that look like spam

**Implementation**: `email_sender/guardrails_email.py` → `EmailGuardrails.check_spam_score()`

**Detects**:
- ❌ Multiple exclamation marks (!!!)
- ❌ Excessive caps (CLICK HERE NOW)
- ❌ Suspicious keywords (FREE, WIN, PRIZE)
- ❌ Too many links
- ❌ Shortened URLs (bit.ly, tinyurl)

**Scoring**:
- **0-15**: Low risk (allowed)
- **15-30**: Medium risk (warning)
- **30+**: High risk (blocked)

**Example**:
```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()

result = guardrails.check_spam_score(
    subject="FREE!!! Click NOW!!!",
    body="WIN $$$$ CLICK HERE!!!"
)

print(f"Spam score: {result['spam_score']}")  # 65
print(f"Is spam: {result['is_spam']}")        # True
```

---

### 4. Rate Limiting Guardrail

**Purpose**: Prevent exceeding sending limits and avoid being flagged as spam

**Implementation**: `email_sender/guardrails_email.py` → `EmailGuardrails.check_rate_limits()`

**Limits**:
- **Hourly**: 50 emails per hour
- **Daily**: 500 emails per day (Gmail limit)

**Example**:
```python
guardrails = EmailGuardrails()

# Check before sending
can_send, message = guardrails.check_rate_limits()

if not can_send:
    print(f"❌ {message}")  # "Hourly limit reached: 50/50 emails"
else:
    # Send email
    guardrails.record_send()  # Record for tracking
```

---

### 5. Email Validation Guardrail

**Purpose**: Validate email content quality and appropriateness

**Implementation**: `guardrails.py` → `validate_email_content()`

**Checks**:
- ✅ Professional tone
- ✅ Personalization elements
- ✅ Clear call-to-action
- ✅ No unreplaced merge tags
- ✅ Appropriate length

**Example**:
```python
from guardrails import validate_email_content

result = await validate_email_content(
    email_body="Hi {{NAME}}, check this out!",
    subject="Quick question"
)

# Result shows issues
if result.issues:
    print("Issues found:", result.issues)
    # ["Unreplaced merge tags detected"]
```

---

## Structured Outputs

**Structured outputs** use Pydantic models to ensure AI responses follow a specific format, making them more reliable and easier to process.

### Benefits

- ✅ **Type Safety**: Guaranteed data types
- ✅ **Validation**: Automatic validation of values
- ✅ **Consistency**: Same format every time
- ✅ **Error Handling**: Clear error messages

### Example Models

#### 1. NameCheckOutput

```python
from pydantic import BaseModel, Field

class NameCheckOutput(BaseModel):
    is_name_in_message: bool = Field(
        description="True if name detected"
    )
    name: str = Field(
        description="The detected name"
    )

# Usage
result = NameCheckOutput(
    is_name_in_message=True,
    name="Alice"
)
```

#### 2. EmailValidationOutput

```python
class EmailValidationOutput(BaseModel):
    is_valid: bool
    contains_spam_indicators: bool
    tone_appropriate: bool
    has_personalization: bool
    issues: List[str] = Field(default_factory=list)

# Usage
validation = EmailValidationOutput(
    is_valid=True,
    contains_spam_indicators=False,
    tone_appropriate=True,
    has_personalization=True,
    issues=[]
)
```

#### 3. EmailContent

```python
class EmailContent(BaseModel):
    subject: str
    body: str
    recipient_email: str
    
    @validator('recipient_email')
    def validate_email(cls, v):
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', v):
            raise ValueError(f"Invalid email: {v}")
        return v

# Usage - automatic validation
email = EmailContent(
    subject="Test",
    body="Hello",
    recipient_email="invalid-email"  # ❌ Raises ValueError
)
```

---

## Usage Examples

### Example 1: Basic Input Guardrail

```python
from guardrails import GuardrailSystem
import asyncio

async def main():
    system = GuardrailSystem()
    
    # Check user input
    message = "Send email to John about our product"
    result = await system.check_input(message)
    
    if result["passed"]:
        print("✅ Input is safe to process")
        # Process with AI agent
    else:
        print(f"❌ Blocked: {result['blocked_reason']}")

asyncio.run(main())
```

### Example 2: Email Sending with Full Guardrails

```python
from email_sender.guardrails_email import EmailGuardrails

def send_protected_email(subject, body, recipient):
    guardrails = EmailGuardrails()
    
    # Run all checks
    result = guardrails.run_all_checks(
        subject=subject,
        body=body,
        recipient_email=recipient
    )
    
    if not result["passed"]:
        print("❌ Email blocked:")
        for issue in result["blocking_issues"]:
            print(f"  - {issue}")
        return False
    
    if result["warnings"]:
        print("⚠️  Warnings:")
        for warning in result["warnings"]:
            print(f"  - {warning}")
    
    # Show spam score
    print(f"Spam score: {result['checks']['spam']['spam_score']}")
    
    # Send email
    print("✅ Sending email...")
    # ... actual sending logic ...
    guardrails.record_send()
    
    return True

# Usage
send_protected_email(
    subject="Quick question",
    body="Hi, I wanted to ask about...",
    recipient="prospect@company.com"
)
```

### Example 3: Complete Workflow

```python
from openai_sdk_agent_with_guardrails import (
    check_input_guardrails,
    send_email_with_guardrails
)
import asyncio

async def protected_workflow():
    # Step 1: Check input
    message = "Send sales email to CEO"
    input_check = await check_input_guardrails(message)
    
    if input_check['requires_review']:
        print("⚠️  Manual review required")
        # Get approval...
    
    # Step 2: Generate email (with AI agent)
    subject = "Your compliance solution"
    body = "Hi, I noticed your company..."
    recipient = "ceo@company.com"
    
    # Step 3: Send with guardrails
    result = await send_email_with_guardrails(
        subject=subject,
        body=body,
        recipient_email=recipient
    )
    
    print(f"Result: {result['status']}")

asyncio.run(protected_workflow())
```

---

## Configuration

### Adjusting Rate Limits

```python
from email_sender.guardrails_email import EmailGuardrails

# Custom limits
guardrails = EmailGuardrails()
guardrails.hourly_limit = 100  # Increase to 100/hour
guardrails.daily_limit = 1000  # Increase to 1000/day
```

### Customizing Spam Detection

```python
# Add custom spam patterns
guardrails.spam_patterns.append(r'URGENT!!!+')

# Add custom suspicious keywords
guardrails.suspicious_keywords.extend([
    'your custom', 'blocked keywords'
])
```

### Disabling Guardrails (Development Only)

```python
from guardrails import GuardrailSystem

system = GuardrailSystem()

# Disable for testing
system.disable_guardrails()

# Re-enable
system.enable_guardrails()
```

---

## Testing Guardrails

### Test Script 1: Email Guardrails

```bash
python email_sender/guardrails_email.py
```

**Output**:
```
==================================================
Example 1: Professional Email
==================================================
✅ Passed: True
Blocking issues: []
Warnings: []

==================================================
Example 2: Spammy Email
==================================================
✅ Passed: False
Blocking issues: ['High spam score: 65']
Spam score: 65
```

### Test Script 2: Main Guardrails

```bash
python guardrails.py
```

### Test Script 3: Full Workflow

```bash
python openai_sdk_agent_with_guardrails.py
```

**Expected Output**:
```
==================================================
🚀 PROTECTED EMAIL WORKFLOW
==================================================

==================================================
🛡️  INPUT GUARDRAIL CHECK
==================================================

📝 Message: Send out a cold sales email...

🔍 Name detected: True
   Found name: 'Alice'

⚠️  WARNING: Personal name detected in input!

==================================================
🛡️  RUNNING GUARDRAIL CHECKS
==================================================

📊 Guardrail Results:
   Passed: True

📈 Spam Score: 5/100 (low severity)

📧 Sending Statistics:
   Last hour: 0/50
   Last 24h: 0/500

✅ All guardrails passed - sending email...
📬 Email sent! Status: 202

📊 FINAL RESULT:
   Status: success
   ✅ Email sent successfully!
```

---

## Statistics and Monitoring

### Get Sending Statistics

```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()
stats = guardrails.get_statistics()

print(f"Sent last hour: {stats['sent_last_hour']}/{stats['hourly_limit']}")
print(f"Sent last 24h: {stats['sent_last_24h']}/{stats['daily_limit']}")
print(f"Hourly remaining: {stats['hourly_remaining']}")
print(f"Daily remaining: {stats['daily_remaining']}")
```

---

## Best Practices

### ✅ DO:

1. **Always run input guardrails** before processing user input
2. **Always run output guardrails** before sending emails
3. **Check rate limits** before each send operation
4. **Log guardrail decisions** for auditing
5. **Monitor spam scores** to improve email quality
6. **Review blocked content** to improve guardrails

### ❌ DON'T:

1. **Don't disable guardrails in production**
2. **Don't ignore warnings** - they indicate potential issues
3. **Don't bypass rate limits** - you'll get flagged as spam
4. **Don't send emails with high spam scores**
5. **Don't use disposable email addresses**

---

## Guardrail Decision Flow

```
┌─────────────────┐
│  User Input     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ Input Guardrail │
│ - Name Check    │
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ Passed? │
    └────┬────┘
         ↓ Yes
┌─────────────────┐
│ AI Processing   │
└────────┬────────┘
         ↓
┌─────────────────┐
│Output Guardrail │
│ - Safety Check  │
│ - Spam Score    │
│ - Quality Check │
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ Passed? │
    └────┬────┘
         ↓ Yes
┌─────────────────┐
│Rate Limit Check │
└────────┬────────┘
         ↓
    ┌────┴────┐
    │ Within  │
    │ Limit?  │
    └────┬────┘
         ↓ Yes
┌─────────────────┐
│  Send Email ✅  │
└─────────────────┘
```

---

## Troubleshooting

### Issue: Emails being blocked by spam guardrail

**Solution**:
1. Check spam score: `result['checks']['spam']['spam_score']`
2. Review issues: `result['checks']['spam']['issues']`
3. Remove excessive caps, exclamation marks, suspicious keywords
4. Use professional language

### Issue: Rate limit exceeded

**Solution**:
1. Check statistics: `guardrails.get_statistics()`
2. Wait for limits to reset (1 hour for hourly, 24h for daily)
3. Adjust limits if needed: `guardrails.hourly_limit = 100`

### Issue: Personal name flagged incorrectly

**Solution**:
1. Review the name detection logic in `guardrails.py`
2. Add exceptions for titles (CEO, Manager, etc.)
3. Adjust sensitivity as needed

---

## Related Documentation

- **[Main README](../README.md)** - Project overview
- **[Email Sender Guide](email_sender/README.md)** - Email module documentation
- **[Gmail Setup](email_sender/SETUP_GUIDE.md)** - Gmail configuration
- **[Tests README](tests/README.md)** - Testing guide

---

**Last Updated**: October 16, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
