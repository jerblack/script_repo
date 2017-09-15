# https://github.com/astrada/google-drive-ocamlfuse


sudo add-apt-repository ppa:alessandro-strada/ppa
sudo apt-get update
sudo apt-get install google-drive-ocamlfuse
# Mount Google Drive

# /bin/bash 
google-drive-ocamlfuse /home/$USER/shares/desktop.google -label Desktop.Google

# Unmount Google Drive

# /bin/bash
fusermount -u ~/Shares/desktop.google

