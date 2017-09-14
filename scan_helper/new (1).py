#!/usr/bin/python2
import httplib2
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
    flags.noauth_local_webserver = True
except ImportError:
    flags = None


class Config:
    scopes = 'https://www.googleapis.com/auth/drive'
    client_secret_file = 'client_secrets.json'
    client_credentials_file = 'credentials.json'
    app_name = 'wormhole-file-transfer'


class Drive:
    def __init__(self):
        self.credentials = None
        self.get_creds()
        self.http = self.creds.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)

    def get_creds(self):
        """
        Gets valid creds from storage.
        If nothing stored, or if creds invalid, OAuth2 flow used to get new creds.
        """
        store = oauth2client.file.Storage(Config.client_credentials_file)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(Config.client_secret_file, Config.scopes)
            flow.user_agent = Config.app_name
            creds = tools.run_flow(flow, store, flags)
        self.credentials = creds

    def list_10_files(self):
        results = self.service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))


def main():
    """Shows basic usage of the Google Drive API.

    Creates a Google Drive API service object and outputs the names and IDs
    for up to 10 files.
    """
    drive = Drive()
    drive.list_10_files()

if __name__ == '__main__':
    main()
    # print type(flags)
    # print flags
