#!/usr/bin/python3

import os, time, sys, subprocess

acd_dec = '/home/jeremy/acd_dec'
acd_enc = '/home/jeremy/acd_enc'
interval = 600
enc_xml = '/home/jeremy/.config/enc/.encfs6.xml'
pw_file = '/home/jeremy/.config/enc/k'
path = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
read_only = False

def start():
    os.environ['PATH'] = path
    os.environ['ENCFS6_CONFIG'] = enc_xml
    # time.sleep(30)

    while True:
        if not os.path.exists(acd_dec) or not os.listdir(acd_dec):
            print("acd_dec folder is not accessible, resetting")
            try:
                os.makedirs(acd_dec, exist_ok=True)
            except FileExistsError:
                pass
            try:
                os.makedirs(acd_enc, exist_ok=True)
            except FileExistsError:
                pass

            subprocess.call(['fusermount', '-u', acd_dec])
            subprocess.call(['fusermount', '-u', acd_enc])
            subprocess.Popen(['rclone', 'mount', 'gdc:backup/', acd_enc, '--allow-other'],
                              stdin=None, stdout=None, stderr=None)
            # time.sleep(3)
            while not os.listdir(acd_enc):
                time.sleep(0.5)
            subprocess.call(['encfs', acd_enc, acd_dec, '-o', 'nonempty', '-o', 'allow_other',
                 '--extpass=\"{}\"'.format(pw_file)])
            # sys.exit()
        time.sleep(interval)

start()