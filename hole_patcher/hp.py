#!/usr/bin/python3


import httplib2, os, sys, time, functools, signal, subprocess, shutil, io
import sqlite3 as sql
from pprint import pprint
from apiclient import discovery, http, errors
from oauth2client import file, client, tools
from subprocess import Popen, PIPE, call
from multiprocessing import Pool as ThreadPool
from enum import Enum
from progress.bar import Bar

class Config:
    app_name = 'hole_patcher'
    check_drive_changes_minutes = 15
    check_db_changes_seconds = 30
    use_remote_subfolder = True
    remote_subfolder = "/backup/"
    local_path = "Z:\\_media\\"
    # local_path = "."
    tmp_path = config_folder = db = client_credentials = client_secret = ''
    tmp_extension = 'dl'

class Main:
    def __init__(self):
        self.config_loader()
        self.db = DB()
        self.drive = Drive()
        # self.do_first_run()
        Downloader()

    @staticmethod
    def config_loader():
        Config.tmp_path = os.path.join(
            Config.local_path, '.tmp')
        Config.config_folder = os.path.join(
            os.path.expanduser('~'), '.{}'.format(Config.app_name))
        Config.db = os.path.join(
            Config.config_folder, Config.app_name + '.db')
        Config.client_secret = os.path.join(Config.config_folder, "client_secrets.json")
        Config.client_credentials = os.path.join(Config.config_folder, 'credentials.json')
        os.makedirs(Config.tmp_path, exist_ok=True)
        os.makedirs(Config.config_folder, exist_ok=True)

    def do_first_run(self):
        if self.db.get_first_run() or self.db.get_start_token() == "0":
            print("First run called")
            self.db.remove_all_data()
            print("Clear existing db data")
            self.db.verify()
            print("Setup db")
            self.drive.get_start_token()
            self.db.set_start_token(self.drive.start_token)
            print("Retrieved start token: {}".format(self.drive.start_token))
            print("Getting folders from Google")
            self.drive.get_folders()
            print("Finished getting folders from Google")
            print("Adding folders to db")
            self.db.add_folder(self.drive.folders.values())
            print("Finished adding folders to db")
            print("Getting info about files on Google")
            self.drive.get_files()
            print("Finished getting info about files on Google")
            print("Adding file information to db")
            self.db.add_file(self.drive.files.values())
            print("Finished adding file information to db")
            print("Marked first_run false, first_run is complete")

            self.db.set_first_run(False)

    def check_client_secret(self):
        # TODO: verify that client secret exists where it should and create it if not
        pass


