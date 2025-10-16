# 📚 API Reference

## ResearchManager

Main orchestrator for the deep research pipeline.

### Constructor

```python
ResearchManager(api_key: str = None, model: str = "gpt-4o-mini")
```

**Parameters:**
- `api_key` (str, optional): OpenAI API key. If None, reads from `OPENAI_API_KEY` environment variable.
- `model` (str, default="gpt-4o-mini"): Model to use for all agents.

**Returns:** ResearchManager instance

**Example:**
```python
from deep_research import ResearchManager

# Using environment variable
manager = ResearchManager()

# With explicit API key
manager = ResearchManager(api_key="sk-...")

# With custom model
manager = ResearchManager(model="gpt-4o")
```

---

### Methods

#### `async run(query: str) -> str`

Run the complete deep research process.

**Parameters:**
- `query` (str): Research question or topic

**Returns:** str - The markdown report content

**Raises:**
- `ValueError`: If query is empty or too short
- `Exception`: For API or network errors

**Example:**
```python
import asyncio

async def main():
    manager = ResearchManager()
    report = await manager.run("Latest AI frameworks in 2025")
    print(f"Report: {report[:500]}...")

asyncio.run(main())
```

**Side Effects:**
- Creates OpenAI trace (accessible via `manager.trace_url`)
- Sends email to `RECIPIENT_EMAIL`
- Updates `manager.current_status`

---

#### `async plan_searches(query: str) -> WebSearchPlan`

Step 1: Create strategic search plan.

**Parameters:**
- `query` (str): Research query

**Returns:** `WebSearchPlan` - Structured plan with 3-5 searches

**Example:**
```python
plan = await manager.plan_searches("AI agent frameworks")

for search in plan.searches:
    print(f"Query: {search.query}")
    print(f"Reason: {search.reason}\n")
```

---

#### `async perform_searches(search_plan: WebSearchPlan) -> List[str]`

Step 2: Execute all searches in parallel.

**Parameters:**
- `search_plan` (`WebSearchPlan`): Plan from planner agent

**Returns:** `List[str]` - List of search summaries

**Example:**
```python
plan = await manager.plan_searches(query)
results = await manager.perform_searches(plan)

print(f"Got {len(results)} summaries")
```

---

#### `async write_report(query: str, search_results: List[str]) -> ReportData`

Step 3: Synthesize results into comprehensive report.

**Parameters:**
- `query` (str): Original research query
- `search_results` (`List[str]`): Summaries from search agent

**Returns:** `ReportData` - Structured report with markdown content

**Example:**
```python
report = await manager.write_report(query, search_results)

print(f"Summary: {report.short_summary}")
print(f"Word count: {len(report.markdown_report.split())}")
print(f"Follow-ups: {report.follow_up_questions}")
```

---

#### `async send_email(report: ReportData) -> Dict[str, str]`

Step 4: Convert to HTML and send via Gmail SMTP.

**Parameters:**
- `report` (`ReportData`): Report from writer agent

**Returns:** `Dict[str, str]` - Status of email operation

**Example:**
```python
result = await manager.send_email(report)

if result['status'] == 'success':
    print("Email sent!")
else:
    print(f"Error: {result['message']}")
```

---

### Properties

#### `current_status: str`

Current pipeline status message (read-only).

**Possible Values:**
- `"Idle"`
- `"Planning searches..."`
- `"Searching and summarizing..."`
- `"Writing comprehensive report..."`
- `"Converting to HTML and sending email..."`
- `"Complete! ✅"`

**Example:**
```python
print(manager.current_status)  # "Searching and summarizing..."
```

---

#### `trace_url: str | None`

OpenAI trace URL for current/last execution (read-only).

**Example:**
```python
await manager.run(query)
print(f"View trace: {manager.trace_url}")
# https://platform.openai.com/traces/trace?trace_id=...
```

---

## Agent Factories

### `create_planner_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent`

Create the Planner Agent.

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str, default="gpt-4o-mini"): Model to use

**Returns:** Configured `Agent` instance

**Example:**
```python
from deep_research.agents import create_planner_agent
from openai.lib._agents import Runner

planner = create_planner_agent(api_key="sk-...")
result = await Runner.run(planner, "Query: AI frameworks")
print(result.final_output.searches)
```

---

### `create_search_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent`

Create the Search Agent with WebSearchTool.

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str, default="gpt-4o-mini"): Model to use

**Returns:** Configured `Agent` instance

**Example:**
```python
from deep_research.agents import create_search_agent

search_agent = create_search_agent(api_key="sk-...")
input_data = "Search term: OpenAI agents\nReason: Need docs"
result = await Runner.run(search_agent, input_data)
print(result.final_output)  # Summary text
```

---

### `create_writer_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent`

Create the Writer Agent.

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str, default="gpt-4o-mini"): Model to use

**Returns:** Configured `Agent` instance

**Example:**
```python
from deep_research.agents import create_writer_agent

writer = create_writer_agent(api_key="sk-...")
input_data = f"Query: {query}\n\nResults: {search_results}"
result = await Runner.run(writer, input_data)
print(result.final_output.markdown_report)
```

---

### `create_email_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent`

Create the Email Agent with send_email tool.

**Parameters:**
- `api_key` (str): OpenAI API key
- `model` (str, default="gpt-4o-mini"): Model to use

**Returns:** Configured `Agent` instance

