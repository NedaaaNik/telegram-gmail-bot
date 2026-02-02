import os
import time
import requests
import socket  # <--- NEW IMPORT
import requests.packages.urllib3.util.connection as urllib3_cn # <--- NEW IMPORT
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google import genai

# ---  FIX: FORCE IPV4  ---
# This forces Python to ignore the unstable IPv6 connection
def allowed_gai_family():
    return socket.AF_INET

urllib3_cn.allowed_gai_family = allowed_gai_family
# -----------------------------

# --- CONFIGURATION ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly'] 

# Store IDs to avoid duplicates
processed_email_ids = set()

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        # Increased timeout to 30 seconds for bad internet
        requests.post(url, json=payload, timeout=30)
    except Exception as e:
        print(f"Error sending Telegram: {e}")

# ... (The rest of the code remains EXACTLY the same as before) ...
# ... Copy paste the 'authenticate_gmail', 'summarize_email', etc functions here ...

def authenticate_gmail():
    """Standard Gmail Auth"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def summarize_email(sender, subject, body):
    """Uses Gemini to summarize."""
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = f"""
    You are a helpful assistant. Summarize this incoming email in 1-2 sentences.
    Start with " *New Email*"
    
    From: {sender}
    Subject: {subject}
    Body: {body}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"\n GEMINI ERROR: {e}\n")
        return f" *New Email from {sender}*\nSubject: {subject}\n(Could not summarize)"

def check_for_new_emails(service):
    print("Checking inbox...")
    results = service.users().messages().list(userId='me', q='is:unread', maxResults=5).execute()
    messages = results.get('messages', [])

    for msg in messages:
        msg_id = msg['id']
        if msg_id in processed_email_ids:
            continue
            
        processed_email_ids.add(msg_id)
        
        txt = service.users().messages().get(userId='me', id=msg_id).execute()
        headers = txt['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
        sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
        snippet = txt.get('snippet', '')

        print(f"Found new email: {subject}")
        summary = summarize_email(sender, subject, snippet)
        send_telegram_message(summary)

if __name__ == '__main__':
    print(" Agent started (IPv4 Mode). Watching for emails...")
    service = authenticate_gmail()
    
    # Pre-fill cache
    initial = service.users().messages().list(userId='me', q='is:unread', maxResults=10).execute()
    for m in initial.get('messages', []):
        processed_email_ids.add(m['id'])
    print(f"Ignored {len(processed_email_ids)} existing unread emails. Waiting for NEW ones...")

    try:
        while True:
            check_for_new_emails(service)
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping Agent.")