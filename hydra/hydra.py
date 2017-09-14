#!/usr/bin/python3

import os, subprocess, sys, functools, time, signal, shutil, socket, sqlite3, logging
from os import walk
from os.path import join, splitext, exists
from multiprocessing import Pool as ThreadPool
from threading import Thread
from enum import Enum

from pprint import pprint


"""
    Hydra handles importing, encrypting, and uploading newly downloaded files to three different accounts
    - each major function runs in a separate thread
        - importer
            - watches import folder and moves new files into decrypted view
              of an enc_fs mount
            - this is slow because it's moving the files from an SMB mount so
              the files are not moved into their final destination folder directly
            - if the free space on the target disk drops to a certain level (100GB), the import
              process is paused
            - once the move process is complete, the files are all renamed into
              their final destination folder which is on the same disk
            - files are imported in batches of 30 to ensure the upload folder always has
              files to work on

        - uploader
            - there are two versions of the uploader, one for Google Drive and one
              for Amazon Cloud Drive
              - ACD is handled by wrapping acd_cli
              - Google Drive is handled by wrapping gdrive
            - the uploader uploads to 2 Google Drive accounts and one ACD account
            - On successful upload, a marker file is created with the same name as
              the file with an additional marker extension [fil_name.txt.acd]
            - On failure, not happens, it just moves on to try again later once
              the batch starts over
            - there are 3 different download threads for each of the 3 accounts
              this means 9 simultaneous uploads across two different services,
              which is usually able to max out my upload channel on my gigabit
              fiber connection

        - cleaner
            - periodically scans the upload folder for files that have all three
              markers, meaning the file was successfully uploaded to all three services
            - if all three markers are present, the file and the markers are all deleted
            - orphan markers are also scanned for (markers with no companion file) and removed


"""

class Config:
    progress_markers = ('.gdc', '.gds')
    # progress_markers = ('.gdc', '.gds', '.acd')
    server = socket.gethostname()
    # accts = ('gdc', 'gds', 'acd')
    accts = ('gdc', 'gds',)
    # accts = ('acd',)
    base_path = "backup/"
    base_id = {
        'gdc': '0ByxWOPrynoZYdkVGZWY2aEJEUmc',
        'gds': '0Bw-qGjy25G3YRWVRa25vVkRyMlk'
    }
    acd_config = "/home/jeremy/.cache/acd_cli/"
    acd_clean_interval = 10
    acd_sync = False
    bad_path_file = 'bad_paths'
    acd_failed_file = join(acd_config, 'acd_failed')
    gd_config = "/home/jeremy/.gdrive/"
    active = True
    debug = False
    interval = 10  # seconds
    acd_max_size = 50 * 1024 * 1024 * 1024  # 50GB
    if server == "vm":
        import_src = "/home/jeremy/smb/server.z/_work/ul_archive"
        import_dst = "/home/jeremy/_work/copying_dec"
        stage_src = "/home/jeremy/_work/copying_enc"
        upload_src = "/home/jeremy/_work/archive_enc"
        free_threshold = 200 * 1024 * 1024 * 1024  # 200GB
        batch = 30
        threads = 3
        import_threads = 3
    if server == "hydra":
        import_src = "/home/jeremy/island/_sorted"
        import_dst = "/home/jeremy/_import_dec"
        stage_src = "/home/jeremy/_import_enc"
        upload_src = "/home/jeremy/_upload"
        free_threshold = 60 * 1024 * 1024 * 1024  # 60GB
        batch = 100
        import_threads = 3
        threads = 3
    if server == "fortress":
        import_src = "/home/jeremy/hydra/_import_src"
        import_dst = "/home/jeremy/hydra/_import_dec"
        stage_src = "/home/jeremy/hydra/_import_enc"
        upload_src = "/home/jeremy/hydra/_upload_src"
        free_threshold = 60 * 1024 * 1024 * 1024  # 60GB
        batch = 3
        threads = 3
        import_threads = 1
    uploader_on = True
    importer_on = True
    cleaner_on = True
    log_file = os.path.join(os.path.dirname(sys.argv[0]), 'hydra_errors')

