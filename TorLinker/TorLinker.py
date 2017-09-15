"""

Tor Linker
    Watches seed folder for newly finished torrents and uses hardlinks to mirror them to another folder
    This allows you to move and delete the hardlinks as if they were files, while maintaining to torrent you
    are seeding in its current location.
    History is maintained in TorLinker.db so links for a new torrent are only created once, even if those links
    are moved or deleted.

"""

import sqlite3 as sql
import os, time, ctypes, platform
if 'Windows' in platform.system():
    import ntfsutils.hardlink as hardlink

class options:
    # seed_folder = r"C:\Torrents\seeding"
    # link_folder = r"C:\Torrents\finished"
    link_folder = r""
    seed_folder = r""
    db_file = r"TorLinker.db"
    check_interval = 60  # seconds


def main():
    if 'Windows' in platform.system():
        ctypes.windll.kernel32.SetConsoleTitleA("TorLinker")

    if bool(options.link_folder) and bool(options.seed_folder):
        no_seed = False
        no_link = False

        if not os.path.exists(options.seed_folder):
            print 'Your seed folder \"' + options.seed_folder + '\" does not exist'
            print 'Update this py file with the correct path'
            no_seed = True

        if not os.path.exists(options.link_folder):
            print 'Your link folder \"' + options.link_folder + '\" does not exist'
            print 'Update this py file with the correct path'
            no_link = True

        if no_link or no_seed:
            quit()

        print 'TorLinker started, checking every', str(options.check_interval), 'seconds'
        print 'Monitoring folder \"' + options.seed_folder + '\" for new torrents'
        print 'Torrents will be linked to \"' + options.link_folder + '\"'
        print 'Link history is saved to \"' + options.db_file + '\"'
        while True:
            time.sleep(options.check_interval)
            l = Linker()
            l.start()
    else:
        print """
    Attention: Missing Configuration

    You must edit this py file before using it to add your source and target paths
    Add source path to options.seed_folder
    Add target path to options.link_folder

    This script will now exit
              """


class Linker:
    """
        linker will be run on a timer every options.check_interval
        linker needs to do the following
        get all currently known roots from db
        get all files and folders in seed_root
        check each file and folder against known roots
        (roots are files and folders in root level of seed_root, not any files/folders nested in those root folders
        if not known
            add to root db with hardlink_progress = not_started
            if file
                hardlink_progress = started
                link to same file name in root of link_folder
                hardlink_progress = finished
            if folder
                hardlink_progress = started
                create root folder with same name in link_folder
                recreate folder structure to mirror subfolders from root in seed_folder
                print "created", folder
                recreate file structure using hardlink to files in same hierarchy as seed_folder
                hardlink_progress = finished


    """

    def __init__(self):
        self.new_roots = []

    def start(self):

        db = Database()
        fs = FileSystem()

        for fsr in fs.roots:
            if fsr not in db.roots:
                self.new_roots.append(fsr)

        for nr in self.new_roots:
            print "Found new torrent:", nr
            db.add_root(nr)
            db.set_link_progress(nr, "started")
            fs.create_links(os.path.join(options.seed_folder, nr))
            db.set_link_progress(nr, "finished")


class FileSystem:
    '''
        get all files and folders in root of seed folder
        load them in self.roots
    '''

    def __init__(self):
        self.roots = os.listdir(options.seed_folder)

    def create_links(self, root):
        seed_path = os.path.join(options.seed_folder, root)
        if os.path.isfile(seed_path):
            cur_file = os.path.join(seed_path, root)
            new_file = cur_file.replace(options.seed_folder, options.link_folder)

            if not os.path.exists(new_file):
                print 'Linking:', new_file
                if 'Windows' in platform.system():
                    hardlink.create(cur_file, new_file)
                else:
                    os.link(cur_file, new_file)
            else:
                print "File Exists:", new_file
        else:
            for start_dir, sub_dirs, files in os.walk(root):

                new_dir = start_dir.replace(options.seed_folder, options.link_folder)

                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                else:
                    print 'Folder Exists:', new_dir

                for f in files:
                    cur_file = os.path.join(start_dir, f)
                    new_file = cur_file.replace(options.seed_folder, options.link_folder)
                    if not os.path.exists(new_file):
                        print 'Linking:', new_file
                        hardlink.create(cur_file, new_file)
                    else:
                        print "File Exists:", new_file


class Database:
    '''
        Database is used primarily to track which torrents have already been linked.
        hardlink_progress is mainly used to track the linking progress for troubleshooting
    '''

    def __init__(self):
        self.conn = sql.connect(options.db_file)
        self.c = self.conn.cursor()
        self.opened = True
        self.c.execute('CREATE TABLE IF NOT EXISTS roots (root_entry TEXT, hardlink_progress TEXT);')

        self.roots = self.get_roots()

    def add_root(self, root_entry):
        if not self.opened:
            self.__init__()
        self.c.execute('INSERT INTO roots VALUES(?,?);', (root_entry, 'not_started'))
        self.close()

    def get_roots(self):
        if not self.opened:
            self.__init__()
        self.c.execute('SELECT root_entry FROM roots;', ())
        r = self.c.fetchall()
        t = []
        for i in r:
            t.append(i[0])
        return t
        self.close()

    def set_link_progress(self, root_entry, progress):
        if not self.opened:
            self.__init__()
        self.c.execute('UPDATE roots SET hardlink_progress=? WHERE root_entry=?', (progress, root_entry))
        self.close()

    def close(self):
        self.conn.commit()
        self.conn.close()
        self.opened = False

    def clear(self):
        if not self.opened:
            self.__init__()
        self.c.execute('DROP TABLE roots;', ())
        self.close()


if __name__ == "__main__":
    main()
