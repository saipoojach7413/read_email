from __future__ import print_function
import base64
import os
import pickle
from bs4 import BeautifulSoup

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from db import insert_email   # DB insert function

# ---------------------------------------------
# CONFIG
# ---------------------------------------------
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TARGET_PERSONS = [
    "sumathikannuri2003@gmail.com",
    "vallimanasa21@gmail.com",
    "likhith4534@gmail.com",
    "bharani@360digitmg.com",
    "drive-shares-dm-noreply@google.com",
]

ATTACHMENTS_DIR = "attachments"
os.makedirs(ATTACHMENTS_DIR, exist_ok=True)


# ---------------------------------------------
# BUILD OR QUERY
# ---------------------------------------------
def build_or_query(person_list, field):
    joined = " OR ".join(person_list)
    return f'{field}:({joined})'


# ---------------------------------------------
# AUTHENTICATION
# ---------------------------------------------
def authenticate_gmail():
    creds = None

    if os.path.exists("token.json"):
        with open("token.json", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.json", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------
# EXTRACT EMAIL BODY
# ---------------------------------------------
def extract_text(payload):
    if "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType")
            data = part["body"].get("data")

            if mime == "text/plain" and data:
                return base64.urlsafe_b64decode(data).decode("utf-8")

            if mime == "text/html" and data:
                html = base64.urlsafe_b64decode(data).decode("utf-8")
                soup = BeautifulSoup(html, "html.parser")
                return soup.get_text()

    if payload.get("mimeType") == "text/plain":
        data = payload["body"].get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8")

    return "No body found."


# ---------------------------------------------
# DOWNLOAD ATTACHMENTS
# ---------------------------------------------
def download_attachments(service, msg_id, payload):
    attachments = []

    if "parts" not in payload:
        return attachments

    for part in payload["parts"]:
        filename = part.get("filename")
        body = part.get("body", {})
        attachment_id = body.get("attachmentId")

        if filename and attachment_id:
            att = service.users().messages().attachments().get(
                userId="me",
                messageId=msg_id,
                id=attachment_id
            ).execute()

            data = base64.urlsafe_b64decode(att["data"])
            filepath = os.path.join(ATTACHMENTS_DIR, filename)

            with open(filepath, "wb") as f:
                f.write(data)

            attachments.append(filepath)

    return attachments


# ---------------------------------------------
# READ EMAILS BY QUERY
# ---------------------------------------------
def read_by_query(query, label):
    service = authenticate_gmail()

    results = service.users().messages().list(
        userId="me", q=query
    ).execute()

    messages = results.get("messages", [])

    print("\n==========================")
    print(f"📌 {label} — Found: {len(messages)} mails")
    print("==========================")

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="full"
        ).execute()

        headers = msg_data["payload"]["headers"]
        sender, subject = "", ""

        for h in headers:
            if h["name"] == "From":
                sender = h["value"]
            elif h["name"] == "Subject":
                subject = h["value"]

        body = extract_text(msg_data["payload"])

        # DOWNLOAD FILES
        attachments = download_attachments(
            service, msg["id"], msg_data["payload"]
        )

        print("\n------------------------------------")
        print(f"📨 From: {sender}")
        print(f"📝 Subject: {subject}")
        print("------------------------------------")
        print("📄 Body:")
        print(body)
        print("------------------------------------")

        if attachments:
            print("📎 Attachments:")
            for a in attachments:
                print("  -", a)
        else:
            print("📎 No attachments")

        print("------------------------------------")

        # SAVE TO DATABASE
        inserted_id = insert_email(sender, subject, body, msg_data)

        if inserted_id:
            print(f"✅ Stored in DB (id={inserted_id})")
        else:
            print("⚠️ Failed to store in DB")


# ---------------------------------------------
# MAIN RUNNER
# ---------------------------------------------
if __name__ == "__main__":

    inbox_or_query = build_or_query(TARGET_PERSONS, "from")
    inbox_query = f"in:inbox {inbox_or_query}"
    read_by_query(inbox_query, f"INBOX mails FROM {TARGET_PERSONS}")

    sent_or_query = build_or_query(TARGET_PERSONS, "to")
    sent_query = f"in:sent {sent_or_query}"
    read_by_query(sent_query, f"SENT mails TO {TARGET_PERSONS}")

