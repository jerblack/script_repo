#!/usr/bin/python3


"""
hole patcher 2

faster, stores state, no longer needs full scan, uses changes api


on start
    call config_loader
    if no db or no start token in db or config.first_run = true in db
        do first run
    start change watcher thread
    start download_controller thread
        start Config.download_threads number of individual download threads


        


1st run   
    - enumerate all google drive files using new drive class
    - get array of all files
        - to allow starting from subfolder, only add files to array that have base folder in path
        - include size in bytes from google, as well as google_path, local_tmp_path, local_final_path, id, name
            local_incoming_path inserts a .tmp folder at the base of the target path to ensure they are on the 
                same spindle
            - check if local file doesn't exist or if local size != google_size
                    mark file as needs download if so
        - local_path should just replace google specific portion of substring with local specific substring
        - add all files to db
    save start token to db
    set config.first_run to false in db

change_watcher thread
    every config.interval
    - get changes since last run
        if changes
        - convert to files, add files to db, compare files with local, mark download needed = true in db if necessary    
        - save new start token to db

downloader thread
    main thread
        checks db for files marked need_download, creates queue of objects with info needed to download file and
            update db (google_path, local_path, id)
        keep running tally of bytes, use in log to show total bytes remaining, subtract file bytes from total bytes as 
            files is few into download thread
    
    downloader thread
        os.makedirs(os.path.dirname(local_tmp_path), exist_ok=True)
        spawns rsync with command line ['rsync', '-avmW', google_path, local_tmp_path]
        os.rename successful download from local_tmp_path to local_final_path
        mark file in db as download needed = False (update file by id)
        repeat every 30 seconds
        
    - for all files in file db marked needs download
        use multithreaded download using rsync from google path to local path
            as successfully download, mark as completed in db
    
    




"""

import httplib2, os, sys, time, functools, signal, subprocess, shutil
import sqlite3 as sql
from pprint import pprint
from apiclient import discovery
from oauth2client import file, client, tools
from subprocess import Popen, PIPE, call
from multiprocessing import Pool as ThreadPool
from enum import Enum


class Config:
    scope = 'https://www.googleapis.com/auth/drive.metadata.readonly'
    client_secret = 'client_secrets.json'
    client_credentials = 'credentials.json'
    app_name = 'hole_patcher'
    downloader_interval = 30
    change_watcher_interval = 15 * 60  # 15 minutes
    active = False
    use_remote_subfolder = True
    remote_subfolder = "/backup/"
    # local_base_path = "/home/jeremy/server_z/_media/"
    local_base_path = "."
    local_tmp_path = os.path.join(local_base_path, '.tmp') + '/'
    config_folder = os.path.join(os.path.expanduser('~'),
                                 '.{}'.format(app_name))
    db = os.path.join(config_folder, app_name+'.db')


