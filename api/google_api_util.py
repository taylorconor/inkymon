import os.path

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


def _get_service(name, scopes):
    """ Create, initialise and authenticate a Google API service object. """

    credentials = None
    token_file = '.' + name + '_token.json'
    credentials_file = '.' + name + '_credentials.json'
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        credentials = Credentials.from_authorized_user_file(token_file, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, scopes)
            credentials = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'w') as token:
            token.write(credentials.to_json())
    service = build(name, 'v3', credentials=credentials)
    return service


def get_drive_service():
    return _get_service('drive', ['https://www.googleapis.com/auth/drive.readonly'])


def get_calendar_service():
    return _get_service('calendar', ['https://www.googleapis.com/auth/calendar.readonly'])