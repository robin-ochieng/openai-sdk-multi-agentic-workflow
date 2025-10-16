"""
File Operations Tool
Save research reports to disk
"""

import os
from datetime import datetime
from typing import Dict


def save_report_tool(report_content: str, query: str) -> Dict[str, str]:
    """
    Save research report to disk
    
    Args:
        report_content: The markdown report content to save
        query: The research query (used for filename)
        
    Returns:
        Dict with status and file path
    """
    try:
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename from query and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in query)
        safe_query = safe_query[:50]  # Limit length
        filename = f"{safe_query}_{timestamp}.md"
        
        filepath = os.path.join(reports_dir, filename)
        
        # Write report to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return {
            "status": "success",
            "filepath": filepath,
            "message": f"Report saved to {filepath}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "filepath": "",
            "message": f"Error saving report: {str(e)}"
        }
