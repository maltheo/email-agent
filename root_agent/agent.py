from google.adk.agents.llm_agent import Agent
from .tools import list_emails, read_email, search_emails, send_email

root_agent = Agent(
    model='gemini-2.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
    tools=[list_emails, read_email, search_emails, send_email],
)
