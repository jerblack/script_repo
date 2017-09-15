on error resume next
dim iTunes, colSources, objSource, colPlaylists, objPlaylist, archiveDate
dim Track, count
count = 0
set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Music Podcasts")
' get all tracks in the playlist
Set Track = objPlaylist.Tracks
'iterate through them
for i = 1 to Track.Count

			msgbox Track(i).Kind
			'Track(i).Enabled = True
			'count = count + 1


next
Set CurTrack = nothing
set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