**Example:**
```python
from deep_research.agents import create_email_agent

email_agent = create_email_agent(api_key="sk-...")
result = await Runner.run(email_agent, markdown_report)
print(result.final_output)  # Email status
```

---

## Data Models

All models use Pydantic for validation and type safety.

### `WebSearchItem`

Single web search item.

**Fields:**
- `reason` (str): Why this search is important
- `query` (str): Search term to use

**Example:**
```python
from deep_research.models import WebSearchItem

item = WebSearchItem(
    reason="Need market overview",
    query="AI frameworks 2025"
)
```

---

### `WebSearchPlan`

Plan containing multiple searches.

**Fields:**
- `searches` (List[WebSearchItem]): 3-5 search items

**Constraints:**
- `min_items=3`
- `max_items=5`

**Example:**
```python
from deep_research.models import WebSearchPlan, WebSearchItem

plan = WebSearchPlan(
    searches=[
        WebSearchItem(reason="...", query="..."),
        WebSearchItem(reason="...", query="..."),
        # ... 3-5 total
    ]
)
```

---

### `ReportData`

Final comprehensive report.

**Fields:**
- `short_summary` (str): 2-3 sentence overview
- `markdown_report` (str): Full report (5-10 pages, 1000+ words)
- `follow_up_questions` (List[str]): Suggested further research

**Example:**
```python
from deep_research.models import ReportData

report = ReportData(
    short_summary="AI frameworks in 2025...",
    markdown_report="# Report\n\n## Introduction...",
    follow_up_questions=["How do costs compare?", "..."]
)
```

---

## UI Functions

### `create_ui() -> gr.Blocks`

Create the Gradio web interface.

**Returns:** Configured `gradio.Blocks` instance

**Example:**
```python
from deep_research.ui import create_ui

demo = create_ui()
demo.launch()
```

---

### `launch_ui(share: bool = False, server_port: int = 7860)`

Launch the Gradio interface.

**Parameters:**
- `share` (bool, default=False): Create public URL
- `server_port` (int, default=7860): Port number

**Returns:** None (blocks until server stops)

**Example:**
```python
from deep_research.ui import launch_ui

# Local only
launch_ui()

# Public URL
launch_ui(share=True)

# Custom port
launch_ui(server_port=8080)
```

---

## Tools

### `save_report_tool(report_content: str, query: str) -> Dict[str, str]`

Save report to disk.

**Parameters:**
- `report_content` (str): Markdown content
- `query` (str): Research query (for filename)

**Returns:**
```python
{
    "status": "success" | "error",
    "filepath": str,
    "message": str
}
```

**Example:**
```python
from deep_research.tools import save_report_tool

result = save_report_tool(
    report_content="# Report\n\n...",
    query="AI frameworks"
)

if result['status'] == 'success':
    print(f"Saved to: {result['filepath']}")
```

---

### `calculate_tool(expression: str) -> float | str`

Evaluate mathematical expression.

**Parameters:**
- `expression` (str): Math expression (e.g., "2 + 2", "100 / 4")

**Returns:** `float` - Result, or `str` - Error message

**Example:**
```python
from deep_research.tools import calculate_tool

result = calculate_tool("10 * 5")
print(result)  # 50.0

result = calculate_tool("100 / 0")
print(result)  # "Error: Division by zero"
```

---

## Environment Variables

### Required

```env
OPENAI_API_KEY=sk-proj-...
GMAIL_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@email.com
```

### Optional

```env
OPENAI_MODEL=gpt-4o-mini  # Default model
ENVIRONMENT=development   # deployment, production
```

---

## Error Codes

### Email Agent Responses

```python
{
    "status": "success",
    "message": "Email sent to user@email.com"
}

{
    "status": "blocked",
    "message": "Blocked by guardrails: High spam score: 85"
}

{
    "status": "error",
    "message": "SMTP failed: Authentication error"
}
```

---

## Type Hints

All functions include full type hints for IDE support:

```python
from typing import List, Dict
from deep_research.models import WebSearchPlan, ReportData

async def run(self, query: str) -> str: ...
async def plan_searches(self, query: str) -> WebSearchPlan: ...
async def perform_searches(self, plan: WebSearchPlan) -> List[str]: ...
async def write_report(self, query: str, results: List[str]) -> ReportData: ...
async def send_email(self, report: ReportData) -> Dict[str, str]: ...
```

---

## Complete Usage Example

```python
import asyncio
import os
from dotenv import load_dotenv
from deep_research import ResearchManager
from deep_research.models import WebSearchPlan

# Load environment
load_dotenv()

async def main():
    # Initialize
    manager = ResearchManager(
        api_key=os.getenv('OPENAI_API_KEY'),
        model="gpt-4o-mini"
    )
    
    # Run complete pipeline
    query = "Latest AI agent frameworks in 2025"
    
    try:
        # Option 1: Full pipeline
        report = await manager.run(query)
        print(f"✅ Complete! Trace: {manager.trace_url}")
        
        # Option 2: Step-by-step
        plan = await manager.plan_searches(query)
        results = await manager.perform_searches(plan)
        report_data = await manager.write_report(query, results)
        await manager.send_email(report_data)
        
        # Access data
        print(f"Summary: {report_data.short_summary}")
        print(f"Word count: {len(report_data.markdown_report.split())}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

# Run
asyncio.run(main())
```

---

For more details, see:
- [README.md](./README.md) - Getting started guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production setup
