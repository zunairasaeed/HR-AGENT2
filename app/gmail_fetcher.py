import os
import base64
import time
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# OAuth scopes – just read-only access to Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Folder to save resumes
SAVE_DIR = "data/resumes"
os.makedirs(SAVE_DIR, exist_ok=True)

# Your exact credentials file name from GCP
CREDENTIALS_FILE = "credentials.json"

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
        creds = flow.run_local_server(port=0)  # opens browser automatically
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_resumes_from_gmail():
    creds = authenticate_gmail()
    service = build('gmail', 'v1', credentials=creds)

    result = service.users().messages().list(userId='me', q="has:attachment").execute()
    messages = result.get('messages', [])

    print(f"📩 Found {len(messages)} emails with attachments.\n")

    for msg in messages:
        msg_id = msg['id']
        msg_data = service.users().messages().get(userId='me', id=msg_id).execute()
        payload = msg_data.get('payload', {})
        parts = payload.get('parts', [])

        for part in parts:
            filename = part.get("filename")
            body = part.get("body", {})
            if filename and filename.endswith((".pdf", ".docx")):
                att_id = body.get("attachmentId")
                if att_id:
                    att = service.users().messages().attachments().get(
                        userId='me', messageId=msg_id, id=att_id).execute()
                    file_data = base64.urlsafe_b64decode(att['data'].encode('UTF-8'))
                    save_path = os.path.join(SAVE_DIR, filename)
                    with open(save_path, "wb") as f:
                        f.write(file_data)
                    print(f"✅ Saved: {filename}")
        time.sleep(0.5)

if __name__ == "__main__":
    fetch_resumes_from_gmail()
