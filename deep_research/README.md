# 🔬 Deep Research Agent Package

> **Modular AI-Powered Research System with 4-Agent Pipeline**

A comprehensive deep research automation system built with OpenAI's Agent SDK, featuring structured outputs, web search, guardrails-protected email delivery, and a Gradio web interface.

---

## 📦 What's Inside

```
deep_research/
├── agents/          # 4 specialized AI agents
├── models/          # Pydantic structured outputs
├── tools/           # Function tools (search, calc, file ops)
├── ui/              # Gradio web interface
├── docs/            # Comprehensive documentation
├── reports/         # Generated reports (auto-created)
├── research_manager.py  # Pipeline orchestrator
├── app.py           # Main entry point
├── examples.py      # Quick start examples
└── requirements.txt # Dependencies
```

## ✨ Key Features

- 🤖 **4-Agent Pipeline**: Planner → Search → Writer → Email
- 📊 **Structured Outputs**: Type-safe Pydantic models
- 🛡️ **Guardrails Protected**: Spam detection, rate limiting, safety checks
- 🌐 **Web Search**: OpenAI hosted WebSearchTool
- 📧 **Gmail Integration**: SMTP delivery with validation
- 🖥️ **Gradio UI**: Simple, intuitive web interface
- 📈 **OpenAI Traces**: Full execution transparency
- 🧩 **Modular Design**: Easy to extend and customize

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r deep_research/requirements.txt
```

### 2. Configure Environment

Ensure your `.env` file has:

```env
OPENAI_API_KEY=sk-proj-your_key
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@email.com
```

### 3. Run!

**Option A: Web Interface**
```bash
python deep_research/app.py
```

**Option B: Command Line**
```python
import asyncio
from deep_research import ResearchManager

async def main():
    manager = ResearchManager()
    report = await manager.run("Latest AI frameworks in 2025")
    print(f"Trace: {manager.trace_url}")

asyncio.run(main())
```

**Option C: Examples**
```bash
python deep_research/examples.py
```

## 📚 Documentation

- **[README.md](./docs/README.md)** - Complete guide and features
- **[ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - System design deep dive
- **[API_REFERENCE.md](./docs/API_REFERENCE.md)** - Full API documentation
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - Production deployment guide

## 🏗️ How It Works

```
User Query
    ↓
[1] Planner Agent
    Creates 5 strategic search queries
    ↓
[2] Search Agent (×5 parallel)
    Performs web searches
    Summarizes findings
    ↓
[3] Writer Agent
    Synthesizes comprehensive report
    5-10 pages, 1000+ words, markdown
    ↓
[4] Email Agent
    Converts to professional HTML
    Validates with guardrails
    Sends via Gmail SMTP
    ↓
Report Delivered to Inbox ✉️
```

## 🎯 Use Cases

- **Research Reports**: Automated literature reviews
- **Market Analysis**: Industry trend reports
- **Technical Documentation**: Framework comparisons
- **Competitive Intelligence**: Market landscape analysis
- **Academic Research**: Topic exploration and synthesis

## 🛡️ Guardrails

Every email is protected by:
- ✅ Spam detection (0-100 scoring)
- ✅ Rate limiting (50/hour, 500/day)
- ✅ Content safety checks
- ✅ Email format validation
- ✅ Personalization warnings

## 📊 Cost Estimate

**Per research query (using gpt-4o-mini):**
- Planner: ~$0.00015
- Searches (×5): ~$0.0015
- Writer: ~$0.003
- Email: ~$0.0003
- **Total: ~$0.005** ($5 for 1000 queries)

## 🔧 Customization

### Change Search Count
```python
# In agents/planner_agent.py
HOW_MANY_SEARCHES = 3  # Reduce for speed
```

### Use GPT-4
```python
manager = ResearchManager(model="gpt-4o")
```

### Modify Report Length
```python
# In agents/writer_agent.py
INSTRUCTIONS = "...Aim for 10-15 pages, 2000+ words..."
```

## 📖 Examples

### Example 1: Basic Usage
```python
from deep_research import ResearchManager
import asyncio

async def main():
    manager = ResearchManager()
    report = await manager.run("AI agent frameworks 2025")
    print(report)

asyncio.run(main())
```

### Example 2: Step-by-Step
```python
manager = ResearchManager()

# Step 1: Plan
plan = await manager.plan_searches(query)
print(f"Searches: {[s.query for s in plan.searches]}")

# Step 2: Search
results = await manager.perform_searches(plan)

# Step 3: Write
report = await manager.write_report(query, results)

# Step 4: Email
await manager.send_email(report)
```

### Example 3: Custom Integration
```python
from deep_research.agents import create_search_agent
from openai.lib._agents import Runner

search_agent = create_search_agent(api_key)
result = await Runner.run(search_agent, "Search term: OpenAI agents")
print(result.final_output)  # Summary text
```

## 🐛 Troubleshooting

**Import errors?**
```bash
pip install --upgrade openai pydantic gradio
```

**Email not sending?**
- Check Gmail App Password (not regular password)
- Verify `.env` configuration
- Check guardrails logs

**Web search not working?**
- Ensure OpenAI account has Agent SDK access
- Verify API key permissions

## 📦 Package Structure

```python
from deep_research import ResearchManager
from deep_research.models import WebSearchPlan, ReportData
from deep_research.agents import create_planner_agent
from deep_research.ui import launch_ui
```

## 🤝 Integration

This package integrates with:
- `email_sender` package (from parent project)
- `email_sender.guardrails_email` (validation)
- OpenAI Agent SDK
- Gradio for UI

## 📝 License

Part of the OpenAI SDK Multi-Agentic Workflow project.
See parent repository for license details.

## 🙏 Credits

Built with:
- OpenAI Agent SDK
- Pydantic for structured outputs
- Gradio for web UI
- Gmail SMTP for email delivery
- Guardrails from parent project

---

**Ready to start?** Run `python deep_research/examples.py` for guided examples!

For detailed documentation, see [`docs/README.md`](./docs/README.md)