class Cache:
    google_ids = {
        'gdc': {},
        'gds': {}
    }
    gd_folder_ids = {
        'gdc': {},
        'gds': {}
    }
    gd_path_cache = {
        'gdc': {},
        'gds': {}
    }
    gd_paths = {
        'gdc': [],
        'gds': []
    }
    acd_path_cache = [Config.base_path]
    bad_paths = ['_gsdata_']
    list_count = 0
    acd_count = 0

class Kind(Enum):
    importer = 1
    uploader = 2
    cleaner = 3
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
        if self.kind == Kind.importer:
            prefix = Colors.red + "[IMPORT][{}][{} free][{} to import]". \
                format(say.get_time(), say.get_free_space(), say.get_folder_size(Config.import_src))
        elif self.kind == Kind.uploader:
            prefix = Colors.green + "[UPLOAD][{}][{} free][{} to upload]". \
                format(say.get_time(), say.get_free_space(), say.get_folder_size(Config.upload_src))
        elif self.kind == Kind.cleaner:
            prefix = Colors.yellow + "[CLEANER][{}][{} free][{} to upload]". \
                format(say.get_time(), say.get_free_space(), say.get_folder_size(Config.upload_src))
        else:
            prefix = Colors.blue + "[MAIN][{}][{} free]".format(say.get_time(), say.get_free_space())
        msg = "{} {}".format(prefix, self.text) + Colors.end
        sys.stdout.write("\n" + msg + "\n")

    @staticmethod
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_free_space():
        st = os.statvfs(Config.upload_src)
        free = st.f_bavail * st.f_frsize
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

def dbg(text):
    if Config.debug:
        sys.stdout.write(Colors.pink + text + Colors.end + "\n")

def start():
    say(Kind.main, "Hail Hydra")

    def go_uploader(acct):
        while True and Config.uploader_on:
            try:
                Upload(acct)
            except Exception as e:
                logger.exception(e)
            finally:
                pass
            time.sleep(Config.interval)
        say(Kind.main, "Uploader is disabled")

    def go_cleaner():
        while True and Config.cleaner_on:
            try:
                Cleaner()
            except Exception as e:
                logger.exception(e)
            finally:
                pass
            time.sleep(Config.interval)
        say(Kind.main, "Cleaner is disabled")

    def go_importer():
        while True and Config.importer_on:
            try:
                Importer()
            except Exception as e:
                logger.exception(e)
            finally:
                pass
            time.sleep(Config.interval)
        say(Kind.main, "Importer is disabled")

    def delay():
        if len(sys.argv) == 2:
            seconds = int(sys.argv[1])
            say(Kind.main, "Delaying startup by {} seconds".format(seconds))
            time.sleep(seconds)

    def threader():
        if Config.uploader_on:
            for acct in Config.accts:
                uploader = Thread(target=go_uploader, args=(acct,))
                uploader.setDaemon(True)
                say(Kind.uploader, "Starting {} uploader thread".format(acct.upper()))
                uploader.start()

        if Config.importer_on:
            imp = Thread(target=go_importer)
            imp.setDaemon(True)
            say(Kind.importer, "Starting Importer thread")
            say(Kind.importer, "Checking for new files every {} seconds.".format(Config.interval))
            imp.start()

        if Config.cleaner_on:
            cln = Thread(target=go_cleaner)
            cln.setDaemon(True)
            say(Kind.cleaner, "Starting Cleaner thread")
            cln.start()

    threader()
    delay()
    while True:
        signal.pause()


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

