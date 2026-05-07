# Email Agent

AI-powered email assistant built with Google ADK (Agent Development Kit) and Gemini.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Add your Google OAuth credentials:
   - Place your `client_secret_*.json` file in the project root
   - Or set `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` in `.env`

## Usage

### Custom Tools (default)

Uses the built-in custom Gmail tools:
```bash
uv run main.py
```

### MCP Mode

Uses the Google Workspace MCP server for Gmail:
```bash
GOOGLE_GMAIL_MODE=mcp uv run main.py
```

## Gmail Modes

| Mode | Tools Available |
|------|----------------|
| `custom` | list_emails, read_email, search_emails, send_email |
| `mcp` | search_gmail_messages, get_gmail_message_content, send_gmail_message, get_gmail_messages_content_batch |

## Security

Sensitive files are excluded from git:
- `.env` (API keys, OAuth credentials)
- `client_secret_*.json` (OAuth client secret)
- `token.json` (OAuth token)

## Requirements

- Python 3.11+
- uv (package manager)
- Google Cloud project with Gmail API enabled
- OAuth 2.0 Desktop app credentials
