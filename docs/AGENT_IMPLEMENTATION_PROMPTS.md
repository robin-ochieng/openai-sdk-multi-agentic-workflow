# Agent Enhancement Implementation Prompts

> Use these prompts directly with GitHub Copilot Chat (or another AI pair-programmer) to implement the four-phase Agent Enhancements Roadmap. Each prompt is engineered to provide clear context, deliverables, and acceptance criteria so the assistant can generate production-quality code.

---

## Phase 1 – Foundation & Governance

### Prompt 1: Query Analyzer Agent
```
You are updating the deep_research project (Python, FastAPI, OpenAI SDK). Implement a QueryAnalyzerAgent and related Pydantic models under deep_research/research_agents/ so every research request is classified before planning. Requirements:
1. The agent inspects user queries and returns structured data: query_type, complexity, time_sensitivity, primary_entities, secondary_entities, geographic_scope, time_range, audience_level, required_depth, recommended_sections, required_data_points, visualization_opportunities, estimated_research_time, recommended_search_count.
2. Add a QueryAnalysis schema under deep_research/models.py (or a new models/query_analysis.py) that enforces enums and optional fields.
3. Update ResearchManager so plan_searches() accepts the analysis output and forwards context to planner/search agents.
4. Include logging and docstrings that explain how to extend classifications.
5. Provide unit tests or doc tests covering at least two query examples.
```

### Prompt 2: Source Validator Agent
```
In deep_research, add a SourceValidatorAgent (deep_research/research_agents/source_validator_agent.py) that scores each source before the writer uses it. Requirements:
1. Accept source metadata (url, title, snippet, publication_date) and produce SourceCredibility with scores for authority, recency, objectivity, corroboration, plus overall score (0-100) and include/exclude recommendation.
2. Maintain allow/deny lists of domains; load defaults from JSON (deep_research/config/source_domains.json) and gracefully handle missing files.
3. Integrate with ResearchManager.perform_searches(): after each search, validate sources and discard those flagged “exclude” while tagging surviving ones with score badges.
4. Emit structured logs showing reason for exclusion.
5. Add tests covering high-quality, outdated, and suspicious domains.
```

### Prompt 3: Enhanced Writer Wiring
```
Refactor writer_agent integration so ReportData captures metadata from QueryAnalysis and SourceValidator. Steps:
1. Extend ReportData in deep_research/models/report_models.py with fields: query_analysis (optional), source_metrics (avg score, count, distribution), and planning_notes.
2. Ensure writer_agent receives query_analysis + validated source summaries to influence structure.
3. Update report_formatter.py to surface source credibility badges and a short “Methodology & Source Quality” section in every report.
4. Add regression tests ensuring new fields serialize and render correctly.
```

---

## Phase 2 – Specialized Research Pipelines

### Prompt 4: Academic Research Agent
```
Create AcademicResearchAgent in deep_research/research_agents/academic_agent.py. Responsibilities:
1. Use Semantic Scholar (mock or real API) to fetch peer-reviewed papers; fall back to WebSearchTool when API unavailable.
2. Return AcademicSource objects capturing title, authors, venue, year, citation_count, doi, summary, relevance_score.
3. Provide filtering by year range, minimum citations, and fields of study.
4. Add a dispatcher in ResearchManager so QueryAnalysis decides when to invoke academic research and merge results with standard search outputs.
5. Include unit tests with fixtures for API responses.
```

### Prompt 5: Market Intelligence Agent
```
Implement MarketIntelligenceAgent (deep_research/research_agents/market_agent.py) with these behaviors:
1. Aggregate data from public filings (SEC 10-K via sec-api, stub acceptable) and trusted market blogs; parse revenue, growth rate, TAM/SAM/SOM estimates.
2. Generate MarketSnapshot objects containing key metrics, competitor list, pricing benchmarks, and risk notes.
3. Ensure ResearchManager routes relevant queries (query_type == "market_research" or "competitive_analysis") through this agent and attaches outputs to DataSynthesizer later.
4. Cover parsing logic with tests using sample filing text.
```

