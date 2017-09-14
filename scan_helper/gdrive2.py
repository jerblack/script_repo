'''
    authentication

    file listing
    identifying folders
    building paths

    upload files
    master upload controller spawns file_upload threads, which spawns chunk_upload threads
    master upload controller
        passed list of file_paths
        loads list into file upload queue
        polls file_upload controller thread to ensure it's still functioning, kills and respawns if not
    file_upload controller
        watches for files in Queue, extracts one, begins uploading, continues
        runs in own thread, number of threads equals number of files uploading simultaneously
        number of simultaneous file uploads is user.specified
        creates upload chunk jobs of same size (user.specified)
        chunk jobs iterate through bye range in chunks with start and end address specified
        loads chunks into queue
        handles finished chunk upload callbacks
        gets new file from Queue when finished
        polls chunk_uploads threads to ensure it's still functioning, kills and respawns if not

    chunk_upload controller
        chunk_upload job uploads byte range of file
        watches for chunks in queue, extracts one, uploads that byte range, notifies file_upload controller on completion
        runs in own thread, number of threads equals number of chunks uploading simultaneously
        number of simultaneous chunk uploads is user.specified
        total chunk upload threads is total file upload threads * number of chunks per thread
        automatically handle errors


    create folder, check if folder exists, check if file exists, check if byte range uploaded


'''
import json
import webbrowser

import httplib2

from apiclient import discovery
from oauth2client import client
#
if __name__ == '__main__':
    flow = client.OAuth2WebServerFlow(
        client_id='client_secrets.json',
        scope='https://www.googleapis.com/auth/drive',
        redirect_uri='http://localhost:8080/')

    auth_uri = flow.step1_get_authorize_url()
    webbrowser.open(auth_uri)
#
#     auth_code = raw_input('Enter the auth code: ')
#
#     credentials = flow.step2_exchange(auth_code)
#     http_auth = credentials.authorize(httplib2.Http())
#
#     drive_service = discovery.build('drive', 'v2', http_auth)
#     files = drive_service.files().list().execute()
#     for f in files['items']:
#         print f['title']

