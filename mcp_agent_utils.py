# mcp_agent_utils.py
# Utility-focused MCP server
# Install: pip install mcp

from mcp.server.fastmcp import FastMCP

# Create MCP server for utility operations
mcp = FastMCP("UtilsAgent")

@mcp.tool()
def get_current_time() -> str:
    """Get current time"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@mcp.tool()
def get_date_info() -> str:
    """Get detailed date information"""
    from datetime import datetime
    now = datetime.now()
    return f"Date: {now.strftime('%Y-%m-%d')}, Day: {now.strftime('%A')}, Week: {now.isocalendar()[1]}"

@mcp.tool()
def format_text(text: str, style: str = "upper") -> str:
    """
    Format text in different styles
    
    Args:
        text: Text to format
        style: Format style (upper, lower, title, capitalize)
    """
    try:
        if style == "upper":
            return text.upper()
        elif style == "lower":
            return text.lower()
        elif style == "title":
            return text.title()
        elif style == "capitalize":
            return text.capitalize()
        else:
            return f"Unknown style: {style}"
    except Exception as e:
        return f"Format error: {e}"

@mcp.tool()
def count_words(text: str) -> str:
    """Count words in text"""
    try:
        words = text.split()
        chars = len(text)
        lines = text.count('\n') + 1
        return f"Words: {len(words)}, Characters: {chars}, Lines: {lines}"
    except Exception as e:
        return f"Count error: {e}"

@mcp.tool()
def reverse_text(text: str) -> str:
    """Reverse text"""
    try:
        return text[::-1]
    except Exception as e:
        return f"Reverse error: {e}"

if __name__ == "__main__":
    mcp.run()
