import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64

def parse_date(date_str, date_format='%Y-%m-%d'):
    try:
        return datetime.datetime.strptime(date_str, date_format).date()
    except ValueError:
        return datetime.datetime.strptime(date_str,  '%Y-%m-%dT%H:%M:%S.%fZ').date()

def send_gmail(access_token, refresh_token, client_id, client_secret, sender, to, subject, message_text):
    credentials = Credentials(
        access_token,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri='https://oauth2.googleapis.com/token'
    )

    service = build('gmail', 'v1', credentials=credentials)

    message = create_message(sender, to, subject, message_text)
    response = send_message(service, "me", message)
    return response

def create_message(sender, to, subject, message_text):
    message = {'raw': base64.urlsafe_b64encode(bytes("From: {}\nTo: {}\nSubject: {}\n\n{}".format(sender, to, subject, message_text), "utf-8")).decode("utf-8")}
    return message

def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except Exception as error:
        print('An error occurred: %s' % error)
        return None
