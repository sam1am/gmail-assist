import os
import pickle
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
from bs4 import BeautifulSoup
from openai_api import evaluate_importance
import time
from termcolor import colored
from multiprocessing import Process, Queue


# Define function to connect to Gmail API
def connect_gmail_api():
    print("Connecting to Gmail API...")
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            print("Loaded credentials from token.pickle")
    if not creds or not creds.valid:
        print("Refreshing credentials...")
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/gmail.modify'])
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def get_label_ids_by_name(service, label_names):
    label_ids = {}
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        for label in labels:
            if label['name'] in label_names:
                label_ids[label['name']] = label['id']

        return label_ids
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None


def label_unread_emails(service, label_ids):
    while True:
        try:
            results = service.users().messages().list(userId='me', q='is:unread').execute()
            print(f"Found {len(results['messages'])} unread messages.")
            messages = results.get('messages', [])

            if not messages:
                print('No unread messages found.')
                break
            else:
                print('Proceeding with labeling...')
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                    sender, subject, body = extract_email_data(msg)

                    importance = evaluate_importance(sender, subject, body)
                    if importance:
                        label_id = label_ids.get(importance)
                        if label_id:
                            service.users().messages().modify(userId='me', id=message['id'], body={'addLabelIds': [label_id]}).execute()
                            print(colored(f"✓{importance}\n", 'blue'))
                            print("Finished at: " + time.strftime("%H:%M:%S", time.localtime()))
                            print("\n")
                        else:
                            print(f"Error: Invalid importance rating for message {message['id']}")
                    else:
                        print(f"Error: Failed to evaluate importance for message {message['id']}")

        except HttpError as error:
            print(f"An error occurred while labeling: {error}")
            break


def extract_email_data(msg):
    headers = msg['payload']['headers']
    sender = ''
    subject = ''
    for header in headers:
        if header['name'] == 'From':
            sender = header['value']
        elif header['name'] == 'Subject':
            subject = header['value']
    
    if 'parts' in msg['payload']:
        parts = msg['payload']['parts']
        body = ''
        for part in parts:
            if part['mimeType'] == 'text/plain':
                body = part['body'].get('data', '')
            elif part['mimeType'] == 'text/html':
                html = part['body'].get('data', '')
                soup = BeautifulSoup(html, 'html.parser')
                body += soup.get_text()
        if not body:
            body = parts[0]['body'].get('data', '')
    else:
        body = msg['payload']['body'].get('data', '')

    try:
        if body:
            body = base64.urlsafe_b64decode(body).decode()
        else:
            body = ''
    except binascii.Error as e:
        print(f"Error decoding base64-encoded data: {e}")
    
    return sender, subject, body
