#! /bin/bash

# rclone size gdu:transfer
#

# for f in ~/bin/*; do
# 	echo $f
# done
decrypted="/home/jeremy/shares/server.x/_work/tv"
for f in ${decrypted}/*; do
	if [ -d "$f" ]; then
		echo "checking $f"
		unrarall --clean=all --full-path "$f"
	fi
done		