# OpenAI SDK Agents - Sales Email Automation

An intelligent agent system built with OpenAI's SDK for automated cold sales email generation and delivery.

## 🚀 Features

- **Multiple Sales Agent Personas**: Professional, engaging, and concise email writing styles
- **Intelligent Email Selection**: Automated comparison and selection of best email drafts
- **HTML Email Formatting**: Automatic conversion of text emails to professional HTML
- **Subject Line Generation**: AI-powered subject line creation
- **Automated Email Delivery**: Integration with SendGrid for reliable email sending
- **Agent Collaboration**: Tools and handoffs for seamless agent interaction
- **Async Processing**: Parallel email generation for improved performance
- **🛡️ Guardrails & Structured Outputs**: Production-grade safety and validation (NEW!)
  - Input validation (name detection, content safety)
  - Output validation (spam detection, quality checks)
  - Rate limiting (50/hour, 500/day)
  - Structured outputs with Pydantic models

## 📋 Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)
- OpenAI API key
- SendGrid account and API key

## 🛠️ Installation

### 1. Install Poetry (if not already installed)

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### 2. Clone or navigate to the project directory

```powershell
cd "c:\Users\Robin Ochieng\OneDrive - Kenbright\Gig\AI Agents\Projects\OpenAI SDK Agents"
```

### 3. Install dependencies

```powershell
poetry install
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
cp .env.example .env
```

Edit `.env` with your actual values:
```env
OPENAI_API_KEY=sk-...
SENDGRID_API_KEY=SG...
SENDER_EMAIL=your_verified_email@example.com
RECIPIENT_EMAIL=recipient@example.com
```

