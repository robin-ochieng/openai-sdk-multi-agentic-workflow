"""
OpenAI SDK Sales Agent System
An automated cold email generation and delivery system using multiple AI agents
"""

# Core imports
from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
import os
from sendgrid.helpers.mail import Mail, Email, To, Content
import asyncio

# Load environment variables from .env file
load_dotenv(override=True)


# ============================================================================
# EMAIL TESTING
# ============================================================================

def send_test_email():
    """Test SendGrid email functionality - use this first to verify setup"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDER_EMAIL', 'your_email@example.com'))
    to_email = To(os.environ.get('RECIPIENT_EMAIL', 'recipient@example.com'))
    content = Content("text/plain", "This is an important test email")
    mail = Mail(from_email, to_email, "Test email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"SendGrid response status: {response.status_code}")
    return response.status_code


# ============================================================================
# AGENT INSTRUCTIONS - Customize these for your company
# ============================================================================

# Agent 1: Professional and formal tone
instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

# Agent 2: Engaging and witty tone
instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

# Agent 3: Brief and concise tone
instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."


# ============================================================================
# AGENT DEFINITIONS - Three different writing styles
# ============================================================================

# Create sales agent 1: Professional style
sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini"
)

# Create sales agent 2: Engaging style
sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini"
)

# Create sales agent 3: Concise style
sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini"
)


# ============================================================================
# DEMO FUNCTIONS
# ============================================================================

async def demo_streamed_response():
    """Demo: Stream a single email response token-by-token in real-time"""
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    # Print each token as it's generated
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


async def generate_parallel_emails():
    """Generate emails from all three agents simultaneously for speed"""
    message = "Write a cold sales email"
    
    # Run all three agents at the same time (parallel execution)
    with trace("Parallel cold emails"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
    
    # Extract the final outputs from each agent
    outputs = [result.final_output for result in results]
    
    # Display all generated emails
    for output in outputs:
        print(output + "\n\n")
    
    return outputs


# ============================================================================
# EMAIL SELECTION AGENT
# ============================================================================

# Agent that picks the best email from multiple options
sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only.",
    model="gpt-4o-mini"
)


async def select_best_email():
    """Generate multiple emails and use AI to select the best one"""
    message = "Write a cold sales email"
    
    # Generate emails from all three agents and pick the winner
    with trace("Selection from sales people"):
        # Step 1: Generate all emails in parallel
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )
        outputs = [result.final_output for result in results]

        # Step 2: Format emails for comparison
        emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)

        # Step 3: Use sales_picker agent to select the best
        best = await Runner.run(sales_picker, emails)

        print(f"Best sales email:\n{best.final_output}")
        return best.final_output


# ============================================================================
# TOOLS - Convert agents to tools for collaboration
# ============================================================================

# Recreate agents for use with tools
sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini",
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini",
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini",
)


# ============================================================================
# EMAIL SENDING TOOLS
# ============================================================================

@function_tool
def send_email(body: str):
    """Send out a plain text email - callable as a tool by agents"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDER_EMAIL', 'your_email@example.com'))
    to_email = To(os.environ.get('RECIPIENT_EMAIL', 'recipient@example.com'))
    content = Content("text/plain", body)
    mail = Mail(from_email, to_email, "Sales email", content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"Email sent! Status: {response.status_code}")
    return {"status": "success", "status_code": response.status_code}


# Convert agents to tools so other agents can use them
description = "Write a cold sales email"

tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

# Combine agent tools with email sending tool
tools = [tool1, tool2, tool3, send_email]


# ============================================================================
# SALES MANAGER AGENT
# ============================================================================

# Instructions for the sales manager (orchestrator)
instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
 
