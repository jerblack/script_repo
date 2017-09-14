- **SSH Server**

Installs SSH server, changes port, disables PermitRootLogin, install fail2ban

      #!/bin/bash
      PORT=5150
      SSHCONFIG=/etc/ssh/sshd_config
      echo "___Installing SSH Server___"
      sudo apt install openssh-server -y
      echo "___Opening Firewall Port $PORT ___"
      sudo ufw allow $PORT
      echo "___Disabling Root Login, Changing SSH Server Port to $PORT ___"
      sudo sed -i s/Port\ [0-9]*/Port\ $PORT/g $SSHCONFIG
      sudo sed -i s/PermitRootLogin\ [a-zA-Z\-]*/PermitRootLogin\ no/g  $SSHCONFIG
      echo "___Installing fail2ban___"
      sudo apt install fail2ban -y


- **Setup MATE with my defaults**

      #!/bin/bash
      
      # formatted logger
      say () { echo "___$1___"; return 0; }
      
      # say "Installing dconf-tools"
      # sudo apt install dconf-tools -y
      
      MAIN="
      [settings-daemon/plugins/media-keys]
      next='disabled'
      play='disabled'
      volume-up='disabled'
      volume-down='disabled'
      media='disabled'
      stop='disabled'
      home='XF86AudioRecord'
      pause='disabled'
      eject='disabled'
      previous='disabled'
      
      [desktop/peripherals/keyboard]
      numlock-state='on'
      
      [desktop/background]
      color-shading-type='solid'
      primary-color='#000000000000'
      picture-options='wallpaper'
      picture-filename=''
      secondary-color='#000000000000'
      
      [desktop/font-rendering]
      dpi=120.0
      
      [desktop/interface]
      show-input-method-menu=false
      enable-animations=false
      gtk-theme='Arc-Dark'
      show-unicode-menu=false
      
      [pluma]
      insert-spaces=true
      bracket-matching=true
      auto-indent=true
      side-pane-visible=true
      create-backup-copy=true
      statusbar-visible=true
      
      [pluma/plugins/filebrowser/on-load]
      virtual-root='file:///home/jeremy/bin'
      tree-view=true
      root='file:///'
      
      [marco/general]
      theme='Arc-Dark'
      
      [caja/preferences]
      executable-text-activation='display'
      default-folder-viewer='list-view'
      
      [caja/window-state]
      side-pane-view='tree'
      start-with-sidebar=true
      
      [caja/desktop]
      network-icon-visible=true
      computer-icon-visible=true
      trash-icon-visible=true
      
      [mate-menu/plugins/applications]
      swap-generic-name=true
      
      [caja-open-terminal]
      desktop-opens-home-dir=true
      "
      
      # echo "$numlk"
      say "Applying MATE settings"
      echo "$MAIN" | dconf load /org/mate/ 
      
      dconf write /org/mate/mate-menu/applet-text "'$(hostname)  '"
      
      say "Finished applying MATE settings"

- **Set black background in MATE**

      #!/bin/bash
      dconf write /org/mate/desktop/background/color-shading-type "'solid'"
      dconf write /org/mate/desktop/background/picture-filename "''"
      dconf write /org/mate/desktop/background/primary-color "'#000000000000'"
      dconf write /org/mate/desktop/background/secondary-color "'#000000000000'"

- **Set black background in Gnome**

      #! /bin/bash
      SRC_URI=https://i.imgur.com/uomkVIL.png
      FNAME=black
      cd ~/Pictures
      wget $SRC_URI -O $FNAME.png
      gsettings set org.gnome.desktop.background picture-uri file://$PWD/$FNAME.png

- **Set 12-hour clock**

      #! /bin/bash
      # set for Gnome
      gsettings set org.gnome.desktop.interface clock-format 12h
      # alternately, clock-format 24h
      # set for Mate
      dconf write /org/mate/panel/objects/clock/prefs/format "'12-hour'"
      # alternately, clock-format "'24-hour'"


