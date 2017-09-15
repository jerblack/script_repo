'on error resume next
dim iTunes, colSources, objSource, colPlaylists, objPlaylist, Track
set iTunes = CreateObject("iTunes.Application")
set colSources = iTunes.Sources
set objSource = colSources.ItemByName("Library")
set colPlaylists = objSource.Playlists
set objPlaylist = colPlaylists.ItemByName("Music to Archive")
' get all tracks in the playlist
set Track = objPlaylist.Tracks

'Delete first track in playlist until playlist is empty
Do until Track.Count = 0

	Track(1).delete

Loop


set Track = nothing
set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

