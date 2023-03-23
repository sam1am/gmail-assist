import os
import pickle
import openai
import base64
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import email
from bs4 import BeautifulSoup
import time

with open('openaikey.txt', 'r') as file:
    openai.api_key = file.read().replace('\n', '')


def evaluate_importance(sender, subject, body):
    # delay 1 second to avoid rate limiting
    time.sleep(3)
    # Remove markup from body using BeautifulSoup
    soup = BeautifulSoup(body, "html.parser")
    body = soup.get_text()
    # remove spaces and newlines
    body = body.replace(" ", "").replace("\n", "")
    # truncate body to 140 characters max
    body = body[:140]
    print(f"Evaluating importance of email from {sender} with subject {subject} and body {body}")
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt="I will provide an email and you will respond with a score from 1 to 5 based on how important it is based on the information provided. Please rate the email based on the following guidelines:\n"
                "1 - Junk or spam (promotional ads, unsolicited messages, phishing attempts, etc.)\n"
                "2 - Non-urgent updates from companies or organizations (newsletters, product updates, etc.)\n"
                "3 - General correspondence or updates (personal messages, social media notifications, etc.)\n"
                "4 - Important personal messages (from close friends or family members, urgent updates, personal emergencies)\n"
                "5 - Urgent or time-sensitive messages (medical or financial alerts, travel updates, etc.)\n"
                "Please note that coupons or deals should be considered as junk or spam unless they are specifically requested by the recipient.\n"
                "Please provide a score and nothing else for the following email:\n"
                f"Sender: {sender}\n"
                f"Subject: {subject}\n"
                f"Truncated Body: {body}\n"
                "Score: ",
            temperature=0.5,
            max_tokens=3,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        importance = response.choices[0].text.strip()
        print(f"Importance: {importance}")

        # Update the importance value to match the keys in the label_ids dictionary
        if importance == "1":
            return "gptCrap"
        elif importance == "2":
                return "gptLow"
        elif importance == "3":
            return "gptNormal"
        elif importance == "4":
            return "gptHigh"
        elif importance == "5":
            return "gptUrgent"
        else:
            return None

    except Exception as e:
        print(f"Error during importance evaluation: {e}")
        return None

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
        print("Connecting to Gmail API...")
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
    print("Labeling unread emails...")
    try:
        results = service.users().messages().list(userId='me', q='is:unread -label:gptUrgent -label:gptHigh -label:gptNormal -label:gptLow -label:gptCrap').execute()
        print(f"Found {len(results['messages'])} unread messages.")
        messages = results.get('messages', [])
        if not messages:
            print('No unread messages found.')
        else:
            print('Labeling unread messages:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                headers = msg['payload']['headers']
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
                            body = part['body']['data']
                        elif part['mimeType'] == 'text/html':
                            html = part['body']['data']
                            soup = BeautifulSoup(html, 'html.parser')
                            body += soup.get_text()
                    body = base64.urlsafe_b64decode(body).decode()
                else:
                    body = msg['payload']['body']['data']
                    body = base64.urlsafe_b64decode(body).decode()
                info = f"Sender: {sender}\nSubject: {subject}\nBody: {body}"
                importance = evaluate_importance(sender, subject, body)
                if importance:
                    label_id = label_ids.get(importance)
                    if label_id:
                        service.users().messages().modify(userId='me', id=message['id'], body={'addLabelIds': [label_id]}).execute()
                        print(f"Message {message['id']} labeled as {importance}")
                    else:
                        print(f"Error: Invalid importance rating for message {message['id']}")
                else:
                    print(f"Error: Failed to evaluate importance for message {message['id']}")
    except HttpError as error:
        print(f"An error occurred while labeling: {error}")


    
def main():
    print("Starting script...")
    service = connect_gmail_api()
    print("Connected to Gmail API")
    if service:
        label_ids = get_label_ids_by_name(service, ['gptUrgent', 'gptHigh', 'gptNormal', 'gptLow', 'gptCrap'])
        if label_ids:
            print(f"Label IDs: {label_ids}")
            label_unread_emails(service, label_ids)
        else:
            print("Error: Could not fetch label IDs")
    else:
        print("Error connecting to Gmail API")


if __name__ == '__main__':
    main()


