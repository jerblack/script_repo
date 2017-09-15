cp -a ~/torrents/seeding/. ~/torrents/finished/

# Setup automounting encfs

encfs ~/torrents/encrypted ~/torrents/finished

mkdir -p /mnt/torrents/.enc
cd /mnt/torrents/.enc

mv /home/jeremy/torrents/encrypted/.encfs6.xml /home/jeremy/.config/enc/.encfs6.xml

echo <password> > ~/.config/enc/k

## create ~/.config/enc/encwrap

#!/bin/bash
ENCFS6_CONFIG="/home/jeremy/.config/enc/.encfs6.xml" encfs --public --extpass="cat /home/jeremy/.config/enc/k" $*

## add encfs entry to /etc/fstab
/mnt/torrents/.enc/encwrap#/mnt/torrents/encrypted /mnt/torrents/finished fuse rw,auto,user 0 0

-or-

/home/jeremy/.config/enc/encwrap#/home/jeremy/shares/server.z/_work/enc /home/jeremy/shares/server.z/_work/dec fuse rw,auto,user 0 0


## lockdown config files

sudo chown root:root .encfs6.xml k encwrap
sudo chmod 440 .encfs6.xml k
sudo chmod 550 encwrap

mv -v ~/shares/server.z/_work/dec/* ~/shares/server.x/_work/proc/