"""
Calculator Tool
Perform mathematical calculations and data analysis
"""

from typing import Union


def calculate_tool(expression: str) -> Union[float, str]:
    """
    Evaluate a mathematical expression safely
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "10 * 5")
        
    Returns:
        Result of the calculation or error message
        
    Examples:
        >>> calculate_tool("2 + 2")
        4.0
        >>> calculate_tool("100 / 4")
        25.0
    """
    try:
        # Safe evaluation - only allows basic math operations
        # Remove any potentially dangerous characters
        allowed_chars = set('0123456789+-*/().,e ')
        if not all(c in allowed_chars for c in expression):
            return "Error: Expression contains invalid characters"
        
        # Evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})
        
        return float(result)
        
    except ZeroDivisionError:
        return "Error: Division by zero"
    except Exception as e:
        return f"Error: {str(e)}"