3. Use the send_email tool to send the best email (and only the best email) to the user.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must send ONE email using the send_email tool — never more than one.
"""

# Create the sales manager with access to all agent tools
sales_manager = Agent(name="Sales Manager", instructions=instructions, tools=tools, model="gpt-4o-mini")


async def run_sales_manager():
    """Run the sales manager workflow: generate, select, and send email"""
    message = "Send a cold sales email addressed to 'Dear CEO'"
    
    # Execute sales manager with OpenAI tracing enabled
    with trace("Sales manager"):
        result = await Runner.run(sales_manager, message)
        return result


# ============================================================================
# HTML EMAIL FORMATTING AGENTS
# ============================================================================

# Agent to generate compelling subject lines
subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

# Agent to convert plain text to HTML format
html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

# Create subject writer agent and convert to tool
subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

# Create HTML converter agent and convert to tool
html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")


@function_tool
def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send out a formatted HTML email with subject line - callable as a tool"""
    sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email(os.environ.get('SENDER_EMAIL', 'your_email@example.com'))
    to_email = To(os.environ.get('RECIPIENT_EMAIL', 'recipient@example.com'))
    content = Content("text/html", html_body)
    mail = Mail(from_email, to_email, subject, content).get()
    response = sg.client.mail.send.post(request_body=mail)
    print(f"HTML Email sent! Subject: {subject}, Status: {response.status_code}")
    return {"status": "success", "status_code": response.status_code, "subject": subject}


# Tools for the email formatter agent
tools = [subject_tool, html_tool, send_html_email]

# Email formatter agent instructions
instructions ="You are an email formatter and sender. You receive the body of an email to be sent. \
You first use the subject_writer tool to write a subject for the email, then use the html_converter tool to convert the body to HTML. \
Finally, you use the send_html_email tool to send the email with the subject and HTML body."


# ============================================================================
# EMAIL MANAGER AGENT (with handoffs)
# ============================================================================

# Create the email formatting/sending agent
emailer_agent = Agent(
    name="Email Manager",
    instructions=instructions,
    tools=tools,
    model="gpt-4o-mini",
    handoff_description="Convert an email to HTML and send it")

# Tools and handoffs for the automated SDR
tools = [tool1, tool2, tool3]  # Three sales agents as tools
handoffs = [emailer_agent]     # Email manager for handoff

# Full automated SDR instructions
sales_manager_instructions = """
You are a Sales Manager at ComplAI. Your goal is to find the single best cold sales email using the sales_agent tools.
 
Follow these steps carefully:
1. Generate Drafts: Use all three sales_agent tools to generate three different email drafts. Do not proceed until all three drafts are ready.
 
2. Evaluate and Select: Review the drafts and choose the single best email using your judgment of which one is most effective.
You can use the tools multiple times if you're not satisfied with the results from the first try.
 
3. Handoff for Sending: Pass ONLY the winning email draft to the 'Email Manager' agent. The Email Manager will take care of formatting and sending.
 
Crucial Rules:
- You must use the sales agent tools to generate the drafts — do not write them yourself.
- You must hand off exactly ONE email to the Email Manager — never more than one.
"""

# Create the full automated SDR sales manager
sales_manager = Agent(
    name="Sales Manager",
    instructions=sales_manager_instructions,
    tools=tools,
    handoffs=handoffs,
    model="gpt-4o-mini")


async def run_automated_sdr():
    """🚀 Run the full automated SDR: generate, select, format, and send email"""
    message = "Send out a cold sales email addressed to Dear CEO from Alice"
    
    # Execute with OpenAI tracing for visibility
    with trace("Automated SDR"):
        result = await Runner.run(sales_manager, message)
        return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function to run the sales automation system"""
    print("=" * 60)
    print("OpenAI SDK Sales Agent System")
    print("=" * 60)
    
    # 📝 INSTRUCTIONS: Uncomment ONE function below to run it
    # Start with #1 to test your setup, then try the others!
    
    # 1. 📧 Test SendGrid connection (START HERE!)
    # send_test_email()
    
    # 2. 🎬 Demo: Watch email being written token-by-token
    # await demo_streamed_response()
    
    # 3. 📝 Generate 3 emails with different styles (parallel)
    # await generate_parallel_emails()
    
    # 4. 🏆 Generate 3 emails and AI picks the best one
    # await select_best_email()
    
    # 5. 🔧 Sales manager: generate, select, send (plain text)
    # await run_sales_manager()
    
    # 6. 🚀 FULL AUTOMATION: generate, select, HTML format, and send
    await run_automated_sdr()
    
    print("\n" + "=" * 60)
    print("Execution complete! Check your email and OpenAI traces.")
    print("Traces: https://platform.openai.com/traces")
    print("=" * 60)


# Program entry point
if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())