class DB:
    def __init__(self):
        self.conn = sql.connect(Config.db)
        self.conn.isolation_level = None
        self.cursor = self.conn.cursor()
        self.verify()

    def close(self):
        self.conn.close()

    def execute(self, cmd):
        self.cursor.execute(cmd)

    def verify(self):
        cmds = [
            'CREATE TABLE IF NOT EXISTS folders(id TEXT PRIMARY KEY, path TEXT UNIQUE, parent TEXT ,name TEXT);',
            'CREATE TABLE IF NOT EXISTS files(id TEXT PRIMARY KEY, name TEXT, path TEXT UNIQUE,' \
            ' remote_size INTEGER, local_size INTEGER, need_download BOOLEAN, parent TEXT);',
            'CREATE TABLE IF NOT EXISTS state(id INTEGER PRIMARY KEY , start_token TEXT,'
            ' last_check_date TEXT, first_run BOOLEAN);',
            'SELECT * FROM state WHERE id = 0'
            ]
        for cmd in cmds:
            self.execute(cmd)
        state_rows = self.cursor.fetchall()
        if state_rows.__len__() == 0:
            cmd = "INSERT INTO state VALUES(0,'0', 'never', 1)"
            self.execute(cmd)

    def remove_all_data(self):
        cmds = [
            "DELETE FROM files;",
            "DELETE FROM folders;"
        ]
        for cmd in cmds:
            self.execute(cmd)

    def update_last_check_date(self):
        cmd = "UPDATE state SET last_check_date=datetime(CURRENT_TIMESTAMP, 'localtime') WHERE id = 0"
        self.execute(cmd)

    def get_last_check_date(self):
        cmd = "SELECT last_check_date FROM state WHERE id = 0;"
        self.execute(cmd)
        return self.cursor.fetchone()[0]

    def set_start_token(self, start_token):
        cmd = """UPDATE state SET start_token="{}" WHERE id = 0""".format(start_token)
        self.execute(cmd)

    def get_start_token(self):
        cmd = "SELECT start_token FROM state WHERE id = 0;"
        self.execute(cmd)
        return self.cursor.fetchone()[0]

    def not_first_run(self):
        cmd = """UPDATE state SET first_run = 0 """
        self.execute(cmd)

    def get_first_run(self):
        cmd = "SELECT first_run FROM state WHERE id = 0;"
        self.execute(cmd)
        return bool(self.cursor.fetchone()[0])

    def add_file(self, file_object):
        fo = file_object
        cmd = "INSERT OR REPLACE INTO files VALUES('{}','{}','{}',{},{},{}, '{}');".format(
                fo.id, fo.name, fo.path, fo.remote_size, fo.local_size, int(fo.needs_download), fo.parent)
        # print(cmd)
        self.execute(cmd)

    def add_files(self, file_array):
        for fo in file_array:
            cmd = "INSERT OR REPLACE INTO files VALUES('{}','{}','{}',{},{},{},'{}');".format(
                fo.id, fo.name, fo.path, fo.remote_size, fo.local_size, int(fo.needs_download), fo.parent)
            self.execute(cmd)

    def add_folder(self, folder_object):
        fo = folder_object
        cmd = "INSERT OR REPLACE INTO folders VALUES('{}','{}', '{}', '{}');".format(
                fo.id, fo.path, fo.parent, fo.name)
        # print(cmd)
        self.execute(cmd)

    def add_folders(self, folder_array):
        for fo in folder_array:
            cmd = "INSERT OR REPLACE INTO folders VALUES('{}','{}','{}','{}');".format(fo.id, fo.path, fo.parent, fo.name)
            self.execute(cmd)

    def remove_file(self, file_object):
        cmd = "DELETE from files WHERE id = '{}';".format(file_object.id)
        self.execute(cmd)

    def remove_files(self, file_array):
        for fo in file_array:
            cmd = "DELETE from files WHERE id = '{}';".format(fo.id)
            self.execute(cmd)

    def remove_folder(self, folder_object):
        cmd = "DELETE from folders WHERE id = '{}';".format(folder_object.id)
        self.execute(cmd)

    def remove_folders(self, folder_array):
        for fo in folder_array:
            cmd = "DELETE from folders WHERE id = '{}';".format(fo.id)
            self.execute(cmd)

    def get_download_needed(self):
        cmd = "SELECT id, name, path, remote_size, local_size, parent FROM files WHERE need_download = 1;"
        self.execute(cmd)
        files = self.cursor.fetchall()
        file_array = []
        if files:
            for fi in files:
                f = File(fi[1], fi[0], fi[5], fi[2], fi[3])
                f.local_final_path = os.path.join(Config.local_base_path,
                                                  f.path)
                f.local_tmp_path = f.local_final_path.replace(Config.local_base_path,
                                                              Config.local_tmp_path)
                f.local_exists = os.path.exists(f.local_final_path)
                if f.local_exists:
                    f.local_size = os.path.getsize(f.local_final_path)
                f.needs_download = True
                file_array.append(f)
        return file_array

    def make_dls(self, num):
        cmd = """ UPDATE files 
                  SET need_download = 1 
                  WHERE id in 
                    (SELECT id 
                      FROM files
                      LIMIT {});""".format(num)
        self.execute(cmd)

    def set_download_needed(self, file_object, true_false):
        cmd = "UPDATE files SET need_download={} where id = '{}';".format(
            int(true_false), file_object.id)
        self.execute(cmd)


