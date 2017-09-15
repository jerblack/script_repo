' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
on error resume next


	Set Track = iTunes.SelectedTracks
	for i = 1 to Track.Count
	tName = Track(i).Name
	id3Parts = Split(tName,"-",2)
	Track(i).Artist = Trim(id3Parts(0))
	Track(i).Name = Trim(id3Parts(1))
	next


	Set Track = nothing
' Do the appropriate thing
'hyphenLoc = InStr(tName,"-")
'wscript.echo "hyphenLoc: " & hyphenLoc
'tArtist = Trim(Left(tName,hyphenLoc - 1))
'wscript.echo "tNewName: " & tNewName
'tNewName = Trim(Right(tName,hyphenLoc - 1))
'wscript.echo "tArtist: " & tArtist
'Track(i).Name = tNewName
'Track(i).Artist = tArtist


' Done; release object

set iTunes = nothing
msgbox "Done!"

rem End of script.
