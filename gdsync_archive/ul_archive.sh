#!/bin/bash

root="/home/jeremy"; work="${root}/_work"
local_archive="${root}/shares/server.z/_work/ul_archive"
archive_dec="${work}/archive_dec"; archive_enc="${work}/archive_enc"
max_size="+6G"; chunk_size="5G"
sync_size=250 #250GB 


sync_size=$[$sync_size*1000000000]

targets=("gdu:backup" "amzn:backup")

say () { echo "___$1___"; return 0; }

encrypt_files_limit () {
	#!/bin/bash
	size=0
	find "$local_archive" -type f -print | while read f; do
		if ! [[ $(grep Trash-1000 -q) ]];then
			sz=$(stat "$f" -c %s)
			let size+=sz
			if [[ $size -lt $sync_size ]]; then
				fname="$(basename "$f")"
				dname="$(dirname "$f")"
				say "Encrypting $fname"
				mv --verbose "$f" "${archive_dec}/${fname}"
			else
				echo "Hit maximum size"
				return 0
			fi
			# echo $size
		fi
	done
}

upload_files () {
	if [ "$(ls ${archive_enc})" ]; then
		say "Uploading to Amazon Drive archive"
		rclone --retries 50 --exclude .Trash-1000 --checksum --ignore-times copy "$archive_enc" amzn:backup
		say "Uploading to Google Drive archive"
		rclone --retries 50 --exclude .Trash-1000 copy "$archive_enc" gdu:archive
		say "Finished all uploads"
	fi
}

split_large_files () {
	say "Splitting files larger than ${max_size/+/}"
	find "$local_archive" -size "$max_size" -print | while read f; do 
		fname="$(basename "$f")"
		dname="$(dirname "$f")"
		say "Splitting $fname"
		mv --verbose "$f" "${dname}/split_file"
		fname_under="${fname// /_}"
		split --verbose -b "$chunk_size" -d split_file "$fname.chunk."
		echo "cat \"$fname_under.chunk.\"* > \"$fname_under\"" > "join_${fname_under}.sh"
		echo "mv \"$fname_under\" \"$fname\"" >> "join_${fname_under}.sh"
		chmod +x "join_${fname_under}.sh"
		rm split_file
	done
}



loop_uploader () {
	# upload in 250GB chunks until finished
	while [ "$(ls ${local_archive})" ]; do
		rm -rf "${local_archive}/.Trash-1000"
		split_large_files
		encrypt_files_limit
		upload_files
		sleep 600

	done

}

main () {
	say "Uploading files to archive"
	# loop_uploader
	rm -rf "${local_archive}/.Trash-1000"
	split_large_files
	# encrypt_files_limit
	# upload_files
}
main











# encrypt_files () {
# 	if [ "$(ls ${local_archive})" ]; then
# 		# local_archive has files in it
# 		say "Encrypting files for archive."
# 		rsync -avmW --exclude=.Trash-1000 --remove-source-files --progress "${local_archive}/" "${archive_dec}/"
# 		touch "${local_archive}/hold"
# 		find "${local_archive}" -empty -type d -delete
# 		rm "${local_archive}/hold"
# 	fi
# }