class Drive:
    scope = 'https://www.googleapis.com/auth/drive.metadata.readonly'

    def __init__(self):
        self.db = DB()
        self.credentials = Drive.get_credentials()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)
        self.root_id = self.get_root_id()
        self.folders = {
            'root': Folder("\\", self.root_id, "root"),
            self.root_id: Folder("\\", self.root_id, "root")
        }
        self.folders['root'].path = '/'
        self.files = {}
        self.start_token = self.db.get_start_token()

    @staticmethod
    def get_credentials():
        store = file.Storage(Config.client_credentials)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(Config.client_secret, Drive.scope)
            flow.user_agent = Config.app_name
            credentials = tools.run_flow(flow, store)
        return credentials

    def get_root_id(self):
        results = self.service.files().list(q="'root' in parents and trashed=false",
                                            pageSize=1,
                                            fields="files(id,name,parents)").execute()
        items = results.get('files', [])
        if not items:
            return None
        else:
            return items[0]['parents'][0]

    def get_folders(self):
        def build_paths(id=None, path=None):
            if not id:
                id = self.root_id
                path = '\\'
            self.folders[id].path = path
            if self.folders[id].subfolders:
                for sub in self.folders[id].subfolders:
                    build_paths(sub, os.path.join(path, self.folders[sub].name))

        next_page_token = None
        i = 0
        while True:
            results = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                                                pageSize=1000, pageToken=next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id, parents)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                bar = Bar(str(i), max=len(items))
                for item in items:
                    if item['id'] not in self.folders:
                        self.folders[item['id']] = Folder(item['name'], item['id'], item['parents'][0])
                        self.folders[item['id']].get_included()
                        bar.next()
                bar.finish()
            i += 1000

            if next_page_token is None:
                break
        for name, obj in self.folders.items():
            if obj.parent != "" and obj.parent in self.folders:
                self.folders[obj.parent].subfolders.append(obj.id)
            else:
                print("obj.parent {} not found in self.folders with name {}".format(obj.parent, obj.name))
        build_paths()

    def get_files(self):
        next_page_token = None
        i = 0
        while True:
            results = self.service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false",
                                                pageSize=1000, pageToken=next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id, parents, size)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                bar = Bar(str(i), max=(items))
                for item in items:
                    self.files[item['id']] = File(item['name'],
                                                  item['id'],
                                                  item['parents'][0],
                                                  self.folders[item['parents'][0]].path,
                                                  int(item['size']))
                    bar.next()
                bar.finish()
            i += 1000

            if next_page_token is None:
                break
        print("Number of files {}".format(self.files.__len__()))

    def get_start_token(self):
        # 44565644
        results = self.service.changes().getStartPageToken().execute()
        self.start_token = results.get("startPageToken")
        # self.start_token = 44565644
        return self.start_token

    def get_changes(self):
        next_page_token = self.start_token
        while next_page_token is not None:
            results = self.service.changes().list(pageToken=next_page_token, spaces='drive').execute()
            for change in results.get('changes'):
                # print("fileId: {} , removed: {}, file: {}, type: {}".format([change.get('fileId, removed, file, type')]))
                pprint(change)
                self.handle_change(change)
            if 'newStartPageToken' in results:
                self.start_token = results.get('newStartPageToken')
            next_page_token = results.get('nextPageToken')
        print(self.start_token)

    def handle_change(self, change):
        pass

    def download_file(self, file_object):
        id = file_object if type(file_object) is str else file_object.id
        request = self.service.files().get_media(fileId=id)
        dst_file = os.path.join(Config.tmp_path, "{}.{}".format(id, Config.tmp_extension))
        fh = io.FileIO(dst_file, mode='wb')
        downloader = http.MediaIoBaseDownload(fh, request, chunksize=1024*1024)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("\rDownload {}%.".format(int(status.progress() * 100)))
        print('Finished downloading {}'.format(dst_file))
        return dst_file

    # def upload_file(self, src_file):
    #     """
    #         need to derive google path from src_file path
    #         need to create parent path on drive
    #         need to verify if parent exists
    #         need to figure out how to enumerate and control retries
    #
    #     :param src_file:
    #     :return:
    #     """
    #     name = os.path.basename(src_file)
    #     media = http.MediaFileUpload(src_file, mimetype='application/octet-stream', resumable=True)
    #     request = self.service.insert(media_body=media, body={'name': 'Pig'})
    #     response = None
    #     while response is None:
    #         try:
    #             status, response = request.next_chunk()
    #             if status:
    #                 print("Uploaded %d%%." % int(status.progress() * 100))
    #         except errors.HttpError as e:
    #             if e.resp.status in [404]:
    #
    #             # Start the upload all over again.
    #             elif e.resp.status in [500, 502, 503, 504]:
    #             # Call next_chunk() again, but use an exponential backoff for repeated errors.
    #             else:
    #         # Do not retry. Log the error and fail.
    #     print("Upload Complete!")





