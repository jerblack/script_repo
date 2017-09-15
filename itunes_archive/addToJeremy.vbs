
dim iTunes, CurTrack, colSources, objSource, colPlaylists, objPlaylist

Set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Jeremy's Bookmarks")

Set CurTrack = iTunes.CurrentTrack

objPlaylist.AddTrack(CurTrack)

set iTunes = nothing
set CurTrack = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

