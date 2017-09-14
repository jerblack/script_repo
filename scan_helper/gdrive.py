from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from pydrive.files import GoogleDriveFile
from pydrive.files import MediaIoBaseUpload
import os, logging
import pprint
import httplib2

src_folder = r'd:/test'
gdrive_portal_root = 'portal'
test_file = r'd:/test/b/plans.rar'
move = True


def DeleteFile(self):
    try:
        self.auth.service.files().delete(fileId=self['id']).execute()
    except errors.HttpError, error:
        print('An error occurred: %s' % error)
GoogleDriveFile.Delete = DeleteFile

def _BuildMediaBody(self):
    """Build MediaIoBaseUpload to get prepared to upload content of the file.
    Sets mimeType as 'application/octet-stream' if not specified.
    :returns: MediaIoBaseUpload -- instance that will be used to upload content.
    """
    if self.get('mimeType') is None:
      self['mimeType'] = 'application/octet-stream'
    return MediaIoBaseUpload(self.content, self['mimeType'], resumable=True)

GoogleDriveFile._BuildMediaBody = _BuildMediaBody

def start():
    # httplib2.debuglevel = 1
    g = Drive()
    # g.create_folder('/fourt/2/3/asd/3y3y56/fsss/565/sdsfdsf/2222/')
    # g.upload_file(test_file)
    pprint.pprint(dir(g.auth.service))

class GoogleDriveFile:
    def __init__(self, title, id, is_folder, parent_id):
        self.title = title
        self.id = id
        self.parent_id = parent_id
        self.parent_ids = []
        self.path = ''
        self.isFolder = is_folder
        self.files = []
        self.isRoot = False


class Drive:
    # root_id = 0
    root_id = '0ByxWOPrynoZYVHJHYW5sMjR3UFE'

    # Creates local webserver and auto handles authentication
    def __init__(self):
        self.auth = GoogleAuth()
        self.auth.LocalWebserverAuth(port_numbers=[8080, 8123])
        self.drive = GoogleDrive(self.auth)
        self.root_id = self._get_root_id()
        self.root = self._get_root()
        self.paths = {}
        self.ids = {}
        self.folders = {}

    def dir(self, folder_id=0, path=0, parents=[]):
        if folder_id == 0:
            logging.info('Now enumerating files in portal folder.')
            folder_id = self.root_id
            self.root.files = self.dir(folder_id, '/', [])
            return self.root.files
        else:
            logging.info('Enumerating files in: '+path)
            files = []
            query = "'" + folder_id + "' in parents and trashed=False"
            file_list = self.drive.ListFile({'q': query}).GetList()
            for f in file_list:
                gf = GoogleDriveFile(f['title'], f['id'], False, f['parents'][0]['id'])
                gf.parent_ids = parents
                gf.parent_ids = [gf.parent_id] + gf.parent_ids
                gf.path = path + gf.title
                self.paths[gf.path] = gf.id
                self.ids[gf.id] = gf.path
                if f['mimeType'] == "application/vnd.google-apps.folder":
                    gf.isFolder = True
                    self.folders[gf.path] = gf.id
                    gf.files = self.dir(f['id'], gf.path + '/', gf.parent_ids)
                files.append(gf)
            return files

    def _get_root_id(self):
        if not self.root_id:
            query = "title='" + gdrive_portal_root + "' and " + \
                    "'root' in parents and trashed=false and" + \
                    "mimeType='application/vnd.google-apps.folder'"
            f = self.drive.ListFile({'q': query}).GetList()
            if len(f):
                return f[0]['id']
            else:
                f = self.drive.CreateFile(
                    {'title': gdrive_portal_root,
                     'mimeType': "application/vnd.google-apps.folder"})
                f.Upload()
                return self._get_root_id()
        else:
            return self.root_id

    def _get_root(self):
        root = GoogleDriveFile(gdrive_portal_root, self._get_root_id(), True, 0)
        return root

    def _get_path(self, id):
        if not self.ids:
            self.dir()
        if id == self.root_id:
            return '/'
        return self.ids[id]

    def _get_id(self, path):

        if not self.paths:
            self.dir()
        if path == '/':
            return self.root_id
        return self.paths[path]

    def _get_parent_id(self, id):
        path = self._get_path(id)
        return self._get_id(os.path.split(path)[0])

    def _file_exists(self, path):
        if not self.paths:
            self.dir()
        return path in self.paths

    def create_folder(self, path):
        if not self.paths:
            self.dir()
        if path == '/':
            return self.root_id
        else:
            if path.endswith('/'):
                path = path[:-1]
            if not path.startswith('/'):
                path = '/' + path
        if path not in self.paths:
            parent = self.create_folder(os.path.split(path)[0])
            params = {
                'title': os.path.split(path)[1],
                'parents': [{'id': parent}],
                'mimeType': "application/vnd.google-apps.folder"
            }
            folder = self.drive.CreateFile(params)
            folder.Upload()
            self.ids[folder['id']] = path
            self.paths[path] = folder['id']
            return folder['id']
        else:
            return self.paths[path]

    def upload_file(self, path):
        rel_path = path.replace(src_folder, '')
        logging.info('Upload called on '+rel_path)
        if os.path.exists(path):
            if not self.paths:
                self.dir()
            if rel_path not in self.paths:
                parent = self.create_folder(os.path.split(rel_path)[0])
                title = os.path.split(rel_path)[1]
                params = {
                    'title': title,
                    'parents': [{'id': parent}],
                }
                f = self.drive.CreateFile(params)
                f.SetContentFile(path)
                logging.info('Uploading file ' + rel_path)
                f.Upload()
                self.ids[f['id']] = rel_path
                self.paths[rel_path] = f['id']
            else:
                logging.warning('File already exists in cloud '+rel_path)

        else:
            print logging.warning(rel_path+' not found')


    def remove_empty_folders(self):
        pass


# move specified file to folder on Google Drive

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info('Starting portal-gun uploader')
    start()
