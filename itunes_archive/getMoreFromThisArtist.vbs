dim iTunes, CurTrack, colSources, objSource, colPlaylists, objPlaylist

Set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Find more from artist")

Set CurTrack = iTunes.CurrentTrack
CurTrack.Rating = 100
objPlaylist.AddTrack(CurTrack)

set iTunes = nothing
set CurTrack = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing
