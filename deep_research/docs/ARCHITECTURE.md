# 🏗️ Architecture Deep Dive

## System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Gradio Web UI                          │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Query Input │  │ Status Panel │  │ Report View  │       │
│  └──────┬──────┘  └──────────────┘  └──────────────┘       │
└─────────┼───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Research Manager                          │
│  • Orchestrates 4-agent pipeline                            │
│  • Manages async execution                                  │
│  • Tracks progress and traces                               │
└─────────┬───────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Pipeline                            │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ [1] Planner Agent                                   │    │
│  │     • Input: User query (string)                    │    │
│  │     • Output: WebSearchPlan (5 searches)            │    │
│  │     • Model: gpt-4o-mini                            │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                              │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │ [2] Search Agent (×5 parallel)                      │    │
│  │     • Input: WebSearchItem                          │    │
│  │     • Tool: WebSearchTool (hosted by OpenAI)        │    │
│  │     • Output: String summary (<300 words)           │    │
│  │     • Parallel execution with asyncio               │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                              │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │ [3] Writer Agent                                    │    │
│  │     • Input: Query + all search summaries           │    │
│  │     • Process: Create outline → Write report        │    │
│  │     • Output: ReportData (markdown, 1000+ words)    │    │
│  │     • Model: gpt-4o-mini                            │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │                                              │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │ [4] Email Agent                                     │    │
│  │     • Input: ReportData.markdown_report             │    │
│  │     • Tool: send_email (function_tool)              │    │
│  │     • Process: MD → HTML → Validate → Send          │    │
│  │     • Output: Email confirmation                    │    │
│  └────────────┬───────────────────────────────────────┘    │
└───────────────┼──────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              Gmail SMTP + Guardrails                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ Guardrails Validation Pipeline                      │    │
│  │  1. Spam score check (0-100 scale)                  │    │
│  │  2. Email format validation                         │    │
│  │  3. Content safety checks                           │    │
│  │  4. Rate limit enforcement                          │    │
│  │  5. Personalization warnings                        │    │
│  └────────────┬───────────────────────────────────────┘    │
│               │ ✅ Pass                                      │
│  ┌────────────▼───────────────────────────────────────┐    │
│  │ Gmail SMTP Sender                                   │    │
│  │  • TLS encryption                                   │    │
│  │  • Retry logic (3 attempts)                         │    │
│  │  • HTML email support                               │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
          📧 Inbox Delivery
```

---

## Component Details

### 1. Planner Agent

**Purpose**: Analyze user query and create strategic search plan

**Input Schema**:
```python
input: str  # User's research query
```

**Output Schema** (Pydantic):
```python
class WebSearchPlan(BaseModel):
    searches: List[WebSearchItem] = Field(
        min_items=3,
        max_items=5
    )

class WebSearchItem(BaseModel):
    reason: str  # Why this search matters
    query: str   # Search term
```

**Agent Configuration**:
```python
Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=WebSearchPlan,  # Structured output
)
```

**Key Features**:
- Structured output enforcement via Pydantic
- Reasons about search importance
- Generates 3-5 diverse, targeted queries
- No tools required (pure reasoning)

**Example Output**:
```json
{
  "searches": [
    {
      "reason": "Need to understand current market landscape",
      "query": "AI agent frameworks 2025 market overview"
    },
    {
      "reason": "Technical comparison is essential",
      "query": "OpenAI Agents SDK vs LangChain comparison"
    }
    // ... 3 more
  ]
}
```

---

### 2. Search Agent

**Purpose**: Execute web searches and summarize findings

**Input Schema**:
```python
input: str  # "Search term: {query}\nReason: {reason}"
```

**Output Schema**:
```python
output: str  # Plain text summary (2-3 paragraphs, <300 words)
```

**Tools**:
- `WebSearchTool(search_context_size="low")` - OpenAI hosted tool

**Agent Configuration**:
```python
Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
    model_settings=ModelSettings(tool_choice="required"),
)
```

**Execution Pattern**:
```python
# Parallel execution with asyncio
tasks = [
    asyncio.create_task(search(item))
    for item in plan.searches
]
results = await asyncio.gather(*tasks)
```

**Key Features**:
- Parallel execution (5 searches simultaneously)
- Tool choice = "required" (must use WebSearchTool)
- Concise summaries (no fluff)
- Captures essence, not complete sentences

**Example Output**:
```
OpenAI Agents SDK released December 2024. Key features: multi-agent
orchestration, built-in tools (web search, code interpreter), structured
outputs via Pydantic. Compared to LangChain: simpler API, native OpenAI
integration, but less ecosystem maturity. Early adopters report 60%
faster development time. Main limitation: OpenAI-only, no local model
support. Best for: production apps needing reliability over flexibility.
```

---

### 3. Writer Agent

**Purpose**: Synthesize search results into comprehensive report

**Input Schema**:
```python
input: str  # "Original query: {query}\n\nSearch results: {results}"
```

**Output Schema** (Pydantic):
```python
class ReportData(BaseModel):
    short_summary: str  # 2-3 sentences
    markdown_report: str  # 5-10 pages, 1000+ words
    follow_up_questions: List[str]  # Suggested research
