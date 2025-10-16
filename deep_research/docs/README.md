# 🔬 Deep Research Agent

> AI-Powered Research System with 4-Agent Pipeline, Structured Outputs, and Gmail SMTP Integration

## 📋 Overview

The Deep Research Agent is a sophisticated multi-agent system that automates the research process from query to comprehensive report delivery. It uses OpenAI's Agent SDK with structured outputs, web search capabilities, and guardrails-protected email delivery.

### Key Features

✅ **4-Agent Pipeline Architecture**
- **Planner Agent**: Strategizes 5 targeted web searches
- **Search Agent**: Performs searches and summarizes findings
- **Writer Agent**: Synthesizes comprehensive 5-10 page reports
- **Email Agent**: Converts to HTML and delivers via Gmail SMTP

✅ **Structured Outputs with Pydantic**
- Type-safe data models
- Validated agent responses
- Predictable output formats

✅ **Guardrails Protection**
- Spam detection (0-100 scoring)
- Rate limiting (50/hour, 500/day)
- Content safety checks
- Email format validation

✅ **OpenAI Traces**
- Full execution transparency
- Debug and monitoring capabilities
- Agent reasoning visibility

✅ **Gradio Web Interface**
- Simple, intuitive UI
- Real-time progress tracking
- Example queries
- Report preview

---

## 🏗️ Architecture

### Agent Pipeline Flow

```
User Query (via Gradio)
       ↓
[1] Planner Agent
       ├─> Creates 5 strategic searches
       ├─> Uses structured output: WebSearchPlan
       └─> Reasons about search importance
       ↓
[2] Search Agent (×5 parallel)
       ├─> Performs web searches (OpenAI WebSearchTool)
       ├─> Summarizes each result (2-3 paragraphs, <300 words)
       └─> Filters out fluff, captures essence
       ↓
[3] Writer Agent
       ├─> Synthesizes all search results
       ├─> Creates outline and structure
       ├─> Generates comprehensive report
       ├─> Output: 5-10 pages, 1000+ words, markdown format
       └─> Uses structured output: ReportData
       ↓
[4] Email Agent
       ├─> Converts markdown to clean HTML
       ├─> Adds professional styling
       ├─> Runs guardrails validation
       ├─> Sends via Gmail SMTP
       └─> Rate limiting + spam protection
       ↓
Report Delivered to Inbox ✉️
```

### Project Structure

```
deep_research/
├── agents/                    # Agent definitions
│   ├── __init__.py
│   ├── planner_agent.py      # Step 1: Plan searches
│   ├── search_agent.py       # Step 2: Execute searches
│   ├── writer_agent.py       # Step 3: Write report
│   └── email_agent.py        # Step 4: Send email
│
├── models/                    # Pydantic structured outputs
│   ├── __init__.py
│   └── research_models.py    # WebSearchPlan, ReportData, etc.
│
├── tools/                     # Function tools
│   ├── __init__.py
│   ├── web_search.py         # Web search (hosted by OpenAI)
│   ├── file_operations.py    # Save reports to disk
│   └── calculator.py         # Math operations
│
├── ui/                        # Gradio web interface
│   ├── __init__.py
│   └── gradio_app.py         # Web UI implementation
│
├── docs/                      # Documentation
│   ├── README.md             # This file
│   ├── ARCHITECTURE.md       # Detailed architecture
│   ├── API_REFERENCE.md      # API documentation
│   └── DEPLOYMENT.md         # Deployment guide
│
├── reports/                   # Generated reports (auto-created)
│
├── __init__.py               # Package exports
├── research_manager.py       # Main orchestrator
└── app.py                    # Entry point
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key with Agent SDK access
- Gmail account with App Password
- Required packages: `openai`, `pydantic`, `gradio`, `python-dotenv`

### Installation

1. **Install dependencies:**
```bash
pip install openai pydantic gradio python-dotenv
```

2. **Configure environment variables:**

Create/update `.env` file in project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
GMAIL_EMAIL=your_gmail@gmail.com
GMAIL_APP_PASSWORD=your_app_password_here
RECIPIENT_EMAIL=recipient@email.com
```

3. **Run the application:**
```bash
python deep_research/app.py
```

This will:
- Load environment variables
- Initialize the 4-agent system
- Launch Gradio web interface at `http://localhost:7860`
- Open browser automatically

### Using the Web Interface

1. Navigate to `http://localhost:7860`
2. Enter your research query (e.g., "Latest AI Agent frameworks in 2025")
3. Click "🚀 Start Research"
4. Monitor progress in real-time
5. View report preview in the interface
6. Check your email for the comprehensive HTML report
7. Click trace URL to see detailed execution logs

---

## 📖 Usage Examples

### Example 1: Command-Line Usage

```python
import asyncio
from deep_research import ResearchManager

async def main():
    # Initialize manager
    manager = ResearchManager()
    
    # Run research
    query = "Latest AI Agent frameworks in 2025"
    report = await manager.run(query)
    
    print(f"Report length: {len(report)} characters")
    print(f"Trace URL: {manager.trace_url}")

asyncio.run(main())
```

### Example 2: Custom Integration

```python
from deep_research import ResearchManager
from deep_research.models import WebSearchPlan

async def custom_research():
    manager = ResearchManager(model="gpt-4o")
    
    # Step 1: Plan only
    query = "Impact of LLMs on software development"
    plan = await manager.plan_searches(query)
    
    print(f"Planned {len(plan.searches)} searches:")
    for search in plan.searches:
        print(f"  - {search.query}")
        print(f"    Reason: {search.reason}")
    
    # Step 2: Execute searches
    results = await manager.perform_searches(plan)
    
    # Step 3: Write report
    report = await manager.write_report(query, results)
    
    # Step 4: Send email
    await manager.send_email(report)
```

