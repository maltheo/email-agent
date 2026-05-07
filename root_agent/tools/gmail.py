from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2.service_account import Credentials as ServiceAccountCredentials
from google.auth import default
import base64
import os
import logging

logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOKEN_FILE = os.path.join(PROJECT_ROOT, "token.json")
OAUTH_PORT = int(os.environ.get("GOOGLE_OAUTH_PORT", "8085"))


def _get_gmail_credentials():
    """Get Gmail credentials using OAuth2 or service account."""
    # Check for OAuth client secret
    import glob
    client_secret_files = glob.glob(os.path.join(PROJECT_ROOT, "client_secret_*.json"))

    if client_secret_files:
        # Use OAuth2 flow
        creds = None
        if os.path.exists(TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing OAuth token...")
                creds.refresh(Request())
            else:
                logger.info(f"Starting OAuth2 flow on port {OAUTH_PORT}...")
                flow = InstalledAppFlow.from_client_secrets_file(client_secret_files[0], SCOPES)
                creds = flow.run_local_server(port=OAUTH_PORT)

            # Save credentials for next run
            with open(TOKEN_FILE, "w") as token:
                token.write(creds.to_json())
            logger.info("OAuth token saved.")

        return creds
    else:
        # Fall back to service account or default credentials
        service_account_file = os.path.join(PROJECT_ROOT, "credentials.json")
        if os.path.exists(service_account_file):
            creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, SCOPES)
            # Delegate to user if needed (for Workspace accounts)
            # creds = creds.create_delegated("user@yourdomain.com")
        else:
            creds, _ = default(scopes=SCOPES)

        return creds


def _build_gmail_service():
    """Build and return Gmail API service."""
    creds = _get_gmail_credentials()
    return build("gmail", "v1", credentials=creds)


def list_emails(query: str = "", max_results: int = 10) -> str:
    """List Gmail messages, optionally filtered by query string.

    Args:
        query: Gmail search query (e.g., 'from:example.com', 'subject:report', 'after:2024/01/01')
        max_results: Maximum number of results to return

    Returns:
        String representation of message metadata
    """
    service = _build_gmail_service()
    results = service.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()
    messages = results.get("messages", [])

    if not messages:
        return "No emails found."

    output = []
    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()
        payload = msg_data.get("payload", {})
        headers = {h["name"]: h["value"] for h in payload.get("headers", [])}
        output.append(
            f"ID: {msg['id']}\n"
            f"From: {headers.get('From', 'N/A')}\n"
            f"To: {headers.get('To', 'N/A')}\n"
            f"Subject: {headers.get('Subject', 'N/A')}\n"
            f"Date: {headers.get('Date', 'N/A')}\n"
            f"---"
        )

    return "\n".join(output)


def read_email(message_id: str) -> str:
    """Read the content of a specific email by message ID.

    Args:
        message_id: The Gmail message ID

    Returns:
        String representation of the email content
    """
    service = _build_gmail_service()
    msg = service.users().messages().get(
        userId="me", id=message_id, format="full"
    ).execute()

    payload = msg.get("payload", {})
    headers = {h["name"]: h["value"] for h in payload.get("headers", [])}

    # Get body
    body = ""
    if "data" in payload.get("body", {}):
        body = base64.urlsafe_b64decode(payload["body"]["data"]["data"]).decode("utf-8", errors="replace")
    elif payload.get("parts"):
        for part in payload["parts"]:
            if part.get("mimeType") == "text/plain" and "data" in part.get("body", {}):
                body = base64.urlsafe_b64decode(part["body"]["data"]["data"]).decode("utf-8", errors="replace")
                break
        if not body and payload["parts"]:
            # Fallback to first available part
            for part in payload["parts"]:
                if "data" in part.get("body", {}):
                    body = base64.urlsafe_b64decode(part["body"]["data"]["data"]).decode("utf-8", errors="replace")
                    break

    return (
        f"From: {headers.get('From', 'N/A')}\n"
        f"To: {headers.get('To', 'N/A')}\n"
        f"Subject: {headers.get('Subject', 'N/A')}\n"
        f"Date: {headers.get('Date', 'N/A')}\n"
        f"---\n{body}"
    )


def search_emails(query: str = "", max_results: int = 10) -> str:
    """Search Gmail messages using Gmail's search syntax.

    Args:
        query: Gmail search query (e.g., 'from:example.com', 'has:attachment', 'is:unread')
        max_results: Maximum number of results to return

    Returns:
        String representation of matching message metadata
    """
    return list_emails(query=query, max_results=max_results)


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail.

    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body text

    Returns:
        Confirmation message with message ID
    """
    service = _build_gmail_service()

    message = {"raw": ""}
    # Create email message
    mime_msg = f"From: me\r\nTo: {to}\r\nSubject: {subject}\r\n\r\n{body}"
    raw = base64.urlsafe_b64encode(mime_msg.encode("utf-8")).decode("utf-8")
    message["raw"] = raw

    result = service.users().messages().send(
        userId="me", body=message
    ).execute()

    return f"Email sent successfully. Message ID: {result.get('id')}"
