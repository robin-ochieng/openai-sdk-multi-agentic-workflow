# Deep Research Agent - Model Configuration

## 📊 Current Configuration

All agents in the Deep Research pipeline are now configured to use **`gpt-4o`** by default.

### Agent Model Settings

| Agent | Model | Purpose |
|-------|-------|---------|
| **Planner Agent** | `gpt-4o` | Analyzes queries and creates strategic search plans |
| **Search Agent** | `gpt-4o` | Performs web searches and summarizes results |
| **Writer Agent** | `gpt-4o` | Synthesizes findings into comprehensive reports |
| **Email Agent** | `gpt-4o` | Converts reports to HTML and sends via SMTP |

## 🔧 How to Change the Model

### Option 1: At Initialization (Recommended)

```python
from deep_research import ResearchManager

# Use gpt-4o (default)
manager = ResearchManager()

# Or specify a different model for all agents
manager = ResearchManager(model="gpt-4o-mini")
```

### Option 2: Per Agent

You can customize each agent individually when creating them:

```python
from deep_research.research_agents import (
    create_planner_agent,
    create_search_agent,
    create_writer_agent,
    create_email_agent
)

# Mix models as needed
planner = create_planner_agent(api_key, model="gpt-4o")
search = create_search_agent(api_key, model="gpt-4o")
writer = create_writer_agent(api_key, model="gpt-4o")
email = create_email_agent(api_key, model="gpt-4o-mini")  # Lighter model for simple HTML conversion
```

## 💰 Cost Considerations

### GPT-4o Pricing (as of October 2025)
- **Input**: $2.50 per 1M tokens
- **Output**: $10.00 per 1M tokens

### Typical Research Query Costs
For a comprehensive research query (5 searches, 1000+ word report):

- **Planner Agent**: ~500 tokens ($0.001)
- **Search Agent** (5x): ~2,500 tokens each = 12,500 total ($0.03)
- **Writer Agent**: ~3,000 input + 1,500 output = 4,500 total ($0.02)
- **Email Agent**: ~1,500 tokens ($0.004)

**Estimated cost per query: ~$0.055 (5.5 cents)**

## 🎯 Model Selection Guide

### When to use `gpt-4o`:
✅ Complex reasoning required
✅ High-quality report synthesis
✅ Best search query planning
✅ Production use cases

### When to use `gpt-4o-mini`:
✅ Cost-sensitive applications
✅ Simple HTML formatting
✅ High-volume queries
✅ Testing/development

## 📝 Change Log

**2025-10-17**: 
- ✅ Set all agents to use `gpt-4o` as default
- ✅ Fixed Email Agent from `gpt-4o-mini` to `gpt-4o`
- ✅ Updated all docstrings to reflect correct model defaults

## 🔍 Verification

To verify the current model configuration:

```python
from deep_research import ResearchManager

manager = ResearchManager()
print(f"Model: {manager.model}")

# Check individual agents
print(f"Planner: {manager.planner_agent.model}")
print(f"Search: {manager.search_agent.model}")
print(f"Writer: {manager.writer_agent.model}")
print(f"Email: {manager.email_agent.model}")
```

All should show: `gpt-4o` ✅
