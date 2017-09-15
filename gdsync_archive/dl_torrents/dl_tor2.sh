#! /bin/bash
check_interval_mins=10
notify_interval_mins=5 
dl_src="gdu:transfer"
work="/home/jeremy/_work"
encfs_enc="$work/encfs_enc"
encfs_dec="$work/encfs_dec"
decrypted="$work/decrypted"
recycled="$work/recycled"
shares="/home/jeremy/shares/server.x/_work"
mv_dst="$shares/proc/"
mv_dst_tv="$shares/tv/"

mins_so_far=$check_interval_mins # lets script check immediately on startup

say () { echo "___$1___"; return 0; }

say "Starting dl_torrents. Checking every $[check_interval_mins] minutes."

while [ true ]; do
	if [[ $mins_so_far -ge $check_interval_mins ]]; then
		say "Checking for new files on Google."
		# rclone --retries 50 --exclude hold move gdu:transfer /home/jeremy/_work/encfs_enc
		rclone --retries 50 --exclude hold move $dl_src $encfs_enc
		if [ "$(ls ${encfs_dec})" ]; then
			# echo "Not Empty"
			say "Decrypting downloaded files."
			rsync -avmW --exclude=.Trash-1000 --remove-source-files --progress "${encfs_dec}/" "${decrypted}/"
			touch "${encfs_dec}/hold"
			find "${encfs_dec}" -empty -type d -delete
			rm "${encfs_dec}/hold"
		   	say "Extracting archives"
		   	for f in ${decrypted}/*; do
				if [ -d "$f" ]; then
					echo "Extracting archive in $f"
					# http://askubuntu.com/a/531487/547434
					# https://github.com/arfoll/unrarall
					unrarall --clean=all --full-path "$f"
				fi
			done				
			if [ -d "${decrypted}/tv/" ]; then
				if [ "$(ls ${decrypted}/tv)" ]; then
					for f in ${decrypted}/tv/*; do
						if [ -d "$f" ]; then
							echo "Extracting archive in $f"
							unrarall --clean=all --full-path "$f"
						fi
					done
					say "Moving new TV shows"
					rsync --exclude=.Trash-1000  -avmW --remove-source-files --progress "${decrypted}/tv/" "${mv_dst_tv}"
					# touch "${decrypted}/tv/hold"
					find "${decrypted}/tv" -empty -type d -delete
					# rm "${decrypted}/tv/hold
				fi
			fi
			if [ "$(ls ${decrypted})" ]; then
				say "Moving new downloads"
	    		rsync --exclude=.Trash-1000  -avmW --remove-source-files --progress "${decrypted}/" "${mv_dst}"
				touch "${decrypted}/hold"
				find "${decrypted}" -empty -type d -delete
				rm "${decrypted}/hold"
			fi
		fi
		
		mins_so_far=0
		say "Check complete. Will check again in $[check_interval_mins] minutes."
	else
		if [[ $[mins_so_far%notify_interval_mins] -eq 0 ]]; then
			say "Waiting to check. Next check in $[check_interval_mins-mins_so_far] minutes."
		fi
		let mins_so_far+=1
	fi
 	sleep 60
done