## 🔑 Getting API Keys

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### SendGrid API Key
1. Go to [SendGrid](https://sendgrid.com/)
2. Sign up for a free account
3. Navigate to: **Settings** → **API Keys** → **Create API Key**
4. Copy the key immediately (it won't be shown again)

### Verify SendGrid Sender
1. Go to: **Settings** → **Sender Authentication** → **Verify a Single Sender**
2. Add and verify your email address
3. Use this verified email as `SENDER_EMAIL` in `.env`

## 🚀 Usage

### Activate Poetry environment

```powershell
poetry shell
```

### Run the main script

```powershell
python openai_sdk_agent.py
```

## 📁 Project Structure

```
OpenAI SDK Agents/
│
├── openai_sdk_agent.py                  # Main application file
├── openai_sdk_agent_with_guardrails.py  # 🛡️ Protected version with guardrails
├── guardrails.py                        # 🛡️ Main guardrail system
├── pyproject.toml                       # Poetry configuration
├── .env                                 # Environment variables (not in git)
├── .env.example                         # Environment template
├── .gitignore                           # Git ignore rules
├── README.md                            # This file
│
├── docs/                                # 📚 Complete documentation
│   ├── INDEX.md                         # Documentation navigation
│   ├── SETUP.md                         # Detailed setup guide
│   ├── GUARDRAILS.md                    # 🛡️ Guardrails guide (NEW!)
│   ├── AGENT_WORKFLOW_EXPLAINED.md      # Design patterns
│   ├── GMAIL_IMPLEMENTATION.md          # Gmail SMTP guide
│   ├── QUICK_START_GMAIL.md             # Quick Gmail setup
│   └── ... (11 total docs)
│
├── email_sender/                        # 📧 Gmail SMTP module
│   ├── __init__.py
│   ├── config.py                        # Email configuration
│   ├── gmail_sender.py                  # Gmail SMTP sender
│   ├── guardrails_email.py              # 🛡️ Email guardrails (NEW!)
│   ├── email_templates.py               # Pre-built templates
│   ├── validators.py                    # Email validation
│   ├── exceptions.py                    # Custom exceptions
│   ├── README.md                        # Module documentation
│   ├── SETUP_GUIDE.md                   # Gmail App Password guide
│   └── examples/                        # Example scripts
│
└── tests/                               # 🧪 All test files
    ├── README.md                        # Testing guide
    ├── test_gmail.py                    # Gmail SMTP integration test
    ├── test_sales_email.py              # Sales template test
    ├── test_integration.py              # Integration examples
    └── test_gmail_sender.py             # Unit tests for GmailSender
```

## 🛡️ Guardrails & Safety (NEW!)

This project now includes comprehensive guardrails for production-grade AI safety:

### Input Guardrails
- ✅ **Name Detection**: Flags personal names for privacy/compliance
- ✅ **Content Safety**: Prevents inappropriate inputs

### Output Guardrails
- ✅ **Spam Detection**: Scores emails (0-100) and blocks high-risk content
- ✅ **Quality Validation**: Ensures professional tone and personalization
- ✅ **Safety Checks**: Prevents harmful or inappropriate outputs

### Operational Guardrails
- ✅ **Rate Limiting**: 50 emails/hour, 500 emails/day
- ✅ **Email Validation**: Format checking, domain verification
- ✅ **Statistics Tracking**: Monitor sending patterns

### Quick Start with Guardrails

```powershell
# Run protected workflow with all guardrails
python openai_sdk_agent_with_guardrails.py

# Test email guardrails
python email_sender/guardrails_email.py

# Test main guardrail system
python guardrails.py
```

**📖 Full Documentation**: [docs/GUARDRAILS.md](docs/GUARDRAILS.md)

## 🧪 How It Works

1. **Agent Creation**: Three sales agents are created with different writing styles
2. **Parallel Generation**: All agents generate email drafts simultaneously
3. **Selection**: A picker agent selects the best email based on effectiveness
4. **Formatting**: The selected email is converted to HTML with a subject line
5. **Delivery**: The formatted email is sent via SendGrid

## 🔧 Troubleshooting

### SSL Certificate Errors

If you encounter SSL certificate errors:

```powershell
poetry add certifi
```

Then in your code:
```python
import certifi
import os
os.environ['SSL_CERT_FILE'] = certifi.where()
```

### Import Errors

Make sure you're in the Poetry environment:
```powershell
poetry shell
```

### Email Not Received

1. Check your spam folder
2. Verify your SendGrid API key is correct
3. Ensure your sender email is verified in SendGrid
4. Check SendGrid dashboard for delivery logs

## 📝 Customization

### Modify Agent Instructions

Edit the `instructions1`, `instructions2`, and `instructions3` variables in `openai_sdk_agent.py` to change agent behavior.

### Change Company Information

Update the ComplAI references in the instruction strings to match your company.

### Adjust Email Recipients

Modify the recipient list in the `send_html_email` function.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## ⚠️ Important Notes

- **Cost**: This uses OpenAI API which incurs costs per API call
- **Rate Limits**: Be aware of OpenAI and SendGrid rate limits
- **Compliance**: Ensure you comply with anti-spam laws (CAN-SPAM, GDPR, etc.)
- **Testing**: Test thoroughly with your own email before sending to prospects

## � Documentation

For detailed documentation, see the [docs/](./docs/) folder:

- **[Getting Started](./docs/SETUP.md)** - Complete installation and setup
- **[Quick Reference](./docs/QUICK_REFERENCE.md)** - Common commands and shortcuts
- **[Gmail Setup](./docs/QUICK_START_GMAIL.md)** - Gmail SMTP in 3 minutes
- **[Agent Workflow](./docs/AGENT_WORKFLOW_EXPLAINED.md)** - Deep dive into design patterns
- **[Email Module](./email_sender/README.md)** - Gmail SMTP API reference
- **[Documentation Index](./docs/INDEX.md)** - Complete documentation navigation

## �📞 Support

For issues or questions:
- Check the [Documentation Index](./docs/INDEX.md) for comprehensive guides
- Review the [Troubleshooting Guide](./docs/INSTALLATION_SUCCESS.md)
- Check the OpenAI documentation: https://platform.openai.com/docs
- Check the SendGrid documentation: https://docs.sendgrid.com
- Review OpenAI traces: https://platform.openai.com/traces

## 🔗 Repository

**GitHub:** [robin-ochieng/openai-sdk-multi-agentic-workflow](https://github.com/robin-ochieng/openai-sdk-multi-agentic-workflow)

---

Built with ❤️ using OpenAI SDK, SendGrid, and Gmail SMTP
