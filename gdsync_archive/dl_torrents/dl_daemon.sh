#!/bin/bash
base_path="/home/jeremy/bin"

start_daemon () {
    prog_path="$base_path/$1"
    sh_name="$prog_path/$1.sh"
    log="$prog_path/$1.log"
    daemon -n "$1" -r "$sh_name" -l "$log" -o "$log"
}

# start_daemon ul_torrents
start_daemon dl_torrents
