#!/bin/bash

root="gdu:transfer"
paths=("$root")
sample=$(<gduout)


get_subfolders () {
	lsd_output="$(rclonerclon lsd $1)"
	# lsd_output="$sample"
	count=1
	for o in $lsd_output;do
		if [[ $(expr $count % 5) -eq 0 ]]; then
			echo "$1/$o"

		fi
		let count+=1
	done
}

climb_tree () {
	get_subfolders "$root"
	# echo "$sample"
	# root_list_output="$(rclone lsd $root)"


}

main () {
	climb_tree
}

main


# num_objects=$(grep "Total objects: " <<< "$res" | tr -d "Total objects: ")
# echo "num_obj: $num_objects"

# for each folder in transfer
# 	if total objects = 0
# 		purge folder