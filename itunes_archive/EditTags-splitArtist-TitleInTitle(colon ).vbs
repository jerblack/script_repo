' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
set colSources = iTunes.Sources
set objSource = colSources.ItemByName("Library")
set colPlaylists = objSource.Playlists
set objPlaylist = colPlaylists.ItemByName("Z_Colon Fix")
' get all tracks in the playlist
set Track = objPlaylist.Tracks

Do until Track.Count = 0
	tName = Track(1).Name
	id3Parts = Split(tName,": ",2)
	Track(1).Artist = Trim(id3Parts(0))
	Track(1).Name = Trim(id3Parts(1))
	Wscript.Sleep 3000
Loop

set Track = nothing
set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing


rem End of script.