class Upload:
    def __init__(self, acct):
        self.acct = acct
        self.say = functools.partial(say, Kind.uploader)
        self.file_list = []
        try:
            self.threader()
        except Exception as e:
            logger.exception(e)
        finally:
            pass

    def threader(self):
        for root, dirs, files in walk(Config.upload_src):
            i = 1
            for name in files:
                if name[-4:] not in Config.progress_markers:
                    bad_file = False
                    for bp in Cache.bad_paths:
                        if bp in join(root, name):
                            bad_file = True

                    if not bad_file and not exists("{}.{}".format(join(root, name), self.acct)):
                        self.file_list.append((self.acct, join(root, name), i))
                        i += 1
        self.file_list = self.file_list[:Config.batch]
        num_files = self.file_list.__len__()
        for i in range(0, num_files):
            self.file_list[i] = self.file_list[i] + (num_files,)

        if self.file_list.__len__() > 0:
            if self.acct[0] == 'a':
                ACD.clean_acd(self.acct)
                ACD.check_acd_db()
                ACDFolders(self.file_list)
            if self.acct[0] == 'g':
                GoogleFolders(self.file_list, self.acct)

            pool = ThreadPool(Config.threads)
            pool.map(self.uploader, self.file_list)
            pool.close()
            pool.join()
            self.say("Finished uploading for {}".format(self.acct))

    def uploader(self, upload_details):
        try:
            acct, src_file, i, num_files = upload_details
            file_ext = splitext(src_file)[1]
            if file_ext not in Config.progress_markers:
                marker = "{}.{}".format(src_file, acct)
                if exists(src_file) and not exists(marker):
                    self.say("Uploading file to {} [{}/{}]\n  {}".format(acct.upper(), i, num_files, src_file))
                    # print(acct, src_file)
                    if acct[0] == 'g':
                        GoogleUploader(acct, src_file)
                    elif acct[0] == 'a':
                        ACDUploader(src_file)
        except Exception as e:
            logger.exception(e)
        finally:
            pass


class GoogleFolders:
    def __init__(self, file_list, acct):
        self.config = os.path.join(Config.gd_config, acct)
        self.kind = Kind.uploader
        self.say = functools.partial(say, Kind.uploader)
        self.acct = acct
        self.file_list = file_list
        self.folder_list = []
        self._process_list()

    def _process_list(self):
        for f in self.file_list:
            file_path = f[1].replace(Config.upload_src, Config.base_path[:-1])
            folder = os.path.dirname(file_path)
            folder_parts = folder.split('/')
            path_inprogress = ""
            while path_inprogress.__len__() <= folder.__len__():
                path_inprogress += folder_parts.pop(0) + '/'
                if path_inprogress not in self.folder_list:
                    self.folder_list.append(path_inprogress)
        self.folder_list.sort(key = len)
        for f in self.folder_list:
            self.mkpath(f)


    def mkpath(self, path):
        if path[-1] == '/':
            path = path[:-1]
        path_parts = path.split('/')[1:]
        path_inprogress = Config.base_path
        last_id = Config.base_id[self.acct]
        for p in path_parts:
            path_inprogress = os.path.join(path_inprogress, p)
            # print("path_inprogress", path_inprogress)
            if path_inprogress not in Cache.gd_path_cache[self.acct]:
                last_id = self.mkdir(p, last_id)
                self.say("Building path\n  {}:{}".format(self.acct, path_inprogress))
                if last_id:
                    Cache.gd_path_cache[self.acct][path_inprogress] = last_id
            else:
                last_id = Cache.gd_path_cache[self.acct][path_inprogress]

    def mkdir(self, name, parent_id):
        if parent_id in Cache.gd_folder_ids[self.acct] and name in Cache.gd_folder_ids[self.acct][parent_id]:
            return Cache.gd_folder_ids[self.acct][parent_id][name]
        dir_info = self.find_by_name(name, parent=parent_id, is_folder=True)
        if dir_info:
            new_id = dir_info[0]['id']
        else:
            cmd = ['gdrive', '-c', self.config, 'mkdir', '-p', parent_id, name]
            dbg(cmd.__str__())
            ran = run(cmd)
            results = ran.get_result()
            if results:
                new_id = str(results).split()[1]
            else:
                new_id = None
        if parent_id not in Cache.gd_folder_ids[self.acct]:
            Cache.gd_folder_ids[self.acct][parent_id] = {}
        Cache.gd_folder_ids[self.acct][parent_id][name] = new_id
        return new_id

    def find_by_name(self, name, parent=None, is_folder=False):
        helper_file = '{}_by_name'.format(self.acct)
        helper_txt = """#!/bin/bash

if [ "$2" == "true" ]; then
  folder="and mimeType = 'application/vnd.google-apps.folder'"
else
  folder=""
fi

gdrive -c {} list --no-header --absolute --name-width 0 --query " name=\\"$1\\" $folder "
        """.format(self.config)
        helper_path = GoogleUploader.verify_helper(helper_file, helper_txt)
        cmd = [helper_path, name]
        dbg(cmd.__str__())
        if is_folder:
            cmd.append('true')
        ran = run(cmd)
        results = ran.get_result()
        return_val = []
        if results:
            result_list = results.splitlines()
            for res in result_list:
                res_split = str(res)[2:-1].split()
                id, name, kind = res_split[:3]
                id_info = self.find_by_id(id)
                # {'id': '0ByxWOPrynoZYdkVGZWY2aEJEUmc', 'parents': '0ACxWOPrynoZYUk9PVA', 'name': 'backup',
                #   'mime': 'application/vnd.google-apps.folder', 'path': 'backup'}
                if id_info:
                    if not parent or (parent and parent == id_info['parent']):
                        return_val.append(id_info)
        return return_val

    def find_by_id(self, id):
        if id in Cache.google_ids:
            return Cache.google_ids[id]
        cmd = ['gdrive', '-c', self.config, 'info', id]
        dbg(cmd.__str__())
        ran = run(cmd)
        results = ran.get_result()
        parsed = {}
        if results:
            res_lines = results.splitlines()
            for res in res_lines:
                res_id, res_value = str(res)[2:-1].split(": ", 1)
                res_id = res_id.lower()
                if res_id in ('id', 'path', 'mime', 'name', 'size'):
                    parsed[res_id] = res_value
                elif res_id == 'parents':
                    parsed['parent'] = res_value
            Cache.google_ids[id] = parsed
            return parsed
        else:
            return None


