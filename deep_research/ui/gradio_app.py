"""
Gradio Web Interface for Deep Research Agent
Provides simple UI for submitting research queries
"""

import gradio as gr
import asyncio
from ..research_manager import ResearchManager


def create_ui():
    """
    Create and configure the Gradio web interface
    
    Returns:
        Configured Gradio Blocks interface
    """
    
    # Initialize research manager
    manager = ResearchManager()
    
    async def run_research(query: str) -> tuple:
        """
        Execute research and return results
        
        Args:
            query: Research query from user
            
        Returns:
            Tuple of (status_message, markdown_report, trace_url)
        """
        if not query or len(query.strip()) < 5:
            return (
                "❌ Please enter a valid research query (at least 5 characters)",
                "",
                ""
            )
        
        try:
            # Run the research pipeline
            report = await manager.run(query)
            
            status = f"✅ Research complete! Report sent to {manager.current_status}"
            
            return (status, report, manager.trace_url)
            
        except Exception as e:
            error_msg = f"❌ Error during research: {str(e)}"
            return (error_msg, "", "")
    
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
        
        status_output = gr.Textbox(
            label="📌 Status",
            interactive=False,
            lines=2
        )
        
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
                    interactive=False
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
            outputs=[status_output, report_output, trace_output],
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
