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
├── openai_sdk_agent.py      # Main application file
├── pyproject.toml            # Poetry configuration
├── .env                      # Environment variables (not in git)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

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

## 📞 Support

For issues or questions:
- Check the OpenAI documentation: https://platform.openai.com/docs
- Check the SendGrid documentation: https://docs.sendgrid.com
- Review OpenAI traces: https://platform.openai.com/traces

---

Built with ❤️ using OpenAI SDK and SendGrid