class GoogleUploader:
    def __init__(self, acct, src_file):
        self.kind = Kind.uploader
        self.say = functools.partial(say, Kind.uploader)
        self.acct = acct
        self.src_file = src_file
        self.config = os.path.join(Config.gd_config, acct)
        # print(self.config)
        self.upload()

    @staticmethod
    def verify_helper(fname, txt):
        helper_path = os.path.join(os.getcwd(), fname)
        if not os.path.exists(helper_path):
            with open(helper_path, "w") as helper:
                helper.write(txt)
            os.chmod(helper_path, 0o775)
            time.sleep(1)
        return helper_path

    def find_by_id(self, id):
        if id in Cache.google_ids:
            return Cache.google_ids[id]
        cmd = ['gdrive', '-c', self.config, 'info', id]
        dbg(cmd.__str__())
        ran = run(cmd)
        results = ran.get_result()
        parsed = {}
        if results:
            res_lines = results.splitlines()
            for res in res_lines:
                res_id, res_value = str(res)[2:-1].split(": ", 1)
                res_id = res_id.lower()
                if res_id in ('id', 'path', 'mime', 'name', 'size'):
                    parsed[res_id] = res_value
                elif res_id == 'parents':
                    parsed['parent'] = res_value
            Cache.google_ids[id] = parsed
            return parsed
        else:
            return None

    def find_by_name(self, name, parent=None, is_folder=False):
        helper_file = '{}_by_name'.format(self.acct)
        helper_txt = """#!/bin/bash

if [ "$2" == "true" ]; then
  folder="and mimeType = 'application/vnd.google-apps.folder'"
else
  folder=""
fi

gdrive -c {} list --no-header --absolute --name-width 0 --query " name=\\"$1\\" $folder "
        """.format(self.config)
        helper_path = self.verify_helper(helper_file, helper_txt)
        cmd = [helper_path, name]
        dbg(cmd.__str__())
        if is_folder:
            cmd.append('true')
        ran = run(cmd)
        results = ran.get_result()
        return_val = []
        if results:
            result_list = results.splitlines()
            for res in result_list:
                res_split = str(res)[2:-1].split()
                id, name, kind = res_split[:3]
                id_info = self.find_by_id(id)
                # {'id': '0ByxWOPrynoZYdkVGZWY2aEJEUmc', 'parents': '0ACxWOPrynoZYUk9PVA', 'name': 'backup',
                #   'mime': 'application/vnd.google-apps.folder', 'path': 'backup'}
                if not parent or (parent and parent == id_info['parent']):
                    return_val.append(id_info)
        return return_val

    def list_dir(self, fid, only_folders=False):
        helper_file = '{}_list_dir'.format(self.acct)
        helper_text = """#!/bin/bash
if [ "$2" == "true" ]; then
  folder="and mimeType = 'application/vnd.google-apps.folder'"
else
  folder=""
fi
gdrive -c {} list --no-header --absolute --name-width 0 --query " \\"$1\\" in parents $folder "
fi
""".format(self.config)
        helper_path = self.verify_helper(helper_file, helper_text)
        cmd = [helper_path, fid]
        dbg(cmd.__str__())
        if only_folders:
            cmd.append('true')
        ran = run(cmd)
        results = ran.get_result()
        dir_list = []
        if results:
            result_list = results.splitlines()
            for res in result_list:
                res_split = str(res)[2:-1].split()
                res_id, name, kind = res_split[:3]
                info = {'id': res_id, 'name': name, 'mime': kind, 'parent': fid}
                dir_list.append(info)
        return dir_list

    def id_from_path(self, path):
        # print("{} || {}".format(path, Cache.gd_path_cache[self.acct][os.path.join(Config.base_path, path)]))
        if path == Config.upload_src:
            return Config.base_id[self.acct]
        else:
            try:
                return Cache.gd_path_cache[self.acct][os.path.join(Config.base_path, path)]
            except KeyError:
                return None

    def upload(self):
        def mark():
            if Config.active:
                open(self.src_file + "." + self.acct, "a").close()

        def parse_size(size_str):
            num, unit = size_str.split()
            if unit == 'B':
                return 1024
            units = ['KB', 'MB', 'GB', 'TB']
            multiplier = units.index(unit) + 1
            size_in_bytes = float(num) * 10**(multiplier*3)
            return size_in_bytes

        def remote_file_is_smaller(file_info):
            st = os.stat(self.src_file)
            local_size = float(st.st_size)
            if "size" in file_info:
                remote_size = parse_size(file_info['size'])
            # sys.stdout.write(
            #     "\nFILE SIZE COMPARISON: Is Local: {} >= Remote {} {}\n".format(local_size*0.95, remote_size, remote_size <= local_size*0.95))
                return remote_size <= (local_size*0.95)
            else:
                return True

        def file_exists(name, parent):
            result = self.find_by_name(name, parent)
            return result if result else None

        base_path = os.path.dirname(self.src_file).replace(Config.upload_src + "/", "")
        folder_id = self.id_from_path(base_path)
        file_name = os.path.basename(self.src_file)
        upload_cmd = ['gdrive', '-c', self.config, 'upload', '-p', folder_id, self.src_file]
        dbg(upload_cmd.__str__())
        file_exists = file_exists(file_name, folder_id)
        remote_path = "{}/{}".format(base_path, file_name)

        if not file_exists:
            ran = run(upload_cmd, get_stdout=False)
            ex_code = ran.get_result()
            if ex_code == 0:
                mark()
            else:
                self.say("File failed to upload to \"{}\" with exit code ({})\n  {}"
                         .format(self.acct, ex_code, self.src_file))
        elif remote_file_is_smaller(file_exists[0]):
            def rm_file(file_id):
                rm_cmd = ['gdrive', '-c', self.config, 'delete', file_id]
                dbg(rm_cmd.__str__())
                rm_ran = run(rm_cmd, get_stdout=False)
                return rm_ran.get_result()
            self.say("Remote file smaller than new file with the same name, replacing\n  {}:{}"
                     .format(self.acct,remote_path))
            if rm_file(file_exists[0]['id']) == 0:
                ran = run(upload_cmd, get_stdout=False)
                ex_code = ran.get_result()
                if ex_code == 0:
                    mark()
                else:
                    self.say("File failed to upload to \"{}\" with exit code ({})\n  {}"
                         .format(self.acct, ex_code, self.src_file))
        else:
            remote_file_is_smaller(file_exists[0])
            self.say("File already exists\n   {}:{}".format(self.acct, remote_path))
            mark()

