"""
Tools for Deep Research Agent
Provides function tools that agents can use
"""

from .web_search import web_search_tool
from .file_operations import save_report_tool
from .calculator import calculate_tool

__all__ = [
    'web_search_tool',
    'save_report_tool',
    'calculate_tool'
]
