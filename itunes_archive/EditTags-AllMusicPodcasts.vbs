' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
set colSources = iTunes.Sources
set objSource = colSources.ItemByName("Library")
set colPlaylists = objSource.Playlists

' Fix everything in the 'Z_Colon Fix' playlist

set objPlaylist = colPlaylists.ItemByName("KCRW Today's Top Tune")
' get all tracks in the playlist
set Track = objPlaylist.Tracks

Do until Track.Count = 0
	tName = Track(1).Name
	id3Parts = Split(tName,": ",2)
	Track(1).Artist = Trim(id3Parts(0))
	Track(1).Name = Trim(id3Parts(1))
	Wscript.Sleep 2000
Loop

set Track = Nothing
set objPlaylist = Nothing

' Fix everything in the 'Z_Dash Fix' playlist
set objPlaylist = colPlaylists.ItemByName("KEXP & Song of the Day")
set Track = objPlaylist.Tracks

Do until Track.Count = 0
	tName = Track(1).Name
	id3Parts = Split(tName,"-",2)
	'Track(1).Artist = Trim(id3Parts(0))
	Track(1).Name = Trim(id3Parts(1))
	Wscript.Sleep 2000
	
Loop


set Track = nothing
set objPlaylist = nothing
set colPlaylists = nothing
set objSource = nothing
set colSources = nothing
set iTunes = nothing

rem End of script.
