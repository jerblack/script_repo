on error resume next
dim iTunes, CurTrack, i, tName, id3Parts , tAlbum, tArtist, tNewAlbum, Track
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set Track = iTunes.SelectedTracks
	for i = 1 to Track.Count
		tArtist = Track(i).Artist
		tAlbum = Track(i).Album
		tNewAlbum = tArtist & ": " & tAlbum
		Track(i).Album = tNewAlbum
	next

	for i = 1 to Track.Count
		tName = Track(i).Name
		id3Parts = Split(tName,"-",2)
		Track(i).Artist = Trim(id3Parts(0))
		Track(i).Name = Trim(id3Parts(1))
	next

' Done; release object
set Track = nothing
set iTunes = nothing
msgbox "Done"

rem End of script.
