"""
Deep Research Agent - Main Entry Point
Run this to start the Gradio web interface
"""

import asyncio
from dotenv import load_dotenv
from deep_research.ui import launch_ui

# Load environment variables
load_dotenv()


def main():
    """
    Main entry point for Deep Research Agent
    Launches the Gradio web interface
    """
    print("🔬 Starting Deep Research Agent...")
    print("📊 Loading web interface...")
    
    # Launch Gradio UI
    launch_ui(
        share=False,  # Set to True for public URL
        server_port=7860
    )


if __name__ == "__main__":
    main()