class ACD:
    @staticmethod
    def clean_acd(acct, exponent=1):
        if not Config.active or not exists(Config.acd_failed_file):
            return
        if acct[0] == 'a':
            ran = run(['acd_cli', 'old-sync'], get_stdout=False)
            ex_code = ran.get_result()
            if ex_code != 0:
                exponent += 1
                time.sleep(2 ** exponent)
                ACD.clean_acd(acct, exponent)
            else:
                os.remove(Config.acd_failed_file)

    @staticmethod
    def check_acd_db():
        try:
            conn = sqlite3.connect(os.path.join(Config.acd_config, 'nodes.db'))
            c = conn.cursor()
            c.execute("pragma quick_check;")
            conn.commit()
            conn.close()
        except sqlite3.DatabaseError:
            say(Kind.main, "ACD_CLI db damaged, creating new one")
            for acd_file in os.listdir(Config.acd_config):
                keepers = ('oauth_data',)
                if acd_file not in keepers:
                    say(Kind.main, "Deleting {}".format(join(Config.acd_config, acd_file)))
                    os.remove(join(Config.acd_config, acd_file))
            time.sleep(3)
            run(['acd_cli', 'sync'], get_stdout=False)

class ACDFolders:
    def __init__(self, file_list):
        self.file_list = file_list
        self.kind = Kind.uploader
        self.say = functools.partial(say, Kind.uploader)
        self.folder_list = []
        self._process_list()

    def _process_list(self):
        for f in self.file_list:
            file_path = f[1].replace(Config.upload_src, Config.base_path[:-1])
            folder = os.path.dirname(file_path)
            if folder not in self.folder_list:
                self.folder_list.append(folder)
        for f in self.folder_list:
            bad_path = False
            for bp in Cache.bad_paths:
                if bp in f:
                    bad_path = True

            if f not in Cache.acd_path_cache and not bad_path:
                self.say("Creating path\n   {}".format(f))
                mkdir_cmd = ['acd_cli', 'create', '--parents', "/{}/".format(f)]
                dbg(mkdir_cmd.__str__())
                ran = run(mkdir_cmd, get_stdout=False)
                ex_code = ran.get_result()

                if ex_code == 0:
                    Cache.acd_path_cache.append(f)
                else:
                    self.say("Failed to create folder\n  {}".format(f))
                    Cache.bad_paths.append(f)
                    with open(Config.bad_path_file, "a") as bpf:
                        bpf.write("{}\n".format(f))
                    return