class Drive:
    def __init__(self):
        self.credentials = None
        self.get_creds()
        self.http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=self.http)
        self.root_id = self.get_root_id()
        self.folders = {
            'root': Folder("\\", self.root_id, "root"),
            self.root_id: Folder("\\", self.root_id, "root")
        }
        self.folders['root'].path = '/'
        self.paths = {}
        self.files = {}
        self.name_counts = {}
        self.dupes = []
        self.start_token = None
        # print(self.folders['root'].id)

    def get_creds(self):
        """
        Gets valid creds from storage.
        If nothing stored, or if creds invalid, OAuth2 flow used to get new creds.
        """
        store = file.Storage(Config.client_credentials)
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets(Config.client_secret, Config.scope)
            flow.user_agent = Config.app_name
            creds = tools.run_flow(flow, store)
        self.credentials = creds

    def list_8_files(self):
        results = self.service.files().list(q="'root' in parents",
                                            pageSize=8,
                                            fields="nextPageToken, files(name, id, mimeType, parents, trashed)").execute()
        items = results.get('files', [])
        nextPage = results.get("nextPageToken")
        print(nextPage)
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                pprint(item)

    def get_root_id(self):
        results = self.service.files().list(q="'root' in parents and trashed=false",
                                            pageSize=1,
                                            fields="files(id,name,parents)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            return items[0]['parents'][0]

    # def get_dupes(self):
    #     def build_paths(id=None, path=None):
    #         if not id:
    #             id = self.root_id
    #             path = '\\'
    #         self.folders[id].path = path
    #         self.paths[path] = id
    #         if self.folders[id].subfolders:
    #             for sub in self.folders[id].subfolders:
    #                 build_paths(sub, os.path.join(path, self.folders[sub].name))
    #
    #     next_page_token = None
    #     while True:
    #         results = self.service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false",
    #                                             pageSize=1000, pageToken=next_page_token, spaces='drive',
    #                                             fields="nextPageToken, files(name, id)").execute()
    #         items = results.get('files', [])
    #         next_page_token = results.get("nextPageToken")
    #         if items:
    #             for item in items:
    #                 # self.folders[item['id']] = Folder(item['name'], item['id'], item['parents'][0])
    #                 if item['name'] not in self.name_counts:
    #                     self.name_counts[item['name']] = 0
    #                 self.name_counts[item['name']] += 1
    #                 # self.dupes.append(item['name'])
    #
    #         if next_page_token is None:
    #             break
    #
    #     for k, v in self.name_counts.items():
    #         if v > 1:
    #             self.dupes.append(k)
    #     pprint(self.dupes)
    #     # print("Number of folders {}".format(self.folders.__len__()))
    #     # for name, obj in self.folders.items():
    #     #     if obj.parent != "" and obj.parent in self.folders:
    #     #         self.folders[obj.parent].subfolders.append(obj.id)
    #     #     else:
    #     #         print("obj.parent {} not found in self.folders with name {}".format(obj.parent, obj.name))
    #     # build_paths()

    def get_folders(self):
        def build_paths(id=None, path=None):
            if not id:
                id = self.root_id
                path = '\\'
            self.folders[id].path = path
            self.paths[path] = id
            if self.folders[id].subfolders:
                for sub in self.folders[id].subfolders:
                    build_paths(sub, os.path.join(path, self.folders[sub].name))

        next_page_token = None
        while True:
            results = self.service.files().list(q="mimeType='application/vnd.google-apps.folder' and trashed=false",
                                                pageSize=1000, pageToken=next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id, parents)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                for item in items:
                    if item['id'] not in self.folders:
                        self.folders[item['id']] = Folder(item['name'], item['id'], item['parents'][0])

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
        while True:
            results = self.service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false",
                                                pageSize=1000, pageToken=next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id, parents, size)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                for item in items:
                    self.files[item['id']] = File(item['name'],
                                                  item['id'],
                                                  item['parents'][0],
                                                  self.folders[item['parents'][0]].path,
                                                  int(item['size']))
            if next_page_token is None:
                break
        print("Number of files {}".format(self.files.__len__()))

    def get_start_token(self):
        # 44565644
        # results = self.service.changes().getStartPageToken().execute()
        # self.start_token = results.get("startPageToken")
        self.start_token = 44565644
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

        # def handle_change


class File:
    def __init__(self, name, id, parent, path, size):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = os.path.join(path, name)
        self.remote_size = size
        self.local_exists = None
        self.local_size = None
        self.local_tmp_path = None
        self.local_final_path = None
        self.needs_download = False

    @classmethod
    def test_files(cls, num):
        files = []
        for i in range(1,num):
            i_str = str(i)
            f = File("name"+i_str, "id"+i_str,"parent"+i_str,"path"+i_str, 1000*i)
            f.local_exists = False
            f.local_size = 0
            f.path = os.path.join(Config.remote_subfolder,f.path)
            f.local_final_path = f.path.replace(Config.remote_subfolder, Config.local_base_path)
            f.local_tmp_path = f.path.replace(Config.remote_subfolder, Config.local_tmp_path)
            f.needs_download = True
            files.append(f)

        return files


