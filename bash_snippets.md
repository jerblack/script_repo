      # header
      #!/bin/bash
      
      # easier printing function
      say () { echo "___$1___"; return 0; }
      
      
      # get LVM vg free extents for variable
      FREE=$(sudo vgs -o vg_free_count --noheadings --rows)
      echo $FREE
      
      # get DistID (Ubuntu) and DistCode (xenial)
      DistID=$(lsb_release -is)
      DistCode=$(lsb_release -cs)
      echo $DistID
      echo $DistCode
      
      
      # Check if repo already installed before installing
      # http://askubuntu.com/a/182695
      REPO=x2go/stable
      if find /etc/apt/ -name *.list | xargs cat | grep  ^[[:space:]]*deb | grep $REPO -q
      then
      	echo ___$REPO repository is already present___
      else
      	echo ___adding $REPO repository___
      	sudo apt-add-repository ppa:$REPO -y
      fi
      
      
      # Multi-line strings into variables
      VAR=123abc
      text="Uno
      Dos
      Tres
      $VAR
      blah blah banana"
      echo "$text" > outfi.txt
      read -r -d '' text <<- EOM
      	one
      	two - x
      	three
      	seven
      	$VAR
      EOM
      echo "$text" > outfi2.txt
      
      # Multi-line strings directly into files
      VAR=potato
      cat > autmp <<- ENDOFAU
      	text text $VAR text
      ENDOFAU
      cat autmp
      
      # Move folder contents to google drive
      SRC=/home/$USER/torrents/encrypted
      DST=google_drive:transfer
      rclone --exclude /hold --retries 50 move $SRC $DST
      
      # remove empty folders
      find $SRC -empty -type d -delete
      
      # count number of monitors
      xrandr -d :0 -q | grep ' connected' | wc -l
