- **google-drive-ocamlfuse**
FUSE filesystem over Google Drive

      #!/bin/bash
	  # https://github.com/astrada/google-drive-ocamlfuse
	  sudo add-apt-repository ppa:alessandro-strada/ppa
	  sudo apt update && sudo apt install google-drive-ocamlfuse -y
	  
- **Airfoil Speakers**

      #!/bin/bash
	  echo "___installing airfoil speakers___"
	  echo "___adding mono repo (airfoil dependency)___"
	  sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF
	  echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list
	  sudo apt update
	  echo "___downloading airfoil speakers for linux___"
	  cd ~/Downloads/
	  wget https://rogueamoeba.com/airfoil/download/AirfoilSpeakersLinux.all.deb
	  echo "___installing airfoil speakers for linux___"
	  sudo dpkg -i AirfoilSpeakersLinux.all.deb
	  echo "___installing missing airfoil dependencies___"
	  sudo apt install -f -y
     
- **ArcTheme**

      #! /bin/bash
	  say () { echo "___$1___"; return 0; }
	  if [ ! -f /etc/apt/sources.list.d/arc-theme-solid.list ]; then
	    say "Adding Arc-Theme repo"
		wget http://download.opensuse.org/repositories/home:Horst3180/xUbuntu_16.04/Release.key
		sudo apt-key add - < Release.key 
		sudo sh -c "echo 'deb http://download.opensuse.org/repositories/home:/Horst3180/xUbuntu_16.04/ /' >> /etc/apt/sources.list.d/arc-theme-solid.list"
		say "Updating repo database"
		sudo apt update
	  fi
	  say "Installing Arc-Theme-Solid GTK Theme"
	  sudo apt install arc-theme-solid -y
	  say "Applying Arc-Dark Theme"
	  dconf write /org/mate/desktop/interface/gtk-theme "'Arc-Dark'"
	  
