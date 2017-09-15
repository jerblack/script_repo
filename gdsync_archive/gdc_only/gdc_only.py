#!/usr/bin/python3

import os, subprocess, sys, time, signal, shutil
from multiprocessing import Pool as ThreadPool
from threading import Thread


"""
    monitor import_src folder on island
        import_src = "/home/jeremy/island/_gdc_only"
    move all files from import_src to import_dst on hydra
        import_dst = "/home/jeremy/_import_gdc_only_dec"
    after successful move, rename file into stage_src on hydra
        stage_src = "/home/jeremy/_import_gdc_only_enc"
    create .gds and .acd markers for all files in stage_src
    rename all files in stage_src into upload_src
        upload_src = "/home/jeremy/_upload"


"""

class Colors:
    pink = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    white = '\033[1m'
    underline = '\033[4m'
    end = '\033[0m'


class Config:
    bhi_id = "bhi_id:001"
    import_src = "/home/jeremy/island/_gdc_only"
    import_dst = "/home/jeremy/_import_gdc_only_dec"
    stage_src = "/home/jeremy/_import_gdc_only_enc"
    upload_src = "/home/jeremy/_upload"
    keep_folders = ['/home/jeremy/island/_gdc_only/new_downloads',
                    '/home/jeremy/island/_gdc_only/movies/4K']
    interval = 10
    import_threads = 3
    threads = 3
    batch = 100
    free_threshold = 60 * 1024 * 1024 * 1024  # 60GB
    active = True
    debug = False


class say:
    def __init__(self, text):
        if type(text) is not str:
            self.text = str(text)
        else:
            self.text = text
        self.say()

    def say(self):
        prefix = Colors.red + "[{}][{} free][{} to import]".format(
            say.get_time(), say.get_free_space(), say.get_folder_size(Config.import_src))

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


def start():
    say("go gdc_only, {}".format(Config.bhi_id))

    def go():
        while True:
            dbg("starting importer now")
            Importer()
            time.sleep(Config.interval)

    def delay():
        if len(sys.argv) == 2:
            seconds = int(sys.argv[1])
            say("Delaying startup by {} seconds".format(seconds))
            time.sleep(seconds)

    def threader():
        imp = Thread(target=go)
        imp.setDaemon(True)
        say("Starting Importer thread")
        say("Checking for new files every {} seconds.".format(Config.interval))
        imp.start()

    delay()
    threader()
    while True:
        signal.pause()


def dbg(text):
    if Config.debug:
        sys.stdout.write(Colors.pink + text + Colors.end + "\n")


class run:
    def __init__(self, cmd, get_stdout=True):
        self.cmd = cmd
        self.result = None
        if get_stdout:
            self._stdout()
        else:
            self._ex_code()

    def _ex_code(self):
        if Config.active:
            self.result = subprocess.call(self.cmd)
        else:
            say("Run called with {}".format(self.cmd.__str__()))
            self.result = 0

    def _stdout(self):
        if Config.active:
            try:
                self.result = subprocess.check_output(self.cmd)
            except subprocess.CalledProcessError as e:
                say("ERROR: {}".format(e))
        else:
            say("Run called with {}".format(self.cmd.__str__()))
            self.result = None

    def get_result(self):
        return self.result


class Importer:
    def __init__(self):
        self.file_list = []
        self.go_importer()
        self.stage_files()

    def go_importer(self):
        dbg('called go_importer')
        i = 1
        for root, dirs, files in os.walk(Config.import_src):
            dbg("iterating through source folder looking for new files {}".format(Config.import_src))
            for f in files:
                if i > Config.batch:
                    dbg("import batch full")
                    break
                src_file = os.path.join(root, f)
                dst_file = src_file.replace(Config.import_src, Config.import_dst)
                if '_gsdata_' not in src_file:
                    self.file_list.append((src_file, dst_file, i))
                    dbg("added src_file to import file_list {}". format(src_file))
                    i += 1
        num_files = self.file_list.__len__()
        if num_files > Config.batch:
            num_files = Config.batch
        for i in range(0, num_files):
            self.file_list[i] = self.file_list[i] + (num_files,)

        if num_files > 0:
            say("Found new files to import")
            pool = ThreadPool(Config.import_threads)
            pool.map(self.import_file, self.file_list)
            pool.close()
            pool.join()

    def rm_folder(self, src_path):
        dbg('called rm_folder with {}'.format(src_path))

        try:
            dir_path = os.path.dirname(src_path)
            if dir_path not in Config.keep_folders:
                os.rmdir(dir_path)
                say("Removed empty folder\n   {}".format(dir_path))
        except OSError:
            pass

    def import_file(self, import_info):
        def has_enough_space():
            st = os.statvfs(Config.import_dst)
            free = st.f_bavail * st.f_frsize
            return free > Config.free_threshold

        src_file, dst_file, i, total = import_info
        say("Moving file [{}/{}]\n  {}".format(i, total, dst_file.replace(Config.import_dst, "")))
        import_cmd = ['rsync', '-avmW', '--remove-source-files', '--progress', src_file, dst_file]
        if has_enough_space():
            if Config.active:
                os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                run(import_cmd, get_stdout=False)
                self.rm_folder(src_file)
            else:
                dbg(import_cmd.__str__())
        else:
            say("Not enough free space for import")
            time.sleep(60)

    def stage_files(self):
        def create_markers(src_file):
            open(src_file + ".gds", "a").close()
            open(src_file + ".acd", "a").close()

        for root, dirs, files in os.walk(Config.stage_src):
            num_files = files.__len__()
            if num_files > 0:
                say("Creating .acd and .gds markers for new files")
            for f in files:
                src_file = os.path.join(root, f)
                if Config.active:
                    if os.path.exists(src_file):
                        create_markers(src_file)

        for root, dirs, files in os.walk(Config.stage_src):
            num_files = files.__len__()
            if num_files > 0:
                say("Moving imported files into upload folder")
            i = 0
            for f in files:
                i += 1
                src_file = os.path.join(root, f)
                dst_file = src_file.replace(Config.stage_src, Config.upload_src)
                if Config.active:
                    if os.path.exists(src_file):
                        say("Moving file [{}/{}] \n  {}".format(i, num_files, dst_file))
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.move(src_file, dst_file)
                        self.rm_folder(src_file)
            if files.__len__() > 0:
                say("Finished moving imported files into upload folder")

start()
