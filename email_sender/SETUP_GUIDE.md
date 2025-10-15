# Gmail SMTP Setup Guide

Complete step-by-step guide to configure Gmail SMTP for sending emails.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Enable 2-Factor Authentication](#enable-2-factor-authentication)
3. [Generate App Password](#generate-app-password)
4. [Configure Environment Variables](#configure-environment-variables)
5. [Test Your Setup](#test-your-setup)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, make sure you have:

- ✅ A Gmail account (free or paid)
- ✅ Access to Google Account settings
- ✅ Python 3.7+ installed
- ✅ This project downloaded and set up

---

## Enable 2-Factor Authentication

Gmail App Passwords **require** 2-factor authentication (2FA) to be enabled.

### Step 1: Go to Google Account Security

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Or directly visit: [myaccount.google.com/security](https://myaccount.google.com/security)

### Step 2: Enable 2-Step Verification

1. Scroll down to **"How you sign in to Google"**
2. Click **2-Step Verification**
3. Click **Get Started**
4. Follow the prompts to:
   - Enter your password
   - Add a phone number
   - Verify your phone (via SMS or call)
   - Turn on 2-Step Verification

> **Note:** If you already have 2FA enabled, you'll see "2-Step Verification: On". Skip to the next section.

---

## Generate App Password

Once 2FA is enabled, you can create an App Password specifically for this application.

### Step 1: Access App Passwords

1. Go back to **Security** settings
2. Under **"How you sign in to Google"**, click **2-Step Verification**
3. Scroll down to **"App passwords"** (at the bottom)
4. Or directly visit: [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

> **Note:** If you don't see "App passwords", make sure 2FA is enabled.

### Step 2: Create New App Password

1. Click **"Select app"** dropdown
2. Choose **"Other (Custom name)"**
3. Enter a name: `OpenAI SDK Agents` or `Python Email Sender`
4. Click **Generate**

### Step 3: Save Your App Password

1. Google will display a **16-character password** like: `abcd efgh ijkl mnop`
2. **IMPORTANT:** Copy this password immediately - you won't see it again!
3. Remove the spaces: `abcdefghijklmnop` (16 characters)
4. Store it securely

> **Security Tip:** Treat App Passwords like regular passwords. Don't share them or commit them to version control.

---

## Configure Environment Variables

Now add your Gmail credentials to the `.env` file.

### Step 1: Locate Your .env File

The `.env` file is in your project root:
```
OpenAI SDK Agents/
├── .env              ← This file
├── .env.example
├── openai_sdk_agent.py
└── email_sender/
```

### Step 2: Add Gmail Configuration

Open `.env` and add these lines:

```env
# ============================================
# GMAIL SMTP CONFIGURATION
# ============================================

# Your Gmail address
GMAIL_EMAIL=your.email@gmail.com

# Your Gmail App Password (16 characters, no spaces)
# Generate at: https://myaccount.google.com/apppasswords
GMAIL_APP_PASSWORD=abcdefghijklmnop

# Default recipient for test emails (optional)
RECIPIENT_EMAIL=robinochieng74@gmail.com

# SMTP Settings (optional - defaults work for most cases)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_TIMEOUT=30
MAX_RETRIES=3
USE_TLS=true
```

### Step 3: Update Your Information

Replace the placeholders:

1. **GMAIL_EMAIL**: Your actual Gmail address
   ```env
   GMAIL_EMAIL=your.actual.email@gmail.com
   ```

2. **GMAIL_APP_PASSWORD**: The 16-character App Password from Step 2
   ```env
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```
   
   ⚠️ **Remove all spaces** from the App Password!
   
   ❌ Wrong: `abcd efgh ijkl mnop`  
   ✅ Correct: `abcdefghijklmnop`

3. **RECIPIENT_EMAIL**: Where test emails should go
   ```env
   RECIPIENT_EMAIL=robinochieng74@gmail.com
   ```

### Step 4: Save and Verify

1. Save the `.env` file
2. **Never commit** this file to Git (it's already in `.gitignore`)
3. Verify no spaces in the App Password

---

## Test Your Setup

Now let's verify everything is working!

### Test 1: Connection Test

Run the simple test example:

```powershell
cd "C:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
python email_sender\examples\simple_send.py
```

**Expected Output:**
```
📧 Gmail SMTP Test Email Sender
==================================================

1. Loading configuration...
   ✅ Loaded config for: your.email@gmail.com
   ✅ Default recipient: robinochieng74@gmail.com

2. Creating Gmail sender...
   ✅ Gmail sender created

3. Testing SMTP connection...
   ✅ Successfully connected to Gmail SMTP

4. Creating test email...
   ✅ Test email created

5. Sending plain text email...
   ✅ Email sent successfully to 1 recipient(s)
   📬 Recipients: robinochieng74@gmail.com

6. Sending HTML email...
   ✅ HTML email sent successfully to 1 recipient(s)
   📬 Recipients: robinochieng74@gmail.com

==================================================
✅ All tests completed successfully!
📬 Check your inbox at: robinochieng74@gmail.com
```

### Test 2: Check Your Inbox

1. Open Gmail at [mail.google.com](https://mail.google.com)
2. Check inbox for test emails
3. You should see 2 emails:
   - "Test Email - Plain Text"
   - "Test Email - HTML"

### Test 3: Sales Email Example

Run the sales email example:

```powershell
python email_sender\examples\sales_email.py
```

This sends a formatted sales email using templates.

---

## Troubleshooting

### Problem: "GMAIL_EMAIL environment variable is required"

**Cause:** Missing or not loaded from `.env` file

**Solution:**
1. Verify `.env` file exists in project root
2. Check `GMAIL_EMAIL=your.email@gmail.com` is present
3. Ensure no typos in variable name
4. Make sure `python-dotenv` is installed: `poetry install`

---

### Problem: "Gmail authentication failed"

**Cause:** Invalid credentials or using regular password instead of App Password

**Solutions:**

1. **Verify you're using App Password (not regular password)**
   ```env
   # ❌ Wrong - regular Gmail password
   GMAIL_APP_PASSWORD=MyRegularPassword123
   
   # ✅ Correct - 16-character App Password
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```

2. **Check for spaces in App Password**
   ```env
   # ❌ Wrong - contains spaces
   GMAIL_APP_PASSWORD=abcd efgh ijkl mnop
   
   # ✅ Correct - no spaces
   GMAIL_APP_PASSWORD=abcdefghijklmnop
   ```

3. **Verify 2FA is enabled**
   - Go to [myaccount.google.com/security](https://myaccount.google.com/security)
   - Check "2-Step Verification" shows "On"

4. **Generate new App Password**
   - Old one might be expired or revoked
   - Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Delete old password
   - Create new one

---

### Problem: "Connection timeout" or "Cannot connect to Gmail SMTP"

**Causes:**
- Firewall blocking port 587
- Network issues
- Incorrect SMTP settings

**Solutions:**

1. **Check internet connection**
   ```powershell
   ping smtp.gmail.com
   ```

2. **Try alternative port (465 with SSL)**
   ```env
   SMTP_SERVER=smtp.gmail.com
   SMTP_PORT=465
   USE_TLS=false  # Port 465 uses SSL instead
   ```

3. **Check firewall settings**
   - Allow Python through Windows Firewall
   - Allow outbound connections on port 587/465

4. **Test from command line**
   ```powershell
   Test-NetConnection smtp.gmail.com -Port 587
   ```

---

### Problem: "Invalid email address"

**Cause:** Email format is incorrect

**Solutions:**

1. **Check email format**
   ```env
   # ❌ Wrong formats
   GMAIL_EMAIL=notanemail
   GMAIL_EMAIL=missing@domain
   GMAIL_EMAIL=spaces in email@gmail.com
   
   # ✅ Correct format
   GMAIL_EMAIL=your.name@gmail.com
   ```

2. **Verify no extra spaces**
   ```env
   # ❌ Wrong - has spaces
   GMAIL_EMAIL= your.email@gmail.com 
   
   # ✅ Correct - no spaces
   GMAIL_EMAIL=your.email@gmail.com
   ```

---

### Problem: "Send failure after retries"

**Causes:**
- Gmail sending limits exceeded
- Recipient email invalid
- Emails marked as spam

**Solutions:**

1. **Check Gmail sending limits**
   - Free Gmail: 500 emails per day
   - Reset after 24 hours
   - Check: [mail.google.com/mail/u/0/#settings/filters](https://mail.google.com/mail/u/0/#settings/filters)

2. **Verify recipient email**
   - Test with known valid email first
   - Check for typos in recipient address

3. **Check spam folder**
   - Emails might be delivered to spam
   - Mark as "Not spam" to whitelist

4. **Add delay between sends**
   ```python
   import time
   
   for email in recipients:
       sender.send_text_email(...)
       time.sleep(2)  # Wait 2 seconds between emails
   ```

---

### Problem: "ConfigurationError: Invalid configuration"

**Cause:** Configuration validation failed

**Solutions:**

1. **Check App Password length**
   - Must be exactly 16 characters
   - Remove all spaces

2. **Verify all required fields**
   ```env
   GMAIL_EMAIL=your.email@gmail.com          # Required
   GMAIL_APP_PASSWORD=abcdefghijklmnop       # Required (16 chars)
   ```

3. **Check SMTP port**
   ```env
   # Valid ports:
   SMTP_PORT=587  # TLS (recommended)
   SMTP_PORT=465  # SSL
   ```

---

### Problem: Emails go to spam

**Solutions:**

1. **Send test to yourself first**
   - Gmail trusts self-sent emails
   - Mark as "Not spam" if needed

2. **Improve email content**
   - Avoid spam trigger words: "FREE", "URGENT", "CLICK HERE"
   - Use professional formatting
   - Include unsubscribe option for bulk emails

3. **Warm up sending**
   - Start with low volume (5-10 emails/day)
   - Gradually increase over weeks
   - Build sending reputation

---

## Advanced Configuration

### Using Custom SMTP Server

If you want to use a different SMTP provider:

```env
SMTP_SERVER=smtp.sendgrid.net
SMTP_PORT=587
GMAIL_EMAIL=apikey
GMAIL_APP_PASSWORD=your_sendgrid_api_key
```

### Adjusting Timeouts and Retries

For slower connections:

```env
EMAIL_TIMEOUT=60        # Increase to 60 seconds
MAX_RETRIES=5          # Try 5 times before giving up
```

### Disabling TLS (not recommended)

Only for testing:

```env
USE_TLS=false
SMTP_PORT=25  # Non-encrypted port
```

> ⚠️ **Warning:** Sending passwords over non-encrypted connection is dangerous!

---

## Security Best Practices

### ✅ DO:
- Use App Passwords, not regular passwords
- Store credentials in `.env` file
- Add `.env` to `.gitignore`
- Enable 2-factor authentication
- Revoke unused App Passwords
- Use different App Passwords for different apps

### ❌ DON'T:
- Commit `.env` to Git
- Share App Passwords
- Use regular Gmail password in code
- Disable 2FA
- Reuse App Passwords across projects

---

## Quick Reference

### Gmail SMTP Settings
```
Server: smtp.gmail.com
Port: 587 (TLS) or 465 (SSL)
Authentication: Yes
Username: Your Gmail address
Password: 16-character App Password
```

### Useful Links
- [Google Account Security](https://myaccount.google.com/security)
- [App Passwords](https://myaccount.google.com/apppasswords)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [2-Step Verification](https://www.google.com/landing/2step/)

### Support
If issues persist:
1. Review this guide again
2. Check [README.md](README.md) for API documentation
3. Verify environment variables are correctly set
4. Test with `simple_send.py` example

---

## Next Steps

Once setup is complete:

1. ✅ Test with `simple_send.py`
2. ✅ Review [README.md](README.md) for API documentation
3. ✅ Explore example scripts in `examples/`
4. ✅ Integrate with `openai_sdk_agent.py`
5. ✅ Build your own email workflows!

**Happy sending! 📧**