- **AutoHotkey**
Install AutoHotkey and create configuration files needed to drive spotify remote

      #!/bin/bash
      say () { echo "___$1___"; return 0; }
      
      say "Installing autokey and jq"
      sudo apt install autokey-gtk jq -y
      
      say "Starting and killing Autokey to generate default content"
      nohup autokey-gtk > /dev/null &
      sleep 5
      pkill autokey-gtk
      
      FOLDER=x4
      CONFIG="/home/jeremy/.config/autokey/data/$FOLDER/"
      say "Creating config folder"
      mkdir -p $CONFIG
      cd $CONFIG
      
      # makejson <type> <other>
      # makejson folder
      # makejson phrase title keycode
      # makejson script title keycode
      makejson () {
          base='
          {
              "usageCount": 0, 
              "abbreviation": {
                  "wordChars": "[\\w]", 
                  "abbreviations": [], 
                  "immediate": false, 
                  "ignoreCase": false, 
                  "backspace": true, 
                  "triggerInside": false
              }, 
              "modes": [], 
              "hotkey": {
                  "hotKey": null, 
                  "modifiers": []
              }, 
              "filter": {
                  "regex": null, 
                  "isRecursive": false
              }, 
              "showInTrayMenu": false
          }'
      
          if [ "$1" == "folder" ]; then
              json=$(echo $base | \
                  jq .type=\"folder\" | \
                  jq .title=\"$FOLDER\")
              echo "$json" > .folder.json
          fi
      
          if [ "$1" == "phrase" ]; then
              json=$(echo $base | \
                  jq .type=\"phrase\" | \
                  jq .sendMode=\"kb\" | \
                  jq .omitTrigger=false | \
                  jq .prompt=false | \
                  jq .matchCase=false | \
                  jq .modes=[3] | \
                  jq .description=\"$2\" | \
                  jq .hotkey.hotKey=\"\<code$3\>\")
              echo "$json" > .$2.json
          fi
      
          if [ "$1" == "script" ]; then
              json=$(echo $base | \
                  jq .type=\"script\" | \
                  jq .store={} | \
                  jq .omitTrigger=false | \
                  jq .prompt=false | \
                  jq .modes=[3] | \
                  jq .description=\"$2\" | \
                  jq .hotkey.hotKey=\"\<code$3\>\")
              echo "$json" > .$2.json
          fi
      
      }
      
      # makepy name keycode
      makepy () {
          py="cmd = \"python /home/jeremy/bin/pm_cli.py $1\"
      system.exec_command(cmd, getOutput=False)"
          echo "$py" > $1.py
          makejson script $1 $2
      }
      
      # maketxt name modifier letterToPress keycode
      maketxt () {
          echo "<$2>+$3" > $1.txt
          makejson phrase $1 $4
      }
      
      say "Creating config files"
      makejson folder
      
      maketxt closetab ctrl w 156     # s1
      
      makepy closeapp 157             # s2
      makepy moveelectronic 158       # s3
      makepy moveshuffle 163          # s4
      makepy removelater 177          # s5
      makepy cancelremovelater 165    # s6
      makepy thumbsdown 122           # vol down
      makepy thumbsup 123             # vol up
      makepy nexttrack 171            # next track
      makepy playpause 172            # play pause
      makepy skipback 173             # skip back
      
      say "Removing Autokey sample scripts"
      rm -rf ../My\ Phrases
      rm -rf ../Sample\ Scripts
      
      say "Autokey installation is complete"      

- **Btnx**
Btnx is a utility for customizing mouse buttons. This script installs Btnx and creates the needed config files. I am using this to map the forward button to the delete key.

      #!/bin/bash
      
      say () { echo "___$1___"; return 0; }
      
      say "Installing btnx dependencies"
      sudo apt install build-essential libdaemon-dev libgtk2.0-dev libglade2-dev -y
      
      mkdir -p ~/bin/tmp
      cd ~/bin/tmp
      
      say "Downloading and extracting btnx source"
      wget https://github.com/cdobrich/btnx-config/archive/master.zip -O btnx-config.zip
      wget https://github.com/cdobrich/btnx/archive/master.zip -O btnx.zip
      
      unzip btnx-config.zip
      unzip btnx.zip
      
      say "Building btnx"
      cd btnx-master/
      ./configure
      make
      sudo make install
      
      say "Building btnx-config"
      cd ../btnx-config-master/
      ./configure
      make
      sudo make install
      
      say "Cleaning up"
      cd ~/bin/tmp
      rm btnx-config.zip
      rm btnx.zip
      rm -rf ./btnx-config-master/
      rm -rf ./btnx-master/
      
      # http://unix.stackexchange.com/questions/20550/how-to-disable-the-forward-back-buttons-on-my-mouse/20595#20595
      # 
      say "Writing config files"
      
      # run {xev -event mouse} to find the button numbers to disable
      # set to 0 to disable
      echo "pointer = 1 2 3 4 5 6 7 0 0 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24" > ~/.Xmodmap
      
      BTNX1="Default"
      BTNX2="
      Mouse
      vendor_id = 0x1532
      product_id = 0x0029
      revoco_mode = 0
      revoco_btn = 3
      revoco_up_scroll = 5
      revoco_down_scroll = 5
      EndMouse
      
      Button
      name = Forward
      rawcode = 0x01000114
      enabled = 1
      type = 0
      delay = 0
      force_release = 1
      keycode = KEY_DELETE
      mod1 = NONE
      mod2 = NONE
      mod3 = NONE
      EndButton
      
      Button
      name = Back
      rawcode = 0x01000113
      enabled = 1
      type = 0
      delay = 0
      force_release = 1
      keycode = KEY_BACK
      mod1 = NONE
      mod2 = NONE
      mod3 = NONE
      EndButton
      "
      echo "$BTNX1" | sudo tee /etc/btnx/btnx_manager > /dev/null
      echo "$BTNX2" | sudo tee /etc/btnx/btnx_config_Default > /dev/null
      say "Enabling Btnx"
      xmodmap  ~/.Xmodmap
      sudo service btnx restart
      say "Btnx is now installed"
      
- **Google Chrome**

      #! /bin/bash      
      echo "___Changing to ~/Downloads folder___"
      cd ~/Downloads/
      echo "___Downloading Chrome Package___"
      wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
      echo "___Installing Chrome___"
      sudo dpkg -i google-chrome-stable_current_amd64.deb
      echo "___Installing missing dependencies___"
      sudo apt install -f -y

- **DDClient**
DDclient is a dynamic DNS client for Namecheap. This script will install the client and configure it based on cli arguments

      #!/bin/bash
	  conf_file="/etc/ddclient/ddclient.conf"
      working_dir="~/bin"
      
      if [[ $# -eq 3 ]];then 
      	namecheap_login="$1"
      	namecheap_pw="$2"
      	dyn_hostname="$3"
      else
      	echo "Usage: <script> namecheap_login namecheap_pw dyn_hostname"
      	exit 1
      fi
      
      sudo apt install git -y
      mkdir -p "$working_dir"
      cd "$working_dir"
      git clone https://github.com/wimpunk/ddclient.git
      cd ddclient
      sudo cp ddclient /usr/sbin/ 
      sudo mkdir /etc/ddclient
      sudo mkdir /var/cache/ddclient
      
      sudo tee "$conf_file" &>/dev/null <<CONF
      # /etc/ddclient/ddclient.conf
      #
      use=web
      web=checkip.dyndns.org/
      web-skip='IP Address'
      protocol=namecheap
      server=dynamicdns.park-your-domain.com
      login=$1
      password=$2
      $3 
      CONF
      sudo chmod 600 "$conf_file"
      
      sudo cp sample-etc_rc.d_init.d_ddclient.ubuntu /etc/init.d/ddclient
      sudo update-rc.d ddclient defaults
      
      sudo apt-get install perl
      perl -MCPAN -e 'install Data::Validate::IP'
      
      sudo service ddclient start     

- **Midnight Commander**
Console-based file manager that works over SSH

      #!/bin/bash
      echo "___Installing Midnight Commander (mc)___"
      sudo apt install mc

- **Mate desktop environment**

      #!/bin/bash
	  sudo apt-add-repository "deb http://ppa.launchpad.net/ubuntu-mate-dev/ppa/ubuntu vivid main"
      sudo apt-add-repository ppa:ubuntu-mate-dev/xenial-mate
      sudo apt-get update && sudo apt-get upgrade
      sudo apt-get install ubuntu-mate-core ubuntu-mate-desktop

- **Redshift**
Installs blue light filter utility and creates config file

      #! /bin/bash
      echo "___Installing Redshift___"
      sudo apt install redshift-gtk -y
      REBOOT=0
      
      echo "___Writing config file___"
      config_file="/home/$USER/.config/redshift.conf"
      config="
      ; Global settings for redshift
      [redshift]
      ; Set the day and night screen temperatures
      temp-day=4700
      temp-night=3250
      
      ; Enable/Disable a smooth transition between day and night
      ; 0 will cause a direct change from day to night screen temperature.
      ; 1 will gradually increase or decrease the screen temperature.
      transition=0
      
      ; Configuration of the location-provider:
      ; type 'redshift -l PROVIDER:help' to see the settings.
      ; ex: 'redshift -l manual:help'
      ; Keep in mind that longitudes west of Greenwich (e.g. the Americas)
      ; are negative numbers.
      [manual]
      lat=47.58
      lon=-122.3
      "
      touch "$config_file"
      echo "$config" > "$config_file"      
      
      echo "___Configuring Geoclue for Redshift___"
      if cat /etc/geoclue/geoclue.conf | grep redshift -q
      then
      	echo "___geoclue.conf already configured___"
      else
      	FILE=/etc/geoclue/geoclue.conf
      	TEXT="\n[redshift]\nallowed=true\nsystem=false\nusers=\n"
      	sudo sed -i "$ a\\$TEXT" $FILE
      	$REBOOT=1 
      fi
      
      echo "___Updating .desktop file___"
      echo """                   
      [Desktop Entry]
      Version=1.0
      _Name=Redshift
      _GenericName=Color temperature adjustment
      _Comment=Color temperature adjustment tool
      Exec=redshift
      Icon=redshift
      Terminal=true
      Type=Application
      Categories=Utility;
      NoDisplay=true
      """ | sudo tee /usr/share/applications/redshift.desktop > /dev/null

      REBOOTTEXT="___A REBOOT IS REQUIRED FOR CHANGES TO TAKE EFFECT___"
      if [[ $REBOOT == 1 ]]; then
	      echo $REBOOTTEXT
      fi
      echo "___Finished Installing Redshift___"

- **Rclone**
Google Drive CLI

      #! /bin/bash
      cd ~/Downloads
      wget http://downloads.rclone.org/rclone-current-linux-amd64.zip
      unzip -j rclone-current-linux-amd64.zip -d rclone-current-linux-amd64 
      cd rclone-current-linux-amd64
      sudo cp rclone /usr/bin/
      #install manpage
      sudo mkdir -p /usr/local/share/man/man1
      sudo cp rclone.1 /usr/local/share/man/man1/
      sudo mandb 

- **Remmina**
RDP client

      #! /bin/bash
      echo "___Installing Remmina___"
      sudo apt install remmina -y

- **Skype**

      #!/bin/bash
      wget https://download.skype.com/linux/skype-ubuntu-precise_4.3.0.37-1_i386.deb -O ~/Downloads/skype.deb
      sudo dpkg -i ~/Downloads/skype.deb
      sudo apt install -fy

- **Spotify**

      #! /bin/bash      
      #  Instructions from https://www.spotify.com/us/download/linux/
      if ls /etc/apt/sources.list.d | grep -v spotify.list.save | grep spotify.list -q
      then
      	echo "___Spotify Repo already installed___"
      else
      	
      	echo "___Adding Spotify Repository___"
      	sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys BBEBDCB318AD50EC6865090613B00F1FD2C19886
      	echo deb http://repository.spotify.com stable non-free | sudo tee /etc/apt/sources.list.d/spotify.list
      
      	echo "___Updating repo database___"
      	sudo apt update
      fi
      
      echo "___Installing Spotify___"
      sudo apt install spotify-client -y
   
- **Sublime Text 3**

      #! /bin/bash
      REPO=webupd8team/sublime-text-3
      
      if find /etc/apt/ -name *.list | xargs cat | grep  ^[[:space:]]*deb | grep $REPO -q
      then
      	echo ___$REPO repository is already present___
      else
      	echo ___adding $REPO repository___
      	sudo apt-add-repository ppa:$REPO -y
      	echo "___Updating repo database___"
      	sudo apt update
      fi
      
      echo "___Installing Sublime Text___"
      sudo apt install sublime-text-installer -y
      
      echo "___Installing Monokai Sidebar Style___"
      mkdir -p ~/.config/sublime-text-3/Packages/Theme\ -\ Default
      SIDEBAR_THEME="https://gist.githubusercontent.com/jerblack/5d4ec251ca885b53d22ad5c57fd1d138/raw/1efcc83df0cd338c6c1f54c14b30516e64bc8ff7/Default.sublime-theme"
      wget $SIDEBAR_THEME -O ~/.config/sublime-text-3/Packages/Theme\ -\ Default/Default.sublime-theme
      
- **Transmission Remote**

      #!/bin/bash
      sudo apt install transgui -y
      # ~/.config/Transmission Remote GUI/transgui.ini

- **Trash**
trash-cli trashes files recording the original path, deletion date, and permissions. It uses the same trashcan used by KDE, GNOME, and XFCE, but you can invoke it from the command line (and scripts).

      sudo apt install trash-cli

- **VLC**

      #!/bin/bash
      # http://www.videolan.org/vlc/download-ubuntu.html
      echo "___Installing VLC___"
      sudo apt install vlc browser-plugin-vlc libavcodec-extra-53

- **x2go client**

      #! /bin/bash
      REPO=x2go/stable
      
      if find /etc/apt/ -name *.list | xargs cat | grep  ^[[:space:]]*deb | grep $REPO -q
      then
          echo ___$REPO repository is already present___
      else
          echo ___adding $REPO repository___
          sudo apt-add-repository ppa:$REPO -y
      fi
      
      echo ___Updating repo database___
      sudo apt update
      
      echo ___Installing x2goclient___
      sudo apt install x2goclient -y 

- **x2go server**

      #! /bin/bash
      REPO=x2go/stable
      
      if find /etc/apt/ -name *.list | xargs cat | grep  ^[[:space:]]*deb | grep $REPO -q
      then
          echo ___$REPO repository is already present___
      else
          echo ___adding $REPO repository___
          sudo apt-add-repository ppa:$REPO -y
      fi
      
      echo ___Updating repo database___
      sudo apt update
      
      echo ___Installing x2goserver x2goserver-session and x2gomatebindings___
      sudo apt install x2goserver x2goserver-xsession x2gomatebindings -y
      
      # fix crash on login issue
      echo "___add exports to fix crash on logon issue for MATE in x2go___"
      sudo sed -i '$ a\export GSETTINGS_SCHEMA_DIR=/usr/share/mate:/usr/share/mate:/usr/local/share/:/usr/share/:/var/lib/snapd/desktop' /etc/profile
      sudo sed -i '$ a\export XDG_DATA_DIRS=/usr/share/mate:/usr/share/mate:/usr/local/share/:/usr/share/:/var/lib/snapd/desktop' /etc/profile
      
- **x4daemon**
Enables side buttons for Sidewinder x4 keyboard

      #! /bin/bash
      # http://geekparadise.de/x4daemon/
      # enables buttons on Sidewinder x4 keyboard
      say () { echo "___$1___"; return 0; }
      
      say "creating x4daemon folder"
      mkdir -p ~/bin/x4daemon
      cd ~/bin/x4daemon
      
      say "installing dependency libusb-1.0-0-dev"
      sudo apt install libusb-1.0-0-dev
      
      say "downloading and extracting x4daemon source"
      
      wget http://geekparadise.de/x4daemon_download/x4daemon-0.4.4.tar.bz2
      tar -xvjf x4daemon-0.4.4.tar.bz2
      cd x4daemon-0.4.4
      
      say "building and installing x4daemon"
      # autoconf
      ./configure
      make
      sudo make install
      
      # to start: sudo x4daemon -w
      # to start automatically: add 'x4daemon -w -D' to /etc/rc.local, like below
      
      say "configuring x4daemon to start at logon"
      sudo sed -i "s/^exit 0/x4daemon -w -D\nexit 0/g" /etc/rc.local
      
      say "finished installing x4daemon"

- **xpad**
Post-it style note-taking utility

      #!/bin/bash
      sudo apt install xpad -y
