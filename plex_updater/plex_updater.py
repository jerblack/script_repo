#!/usr/bin/python3

import os, sys, subprocess, time
import plexapi.server as ps
from pprint import pprint
import requests as req
uri = "http://localhost:32400"
token = ""
dl_uri = "https://plex.tv/downloads/latest/1?channel=8&build=linux-ubuntu-x86_64&distro=ubuntu&X-Plex-Token={}".format(token)
path="/var/tmp"
interval = 60 * 60 * 12


def download_file(url):
    os.makedirs(path, exist_ok=True)
    local_filename = url.split('/')[-1]
    full_path = os.path.join(path, local_filename)
    if not os.path.exists(full_path):
        r = req.get(url, stream=True)
        print("Downloading new version: {}".format(full_path))
        with open(full_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
    return full_path

def install_update(path):
    cmd = ['dpkg', '-i', path]
    subprocess.call(cmd)

def get_installed_version():
    plex = ps.PlexServer(uri, token)
    return plex.version

def get_new_version():
    r = req.get(dl_uri)
    new_uri = r.history[0].headers['location']
    # new_uri = 'https://downloads.plex.tv/plex-media-server/1.2.7.2987-1bef33a/plexmediaserver_1.2.7.2987-1bef33a_amd64.deb'
    new_ver = new_uri.split('/')[4]
    return new_ver, new_uri

def delete_download(path):
    os.remove(path)

def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S")

def updater():
    cur_ver = get_installed_version()
    new_ver, uri = get_new_version()
    if (cur_ver != new_ver):
        path = download_file(uri)
        install_update(path)
        delete_download(path)
    else:
        print("{} = {}, doing nothing".format(cur_ver, new_ver))

def start():
    while True:
        updater()
        print("Check completed at [{}]. Checking again in {} hours".format(get_time(), interval/3600 ))
        time.sleep(interval)

start()

# plex = ps.PlexServer(uri, token)
# # acct = plex.account()
# # plex_pass = "sync" in acct.subscriptionFeatures
# # installed_ver='1.2.7.2987-1bef33a'
# installed_ver = plex.version
# # pprint(plex.__dict__)
# r = req.get(dl_uri)
# pprint(r.history[0].headers['location'])
# new_uri = 'https://downloads.plex.tv/plex-media-server/1.2.7.2987-1bef33a/plexmediaserver_1.2.7.2987-1bef33a_amd64.deb'
# new_ver = new_uri.split('/')[4]
# print(new_ver == installed_ver)
# {'_library': None,
#  'baseurl': 'http://.:32400',
#  'friendlyName': ' (Local)',
#  'machineIdentifier': '',
#  'myPlex': True,
#  'myPlexMappingState': 'mapped',
#  'myPlexSigninState': 'ok',
#  'myPlexSubscription': '1',
#  'myPlexUsername': '',
#  'platform': 'Linux',
#  'platformVersion': '4.4.0-47-generic (#68-Ubuntu SMP Wed Oct 26 19:39:52 UTC '
#                     '2016)',
#  'session': <requests.sessions.Session object at 0x7f75e9e09320>,
#  'token': '',
#  'transcoderActiveVideoSessions': 0,
#  'updatedAt': 1478849770,
#  'version': '1.2.7.2987-1bef33a'}