```

**Agent Configuration**:
```python
Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o-mini",
    output_type=ReportData,  # Structured output
)
```

**Process**:
1. Analyze all search summaries
2. Create outline (structure and flow)
3. Write comprehensive report in markdown
4. Generate follow-up questions
5. Return structured ReportData

**Key Features**:
- Structured output with 3 fields
- Markdown formatting
- 1000+ word target
- Synthesis, not just concatenation
- Includes next research steps

**Example Output**:
```python
{
  "short_summary": "AI agent frameworks in 2025 are dominated by...",
  "markdown_report": """
# AI Agent Frameworks in 2025: Comprehensive Analysis

## Executive Summary
...

## Market Overview
...

## Technical Comparison
...
""",
  "follow_up_questions": [
    "How do costs compare across frameworks?",
    "What are production deployment patterns?"
  ]
}
```

---

### 4. Email Agent

**Purpose**: Convert report to HTML and send via Gmail SMTP

**Input Schema**:
```python
input: str  # markdown_report from WriterAgent
```

**Tools**:
```python
@function_tool
def send_email(subject: str, html_body: str) -> Dict[str, str]:
    # 1. Initialize Gmail sender
    # 2. Run guardrails validation
    # 3. Send via SMTP if passed
    # 4. Record send for rate limiting
```

**Agent Configuration**:
```python
Agent(
    name="EmailAgent",
    instructions=INSTRUCTIONS,
    tools=[send_email],
    model="gpt-4o-mini",
)
```

**Process**:
1. Convert markdown to clean HTML
2. Add professional styling
3. Generate appropriate subject line
4. Call send_email tool
5. Tool validates with guardrails
6. Send via Gmail SMTP if passed

**Guardrails Integration**:
```python
# Inside send_email function_tool
validation = guardrails.run_all_checks(
    subject=subject,
    body=html_body,
    recipient_email=recipient
)

if not validation['passed']:
    return {"status": "blocked", "message": ...}

# Proceed with sending
sender.send_html_email(...)
guardrails.record_send()  # Track for rate limiting
```

---

## Data Flow

### Complete Pipeline Data Flow

```python
# Input
user_query: str = "Latest AI frameworks in 2025"

# Step 1: Planner
planner_output: WebSearchPlan = {
    "searches": [
        {"reason": "...", "query": "AI frameworks 2025"},
        # ... 4 more
    ]
}

# Step 2: Search (×5 parallel)
search_results: List[str] = [
    "OpenAI Agents SDK...",
    "LangChain ecosystem...",
    "AutoGen framework...",
    "CrewAI multi-agent...",
    "Microsoft Semantic Kernel..."
]

# Step 3: Writer
report: ReportData = {
    "short_summary": "AI frameworks in 2025...",
    "markdown_report": "# Report\n\n## Intro...",
    "follow_up_questions": ["...", "..."]
}

# Step 4: Email
email_result: Dict = {
    "status": "success",
    "message": "Email sent to user@email.com"
}
```

---

## Async Execution

### Research Manager Async Pattern

```python
async def run(self, query: str) -> str:
    # Create trace
    trace_id = get_trace_id()
    
    with trace("Research trace", trace_id=trace_id):
        # Sequential steps
        plan = await self.plan_searches(query)
        
        # Parallel searches
        results = await asyncio.gather(*[
            self.search(item) for item in plan.searches
        ])
        
        # Sequential synthesis
        report = await self.write_report(query, results)
        
        # Sequential email
        await self.send_email(report)
    
    return report.markdown_report
