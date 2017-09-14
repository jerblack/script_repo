#!/usr/bin/python3


"""
    this portion of the program will directly query google drive for any new file changes that have occurred 
    it should have the ability to 
        authenticate user to google drive
        use minimum permissions necessary
        get start token from google
        save start token to file or db
        query for changes
        convert the response into a file path and write the file path into the db with a status of new
        save received start token into file
        
    1st option: check for new files every few minutes
        we can check more often since this appears to be a light touch operation
        every 30 minutes?
        check using start token from file
        
    2nd option:
        watch for changes, registering to receive notifications so updates occur in realtime
    
"""

import httplib2, os, sys, time, psutil
from pprint import pprint
from apiclient import discovery
from oauth2client import file, client, tools
from subprocess import Popen, PIPE, call
from multiprocessing import Pool as ThreadPool



class Config:
    scope = 'https://www.googleapis.com/auth/drive.metadata.readonly'
    client_secret = 'client_secrets.json'
    client_credentials = 'credentials.json'
    app_name = 'wormhole-file-transfer'

"""
    get list of all files
    cache those files to a db
    get changes token
        save to db
    query for changes
    convert new changes to file paths
    write new file objects with paths to db with status of new

"""


class DB:
    pass
    """
        write file to db
        write folder to db
        remove file from db
        remove folder from db
    """


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
            pageSize=8, fields="nextPageToken, files(name, id, mimeType, parents, trashed)").execute()
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
            # pprint(items)
            return items[0]['parents'][0]

    def get_dupes(self):
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
            results = self.service.files().list(q="mimeType!='application/vnd.google-apps.folder' and trashed=false",
                                                pageSize=1000, pageToken=next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                for item in items:
                    # self.folders[item['id']] = Folder(item['name'], item['id'], item['parents'][0])
                    if item['name'] not in self.name_counts:
                        self.name_counts[item['name']] = 0
                    self.name_counts[item['name']] += 1
                # self.dupes.append(item['name'])

            if next_page_token is None:
                break

        for k, v in self.name_counts.items():
            if v > 1:
                self.dupes.append(k)
        pprint(self.dupes)
        # print("Number of folders {}".format(self.folders.__len__()))
        # for name, obj in self.folders.items():
        #     if obj.parent != "" and obj.parent in self.folders:
        #         self.folders[obj.parent].subfolders.append(obj.id)
        #     else:
        #         print("obj.parent {} not found in self.folders with name {}".format(obj.parent, obj.name))
        # build_paths()



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
                                                pageSize=1000, pageToken = next_page_token, spaces='drive',
                                                fields="nextPageToken, files(name, id, parents)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                for item in items:
                    if item['id'] not in self.folders:
                        self.folders[item['id']] = Folder(item['name'], item['id'], item['parents'][0])

            if next_page_token is None:
                break
        # print("Number of folders {}".format(self.folders.__len__()))
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
                                                fields="nextPageToken, files(name, id, parents)").execute()
            items = results.get('files', [])
            next_page_token = results.get("nextPageToken")
            if items:
                for item in items:
                    self.files[item['id']] = File(item['name'],
                                                  item['id'],
                                                  item['parents'][0],
                                                  self.folders[item['parents'][0]].path)
                    self.paths[item['id']] = self.files[item['id']].path
            if next_page_token is None:
                break
        # pprint(self.files)
        print("Number of files {}".format(self.files.__len__()))

    def get_start_token(self):
        # 44565644
        # results = self.service.changes().getStartPageToken().execute()
        # self.start_token = results.get("startPageToken")
        self.start_token = 44565644

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
    def __init__(self, name, id, parent, path):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = os.path.join(path, name)

class Folder:
    def __init__(self, name, id, parent):
        self.name = name
        self.id = id
        self.parent = parent
        self.path = None
        self.subfolders = []

class Plex:
    def __init__(self):
        proc = self._get_plex()
        self.pid = proc['pid']
        self.name = proc['name']
        self.user = proc['username']
        self.uid = proc['uid']
        self.gid = proc['gid']
        self.env = proc['environ']
        self.app_dir = proc['environ']['PLEX_MEDIA_SERVER_HOME']
        self.scanner = os.path.join(self.app_dir, 'Plex Media Scanner')
        self.sections = []
        self._need_sudo()
        # self._get_sections()
        # self.scan_at_once = 3
        # self.analyze_at_once = 3

    @staticmethod
    def _get_plex():
        for proc in psutil.process_iter():
            try:
                if proc.name() == 'Plex Media Server':
                    proc_details = proc.as_dict(attrs=['pid', 'name', 'username', 'gids', 'uids', 'environ'])
                    proc_details['uid'] = proc_details['uids'][0];
                    del proc_details['uids']
                    proc_details['gid'] = proc_details['gids'][0];
                    del proc_details['gids']
                    print(proc_details)
                    return proc_details
            except psutil.NoSuchProcess:
                pass
        return None

    def _need_sudo(self):
        if os.getuid() == self.uid:
            return
        if os.getuid() != 0:
            cmd = ['sudo', '/usr/bin/python3', sys.argv[0]]
            ex_code = call(cmd)
            exit(ex_code)

    def _demote(self):
        def result():
            os.setgid(self.gid)
            os.setuid(self.uid)

        return result

    def _get_sections(self):
        cmd = [self.scanner, '-l']
        with Popen(cmd, preexec_fn=self._demote(), cwd=self.app_dir, env=self.env, stdout=PIPE) as proc:
            for line in proc.stdout:
                id, name = line.__str__()[2:-3].rstrip().lstrip().split(': ')
                self.sections.append((id, name))

    def _scan_section(self, section):
        id, name = section
        cmd = [self.scanner, '--scan', '--refresh', '--section', id]
        sys.stdout.write("Begin scanning section {}: {}\n".format(id, name))
        p = Popen(cmd, preexec_fn=self._demote(), cwd=self.app_dir, env=self.env)
        p.wait()

    def scan(self):
        pool = ThreadPool(self.scan_at_once)
        pool.map(self._scan_section, self.sections)
        pool.close()
        pool.join()

    def _analyze_section(self, section):
        id, name = section
        cmd = [self.scanner, '--analyze', '--section', id, '--log-file-suffix', 'Analysis']
        sys.stdout.write("Begin analyzing section {}: {}\n".format(id, name))
        p = Popen(cmd, preexec_fn=self._demote(), cwd=self.app_dir, env=self.env)
        p.wait()

    def analyze(self):
        pool = ThreadPool(self.analyze_at_once)
        pool.map(self._analyze_section, self.sections)
        pool.close()
        pool.join()

def start():
    if os.getuid() != 0:
        cmd = ['sudo', '/usr/bin/python3', sys.argv[0]]
        call(cmd)
    else:
        plex = Plex()
        if Config.scan:
            plex.scan()
        if Config.analyze:
            plex.analyze()



if __name__ == '__main__':
    # google = Google()
    # google.do_auth()
    print("started")
    print(time.asctime())
    drive = Drive()
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