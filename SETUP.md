# Setup Instructions for OpenAI SDK Agents

## Quick Start Guide

Follow these steps to set up and run the project:

### Step 1: Install Poetry

If you don't have Poetry installed:

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

After installation, restart your terminal or run:
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

Verify installation:
```powershell
poetry --version
```

### Step 2: Install Dependencies

Navigate to the project directory:
```powershell
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
```

Install all dependencies:
```powershell
poetry install
```

### Step 3: Configure Environment Variables

1. Open the `.env` file in the project root
2. Add your API keys and email addresses:

```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxx
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxx
SENDER_EMAIL=your-verified-email@example.com
RECIPIENT_EMAIL=recipient@example.com
```

### Step 4: Get Your API Keys

#### OpenAI API Key:
1. Visit https://platform.openai.com/
2. Sign in or create an account
3. Go to "API Keys" section
4. Click "Create new secret key"
5. Copy the key (starts with `sk-proj-`)

#### SendGrid API Key:
1. Visit https://sendgrid.com/
2. Sign up for a free account
3. Go to Settings → API Keys
4. Click "Create API Key"
5. Give it "Full Access" or "Mail Send" permissions
6. Copy the key (starts with `SG.`)

#### Verify SendGrid Sender:
1. In SendGrid, go to Settings → Sender Authentication
2. Click "Verify a Single Sender"
3. Enter your email address
4. Check your email and click the verification link
5. Use this verified email as `SENDER_EMAIL` in `.env`

### Step 5: Run the Application

Activate the Poetry environment:
```powershell
poetry shell
```

Run the application:
```powershell
python openai_sdk_agent.py
```

### Step 6: Customize (Optional)

Edit `openai_sdk_agent.py` and uncomment different functions in the `main()` function:

```python
async def main():
    # Uncomment the function you want to run:
    
    # 1. Test email sending
    # send_test_email()
    
    # 2. Demo streamed response
    # await demo_streamed_response()
    
    # 3. Generate parallel emails
    # await generate_parallel_emails()
    
    # 4. Select best email
    # await select_best_email()
    
    # 5. Run sales manager
    # await run_sales_manager()
    
    # 6. Run full automated SDR (default)
    await run_automated_sdr()
```

## Troubleshooting

### Import Errors
Make sure you're in the Poetry environment:
```powershell
poetry shell
```

### SSL Certificate Errors
```powershell
poetry add certifi
```

Then add to your code:
```python
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
```

### Email Not Received
1. Check spam folder
2. Verify SendGrid API key is correct
3. Ensure sender email is verified in SendGrid
4. Check SendGrid dashboard for delivery logs at https://app.sendgrid.com/email_activity

### Poetry Not Found
Add Poetry to PATH:
```powershell
$env:Path += ";$env:APPDATA\Python\Scripts"
```

Or restart your terminal after installation.

## Project Commands

```powershell
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run the script
python openai_sdk_agent.py

# Add a new package
poetry add package-name

# Update dependencies
poetry update

# Exit virtual environment
exit
```

## Next Steps

1. Test with `send_test_email()` first
2. Customize agent instructions for your company
3. Modify email templates
4. Add more agents or tools as needed
5. Check OpenAI traces at https://platform.openai.com/traces

## Support

- OpenAI Documentation: https://platform.openai.com/docs
- SendGrid Documentation: https://docs.sendgrid.com
- Poetry Documentation: https://python-poetry.org/docs

Enjoy building with AI agents! 🚀