class ACDUploader:
    def __init__(self, src_file):
        self.src_file = src_file
        self.dst_file = src_file.replace(Config.upload_src, Config.base_path[:-1])
        self.dst_folder = os.path.dirname(self.dst_file)
        self.kind = Kind.uploader
        self.say = functools.partial(say, Kind.uploader)
        self.acct = 'acd'
        self.upload()

    def upload(self):
        for bp in Cache.bad_paths:
            if bp in self.dst_file:
                self.say("Skipping file in known bad path \n  {}".format(self.dst_file))
                return

        ul_cmd = ['acd_cli', 'upload', '-o', '-x 4', '-r 4', self.src_file, "{}/"
            .format(self.dst_folder)
            .replace("//", "/")]
        dbg(ul_cmd.__str__())
        if Config.active:
            # don't try to upload files too large for Amazon Drive
            if os.path.getsize(self.src_file) > Config.acd_max_size:
                open(self.src_file + "." + self.acct, "a").close()
                self.say("File too large for Amazon Drive. Upload not attempted:\n  {}".format(self.src_file))
                return
            ran = run(ul_cmd, get_stdout=False)
            ex_code = ran.get_result()
            if ex_code == 0:
                try:
                    open(self.src_file + "." + self.acct, "a").close()
                    self.say("Upload Successful:\n  {}".format(self.src_file))
                except:
                    pass
            else:
                self.say(
                    "File failed to upload to \"{}\" with exit code ({})\n  {}"
                        .format(self.acct, ex_code, self.src_file))
                open(Config.acd_failed_file, "a").close()
                # Config.acd_sync = True
                # time.sleep(10)


