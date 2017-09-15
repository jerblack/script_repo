from TorLinker import options as o
import os


for dir, subdirs, files in os.walk(o.seed_folder):
    print 'dir is',dir
    for subdir in subdirs:
        print os.path.join(dir,subdir)
    for file in files:
        print 'file is', file
    print '----'

