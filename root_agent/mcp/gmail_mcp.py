from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters


def get_gmail_mcp_tools():
    """Return MCP toolset for Gmail operations.

    Connects to the Google Workspace MCP server via uvx and exposes
    Gmail core tools: search, read, send, and batch operations.

    Returns:
        McpToolset: Configured toolset for Gmail MCP tools.

    Raises:
        RuntimeError: If the MCP server fails to initialize.
    """
    try:
        return McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='uvx',
                    args=['workspace-mcp', '--tools', 'gmail', '--tool-tier', 'core']
                )
            )
        )
    except Exception as e:
        raise RuntimeError(
            "Failed to initialize MCP Gmail tools. "
            "To use MCP mode, ensure 'uvx' is installed (uv pip install uv). "
            "Set GOOGLE_GMAIL_MODE=custom to use custom tools instead."
        ) from e
