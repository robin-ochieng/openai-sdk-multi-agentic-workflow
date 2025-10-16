"""
Quick Start Example - Deep Research Agent
Run this to see the system in action
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def example_1_full_pipeline():
    """Example 1: Run complete research pipeline"""
    from deep_research import ResearchManager
    
    print("\n" + "="*60)
    print("EXAMPLE 1: Full Research Pipeline")
    print("="*60)
    
    # Initialize manager
    manager = ResearchManager()
    
    # Run research
    query = "Latest AI Agent frameworks in 2025"
    print(f"\nQuery: {query}")
    
    report = await manager.run(query)
    
    print(f"\n✅ Complete!")
    print(f"📊 Trace: {manager.trace_url}")
    print(f"📧 Check your email: {os.getenv('RECIPIENT_EMAIL')}")
    print(f"\nReport preview (first 500 chars):")
    print(report[:500] + "...")


async def example_2_step_by_step():
    """Example 2: Step-by-step execution with inspection"""
    from deep_research import ResearchManager
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Step-by-Step Execution")
    print("="*60)
    
    manager = ResearchManager()
    query = "Impact of large language models on software development"
    
    # Step 1: Plan
    print("\n[STEP 1] Planning searches...")
    plan = await manager.plan_searches(query)
    print(f"✅ Planned {len(plan.searches)} searches:")
    for i, search in enumerate(plan.searches, 1):
        print(f"   {i}. {search.query}")
        print(f"      → {search.reason}")
    
    # Step 2: Search
    print("\n[STEP 2] Performing searches...")
    results = await manager.perform_searches(plan)
    print(f"✅ Collected {len(results)} summaries")
    print(f"\nFirst summary preview:")
    print(results[0][:200] + "...")
    
    # Step 3: Write
    print("\n[STEP 3] Writing report...")
    report = await manager.write_report(query, results)
    print(f"✅ Report written:")
    print(f"   Summary: {report.short_summary}")
    print(f"   Length: {len(report.markdown_report)} characters")
    print(f"   Follow-ups: {len(report.follow_up_questions)} questions")
    
    # Step 4: Email
    print("\n[STEP 4] Sending email...")
    email_result = await manager.send_email(report)
    print(f"✅ Email status: {email_result}")


async def example_3_custom_model():
    """Example 3: Using different model"""
    from deep_research import ResearchManager
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Custom Model Configuration")
    print("="*60)
    
    # Use GPT-4 for higher quality (more expensive)
    manager = ResearchManager(model="gpt-4o")
    
    query = "Best practices for building multi-agent systems"
    print(f"\nQuery: {query}")
    print(f"Model: GPT-4o (higher quality)")
    
    report = await manager.run(query)
    print(f"\n✅ Complete! High-quality report generated.")


async def example_4_individual_agents():
    """Example 4: Using individual agents directly"""
    from deep_research.agents import create_planner_agent
    from openai.lib._agents import Runner
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Using Individual Agents")
    print("="*60)
    
    # Create just the planner agent
    planner = create_planner_agent(
        api_key=os.getenv('OPENAI_API_KEY'),
        model="gpt-4o-mini"
    )
    
    # Run it directly
    query = "Autonomous AI agents in robotics"
    result = await Runner.run(planner, f"Query: {query}")
    
    print(f"\nPlanner output:")
    for i, search in enumerate(result.final_output.searches, 1):
        print(f"\n{i}. Query: {search.query}")
        print(f"   Reason: {search.reason}")


def example_5_gradio_ui():
    """Example 5: Launch Gradio web interface"""
    from deep_research.ui import launch_ui
    
    print("\n" + "="*60)
    print("EXAMPLE 5: Gradio Web Interface")
    print("="*60)
    
    print("\nLaunching web interface...")
    print("Navigate to http://localhost:7860")
    print("Press Ctrl+C to stop\n")
    
    launch_ui(share=False, server_port=7860)


async def run_all_examples():
    """Run all async examples"""
    # Example 1: Full pipeline
    await example_1_full_pipeline()
    
    # Wait a bit
    print("\n" + "="*60)
    input("Press Enter to continue to Example 2...")
    
    # Example 2: Step-by-step
    await example_2_step_by_step()
    
    # Example 3 and 4 commented out to save API calls
    # Uncomment to try them:
    
    # print("\n" + "="*60)
    # input("Press Enter to continue to Example 3...")
    # await example_3_custom_model()
    
    # print("\n" + "="*60)
    # input("Press Enter to continue to Example 4...")
    # await example_4_individual_agents()


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         🔬 DEEP RESEARCH AGENT - QUICK START EXAMPLES       ║
╚══════════════════════════════════════════════════════════════╝

Choose an example to run:

1. Full Research Pipeline (complete workflow)
2. Step-by-Step Execution (see each stage)
3. Custom Model Configuration (use GPT-4)
4. Individual Agent Usage (planner only)
5. Gradio Web Interface (visual UI)
6. Run All Examples (1 & 2)

""")
    
    choice = input("Enter choice (1-6): ").strip()
    
    if choice == "1":
        asyncio.run(example_1_full_pipeline())
    elif choice == "2":
        asyncio.run(example_2_step_by_step())
    elif choice == "3":
        asyncio.run(example_3_custom_model())
    elif choice == "4":
        asyncio.run(example_4_individual_agents())
    elif choice == "5":
        example_5_gradio_ui()
    elif choice == "6":
        asyncio.run(run_all_examples())
    else:
        print("Invalid choice. Run the script again.")
        return
    
    print("\n" + "="*60)
    print("✅ Example complete!")
    print("="*60)
    print("\nNext steps:")
    print("• Check your email for the report")
    print("• View the trace URL for execution details")
    print("• Try modifying the query")
    print("• Run different examples")
    print("\nFor more info, see deep_research/docs/README.md")


if __name__ == "__main__":
    main()
