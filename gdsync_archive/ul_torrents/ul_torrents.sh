#!/bin/bash

seed_folder="/home/jeremy/torrents/seeding"
finished_folder="/home/jeremy/torrents/finished"
encrypted_folder="/home/jeremy/torrents/encrypted/"
google_folder="google_drive:transfer"
history_file="/home/jeremy/torrents/utilities/ul_torrents/history"
mv_log="/home/jeremy/torrents/utilities/ul_torrents/mv_log"
error_log="/home/jeremy/torrents/utilities/ul_torrents/mv_errors"

say () { 
	echo "___$1___"; 
	echo "$(date) >> $1" >> "$mv_log"
	return 0;
}

say_red () {
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	echo -e "${RED}___$1___${NC}"
}

verify_history_file () {
	if ! [ -f  "$history_file" ]; then
		touch "$history_file"
	fi
}

get_new_files () {
	# say "Searching for new downloads"
	# http://askubuntu.com/a/444557/547434
	local files=$(find $seed_folder -exec readlink -f {} \;)
	# files=$(grep " " <<< "$files")
	while read -r line; do
		check_file "$line"
		if [ $? -ne 0 ]; then
			echo "File failed to move: $line" >> "$error_log"
			say_red "File failed to move: $line"
		fi
	done <<< "$files"
}

check_file () {
	local fname="$1"
	grep "$fname" "$history_file" -qwF
	errno=$?
	if [ $errno -ne 0 ]; then
		process_new_file "$fname"
		return $?
	fi
}

process_new_file () {
	local srcname="$1"
	local dstname=${srcname/$seed_folder/$finished_folder}
	say "Found new file: ${srcname#$seed_folder}"
	mkdir -p "$(dirname "$dstname")"
	cp -vf "$srcname" "$dstname"

	if [ -f "$dstname" ]; then
		echo "$srcname" >> "$history_file"
		return 0
	else
		say_red "FAILED TO COPY FILE"
		return 1
	fi
}

 # TODO only run if there's anything to upload
upload_new_files () {
	if [ "$(ls -A ${encrypted_folder})" ]; then
		touch "$encrypted_folder/hold"
		say "Sending new torrents to Google"
		rclone --exclude hold --retries 50 move $encrypted_folder $google_folder
		say "Finished sending torrents to Google"
		find $encrypted_folder -empty -type d -delete
		rm "$encrypted_folder/hold"
	fi

}


main () {
	say "Begin watching for new torrents"
	verify_history_file
	while [ true ]; do
		get_new_files 
		upload_new_files 
		say "Check completed at $(date)"
		sleep 10m
	done
}
main



# watching for new files and upload only those to google

# periodically check for new files in seeding folder
#  - use find to see if any files have a create time equal or newer than the last check time

# for any new files
# 	if file name not in moved.txt file
# 		say filename
# 		copy file to finished folder
# 		add original file path to moved.txt file

# rclone any files in the finished folder to the GDU transfer folder