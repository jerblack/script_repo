# -*- coding: utf_8 -*-
# !/usr/bin/env python
from pm_server_logging import log
import pprint as pp

# ----------------------------------------- #
local_delete_folder = 'Z:/iTunes/Deleted/'
local_archive_folder = 'Z:/iTunes/Archive/'
db = 'poleymote.db'
sp_app_name = 'poleymote:'
http_port = 80
# ----------------------------------------- #

pconfig = {}


def readConfig():
    global pconfig
    log('readConfig',
        "Reading 'pm_settings.ini' into pconfig object")
    # try:
    #     f = open("pm_settings.ini")
    #     pconfig = eval(f.read())
    #     f.close()
    #     return pconfig
    # except IOError:
    #     log('readConfig',
    #         "'pm_settings.ini' not found; calling resetDefaultConfig")

    return resetDefaultConfig()


def updateConfig(new_config):
    global pconfig
    f = open("pm_settings.ini", "w")
    f.write(str(new_config))
    f.close()
    pconfig = new_config


def resetDefaultConfig():
    global pconfig
    log('resetDefaultConfig',
        "Changing all settings to default values," +
        " creating new 'pm_settings.ini'")

    defaults = {
        "Local": {
            "Use_iTunes": True,
            "Index_Local_Music": True,
        },
        "AirFoil": {
            "Use_Airfoil": True,
            "Display_warning_if_not_connected": False
        },
        "Playlists": {
            "Favorite_Playlists":
            [
                {
                    "Name": "Electronic/Dance",
                    "uri":
                    "spotify:user:jerblack:playlist:0m2cGNVm9Zp6l9e09SiffL"
                }, {
                    "Name": "Ambient/Downtempo",
                    "uri":
                    "spotify:user:jerblack:playlist:7a9mjhowih1tHU94Yve7lx"
                }, {
                    "Name": "24 Hours - The Starck Mix",
                    "uri":
                    "spotify:user:jerblack:playlist:7gUXkmNkYCMYmU8GBMHscI"
                }, {
                    "Name": "iTunes Music",
                    "uri":
                    "spotify:user:jerblack:playlist:1rq9Taze8KgK8gTkC9mlzh"
                }, {
                    "Name": "Classical",
                    "uri":
                    "spotify:user:jerblack:playlist:43HpLYeTItmpty8UYgA9Fc"
                }, {
                	"Name": "Rap",
                	"uri":
                	"spotify:user:jerblack:playlist:5PE2Izj6FP89zPQV6U1g05"
                }
            ],
            "Shuffle_Playlists":
            [
                # {
                #     "Name": "Electronic/Dance",
                #     "uri":
                #     "spotify:user:jerblack:playlist:0m2cGNVm9Zp6l9e09SiffL"
                # },
                 {
                	"Name": "Shuffle EPs 1",
                	"uri": 
                	"spotify:user:jerblack:playlist:2u1oaWXztlG7Xd5psYiXqL"
                }, {
                    "Name": "Shuffle Playlist 1",
                    "uri":
                    "spotify:user:jerblack:playlist:5XnrfPufI8J3WuDXSJrj3m"
                }, {
                    "Name": "Shuffle Playlist 2",
                    "uri":
                    "spotify:user:jerblack:playlist:3L5VxdSBxnUPVhwXCoThiG"
                }, {
                    "Name": "Shuffle Playlist 3",
                    "uri":
                    "spotify:user:jerblack:playlist:3HESEQC2UvmA1Ap1q4Q2m1"
                }, {
                    "Name": "Shuffle Playlist 4",
                    "uri":
                    "spotify:user:jerblack:playlist:6MmxBfR7jiX4f9cSi5O2PW"
                }
                # , {
                #     "Name": "iTunes Music",
                #     "uri":
                #     "spotify:user:jerblack:playlist:1hlZqBtgV9Dz8N1Kzr1Dhk"
                # }
            ],
            "Shuffle_Playlist_Size": 250,
            "Automatically_add_music_to_queue_when_nearing_end": True,
            "Spl_base_name": 'Shuffle Playlist',
            "Spl_folder": 'Shuffle Playlists'
                    },
        "Bookmarks": {
            "Support_Multiple_Users": True,
            # Users are created in Settings in the dashboard
            "Users":
            [
            {
                "Name": "Jeremy",
                "uri":
                "spotify:user:jerblack:playlist:4aSwU3mYsVoMV5Wnxo4AbB"
            }, {
                "Name": "Maria",
                "uri":
                "spotify:user:jerblack:playlist:6b82pMJqlIBygf3cHgZZ5p"
            }
        ],
            "Support_Bookmarks": True,
            "Use_Custom_Playlist": False,
            "Automatically_star_track_if_bookmarked": True
            },
        "Delete": {
            "Delete_from_current_playlist": True,
            "Delete_from_all_shuffle_playlists": True,
            "Delete_from_all_favorite_playlists": True,
            "Save_in_purgatory_playlist": False,
            "Custom_purgatory_playlist": "",
            "Delete_local_file": True,
            "Delete_from_iTunes": True,
            "Rate_1_star_in_iTunes": True,
            "Rate_1_star_in_local_tag": True,
            "Move_to_purgatory_folder": True,
            "Custom_purgatory_folder": "",
            "Show_option_for_deleting_all_by_artist": True,
            "Show_option_for_deleting_all_by_album": True,
            "Delete_Track_Queue":"spotify:user:jerblack:playlist:4EtycmfHvTNiQAJmq6kvJi",
            "Delete_Artist_Queue":"spotify:user:jerblack:playlist:4sZzEkCXWz2OZakwsicMYu",
            "Delete_Album_Queue": "spotify:user:jerblack:playlist:6g63R6jX0jncHn6NF2Vfkj"
            },
        "Archive": {
            "Archive_from_current_playlist": True,
            "Archive_from_all_shuffle_playlists": True,
            "Archive_from_all_favorite_playlists": True,
            "Archive_duration": "PLACEHOLDER",
            "Restore_to_original_playlists": True,
            "Restore_to_custom_playlist": False,
            "Custom_restore_playlist": "PLACEHOLDER URI",
            "Archive_Track_Queue":"spotify:user:jerblack:playlist:7g4Wk46Gt6aKVa7CsyZqHC"
            },
        "Heart": {
            "Star_in_Spotify": True,
            "Add_to_bookmarks": True,
            "Rate_5_star_in_iTunes": True,
            "Rate_5_star_in_local_tag": True
            },
        "Logging": {
            "Log_to_file": True,
            "Custom_log_filename": "",
            "Custom_log_path": "",
            "Verbose_Logging": True
            }
        }
    f = open("pm_settings.ini", "w")
    pp.pprint(defaults, f)
    f.close()
    pconfig = defaults
    return pconfig

# ----------------------------------------- #
# End of Config file for Poleymote Settings #
# ----------------------------------------- #