```

**Why Async?**
- Parallel web searches (5× faster)
- Non-blocking UI updates
- Efficient resource usage
- Better user experience

---

## Error Handling

### Guardrails Error Flow

```python
# In email_agent.py send_email tool
try:
    validation = guardrails.run_all_checks(...)
    
    if not validation['passed']:
        # Soft failure - blocked by guardrails
        return {
            "status": "blocked",
            "message": f"Blocked: {validation['blocking_issues']}"
        }
    
    result = sender.send_html_email(...)
    
    if not result.get('success'):
        # SMTP error
        return {
            "status": "error",
            "message": f"SMTP failed: {result.get('message')}"
        }
    
    # Success
    guardrails.record_send()
    return {"status": "success", ...}
    
except Exception as e:
    # Hard failure - unexpected error
    return {
        "status": "error",
        "message": f"Exception: {str(e)}"
    }
```

### Retry Logic

Gmail sender includes retry logic:
```python
for attempt in range(1, max_retries + 1):
    try:
        server.send_message(msg)
        return  # Success
    except Exception as e:
        if attempt < max_retries:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
        else:
            raise SendFailureError(...)
```

---

## Tracing & Monitoring

### OpenAI Trace Structure

```python
with trace("Research trace", trace_id=trace_id):
    # All agent runs are captured
    
    # Planner
    with trace("Plan searches"):
        result = await Runner.run(planner, query)
    
    # Searches (parallel)
    with trace("Perform searches"):
        for item in plan.searches:
            with trace(f"Search: {item.query}"):
                await Runner.run(search_agent, item)
    
    # Writer
    with trace("Write report"):
        await Runner.run(writer, data)
    
    # Email
    with trace("Send email"):
        await Runner.run(email_agent, report)
```

**Trace URL**:
```
https://platform.openai.com/traces/trace?trace_id={trace_id}
```

**What's Captured**:
- All LLM calls and responses
- Tool invocations
- Token usage
- Latency metrics
- Error details
- Reasoning steps

---

## Scalability Considerations

### Current Limits
- **Search parallelization**: 5 concurrent (can increase)
- **Rate limiting**: 50/hour, 500/day (email sending)
- **Report length**: 1000+ words (can adjust)
- **Model**: gpt-4o-mini (fast, cost-effective)

### Scaling Options

**1. Increase Search Count**
```python
# In planner_agent.py
HOW_MANY_SEARCHES = 10  # More comprehensive research
```

**2. Use GPT-4 for Quality**
```python
manager = ResearchManager(model="gpt-4o")
```

**3. Add Caching**
```python
# Cache search results to avoid re-searching
from functools import lru_cache

@lru_cache(maxsize=100)
async def cached_search(query: str):
    return await self.search(query)
```

**4. Batch Processing**
```python
# Process multiple queries
queries = ["Query 1", "Query 2", ...]
results = await asyncio.gather(*[
    manager.run(q) for q in queries
])
```

---

## Security

### API Key Management
- Stored in `.env` file (not committed)
- Loaded via `python-dotenv`
- Never hardcoded

### Email Security
- Gmail App Password (not regular password)
- TLS encryption for SMTP
- Guardrails prevent abuse
- Rate limiting protects reputation

### Input Validation
- Pydantic models validate all data
- Type checking at runtime
- No SQL injection (no database)
- Web search via trusted OpenAI tool

---

## Performance

### Typical Execution Times

| Stage | Duration | Notes |
|-------|----------|-------|
| Planning | 2-5s | Single LLM call |
| Searching | 15-30s | 5 parallel searches |
| Writing | 20-40s | Long-form generation |
| Emailing | 2-5s | SMTP + validation |
| **Total** | **40-80s** | Full pipeline |

### Optimization Opportunities

1. **Reduce search count**: 3 instead of 5 (faster)
2. **Use streaming**: Show progress in real-time
3. **Cache results**: Avoid duplicate searches
4. **Smaller model**: gpt-3.5-turbo (cheaper, faster)

---

This architecture is designed for **modularity, reliability, and extensibility**. Each component can be modified independently without affecting the entire system.