- **Enable automatic updates in Ubuntu**

      #!/bin/bash
      say () { echo "___$1___"; return 0; }
      
      # https://www.reddit.com/r/Ubuntu/comments/4ljps6/setting_up_unattended_automatic_updates_on_ubuntu/
      # https://github.com/Leo-G/DevopsWiki/wiki/Ubuntu-Debian-Unattended-Updates
      say "Installing unattended-upgrades package"
      sudo apt-get install unattended-upgrades
      say "Installing update-notifier-common package"
      sudo apt-get install update-notifier-common
      
      # normally below command is run, but this script autocreates the files instead
      # sudo dpkg-reconfigure unattended-upgrades
      
      DistID=$(lsb_release -is)
      DistCode=$(lsb_release -cs)
      
      say "Allowing updates for DistID=$DistID and DistCode=$DistCode"
      say "RUN THIS SCRIPT AGAIN IF UPGRADING FROM $DistID $DistCode"
      
      # http://stackoverflow.com/a/23930212/2934704 
      # on sending multiline strings to file
      cat > autmp << ENDOFAU
      APT::Periodic::Update-Package-Lists "1";
      APT::Periodic::Download-Upgradeable-Packages "1";
      APT::Periodic::AutocleanInterval "7";
      APT::Periodic::Unattended-Upgrade "1";
      ENDOFAU
      AUFILE='/etc/apt/apt.conf.d/20auto-upgrades'
      say "Creating file $AUFILE"
      sudo chown root:root autmp
      sudo chmod 644 autmp
      sudo mv autmp $AUFILE
      
      cat > uatmp << ENDOFUA
      Unattended-Upgrade::Allowed-Origins {
      	"$DistID:$DistCode-security";
      	"$DistID:$DistCode-updates";
      //	"$DistID:$DistCode-proposed";
      //	"$DistID:$DistCode-backports";
      };
      
      // List of packages to not update (regexp are supported)
      Unattended-Upgrade::Package-Blacklist {
      //	"vim";
      //	"libc6";
      //	"libc6-dev";
      //	"libc6-i686";
      };
      
      // This option allows you to control if on a unclean dpkg exit
      // unattended-upgrades will automatically run 
      //   dpkg --force-confold --configure -a
      // The default is true, to ensure updates keep getting installed
      //Unattended-Upgrade::AutoFixInterruptedDpkg "false";
      
      // Split the upgrade into the smallest possible chunks so that
      // they can be interrupted with SIGUSR1. This makes the upgrade
      // a bit slower but it has the benefit that shutdown while a upgrade
      // is running is possible (with a small delay)
      //Unattended-Upgrade::MinimalSteps "true";
      
      // Install all unattended-upgrades when the machine is shuting down
      // instead of doing it in the background while the machine is running
      // This will (obviously) make shutdown slower
      //Unattended-Upgrade::InstallOnShutdown "true";
      
      // Send email to this address for problems or packages upgrades
      // If empty or unset then no email is sent, make sure that you
      // have a working mail setup on your system. A package that provides
      // 'mailx' must be installed. E.g. "user@example.com"
      //Unattended-Upgrade::Mail "root";
      
      // Set this value to "true" to get emails only on errors. Default
      // is to always send a mail if Unattended-Upgrade::Mail is set
      //Unattended-Upgrade::MailOnlyOnError "true";
      
      // Do automatic removal of new unused dependencies after the upgrade
      // (equivalent to apt-get autoremove)
      Unattended-Upgrade::Remove-Unused-Dependencies "true";
      
      // Automatically reboot *WITHOUT CONFIRMATION*
      //  if the file /var/run/reboot-required is found after the upgrade 
      Unattended-Upgrade::Automatic-Reboot "true";
      
      // If automatic reboot is enabled and needed, reboot at the specific
      // time instead of immediately
      //  Default: "now"
      Unattended-Upgrade::Automatic-Reboot-Time "02:00";
      
      // Use apt bandwidth limit feature, this example limits the download
      // speed to 70kb/sec
      //Acquire::http::Dl-Limit "70";
      ENDOFUA
      
      UAFILE='/etc/apt/apt.conf.d/50unattended-upgrades'
      say "Creating file $UAFILE"
      sudo chown root:root uatmp
      sudo chmod 644 uatmp
      sudo mv uatmp $UAFILE
      
      say "Completed Automatic Update Setup"      
	  
- **Setup LVM system disk**

      #!/bin/bash
      PhyDisk = /dev/sda
      VolGrp = volgrp
      sudo pvcreate $PhyDisk
      sudo vgcreate $VolGrp $PhyDisk
      sudo lvcreate -L 1g -n boot $VolGrp
      sudo lvcreate -L 4g -n swap $VolGrp
      sudo lvcreate -L 40g -n root $VolGrp
      FREE=$(sudo vgs -o vg_free_count --noheadings --rows)
      sudo lvcreate -l $FREE -n home $VolGrp