class DB:
    def __init__(self):
        self.conn = sql.connect(Config.db)
        self.conn.isolation_level = None
        self.cursor = self.conn.cursor()
        self.verify()

    def verify(self):
        cmds = [
            'CREATE TABLE IF NOT EXISTS folders(id TEXT PRIMARY KEY, path TEXT UNIQUE, parent TEXT ,name TEXT);',
            'CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY, name TEXT, path TEXT UNIQUE,' \
            ' remote_size INTEGER, local_size INTEGER, parent TEXT, need_download INT);',
            'CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY , start_token TEXT,'
            ' last_check_time TEXT, first_run INT);',
            'SELECT * FROM state WHERE id = 0'
            ]
        for cmd in cmds:
            self.execute(cmd)
        state_rows = self.cursor.fetchall()
        if state_rows.__len__() == 0:
            cmd = "INSERT INTO state VALUES(0,'0', 'never', 1)"
            self.execute(cmd)

    def close(self):
        self.conn.close()

    def execute(self, cmd):
        self.cursor.execute(cmd)

    def set_last_check_date(self):
        cmd = "UPDATE state SET last_check_time=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE id = 0;"
        self.execute(cmd)

    def get_last_check_date(self):
        cmd = "SELECT last_check_time FROM state WHERE id = 0;"
        self.execute(cmd)
        return self.cursor.fetchone()[0]

    def set_start_token(self, start_token):
        cmd = """UPDATE state SET start_token="{}" WHERE id = 0;""".format(start_token)
        self.execute(cmd)

    def get_start_token(self):
        cmd = "SELECT start_token FROM state WHERE id = 0;"
        self.execute(cmd)
        return self.cursor.fetchone()[0]

    def set_first_run(self, true_false):
        cmd = """UPDATE state SET first_run = {};""".format(int(true_false))
        self.execute(cmd)

    def get_first_run(self):
        cmd = "SELECT first_run FROM state WHERE id = 0;"
        self.execute(cmd)
        return bool(self.cursor.fetchone()[0])

    def add_file(self, file_objects):
        if type(file_objects) is File:
            file_objects = [file_objects]
        bar = Bar('Adding files', max=len(file_objects))
        for fo in file_objects:
            cmd = "INSERT OR REPLACE INTO files VALUES('{}','{}','{}',{},{},'{}',{});".format(
                fo.id, fo.name, fo.path, fo.remote_size, fo.local_size, fo.parent, int(fo.needs_download))
            # print(cmd)
            self.execute(cmd)
            bar.update()
        bar.finish()

    def add_folder(self, folder_objects):
        if type(folder_objects) is Folder:
            folder_objects = [folder_objects]
        bar = Bar('Adding folders', max=len(folder_objects))
        for fo in folder_objects:
            cmd = "INSERT OR REPLACE INTO folders VALUES('{}','{}','{}','{}');".format(fo.id, fo.path, fo.parent, fo.name)
            self.execute(cmd)
            bar.update()
        bar.finish()

    def remove_file(self, file_objects): # take id, obj, or array
        if type(file_objects) is str:
            cmd = "DELETE from files WHERE id = '{}';".format(file_objects)
            self.execute(cmd)
            return
        if type(file_objects) is File:
            file_objects = [file_objects]
        bar = Bar('Removing files', max=len(file_objects))
        for fo in file_objects:
            cmd = "DELETE from files WHERE id = '{}';".format(fo.id)
            self.execute(cmd)
            bar.update()
        bar.finish()

    def remove_folder(self, folder_objects): # take id, obj, or array
        if type(folder_objects) is str:
            cmd = "DELETE from folders WHERE id = '{}';".format(folder_objects)
            self.execute(cmd)
            return
        if type(folder_objects) is Folder:
            folder_objects = [folder_objects]
        bar = Bar('Removing folders', max=len(folder_objects))

        for fo in folder_objects:
            cmd = "DELETE from folders WHERE id = '{}';".format(fo.id)
            self.execute(cmd)
            bar.update()
        bar.finish()

    def remove_all_data(self):
        self.execute("DROP TABLE IF EXISTS files ;")
        self.execute("DROP TABLE IF EXISTS folders ;")
        self.execute("DROP TABLE IF EXISTS state ;")

    def get_file(self, file_id):
        cmd = """SELECT name,id,parent,path,remote_size from files WHERE id = "{}";""".format(file_id)
        self.execute(cmd)
        fi = self.cursor.fetchone()
        return File(fi[0], fi[1], fi[2], fi[3], fi[4])

    def get_folders(self):
        cmd = "SELECT id, path, parent, name FROM folders;"
        self.execute(cmd)
        folders = self.cursor.fetchall()
        folder_dict = {}
        if folders:
            for fo in folders:
                folder_object = Folder(fo[3], fo[0], fo[2])
                folder_object.get_included()
                folder_object.subfolders = self.get_subfolders(folder_object)
                folder_dict[fo[0]] = folder_object
        return folder_dict

    def get_subfolders(self, folder_object):
        cmd = """SELECT id FROM folders WHERE parent = "{}";""".format(folder_object.id)
        self.execute(cmd)
        results = self.cursor.fetchall()
        subs = []
        if results:
            for res in results:
                subs.append(res[0])
        return subs

    def get_downloads(self):
        cmd = "SELECT name, id, parent, path, remote_size FROM files WHERE need_download = 1;"
        self.execute(cmd)
        files = self.cursor.fetchall()
        file_dict = {}
        if files:
            for fi in files:
                file_object = File(fi[0], fi[1], fi[2], fi[3], fi[4])
                file_dict[fi[0]] = file_object
        return file_dict

