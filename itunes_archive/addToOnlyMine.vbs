
dim iTunes, CurTrack, colSources, objSource, colPlaylists, objPlaylist, CurPlaylist

Set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Only Mine")

Set CurTrack = iTunes.CurrentTrack
set CurPlaylist = CurTrack.Playlist

objPlaylist.AddTrack(CurTrack)

wscript.sleep 1000
CurPlaylist.PlayFirstTrack


set iTunes = nothing
set CurTrack = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

