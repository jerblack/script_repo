#!/usr/bin/python3

import os, sys, subprocess
from pprint import pprint




"""
no_avi

no_avi will remux all of the individual avi files in the folder it was run from into mkvs using mkvmerge


iterate through all files in a folder
    if the file has an avi extension
        get the filename and replace avi with mkv
        use this to build the command line
        use subprocess to run the command


"""

class Config:
    work_dir = os.path.curdir
    ext = '.avi'

class Convert:
    def __init__(self):
        self.avis = []
        self.get_files()
        self.process()


    def get_files(self):
        for root, dirs, files in os.walk(Config.work_dir):
            for file in files:
                if os.path.splitext(file.lower())[1] == Config.ext:
                    self.avis.append(file)

    def process(self):
        for avi in self.avis:
            print("Converting avi file: {}".format(avi))
            new_name = avi[:-4] + '.mkv'
            cmd = ['mkvmerge', '-o', new_name, avi]
            print(cmd)
            ran = run(cmd, get_stdout=False)
            if ran.get_result() == 0:
                print("Removing avi file: {}".format(avi))
                # os.remove(os.path.join(Config.work_dir, avi))


class run:
    def __init__(self, cmd, get_stdout=True):
        self.cmd = cmd
        self.result = None
        if get_stdout:
            self._stdout()
        else:
            self._ex_code()

    def _ex_code(self):
        self.result = subprocess.call(self.cmd)

    def _stdout(self):
        try:
            self.result = subprocess.check_output(self.cmd)
        except subprocess.CalledProcessError as e:
            print("ERROR: {}".format(e))

    def get_result(self):
        return self.result



Convert()