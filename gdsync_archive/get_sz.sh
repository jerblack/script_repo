#!/bin/bash

work=/home/jeremy/shares/server.z/_work/upload.1.clouddrive
size=0
max_size=250000000000 #250GB
find "$work" -print | while read f; do 
	sz=$(stat "$f" -c %s)
	let size+=sz
	if [[ $size -lt $max_size ]]; then
		echo $size
	else
		echo "Hit maximum size"
		exit
	fi
	# echo $size
done
