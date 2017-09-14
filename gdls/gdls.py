#!/usr/bin/python3

import os, subprocess, sys, pprint, time, shlex


'''
    The purpose of gdls (ls for google drive) is to find a faster way to get a directory listing from a 
    google drive that does not require individual requests for each file
    
    ideally, i will get a formatted folder listing and parse that body of text into the appropriate folder structure
    folder data structure should include
        path for each file
        size of each file
        
    folder structure can be a list of tuples or dicts
    
    should be able to get folder listing from gdrive or rclone
'''

class Config:
    src = "~/files"
    gd_config = "/home/jeremy/.gdrive/"
    active = True

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
    def __init__(self, text):
        if type(text) is not str:
            self.text = str(text)
        else:
            self.text = text
        self.say()

    def say(self):
        prefix = Colors.green + "[GDLS][{}]".format(say.get_time())
        msg = "{} {}".format(prefix, self.text) + Colors.end
        sys.stdout.write(msg + "\n")

    @staticmethod
    def get_time():
        return time.strftime("%Y-%m-%d %H:%M:%S")


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


def start():
    say("GDLS go")
    process_folder('0ByxWOPrynoZYVHlOamJvb1lpY3M')

class File:
    def __init__(self, id, path, size):
        self.id = id
        self.path = path
        self.size = size

class Files:
    def __init__(self):
        self.files = []
        self.total_bytes = 0

    def add(self, file):
        self.files.append(file)

    def __str__(self):
        if self.files:
            str = ""
            for i, sf in enumerate(self.files):
                str+="{} > {}\n {}\n {}\n".format(i, sf.id, sf.path, sf.size)
            return str
        else:
            print("no files in collection")


def process_folder(id):
    # cmd = "gdrive list --query \"  '0ByxWOPrynoZYMzZXSGFXeHZ3czg' in parents \" --bytes --no-header --absolute --name-width 0"
    # say("Processing folder with id {}".format(id))
    cmd = "gdrive list --query \"  '{}' in parents \" --bytes --no-header --absolute --name-width 0 -m 0".format(id)
    ran = run(shlex.split(cmd))
    result = ran.get_result()
    if result:
        res_lines = result.splitlines()
        # print(res_lines)
        for res in res_lines:
            r = str(res)[2:-1].split()
            if r[2] != 'dir':
                file = File(r[0], r[1], r[3])
                files.add(file)
                files.total_bytes += int(r[3])
            else:
                say("Processing folder with path {}".format(r[1]))
                process_folder(r[0])


files = Files()
start()
print(files)
print("{} total bytes".format(str(files.total_bytes)))
