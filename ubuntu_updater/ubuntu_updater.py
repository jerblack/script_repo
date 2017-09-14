#!/usr/bin/python3

import time, subprocess
interval = 60*60*24  # seconds between checks
wait = 180           # seconds to wait for initial check, allow for system to start fully


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")


def update():
    cmds = [
        ["sudo", "apt", "update"],
        ["sudo", "apt", "upgrade", "-y"]
    ]
    for cmd in cmds:
        subprocess.call(cmd)


def start():
    print("[{}] Ubuntu Updater Loaded.".format(get_time(), wait))
    # time.sleep(wait)
    while True:
        print("[{}] Update Check Start".format(get_time()))
        update()
        print("[{}] Update Check End".format(get_time()))
        print("[{}] Checking again in {} hours".format(get_time(), interval / 3600))
        time.sleep(interval)

start()
