'''
    CloudPush will automatically copy all of the data in a given folder
    into a folder in the virtual drive created with StableBit hard drive.
    As data is copied into the virtual cloud drive, the data is actually copied to a physical cache disk
    with a finite amount of free space. CloudDrive will not upload the data until the file copy is finished
    so the file copy needs to be stopped and then wait for the data to finish uploading
    (files should not be moved to CloudDrive directly. Always Copy, never Cut. Data has been lost this way)

    Tool will enumerate files in source and copy them into destination

    files will be copied one at a time
    after each file is copied the used space on the cache drive is checked
    if the used space on the cache drive exceeds max_used_space
        pause further copy activity until the amount of free space
        increases to the value specified in min_used_space

    this script will iterate through all files and restart the process
    files will only be copied if they do not already exist in the destination
    if a full pass is completed with no files copied (all files exist in destination)
        (optionally: script can stop)
'''

import ctypes, platform, os, shutil, psutil, sys, time


class Options:
    source_folder = r"C:\Torrents\seeding"
    dest_folder = r"G:\Torrents"
    min_used_space = 10  # in %pct
    max_used_space = 90 # in %pct
    cache_drive = r"D:\\"
    skip_folders = ["all", "comics", "tv", "movies"]
    skip_files = []
    run_forever = False
    wait_interval = 20 # in seconds


def main():
    if 'Windows' in platform.system():
        ctypes.windll.kernel32.SetConsoleTitleA("CloudPush")

    print "Starting CloudPush"
    print "Now copying files into CloudDrive"
    while True:
        Copy.begin()
        time.sleep(2)
        if not Options.run_forever:
            break


class Copy:
    @staticmethod
    def log(msg):
        pct = 100-psutil.disk_usage(Options.cache_drive)[3]
        msg = msg.replace(Options.dest_folder, "")
        status = "\r" + (str(pct) + r'% Free > ' + msg + ' <')[:116]
        blank = "\r" + (" " * 116)
        sys.stdout.write(blank)
        sys.stdout.flush()

        sys.stdout.write(status)
        sys.stdout.flush()

    @staticmethod
    def begin():
        for start_dir, sub_dirs, files in os.walk(Options.source_folder):
            if os.path.basename(start_dir) not in Options.skip_folders:
                new_dir = start_dir.replace(Options.source_folder, Options.dest_folder)

                if not os.path.exists(new_dir):
                    # pass
                    os.makedirs(new_dir)
                else:
                    Copy.log("Folder Exists: " + new_dir)

                for f in files:
                    if psutil.disk_usage(Options.cache_drive)[3] < Options.max_used_space:
                        cur_file = os.path.join(start_dir, f)
                        new_file = cur_file.replace(Options.source_folder, Options.dest_folder)
                        if not os.path.exists(new_file):
                            Copy.log('Copying: ' + new_file)
                            shutil.copy(cur_file, new_file)
                        else:
                            Copy.log('File Exists: ' + new_file)
                    else:
                        Copy.wait()
            else:
                print "Skipping folder: " + start_dir


    @staticmethod
    def wait():
        print "\nCloudDrive cache drive has less than", str(100-Options.max_used_space) + "% free space."
        print "Copy will resume once cache drive is", str(100-Options.min_used_space) + "% free."

        while psutil.disk_usage(Options.cache_drive)[3] > Options.min_used_space:
            status = u"\rDrive is {0}% free. ".format(str(100-psutil.disk_usage(Options.cache_drive)[3]))
            sys.stdout.write(status)
            sys.stdout.flush()
            time.sleep(Options.wait_interval)

        print "Copy resumed"


if __name__ == "__main__":
    main()
