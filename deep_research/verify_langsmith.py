"""
Verify LangSmith Configuration
Checks if all required environment variables are set correctly
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load .env from project root
env_path = project_root / '.env'
load_dotenv(env_path)

def verify_langsmith_config():
    """Verify LangSmith configuration"""
    
    print("\n" + "="*60)
    print("🔍 VERIFYING LANGSMITH CONFIGURATION")
    print("="*60 + "\n")
    
    # Check .env file exists
    if env_path.exists():
        print(f"✅ Found .env file at: {env_path}")
    else:
        print(f"❌ .env file not found at: {env_path}")
        return False
    
    # Required environment variables
    required_vars = {
        'LANGSMITH_TRACING': 'Enable/disable tracing',
        'LANGSMITH_API_KEY': 'LangSmith API key',
        'LANGSMITH_ENDPOINT': 'LangSmith API endpoint',
        'LANGSMITH_PROJECT': 'Project name'
    }
    
    print("\n📋 Environment Variables:")
    print("-" * 60)
    
    all_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask API key
            if 'KEY' in var or 'PASSWORD' in var:
                display_value = value[:10] + "..." if len(value) > 10 else "***"
            else:
                display_value = value
            
            print(f"✅ {var:<25} = {display_value}")
            print(f"   └─ {description}")
        else:
            print(f"❌ {var:<25} = NOT SET")
            print(f"   └─ {description}")
            all_set = False
    
    print("-" * 60)
    
    # Check if tracing is enabled
    tracing_enabled = os.getenv('LANGSMITH_TRACING', 'false').lower() == 'true'
    
    if not tracing_enabled:
        print("\n⚠️  LANGSMITH_TRACING is not set to 'true'")
        print("   Set LANGSMITH_TRACING=true in your .env file to enable tracing")
        return False
    
    # Check API key
    api_key = os.getenv('LANGSMITH_API_KEY')
    if not api_key:
        print("\n❌ LANGSMITH_API_KEY is required but not set")
        return False
    
    if not all_set:
        print("\n❌ Some required environment variables are missing")
        return False
    
    print("\n" + "="*60)
    print("✅ LANGSMITH CONFIGURATION VERIFIED!")
    print("="*60)
    
    # Print helpful URLs
    project = os.getenv('LANGSMITH_PROJECT', 'deep-research-agent')
    print(f"\n📊 View traces at: https://smith.langchain.com/")
    print(f"🔗 Project URL: https://smith.langchain.com/o/default/projects/p/{project}")
    
    # Test import
    print("\n" + "="*60)
    print("🧪 TESTING LANGSMITH IMPORT")
    print("="*60 + "\n")
    
    try:
        from deep_research.langsmith_config import configure_langsmith
        print("✅ Successfully imported langsmith_config")
        
        result = configure_langsmith()
        if result:
            print("✅ LangSmith configuration successful!")
        else:
            print("⚠️  LangSmith configuration failed")
            
    except ImportError as e:
        print(f"❌ Failed to import langsmith_config: {e}")
        print("\n💡 Install required packages:")
        print("   pip install -r deep_research/requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error configuring LangSmith: {e}")
        return False
    
    print("\n" + "="*60)
    print("✅ ALL CHECKS PASSED!")
    print("="*60)
    print("\n💡 Next steps:")
    print("   1. Start the API server: python deep_research/api_server.py")
    print("   2. Submit a research query")
    print("   3. View traces at: https://smith.langchain.com/")
    
    return True


if __name__ == "__main__":
    success = verify_langsmith_config()
    sys.exit(0 if success else 1)
