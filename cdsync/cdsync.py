#!/usr/bin/python3

import os, subprocess, sys, functools, time, signal, shutil, socket
from os import walk
from os.path import join, splitext, exists
from multiprocessing import Pool as ThreadPool
from threading import Thread
from enum import Enum
from pprint import pprint


class Config:
    server = socket.gethostname()
    base = "Fgpw0Yhw3Z8AiXLsZH4oHggz/"
    if server == "hydra":
        src = "/home/jeremy/island/acd_enc/{}".format(base)
        compare = "/home/jeremy/island/gdc_enc/{}".format(base)
        copy_target = "/home/jeremy/_copy/{}".format(base)
        finished = "/home/jeremy/_upload/{}".format(base)
    if server == "fortress":
        src = "/home/jeremy/acd_enc/{}".format(base)
        compare = "/home/jeremy/gdc_enc/{}".format(base)
        copy_target = "/home/jeremy/cdsync/_copy/{}".format(base)
        finished = "/home/jeremy/hydra/_upload_src/{}".format(base)
    # src = "/home/jeremy/island/acd_enc"
    # compare = "/home/jeremy/island/gdc_enc"
    # copy_target = "/home/jeremy/_copy"
    # finished = "/home/jeremy/_upload"
    active = True
    debug = False
    dl_queue = []
    threads = 3
    required_space = 30 * 1024 * 1024 * 1024  # 200GB
    queue_limit = 250
    interval = 600
    count = 0

def prep():
    os.makedirs(Config.copy_target, exist_ok=True)
    os.makedirs(Config.finished, exist_ok=True)


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
    def __init__(self, text, color=Colors.green):
        self.color = color
        if type(text) is not str:
            self.text = str(text)
        else:
            self.text = text
        self.say()

    def say(self):
        prefix = self.color + "[{}][{} free][{} queued]".format(
            say.get_time(), say.get_free_space(), Config.dl_queue.__len__() - Config.count)
        msg = "{} {}".format(prefix, self.text) + Colors.end
        sys.stdout.write("\n" + msg + "\n")

    @staticmethod
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def get_free_space():
        st = os.statvfs(Config.copy_target)
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


"""
sync.py
sync three cloud account via their island mounts
  each folder is compared against the other two
  any files that are missing or smaller result in larger file being copied over to _copy folder
"""


class Check:
    def __init__(self):
        Config.dl_queue = []
        Config.count = 0
        self.check_root(Config.src, Config.compare)
        # self.print_queue()
        self.handle_queue()

    def check_root(self, src_path, cmp_path):
        for root, dirs, files in walk(src_path):
            for file in files:
                src_file = join(root, file)
                cmp_file = src_file.replace(src_path, cmp_path)
                if not exists(cmp_file) or os.path.getsize(cmp_file) < os.path.getsize(src_file):
                    Config.count += 1
                    Config.dl_queue.append((Config.count, src_file))
                    say("Appending file {} to queue: {}".format(Config.dl_queue.__len__(), src_file), Colors.yellow)
                else:
                    sys.stdout.write(".")
                    sys.stdout.flush()
                if Config.dl_queue.__len__() >= Config.queue_limit:
                    say("Download queue has reached limit: {}".format(Config.queue_limit), Colors.yellow)
                    return

    def print_queue(self):
        pprint(Config.dl_queue)

    def handle_queue(self):
        if Config.dl_queue:
            say("Found {} files in download queue. Processing now.".format(Config.dl_queue.__len__()), Colors.red)
            pool = ThreadPool(Config.threads)
            Config.dl_queue = sorted(Config.dl_queue)
            pool.map(self.download_file, Config.dl_queue)
            pool.close()
            pool.join()

    def download_file(self, queue_info):
        index, src_file = queue_info
        Config.count = index
        def has_enough_space():
            st = os.statvfs(Config.copy_target)
            free = st.f_bavail * st.f_frsize
            return free > Config.required_space

        while not has_enough_space():
            say("Not enough space in download target", Colors.red)
            time.sleep(300)

        dst_file = src_file.replace(Config.src, Config.copy_target)
        cmd = ['rsync', '-avmW', '--progress', src_file, dst_file]
        say("Copying {}".format(src_file), Colors.red)
        say(cmd.__str__(), Colors.yellow)
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        ran = run(cmd, get_stdout=False)
        # Config.count += 1
        if ran.get_result() == 0:
            say("Moving finished file to upload folder: {}".format(dst_file), Colors.green)
            final_file = dst_file.replace(Config.copy_target, Config.finished)
            os.makedirs(os.path.dirname(final_file), exist_ok=True)
            os.rename(dst_file, final_file)


class run:
    def __init__(self, cmd, get_stdout=True):
        self.cmd = cmd
        self.result = None
        if Config.debug:
            sys.stdout.write(Colors.pink + str(cmd) + Colors.end + "\n")
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


# pprint(paths)

def start():
    prep()
    say("Starting copy engine")
    Check()
    # while True:
    #     Check()
    #     if not Config.dl_queue:
    #         say("Sync finished")
    #         return
    #     say("Finished cycle, restarting in {} seconds".format(Config.interval))
    #     time.sleep(Config.interval)


start()