class Cleaner:
    def __init__(self):
        self.say = functools.partial(say, Kind.cleaner)
        try:
            self.run()
        except Exception as e:
            logger.exception(e)
        finally:
            pass

    def run(self):
        for root, dirs, files in walk(Config.upload_src):
            for name in files:
                file_path = join(root, name)
                if exists(file_path + '.acd') and exists(file_path + '.gdc') and exists(file_path + '.gds'):
                    self.say("Deleting local copy\n   {}".format(file_path))
                    os.remove(file_path + '.acd')
                    os.remove(file_path + '.gdc')
                    os.remove(file_path + '.gds')
                    os.remove(file_path)
            for d in dirs:
                dir_path = join(root, d)
                try:
                    os.rmdir(dir_path)
                    self.say("Removed empty folder\n  {}\n".format(dir_path))
                except OSError:
                    pass


class Importer:
    def __init__(self):
        self.file_list = []
        self.say = functools.partial(say, Kind.importer)
        try:
            self.go_importer()
            self.stage_files()
        except Exception as e:
            logger.exception(e)
        finally:
            pass

    def go_importer(self):
        i = 1
        for root, dirs, files in os.walk(Config.import_src):
            for f in files:
                if i > Config.batch:
                    break
                src_file = os.path.join(root, f)
                dst_file = src_file.replace(Config.import_src, Config.import_dst)
                if '_gsdata_' not in src_file:
                    self.file_list.append((src_file, dst_file, i))
                    i += 1
        num_files = self.file_list.__len__()
        if num_files > Config.batch:
            num_files = Config.batch
        for i in range(0, num_files):
            self.file_list[i] = self.file_list[i] + (num_files,)

        if num_files > 0:
            self.say("Found new files to import")
            pool = ThreadPool(Config.import_threads)
            pool.map(self.import_file, self.file_list)
            pool.close()
            pool.join()

    def import_file(self, import_info):
        def rm_folder(src_path):
            try:
                dir_path = os.path.dirname(src_path)
                os.rmdir(dir_path)
                self.say("Removed empty folder\n   {}".format(dir_path))
            except OSError:
                pass

        def has_enough_space():
            st = os.statvfs(Config.import_dst)
            free = st.f_bavail * st.f_frsize
            return free > Config.free_threshold

        try:
            src_file, dst_file, i, total = import_info
            self.say("Moving file [{}/{}]\n  {}".format(i, total, dst_file.replace(Config.import_dst, "")))
            import_cmd = ['rsync', '-avmW', '--remove-source-files', '--progress', src_file, dst_file]
            if has_enough_space():
                if Config.active:
                    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                    run(import_cmd, get_stdout=False)
                    # rm_folder(src_file)
                else:
                    dbg(import_cmd.__str__())
            else:
                self.say("Not enough free space for import")
                time.sleep(60)
        except Exception as e:
            logger.exception(e)
        finally:
            pass

    def stage_files(self):
        for root, dirs, files in os.walk(Config.stage_src):
            num_files = files.__len__()
            if num_files > 0:
                self.say("Moving imported files into upload folder")
            i = 0
            for f in files:
                i += 1
                src_file = os.path.join(root, f)
                dst_file = src_file.replace(Config.stage_src, Config.upload_src)
                if Config.active:
                    if os.path.exists(src_file):
                        self.say("Moving file [{}/{}] \n  {}".format(i, num_files, dst_file))
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.move(src_file, dst_file)
            if files.__len__() > 0:
                self.say("Finished moving imported files into upload folder")

logging.basicConfig(filename=Config.log_file, level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)
start()
# ACD.check_acd_db()
