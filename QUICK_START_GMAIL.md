# 🚀 Gmail SMTP Quick Start - Testing Guide

## ⚡ 3-Minute Setup

### 1. Get Gmail App Password (First time only)

1. Go to: https://myaccount.google.com/apppasswords
2. Select "Other (Custom name)" → Enter: `Python Email Sender`
3. Click **Generate**
4. Copy the 16-character password (remove spaces)

### 2. Update .env File

Edit `.env` in project root:

```env
GMAIL_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop  # 16 chars, no spaces
RECIPIENT_EMAIL=robinochieng74@gmail.com
```

### 3. Test Email Delivery

```powershell
python email_sender\examples\simple_send.py
```

**Expected Result:** 
- ✅ 2 emails sent
- ✅ Check inbox at robinochieng74@gmail.com

---

## 📧 Quick Commands

### Test SMTP Connection
```powershell
python email_sender\examples\simple_send.py
```
**Sends:** Plain text + HTML test emails

### Test Sales Email Template
```powershell
python email_sender\examples\sales_email.py
```
**Sends:** Professional sales email with formatting

### Run Unit Tests
```powershell
python -m unittest email_sender\tests\test_gmail_sender.py -v
```
**Tests:** All core functionality

---

## 💻 Quick Code Examples

### Send Plain Text Email
```python
from email_sender import EmailConfig, GmailSender

config = EmailConfig.from_env()
sender = GmailSender(config)

result = sender.send_text_email(
    subject="Hello!",
    body="This is a test email.",
    to_email="recipient@example.com"
)
print(result)  # {'success': True, ...}
```

### Send HTML Email
```python
html = "<h1>Hello!</h1><p>This is <b>HTML</b>.</p>"

result = sender.send_html_email(
    subject="HTML Test",
    html_body=html,
    to_email="recipient@example.com"
)
```

### Use Sales Template
```python
from email_sender.email_templates import create_sales_email

plain, html = create_sales_email(
    recipient_name="John",
    product_name="AI Platform",
    value_proposition="Save 10+ hours/week",
    call_to_action="Book a demo!",
    sender_name="Jane",
    sender_title="Sales Rep",
    company_name="Tech Co"
)

sender.send_html_email(
    subject="Transform Your Workflow",
    html_body=html,
    plain_body=plain
)
```

### Test Connection
```python
result = sender.test_connection()
if result['success']:
    print("✅ Connected!")
else:
    print(f"❌ Error: {result['message']}")
```

---

## 🐛 Common Issues & Fixes

### "Authentication failed"
**Fix:** Use App Password (16 chars), NOT regular password
```env
GMAIL_APP_PASSWORD=abcdefghijklmnop  # ✅ App Password
GMAIL_APP_PASSWORD=MyPassword123     # ❌ Regular password
```

### "GMAIL_EMAIL environment variable is required"
**Fix:** Check `.env` file exists and has GMAIL_EMAIL
```powershell
# Verify .env file
cat .env | Select-String "GMAIL"
```

### "Connection timeout"
**Fix:** Check internet and try port 465
```env
SMTP_PORT=465  # Use SSL instead of TLS
```

### Emails go to spam
**Fix:** Send to yourself first, mark "Not spam"

---

## 📊 Gmail Limits

| Metric | Limit |
|--------|-------|
| Emails per day | 500 |
| Recipients per email | 500 |
| Reset period | 24 hours |

**Tip:** Add `time.sleep(2)` between bulk sends

---

## 🔗 Quick Links

- **Setup Guide:** `email_sender/SETUP_GUIDE.md`
- **Full Docs:** `email_sender/README.md`
- **Implementation:** `GMAIL_IMPLEMENTATION.md`
- **Gmail App Passwords:** https://myaccount.google.com/apppasswords
- **Gmail SMTP Info:** https://support.google.com/mail/answer/7126229

---

## ✅ Verification Checklist

Before testing, verify:

- [ ] 2FA enabled on Gmail account
- [ ] App Password generated (16 characters)
- [ ] `.env` file updated with credentials
- [ ] No spaces in GMAIL_APP_PASSWORD
- [ ] RECIPIENT_EMAIL is set

Then run:
```powershell
python email_sender\examples\simple_send.py
```

**Success = 2 emails in inbox!** 📬

---

## 🎯 Integration with Main Agent

Add to `openai_sdk_agent.py`:

```python
from email_sender import EmailConfig, GmailSender

# Initialize once
gmail_config = EmailConfig.from_env()
gmail_sender = GmailSender(gmail_config)

# Replace existing send_email tool
@function_tool
def send_email(subject: str, body: str, to_email: str) -> str:
    """Send email via Gmail SMTP"""
    result = gmail_sender.send_html_email(
        subject=subject,
        html_body=body,
        to_email=to_email
    )
    return f"✅ Sent to {to_email}"
```

---

## 📞 Need Help?

1. **Setup Issues?** → Read `email_sender/SETUP_GUIDE.md`
2. **API Questions?** → Read `email_sender/README.md`
3. **Error Messages?** → Check troubleshooting section above
4. **Gmail Settings?** → Visit https://myaccount.google.com/security

---

**Status: ✅ Ready to Test!**

**Next Step:** Run `python email_sender\examples\simple_send.py`
