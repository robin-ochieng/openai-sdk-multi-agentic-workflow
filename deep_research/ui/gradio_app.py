"""
Gradio Web Interface for Deep Research Agent
Provides simple UI for submitting research queries with real-time progress updates
"""

import gradio as gr
import asyncio
from datetime import datetime
from ..research_manager import ResearchManager


def create_ui():
    """
    Create and configure the Gradio web interface
    
    Returns:
        Configured Gradio Blocks interface
    """
    
    # Initialize research manager
    manager = ResearchManager()
    
    def format_log(message: str, emoji: str = "📌") -> str:
        """Format a log message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {emoji} {message}"
    
    async def run_research(query: str, progress=gr.Progress()):
        """
        Execute research and return results with real-time progress updates
        
        Args:
            query: Research query from user
            progress: Gradio progress tracker
            
        Yields:
            Tuple of (logs, markdown_report, trace_url)
        """
        logs = []
        
        if not query or len(query.strip()) < 5:
            yield (
                "❌ Please enter a valid research query (at least 5 characters)",
                "",
                ""
            )
            return
        

        
        try:
            # Initialize
            logs.append(format_log("🚀 Initializing Deep Research Agent...", "🚀"))
            logs.append(format_log(f"Query: {query}", "🔍"))
            logs.append(format_log("=" * 60, ""))
            yield ("\n".join(logs), "", "")
            
            progress(0, desc="Planning searches...")
            
            # Step 1: Plan searches
            logs.append(format_log("STEP 1: Planning Research Strategy", "🎯"))
            logs.append(format_log("Analyzing query and creating search plan...", "🧠"))
            yield ("\n".join(logs), "", "")
            
            search_plan = await manager.plan_searches(query)
            
            logs.append(format_log(f"✅ Created plan with {len(search_plan.searches)} searches:", "✅"))
            for i, search in enumerate(search_plan.searches, 1):
                logs.append(format_log(f"  {i}. {search.query}", "  🔎"))
                logs.append(format_log(f"     → {search.reason[:80]}...", ""))
            logs.append(format_log("=" * 60, ""))
            yield ("\n".join(logs), "", "")
            
            progress(0.25, desc="Performing web searches...")
            
            # Step 2: Perform searches
            logs.append(format_log("STEP 2: Performing Web Searches", "🌐"))
            yield ("\n".join(logs), "", "")
            
            search_results = await manager.perform_searches(search_plan)
            
            logs.append(format_log(f"✅ Completed {len(search_results)} searches", "✅"))
            for i, (search_item, result) in enumerate(zip(search_plan.searches, search_results), 1):
                logs.append(format_log(f"  {i}. {search_item.query} - {len(result)} chars", "  📄"))
            logs.append(format_log("=" * 60, ""))
            yield ("\n".join(logs), "", "")
            
            progress(0.5, desc="Writing comprehensive report...")
            
            # Step 3: Write report
            logs.append(format_log("STEP 3: Synthesizing Research Report", "✍️"))
            logs.append(format_log("Analyzing findings and creating report...", "📝"))
            yield ("\n".join(logs), "", "")
            
            report_data = await manager.write_report(query, search_results)
            
            logs.append(format_log(f"✅ Generated report: ~{len(report_data.markdown_report.split())} words", "✅"))
            logs.append(format_log(f"Report length: {len(report_data.markdown_report)} characters", "📊"))
            logs.append(format_log("=" * 60, ""))
            yield ("\n".join(logs), report_data.markdown_report, manager.trace_url or "")
            
            progress(0.75, desc="Sending email...")
            
            # Step 4: Send email
            logs.append(format_log("STEP 4: Sending Email", "📧"))
            logs.append(format_log("Converting to HTML and applying guardrails...", "🛡️"))
            yield ("\n".join(logs), report_data.markdown_report, manager.trace_url or "")
            
            email_result = await manager.send_email(
                query=query,
                report_data=report_data,
                recipient_email=None
            )
            
            # email_result is now a dict from the function_tool
            if isinstance(email_result, dict) and email_result.get('status') == 'success':
                logs.append(format_log(f"✅ {email_result.get('message', 'Email sent successfully')}", "✅"))
            elif isinstance(email_result, dict):
                logs.append(format_log(f"⚠️ {email_result.get('message', 'Email sending issue')}", "⚠️"))
            else:
                logs.append(format_log(f"⚠️ Unexpected email result format", "⚠️"))
            
            logs.append(format_log("=" * 60, ""))
            progress(1.0, desc="Complete!")
            
            # Final summary
            logs.append(format_log("🎉 RESEARCH COMPLETE!", "🎉"))
            logs.append(format_log(f"📊 Trace URL: {manager.trace_url}", "🔗"))
            logs.append(format_log(f"📧 Email sent to recipient", "✉️"))
            logs.append(format_log("=" * 60, ""))
            
            yield ("\n".join(logs), report_data.markdown_report, manager.trace_url or "")
            
        except Exception as e:
            logs.append(format_log(f"❌ ERROR: {str(e)}", "❌"))
            logs.append(format_log("Check trace URL for details", "🔍"))
            yield ("\n".join(logs), "", manager.trace_url or "")
    
    # Create Gradio interface
    with gr.Blocks(
        title="🔬 Deep Research Agent",
        theme=gr.themes.Soft()
    ) as demo:
        
        gr.Markdown(
            """
            # 🔬 Deep Research Agent
            
            ### AI-Powered Research System with 4-Agent Pipeline
            
            Enter your research query below and the system will:
            1. **Plan** strategic web searches (5 targeted queries)
            2. **Search** the web and summarize findings
            3. **Write** a comprehensive 5-10 page report (1000+ words)
            4. **Email** the professionally formatted report to your inbox
            
            ---
            """
        )
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(
                    label="🔍 Research Query",
                    placeholder="e.g., Latest AI Agent frameworks in 2025",
                    lines=3,
                    info="What would you like to research?"
                )
                
                submit_btn = gr.Button(
                    "🚀 Start Research",
                    variant="primary",
                    size="lg"
                )
                
            with gr.Column(scale=1):
                gr.Markdown(
                    """
                    ### 📊 Features
                    
                    ✅ **4-Agent Pipeline**
                    - Planner Agent
                    - Search Agent  
                    - Writer Agent
                    - Email Agent
                    
                    ✅ **Structured Outputs**
                    - Type-safe Pydantic models
                    - Validated responses
                    
                    ✅ **Guardrails Protected**
                    - Spam detection
                    - Rate limiting
                    - Content safety
                    
                    ✅ **OpenAI Traces**
                    - Full transparency
                    - Debug visibility
                    """
                )
        
        gr.Markdown("---")
        
        # Progress logs - prominently displayed
        with gr.Accordion("📊 Live Progress & Logs", open=True):
            logs_output = gr.Textbox(
                label="Real-time Execution Logs",
                placeholder="Logs will appear here as the agent works...",
                interactive=False,
                lines=20,
                max_lines=30,
                show_copy_button=True
            )
        
        gr.Markdown("---")
        
        with gr.Tabs():
            with gr.Tab("📄 Report Preview"):
                report_output = gr.Markdown(
                    label="Generated Report",
                    value="*Report will appear here after research completes...*"
                )
            
            with gr.Tab("🔗 Trace Link"):
                trace_output = gr.Textbox(
                    label="OpenAI Trace URL",
                    placeholder="Trace URL will appear here...",
                    interactive=False,
                    show_copy_button=True
                )
                gr.Markdown(
                    """
                    **📊 View Execution Trace:**
                    Click the trace URL above to see detailed execution logs on OpenAI's platform.
                    This shows all agent interactions, tool calls, and reasoning steps.
                    """
                )
        
        gr.Markdown(
            """
            ---
            
            ### 📧 Email Delivery
            
            The comprehensive report will be delivered to: `{}`
            
            **What to expect:**
            - Professional HTML formatting
            - Complete research findings
            - Follow-up research suggestions
            - Sent via Gmail SMTP with guardrails protection
            
            ---
            
            *Powered by OpenAI SDK Agents | Built with Guardrails & Structured Outputs*
            """.format(
                "RECIPIENT_EMAIL (from .env)"
            )
        )
        
        # Connect button to function
        submit_btn.click(
            fn=run_research,
            inputs=[query_input],
            outputs=[logs_output, report_output, trace_output],
            api_name="research"
        )
        
        # Example queries
        gr.Examples(
            examples=[
                ["Latest AI Agent frameworks in 2025"],
                ["Impact of large language models on software development"],
                ["Current state of autonomous AI agents"],
                ["OpenAI Agents SDK vs LangChain comparison"],
                ["Best practices for building multi-agent systems"]
            ],
            inputs=query_input,
            label="💡 Example Queries"
        )
    
    return demo


def launch_ui(share: bool = False, server_port: int = 7860):
    """
    Launch the Gradio web interface
    
    Args:
        share: Create public URL (default: False)
        server_port: Port to run server on (default: 7860)
    """
    demo = create_ui()
    demo.launch(
        share=share,
        server_port=server_port,
        inbrowser=True
    )


if __name__ == "__main__":
    launch_ui()
