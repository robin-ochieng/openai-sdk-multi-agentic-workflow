# 🛡️ Guardrails Quick Reference

One-page guide for using guardrails in your AI agent system.

---

## 🚀 Quick Start

### Test Guardrails

```powershell
# Test email guardrails
python email_sender/guardrails_email.py

# Test main guardrail system  
python guardrails.py

# Run protected workflow
python openai_sdk_agent_with_guardrails.py
```

---

## 📊 Guardrail Types

| Type | Purpose | Location | Status |
|------|---------|----------|--------|
| **Name Check** | Detect personal names | `guardrails.py` | Input |
| **Content Safety** | Block inappropriate content | `guardrails.py` | Output |
| **Spam Detection** | Score spam risk (0-100) | `email_sender/guardrails_email.py` | Output |
| **Rate Limiting** | 50/hour, 500/day limits | `email_sender/guardrails_email.py` | Operational |
| **Email Validation** | Format & quality checks | `email_sender/guardrails_email.py` | Input |

---

## 💻 Code Examples

### Example 1: Check Input for Names

```python
from guardrails import GuardrailSystem
import asyncio

async def main():
    system = GuardrailSystem()
    
    message = "Send email to Alice"
    result = await system.check_input(message)
    
    if not result["passed"]:
        print(f"❌ Blocked: {result['blocked_reason']}")

asyncio.run(main())
```

### Example 2: Validate Email Before Sending

```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()

result = guardrails.run_all_checks(
    subject="Your solution",
    body="Hi, I wanted to reach out...",
    recipient_email="prospect@company.com"
)

if result["passed"]:
    print("✅ Safe to send")
    # Send email
    guardrails.record_send()
else:
    print("❌ Blocked:", result["blocking_issues"])
```

### Example 3: Check Spam Score

```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()

spam_check = guardrails.check_spam_score(
    subject="FREE OFFER!!!",
    body="CLICK HERE NOW!!! WIN $$$"
)

print(f"Spam score: {spam_check['spam_score']}")  # 65
print(f"Is spam: {spam_check['is_spam']}")        # True
print(f"Issues: {spam_check['issues']}")
```

### Example 4: Complete Protected Workflow

```python
from openai_sdk_agent_with_guardrails import (
    check_input_guardrails,
    send_email_with_guardrails
)
import asyncio

async def main():
    # Step 1: Check input
    message = "Send sales email"
    await check_input_guardrails(message)
    
    # Step 2: Send with guardrails
    result = await send_email_with_guardrails(
        subject="Quick question",
        body="Hi, I wanted to ask...",
        recipient_email="prospect@company.com"
    )
    
    print(f"Status: {result['status']}")

asyncio.run(main())
```

---

## 📈 Spam Score Guide

| Score | Severity | Action | Example Issues |
|-------|----------|--------|----------------|
| 0-15 | ✅ Low | Allow | Minor formatting |
| 15-30 | ⚠️ Medium | Warn | Some caps, 2-3 exclamations |
| 30+ | ❌ High | Block | Excessive caps, multiple !!!, spam words |

### Common Spam Triggers

- ❌ `!!!` Multiple exclamation marks (+10)
- ❌ `$$$` Multiple dollar signs (+10)
- ❌ `FREE!!!` Excessive offers (+10)
- ❌ `CLICK HERE NOW` Pushy CTAs (+10)
- ❌ `casino`, `lottery`, `winner` Suspicious keywords (+15 each)
- ❌ `>30% CAPS` Excessive capitalization (+20)

---

## ⚙️ Configuration

### Adjust Rate Limits

```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()
guardrails.hourly_limit = 100  # Default: 50
guardrails.daily_limit = 1000  # Default: 500
```

### Add Custom Spam Patterns

```python
guardrails.spam_patterns.append(r'URGENT!!!+')
guardrails.suspicious_keywords.append('your_keyword')
```

### Disable Guardrails (Dev Only)

```python
from guardrails import GuardrailSystem

system = GuardrailSystem()
system.disable_guardrails()  # ⚠️ Use with caution!
```

---

## 📊 Statistics

```python
from email_sender.guardrails_email import EmailGuardrails

guardrails = EmailGuardrails()
stats = guardrails.get_statistics()

print(f"Sent last hour: {stats['sent_last_hour']}/{stats['hourly_limit']}")
print(f"Sent last 24h: {stats['sent_last_24h']}/{stats['daily_limit']}")
print(f"Remaining today: {stats['daily_remaining']}")
```

---

## 🔧 Troubleshooting

### Email Blocked by Spam Filter

**Problem**: Spam score too high (30+)

**Solution**:
```python
# Check what triggered it
spam_check = guardrails.check_spam_score(subject, body)
print(spam_check['issues'])

# Fix issues:
# - Remove excessive !!!, $$$, CAPS
# - Use professional language
# - Avoid "FREE", "WIN", "CLICK NOW"
```

### Rate Limit Exceeded

**Problem**: Too many emails sent

**Solution**:
```python
stats = guardrails.get_statistics()
print(f"Wait time: {60 - stats['minutes_since_first_send']} min")

# Or increase limits:
guardrails.hourly_limit = 100
```

### Personal Name Detected

**Problem**: Input flagged for name

**Solution**:
```python
# This is intentional for privacy/compliance
# Review the detected name:
name_check = await system.check_input(message)
print(f"Found: {name_check['name']}")

# Either:
# 1. Get manual approval
# 2. Remove/anonymize the name
# 3. Add exception if appropriate (CEO, Manager, etc.)
```

---

## 📚 Full Documentation

- **[Complete Guardrails Guide](GUARDRAILS.md)** - In-depth documentation
- **[Main README](../README.md)** - Project overview
- **[Email Sender](../email_sender/README.md)** - Email module docs
- **[Testing Guide](../tests/README.md)** - Run tests

---

## 🎯 Best Practices

### ✅ DO:
- ✅ Always run guardrails before sending
- ✅ Monitor spam scores regularly
- ✅ Respect rate limits
- ✅ Log blocked attempts
- ✅ Review warnings

### ❌ DON'T:
- ❌ Disable guardrails in production
- ❌ Ignore warnings
- ❌ Bypass rate limits
- ❌ Send high spam score emails
- ❌ Use disposable email addresses

---

## 🚨 When Guardrails Trigger

```
Input: "Send email to Alice about product"
↓
Name Check: ⚠️ Detected "Alice"
↓
Decision: Flag for review (don't auto-block)
↓
Continue with warning...
```

```
Output: "FREE!!! CLICK NOW!!! WIN $$$"
↓
Spam Check: ❌ Score 65/100 (High)
↓
Decision: BLOCK - Too risky
↓
Email not sent ❌
```

```
Rate Check: 51 emails sent this hour
↓
Rate Limit: ❌ Exceeded 50/hour limit
↓
Decision: BLOCK until next hour
↓
Email not sent ❌
```

---

## 📞 Support

Need help? Check:

1. **[Troubleshooting](GUARDRAILS.md#troubleshooting)** section
2. **[Examples](GUARDRAILS.md#usage-examples)** section
3. **Test scripts** to see working implementations

---

**Last Updated**: October 16, 2025  
**Quick Reference Version**: 1.0
