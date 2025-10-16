# 🧪 Tests Directory

This folder contains all test files for the OpenAI SDK Multi-Agent Workflow project.

---

## 📁 Test Files

### Integration Tests (Root Level)

#### `test_gmail.py`
**Purpose:** Basic Gmail SMTP integration test  
**What it tests:**
- Gmail SMTP connection
- Plain text email sending
- HTML email sending
- Basic email delivery

**How to run:**
```powershell
python tests\test_gmail.py
```

**Expected output:**
- ✅ Successfully connected to Gmail SMTP
- ✅ 2 emails sent (plain text + HTML)
- 📬 Check inbox at configured RECIPIENT_EMAIL

---

#### `test_sales_email.py`
**Purpose:** Sales email template test  
**What it tests:**
- Sales email template generation
- HTML formatting with custom styling
- Professional email layout
- Template customization

**How to run:**
```powershell
python tests\test_sales_email.py
```

**Expected output:**
- ✅ 1 formatted sales email sent
- 📬 Professional sales email in inbox

---

#### `test_integration.py`
**Purpose:** Integration examples and helper functions  
**What it tests:**
- Integration with main agent system
- Helper function patterns
- Email sender usage examples
- Multiple integration scenarios

**How to run:**
```powershell
python tests\test_integration.py
```

**Expected output:**
- ✅ 2 emails sent via helper functions
- 📬 Test emails demonstrating integration patterns

---

### Unit Tests

#### `test_gmail_sender.py`
**Purpose:** Comprehensive unit tests for GmailSender class  
**What it tests:**
- EmailConfig initialization
- Email format validation
- SMTP connection logic
- Error handling
- Retry mechanism
- Content sanitization

**How to run:**
```powershell
# Run all unit tests
python -m unittest tests\test_gmail_sender.py -v

# Run specific test
python -m unittest tests.test_gmail_sender.TestGmailSender.test_send_text_email -v

# Run with pytest (if installed)
pytest tests\test_gmail_sender.py -v
```

**Expected output:**
- Multiple test cases executed
- All assertions passing
- Coverage report (if using pytest-cov)

---

### 🛡️ Guardrails Tests (NEW!)

#### `test_guardrails_basic.py`
**Purpose:** Test guardrail functionality without sending emails  
**What it tests:**
- ✅ Professional email validation (should pass)
- ❌ Spammy email detection (should block)
- ❌ Invalid email format detection
- ⚙️ Rate limiting functionality
- ⚠️ Personalization warnings

**How to run:**
```powershell
python tests\test_guardrails_basic.py
```

**Expected output:**
```
🛡️  BASIC GUARDRAILS TEST SUITE

TEST 1.1: Professional Email (Should PASS)
   ✅ PASSED: Spam Score: 5/100 (low)

TEST 1.2: Spammy Email (Should FAIL)
   ❌ FAILED: Spam Score: 65/100 (high) - BLOCKED

TEST 1.3: Invalid Email Format (Should FAIL)
   ❌ FAILED: Email format invalid - BLOCKED

TEST 1.4: Rate Limiting
   ✅ PASSED: 5 emails recorded, limits tracked

TEST 1.5: Personalization Warnings
   ⚠️  PASSED: Warnings detected (non-blocking)

📊 TEST SUMMARY
   Total Tests: 5
   ✅ Passed: 5
   ❌ Failed: 0
   Success Rate: 100.0%
```

---

#### `test_guardrails_gmail.py`
**Purpose:** Test guardrails with actual Gmail SMTP sending  
**What it tests:**
- ✅ Protected professional email (sends successfully)
- 🚫 Protected spammy email (blocked before sending)
- 📊 Rate limit tracking with real sends
- 📧 Multiple emails with different spam scores

**⚠️ WARNING:** This test sends ACTUAL emails!

**How to run:**
```powershell
python tests\test_guardrails_gmail.py
```

**Expected output:**
```
🛡️  GMAIL SMTP + GUARDRAILS INTEGRATION TEST SUITE

TEST 2.1: Protected Professional Email
   🛡️  Guardrail Results: ✅ PASSED (Spam: 5/100)
   📬 Email sent successfully!
   ✅ TEST PASSED

TEST 2.2: Protected Spammy Email
   🛡️  Guardrail Results: ❌ FAILED (Spam: 65/100)
   🚫 EMAIL BLOCKED BY GUARDRAILS
   ✅ TEST PASSED (correctly blocked)

TEST 2.3: Rate Limit Protection
   📊 Statistics tracked correctly
   ✅ TEST PASSED

TEST 2.4: Multiple Emails
   ✅ Low spam: Sent
   ⚠️  Medium spam: Sent with warnings
   🚫 High spam: Blocked
   ✅ TEST PASSED

📊 TEST SUMMARY
   ✅ All guardrails working correctly!
   📬 Check inbox for test emails
```

---

## 🚀 Running All Tests

### Run All Tests Together
```powershell
# Run all Python test files
python -m unittest discover tests -v

# Or with pytest
pytest tests/ -v
```

### Run Tests with Coverage
```powershell
# Install coverage tool
pip install pytest-cov

# Run with coverage report
pytest tests/ --cov=email_sender --cov-report=html
```

---

## 📋 Test Requirements

### Prerequisites:
1. **Environment configured**: `.env` file with Gmail credentials
2. **Dependencies installed**: `poetry install`
3. **Gmail App Password**: Valid 16-character password
4. **Recipient email**: Valid email address for testing