### Prompt 6: News Intelligence + Fact Checker
```
Add NewsIntelligenceAgent and FactCheckerAgent:
- News agent (deep_research/research_agents/news_agent.py) aggregates real-time news via WebSearchTool with focus on timelines; output chronological events with sentiment and source score.
- FactChecker (deep_research/research_agents/fact_checker_agent.py) scans drafted markdown, extracts factual claims, cross-checks against validated sources, and annotates with confidence (verified/uncertain/disputed).
Integrate both into ResearchManager.write_report(): before final formatting, run fact checker and inject a "Verification Status" section summarizing claim counts.
```

---

## Phase 3 – Data & Presentation Layer

### Prompt 7: Data Synthesizer & Chart Generator
```
Add two new modules:
1. DataSynthesizerAgent (deep_research/research_agents/data_synthesizer_agent.py) that converts search outputs into structured datasets (time_series, comparisons, geographic, key_stats). Support unit conversions and deduplication.
2. ChartGeneratorAgent (deep_research/research_agents/chart_generator_agent.py) that accepts synthesized data and emits Chart.js + Vega-Lite spec dictionaries, plus SVG snapshots for PDF export.
Update ReportData to include chart_specs and embed charts in frontend + PDF exports.
```

### Prompt 8: Editor Agent
```
Implement EditorAgent (deep_research/research_agents/editor_agent.py) to polish markdown:
1. Enforce section order (Executive Summary → Introduction → ... → References) and ensure single occurrences of critical headings.
2. Improve readability (target Flesch 55-65) using heuristics and optional LanguageTool integration.
3. Add callouts for recommendations, highlight key metrics, and ensure executive summary hits 200-300 words.
4. Integrate post writer_agent but pre fact_checker to reduce downstream churn.
```

### Prompt 9: PDF/Word Export Enhancements
```
Upgrade services/export/ so PDF and DOCX exports can embed charts and infographics:
1. Extend pdf_generator.py to accept chart SVGs and stat cards from ChartGeneratorAgent.
2. Create docx_generator.py using python-docx with branded headers/footers, tables of key metrics, and dynamic table of figures.
3. Add configuration for client branding (logo, color palette) loaded from yaml.
4. Write integration tests ensuring generated files include at least one chart and the Methodology section.
```

---

## Phase 4 – Advanced Intelligence & Templates

### Prompt 10: Patent & Expert Agents
```
Introduce PatentResearchAgent and ExpertOpinionAgent:
1. Patent agent queries Lens.org/Google Patents (mock acceptable) returning patent families, assignees, IPC codes, and novelty notes.
2. Expert agent mines thought-leader quotes (structured list of quote, expert, credential, sentiment) via curated RSS/LinkedIn scraping stubs.
3. Update ResearchManager to append these sections when QueryAnalysis indicates due_diligence, trend_analysis, or technology focus.
```

### Prompt 11: Industry Template Registry
```
Create deep_research/templates/registry.py defining reusable templates (tech analysis, market research, due diligence, competitive intelligence, industry trends). Each template lists required sections, mandatory visuals, and data fields.
Modify writer_agent to select a template based on QueryAnalysis and enforce missing sections at post-processing time.
```

### Prompt 12: Citation Manager & QA Gate
```
Build CitationManagerAgent (deep_research/research_agents/citation_manager_agent.py) capable of formatting APA/Chicago/IEEE references, resolving DOIs, and ensuring in-text citations match bibliography entries. Add QualityAssurancePipeline that verifies structure, citations, readability, and source coverage before final delivery. If QA fails, loop back to EditorAgent with remediation notes.
```

---

**Usage Tip:** Paste each prompt into Copilot Chat while positioned inside the repository. After receiving code suggestions, review diffs, add tests, and run the existing automation before committing.