class Folder:
    def __init__(self, name, id, parent):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = None
        self.subfolders = []

    @classmethod
    def test_folders(cls, num):
        folders = []
        for i in range(1, num+1):
            i_str = str(i)
            f = Folder("name"+i_str, "id"+i_str, "parent"+i_str)
            f.path = os.path.join(Config.remote_subfolder, f.name)
            folders.append(f)
        return folders


class Kind(Enum):
    downloader = 1
    queuer = 2
    change_watcher = 3
    main = 0


class Colors:
    pink = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    white = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


class say:
    def __init__(self, kind, text):
        self.kind = kind

        if type(text) is not str:
            self.text = str(text)
        else:
            self.text = text
        self.say()

    def say(self):
        if self.kind == Kind.downloader:
            prefix = Colors.red + "[DOWNLOADER][{}][{} free]". \
                format(say.get_time(), say.get_free_space())
        elif self.kind == Kind.queuer:
            prefix = Colors.green + "[QUEUER][{}][{} free]". \
                format(say.get_time(), say.get_free_space())
        elif self.kind == Kind.change_watcher:
            prefix = Colors.yellow + "[CHANGE WATCHER][{}][{} free]". \
                format(say.get_time(), say.get_free_space())
        else:
            prefix = Colors.blue + "[MAIN][{}][{} free]".format(say.get_time(), say.get_free_space())
        msg = "{} {}".format(prefix, self.text) + Colors.end
        sys.stdout.write("\n" + msg + "\n")

    @staticmethod
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_free_space():
        # st = os.statvfs(Config.local_tmp_path)
        # free = st.f_bavail * st.f_frsize
        total, used, free = shutil.disk_usage(Config.local_base_path)
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if free >= prefix[s]:
                value = float(free) / prefix[s]
                return '%.1f%sB' % (value, s)
        return "%sB" % free

    @staticmethod
    def get_folder_size(folder):
        return os.popen("du -hs {}".format(folder)).read().split('\t')[0]


class run:
    def __init__(self, cmd, get_stdout=True):
        self.kind = Kind.main
        self.say = functools.partial(say, Kind.uploader)
        self.cmd = cmd
        self.result = None
        if get_stdout:
            self._stdout()
        else:
            self._ex_code()

    def _ex_code(self):
        if Config.active:
            try:
                self.result = subprocess.call(self.cmd)
            except TypeError:
                say(Kind.main, "Run called with empty cmd")
                self.result = 1
        else:
            say(Kind.main, "Run called with {}".format(self.cmd.__str__()))
            self.result = 0

    def _stdout(self):
        if Config.active:
            try:
                self.result = subprocess.check_output(self.cmd)
            except subprocess.CalledProcessError as e:
                self.say("ERROR: {}".format(e))
        else:
            say("Run called with {}".format(self.cmd.__str__()))
            self.result = None

    def get_result(self):
        return self.result

class Main():
    def __init__(self):
        say(Kind.main, "Starting hole patcher")
        Main.verify_config_folder()
        self.db = DB()
        self.drive = Drive()
        self.start()

    def start(self):
        print("hello")
        # self.first_run()
        self.get_all_files()

    @staticmethod
    def verify_config_folder():
        os.makedirs(Config.config_folder, exist_ok=True)

    def first_run(self):
        if self.db.get_start_token() == '0' or self.db.get_first_run():
            self.db.remove_all_data()
            self.get_all_files()
        self.db.not_first_run()

    def get_all_files(self):
        say(Kind.main, "setting start token")
        self.db.set_start_token(self.drive.get_start_token())
        # self.db.set_start_token("44565645")
        # say(Kind.main, "get_folders")
        # self.drive.get_folders()
        # say(Kind.main, "get_files")
        # self.drive.get_files()
        # say(Kind.main, "adding folders to db")
        # for folder in self.drive.folders.values():
        #     try:
        #         if Config.remote_subfolder in folder.path:
        #             self.db.add_folder(folder)
        #     except TypeError:
        #         print("problem folder")
        #         print(folder.__dict__)
        #
        # say(Kind.main, "adding files to db")
        # for fil in self.drive.files.values():
        #     try:
        #         if Config.remote_subfolder in fil.path:
        #             self.db.add_file(fil)
        #     except TypeError:
        #         print("problem file")
        #         print(fil.__dict__)





if __name__ == '__main__':
    Main()

    # drive.list_8_files()
    # drive.get_folders()
    # print("finished folders")
    # print(time.asctime())
    # drive.get_files()
    # print("finished files")
    # print(time.asctime())
    # drive.get_start_token()
    # print(drive.start_token)
    # drive.get_changes()
    # drive.get_dupes()