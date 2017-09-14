#!/usr/bin/python3
import psutil, os, sys, time
from subprocess import Popen, PIPE, call
from pprint import pprint
from multiprocessing import Pool as ThreadPool

"""
    run as same user that plex service is running under
    set up environment with exports required for scanner
    get list of sections and ids
    stop any existing scans
    start new scan for each section in batches defined by Config.num_threads

"""


class Config:
    interval = 60*60  # 1 hour
    scan = True
    analyze = False


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
        self._get_sections()
        self.scan_at_once = 3
        self.analyze_at_once = 3

    @staticmethod
    def _get_plex():
        for proc in psutil.process_iter():
            try:
                if proc.name() == 'Plex Media Server':
                    proc_details = proc.as_dict(attrs=['pid', 'name', 'username', 'gids', 'uids', 'environ'])
                    proc_details['uid'] = proc_details['uids'][0]; del proc_details['uids']
                    proc_details['gid'] = proc_details['gids'][0]; del proc_details['gids']
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

def loop():
    while True:
        start()
        sys.stdout.write("Scan and Analyze complete. Scanning again in {} minutes\n".format(Config.interval/60))
        time.sleep(Config.interval)

loop()
