"""
Central import module to avoid circular imports
Import the agents SDK before any local modules
"""

# Force import of the global agents package, not our local folder
import sys

# Remove current working directory temporarily
if '' in sys.path:
    sys.path.remove('')
if '.' in sys.path:
    sys.path.remove('.')
    
# Import from site-packages
from agents import (
    Agent,
    Runner,
    WebSearchTool,
    ModelSettings,
    function_tool,
    trace,
    get_current_trace
)

__all__ = [
    'Agent',
    'Runner',
    'WebSearchTool',
    'ModelSettings',
    'function_tool',
    'trace',
    'get_current_trace',
]
