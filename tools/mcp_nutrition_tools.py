"""
MCP Nutrition Tools using CrewAI's stdio transport.
Integrates the mcp-nutrition-tools server for USDA nutrition data.
"""

import os
from pathlib import Path
from crewai.mcp import MCPServerStdio

# Get the path to the MCP nutrition server
PROJECT_ROOT = Path(__file__).parent.parent
MCP_SERVER_PATH = PROJECT_ROOT / "mcp-nutrition-tools" / "src" / "mcp_server.py"

def create_mcp_nutrition_server():
    """
    Create MCP server connection for USDA nutrition tools.
    
    Returns:
        MCPServerStdio: Configured MCP server instance
    """
    # Ensure API key is set
    api_key = os.getenv('FDC_API_KEY') or os.getenv('USDA_API_KEY')
    if not api_key:
        raise ValueError(
            "USDA API key not found. Please set FDC_API_KEY or USDA_API_KEY environment variable."
        )
    
    # Create MCP server with stdio transport
    mcp_server = MCPServerStdio(
        name="usda_nutrition",
        command="python",
        args=[str(MCP_SERVER_PATH)],
        env={
            "FDC_API_KEY": api_key,
            "PYTHONPATH": str(PROJECT_ROOT / "mcp-nutrition-tools")
        }
    )
    
    return mcp_server


# Global MCP server instance
_mcp_nutrition_server = None

def get_mcp_nutrition_server():
    """Get or create the global MCP nutrition server instance."""
    global _mcp_nutrition_server
    if _mcp_nutrition_server is None:
        _mcp_nutrition_server = create_mcp_nutrition_server()
    return _mcp_nutrition_server
