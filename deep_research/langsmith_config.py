"""
LangSmith Configuration for Deep Research Agent
Enables tracing and monitoring via LangSmith
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def configure_langsmith():
    """
    Configure LangSmith tracing from environment variables
    
    Environment variables required:
    - LANGSMITH_TRACING: Set to "true" to enable tracing
    - LANGSMITH_API_KEY: Your LangSmith API key
    - LANGSMITH_ENDPOINT: LangSmith API endpoint (default: https://api.smith.langchain.com)
    - LANGSMITH_PROJECT: Project name for organizing traces
    """
    
    # Check if tracing is enabled
    tracing_enabled = os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    
    if not tracing_enabled:
        print("⚠️  LangSmith tracing is disabled. Set LANGSMITH_TRACING=true to enable.")
        return False
    
    # Get LangSmith configuration
    api_key = os.getenv('LANGSMITH_API_KEY')
    endpoint = os.getenv('LANGSMITH_ENDPOINT', 'https://api.smith.langchain.com')
    project = os.getenv('LANGSMITH_PROJECT', 'deep-research-agent')
    
    if not api_key:
        print("⚠️  LANGSMITH_API_KEY not found. LangSmith tracing disabled.")
        return False
    
    # Set environment variables for LangSmith
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_API_KEY'] = api_key
    os.environ['LANGCHAIN_ENDPOINT'] = endpoint
    os.environ['LANGCHAIN_PROJECT'] = project
    
    print("✅ LangSmith tracing enabled!")
    print(f"   Project: {project}")
    print(f"   Endpoint: {endpoint}")
    print(f"   View traces at: https://smith.langchain.com/")
    
    return True


def get_langsmith_url(run_id: str = None) -> str:
    """
    Get LangSmith trace URL for a specific run
    
    Args:
        run_id: Optional run ID to get specific trace URL
        
    Returns:
        URL to view traces in LangSmith
    """
    project = os.getenv('LANGSMITH_PROJECT', 'deep-research-agent')
    base_url = "https://smith.langchain.com/"
    
    if run_id:
        return f"{base_url}public/{project}/r/{run_id}"
    else:
        return f"{base_url}o/default/projects/p/{project}"


# Configure LangSmith when module is imported
configure_langsmith()
