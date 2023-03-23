from gmail_api import connect_gmail_api, get_label_ids_by_name, label_unread_emails

def main():
    print("Starting script...")
    service = connect_gmail_api()
    print("Connected to Gmail API")
    if service:
        label_ids = get_label_ids_by_name(service, ['gptUrgent', 'gptImportant', 'gptNormal', 'gptLow', 'gptJunk'])
        if label_ids:
            print(f"Label IDs: {label_ids}")
            label_unread_emails(service, label_ids)
        else:
            print("Error: Could not fetch label IDs")
    else:
        print("Error connecting to Gmail API")

if __name__ == '__main__':
    main()

