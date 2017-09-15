on error resume next
dim iTunes, colSources, objSource, colPlaylists, objPlaylist, archiveDate
dim Track, count
count = 0
set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Music")
' get all tracks in the playlist
Set Track = objPlaylist.Tracks
'iterate through them
for i = 1 to Track.Count
'Copy Comment to date variable, converting to date in the process
	if Track(i).Enabled = False then 
		archiveDate = Track(i).Comment
		'Check if date variable in the past
		if archiveDate < date then
			'clear date and select checkmark next to track
			Track(i).Comment = ""
			Track(i).Enabled = True
			count = count + 1
		end if
	end if
next
Set CurTrack = nothing
set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

