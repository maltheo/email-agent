import os
from google.adk.agents.llm_agent import Agent

gmail_mode = os.environ.get("GOOGLE_GMAIL_MODE", "custom")

if gmail_mode == "mcp":
    from .mcp.gmail_mcp import get_gmail_mcp_tools
    agent_tools = [get_gmail_mcp_tools()]
    tool_source = "MCP"
else:
    from .tools import list_emails, read_email, search_emails, send_email
    agent_tools = [list_emails, read_email, search_emails, send_email]
    tool_source = "Custom"

print(f"Using Gmail tools: {tool_source}")

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=agent_tools,
)