class Downloader:
    def __init__(self):
        self.db = DB()
        self.drive = Drive()
        tst_id = '0ByxWOPrynoZYNGtOdVF4NHUtUFk'# <-172mb  3gb-> '0ByxWOPrynoZYdXhyRWlYMnhBS0k'
        self.drive.download_file(tst_id)
        # self.downloads = self.db.get_downloads()
        # for dl in self.downloads:
        #     self.download(dl)

    def download(self, dl):
        print(dl.__dict__)


class ChangeWatcher:
    def __init__(self):
        self.db = DB()
        self.drive = Drive()
        self.get_changes()

    def get_changes(self):
        self.drive.get_changes()

class File:
    def __init__(self, name, id, parent, path, remote_size):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = os.path.join(path, name)
        self.remote_size = remote_size
        self.local_exists = None
        self.local_size = 0
        self.tmp_path = None
        self.local_path = None
        self.needs_download = False
        self.check()

    def check(self):
        if Config.use_remote_subfolder:
            self.local_path = self.path.replace(Config.remote_subfolder, Config.local_path)
        else:
            self.local_path = os.path.join(Config.local_path, self.path)

        if not os.path.exists(self.local_path):
            self.local_exists = False
            self.needs_download = False
        else:
            self.local_exists = True
            self.local_size = os.path.getsize(self.local_path)
            if self.local_size != self.remote_size:
                self.needs_download = True
        self.tmp_path = os.path.join(Config.tmp_path, "{}.tmp".format(self.id))

    @classmethod
    def test_files(cls, num):
        files = []
        for i in range(1, num):
            i_str = str(i)
            f = File("name"+i_str, "id"+i_str,"parent"+i_str,"path"+i_str, 1000*i)
            f.local_exists = False
            f.local_size = 0
            f.path = os.path.join(Config.remote_subfolder,f.path)
            f.local_path = f.path.replace(Config.remote_subfolder, Config.local_path)
            f.tmp_path = f.path.replace(Config.remote_subfolder, Config.tmp_path)
            f.needs_download = True
            files.append(f)

        return files

    # @classmethod
    # def

class Folder:
    def __init__(self, name, id, parent):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = None
        self.subfolders = []
        self.included = None

    def get_included(self):
        try:
            if not Config.use_remote_subfolder:
                self.included = True
            elif self.path.startswith(Config.remote_subfolder):
                self.included = True
            else:
                self.included = False
        except AttributeError:
            self.included = False




if __name__ == '__main__':
    Main()