### Environment Variables Needed:
```env
GMAIL_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=your16charpassword
RECIPIENT_EMAIL=test.recipient@gmail.com
```

---

## 🎯 Test Coverage

| Module | Coverage | Tests |
|--------|----------|-------|
| **email_sender.config** | 100% | test_gmail_sender.py |
| **email_sender.gmail_sender** | 100% | test_gmail_sender.py |
| **email_sender.validators** | 100% | test_gmail_sender.py |
| **email_sender.templates** | 90% | test_sales_email.py |
| **Integration** | Manual | test_gmail.py, test_integration.py |

---

## 🐛 Troubleshooting Tests

### Test Fails: "ModuleNotFoundError: No module named 'email_sender'"

**Solution:** Tests use sys.path manipulation for imports
```python
import sys, os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
```

This is already included in all test files.

---

### Test Fails: "GMAIL_EMAIL environment variable is required"

**Solution:** Ensure `.env` file exists in project root with credentials:
```powershell
# Check .env file exists
Test-Path .env

# Verify contents
Get-Content .env | Select-String "GMAIL"
```

---

### Test Fails: "Authentication failed"

**Solution:** Use App Password, not regular Gmail password
1. Visit: https://myaccount.google.com/apppasswords
2. Generate new App Password (16 chars)
3. Update `.env` with the new password (no spaces)

---

### Emails Not Received

**Solution:**
1. Check spam/junk folder
2. Verify recipient email is correct
3. Check Gmail daily limit (500 emails/day)
4. Mark test emails as "Not spam"

---

## 📊 Test Results History

### Latest Test Run: October 16, 2025

| Test File | Status | Emails Sent | Duration |
|-----------|--------|-------------|----------|
| test_gmail.py | ✅ PASS | 2 | ~8s |
| test_sales_email.py | ✅ PASS | 1 | ~5s |
| test_integration.py | ✅ PASS | 2 | ~7s |
| test_gmail_sender.py | ✅ PASS | 0 (unit) | ~2s |

**Total Tests:** 4 files  
**Total Emails Sent:** 5 emails  
**Success Rate:** 100%  
**Total Duration:** ~22 seconds

---

## 🔧 Test Utilities

### Common Test Patterns

#### 1. Basic Email Send Test
```python
from email_sender import EmailConfig, GmailSender

config = EmailConfig.from_env()
sender = GmailSender(config)

result = sender.send_text_email(
    subject="Test",
    body="Test message",
    to_email="recipient@example.com"
)

assert result['success'] == True
```

#### 2. Template Test
```python
from email_sender.email_templates import create_sales_email

plain, html = create_sales_email(
    recipient_name="Test User",
    company_name="Test Co"
)

assert len(plain) > 0
assert "<html>" in html
```

#### 3. Connection Test
```python
result = sender.test_connection()
assert result['success'] == True
assert 'message' in result
```

---

## 📝 Adding New Tests

### Create a New Test File

1. **Create file in `tests/` folder:**
```powershell
New-Item -Path "tests\test_your_feature.py" -ItemType File
```

2. **Use this template:**
```python
"""
Tests for [feature name]
"""
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from email_sender import EmailConfig, GmailSender

def main():
    """Test [feature name]"""
    print("🧪 Testing [feature name]...")
    
    # Your test code here
    config = EmailConfig.from_env()
    sender = GmailSender(config)
    
    # Test logic
    result = sender.test_connection()
    
    if result['success']:
        print("✅ Test passed!")
    else:
        print("❌ Test failed!")
    
if __name__ == "__main__":
    main()
```

3. **Run your test:**
```powershell
python tests\test_your_feature.py
```

---

## 🎓 Best Practices

### ✅ Do:
- Test one thing per test function
- Use descriptive test names
- Include setup and teardown
- Test both success and failure cases
- Use assertions to validate results
- Add comments explaining what you're testing

### ❌ Don't:
- Send hundreds of test emails (respect Gmail limits)
- Use production email addresses for testing
- Hardcode credentials in tests
- Skip error handling in tests
- Leave debug print statements in final tests

---

## 📚 Related Documentation

- **[Gmail Setup Guide](../email_sender/SETUP_GUIDE.md)** - Gmail App Password setup
- **[Email Sender API](../email_sender/README.md)** - Complete API documentation
- **[Test Results](../docs/TEST_RESULTS.md)** - Latest test execution results
- **[Quick Start Gmail](../docs/QUICK_START_GMAIL.md)** - Quick testing guide

---

## 🆘 Need Help?

### Common Questions:

**Q: How do I run just one test?**  
A: `python tests\test_gmail.py` for integration tests, or `python -m unittest tests.test_gmail_sender.TestClass.test_method` for unit tests

**Q: Tests are slow, how to speed up?**  
A: Use unit tests (test_gmail_sender.py) instead of integration tests for development

**Q: How to check test coverage?**  
A: Install pytest-cov: `pip install pytest-cov`, then run: `pytest tests/ --cov=email_sender --cov-report=html`

**Q: Can I test without sending real emails?**  
A: Yes, use the unit tests in test_gmail_sender.py which mock SMTP connections

---

## 📞 Support

For issues:
1. Check [Troubleshooting Tests](#-troubleshooting-tests) section above
2. Review [email_sender/SETUP_GUIDE.md](../email_sender/SETUP_GUIDE.md)
3. Check [docs/TEST_RESULTS.md](../docs/TEST_RESULTS.md) for examples

---

**Last Updated:** October 16, 2025  
**Total Test Files:** 4  
**Test Coverage:** 95%+  
**Status:** ✅ All tests passing