### Example 3: Using Individual Agents

```python
from deep_research.agents import create_planner_agent
from openai.lib._agents import Runner
import os

# Create planner agent
planner = create_planner_agent(
    api_key=os.getenv('OPENAI_API_KEY'),
    model="gpt-4o-mini"
)

# Run planner
async def plan():
    result = await Runner.run(
        planner,
        "Query: Best practices for multi-agent systems"
    )
    
    # Access structured output
    for search in result.final_output.searches:
        print(f"Search: {search.query}")
        print(f"Reason: {search.reason}\n")

asyncio.run(plan())
```

---

## 🛡️ Guardrails Integration

The Email Agent uses the existing guardrails system from `email_sender`:

### Validation Checks

1. **Spam Score Detection** (0-100 scale)
   - Pattern matching for spam indicators
   - Blocks emails with score ≥30
   - Detects: excessive caps, multiple exclamation marks, suspicious URLs

2. **Rate Limiting**
   - 50 emails per hour
   - 500 emails per 24 hours
   - Prevents abuse and protects reputation

3. **Content Safety**
   - Phishing detection
   - SQL injection prevention
   - Malicious link detection

4. **Email Format Validation**
   - RFC 5322 compliance
   - Domain verification
   - Typo detection (common mistakes)

5. **Personalization Checks** (non-blocking warnings)
   - Generic greeting detection
   - Name presence validation
   - Merge tag verification

### Example Guardrail Output

```
🛡️ GUARDRAIL VALIDATION:
   Overall Status: ✅ PASSED

   ✅ Spam Score: 5/100 (low)
   ✅ Email Format: Valid
   ✅ Content Safety: Safe
   ✅ Rate Limit: 3/50 hourly, 12/500 daily
   
   ⚠️ Warnings (1):
      • Generic greeting detected - consider personalizing
```

---

## 📊 Structured Outputs

All agents use Pydantic models for type-safe, validated outputs:

### WebSearchPlan (Planner Agent Output)

```python
{
    "searches": [
        {
            "reason": "Need to understand current market leaders",
            "query": "top AI agent frameworks 2025"
        },
        # ... 4 more searches
    ]
}
```

### ReportData (Writer Agent Output)

```python
{
    "short_summary": "Brief 2-3 sentence overview...",
    "markdown_report": "# Full Report\n\n## Introduction\n...",
    "follow_up_questions": [
        "How do these frameworks compare in production?",
        "What are the cost implications?"
    ]
}
```

### Benefits

✅ Type safety at compile time
✅ Automatic validation
✅ Clear documentation
✅ IDE autocomplete
✅ Easier testing

---

## 🔍 OpenAI Traces

Every research execution creates a trace for full transparency:

### Accessing Traces

1. **From Web UI**: Click the trace URL in the "Trace Link" tab
2. **From Code**: Access `manager.trace_url` after running research
3. **From Console**: Check printed trace URLs during execution

### What Traces Show

- All agent interactions
- Tool calls and responses
- LLM reasoning steps
- Token usage statistics
- Execution timeline
- Error details (if any)

### Example Trace URL

```
https://platform.openai.com/traces/trace?trace_id=abc123...
```

---

## 🎨 Customization

### Change Model

```python
# Use GPT-4 for better quality
manager = ResearchManager(model="gpt-4o")

# Or specify per agent
from deep_research.agents import create_planner_agent
planner = create_planner_agent(api_key, model="gpt-4o")
```

### Modify Search Count

Edit `deep_research/agents/planner_agent.py`:
```python
HOW_MANY_SEARCHES = 3  # Change from 5 to 3
```

### Adjust Report Length

Edit `deep_research/agents/writer_agent.py`:
```python
INSTRUCTIONS = (
    # ... existing instructions ...
    "Aim for 10-15 pages of content, at least 2000 words."
)
```

### Change Email Styling

The Email Agent auto-converts markdown to HTML. To customize styling, modify the prompt in `deep_research/agents/email_agent.py`:

```python
INSTRUCTIONS = (
    "Convert report to HTML with custom CSS: "
    "Use blue headers, serif fonts, and professional layout..."
)
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: Import errors for `openai.lib._agents`
```bash
# Solution: Upgrade OpenAI SDK
pip install --upgrade openai
```

**Issue**: Gradio not found
```bash
# Solution: Install Gradio
pip install gradio
```

**Issue**: Email not sending
- Check `.env` file has correct Gmail credentials
- Ensure Gmail App Password is set (not regular password)
- Verify recipient email is correct
- Check guardrails aren't blocking (high spam score)

**Issue**: Web search not working
- Ensure OpenAI account has Agent SDK access
- Check API key permissions
- Verify billing is active

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

manager = ResearchManager()
await manager.run("Your query")
```

---

## 📚 Additional Documentation

- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Detailed system design
- **[API_REFERENCE.md](./API_REFERENCE.md)** - Complete API docs
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Production deployment guide
- **[EXAMPLES.md](./EXAMPLES.md)** - More usage examples

---

## 🤝 Contributing

This is a modular package designed for easy extension:

1. Add new agents in `agents/`
2. Create new tools in `tools/`
3. Define new models in `models/`
4. Update pipeline in `research_manager.py`

---

## 📄 License

MIT License - See parent project for details

---

## 🙏 Acknowledgments

- Built with OpenAI Agent SDK
- Uses Guardrails system from parent project
- Gmail SMTP integration from `email_sender` package
- UI powered by Gradio

---

**Questions? Check the docs folder or review the code - it's heavily commented!**
