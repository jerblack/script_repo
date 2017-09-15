' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist, numParts
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
on error resume next
' showname - seasonXepisode - episodetitle

	Set Track = iTunes.SelectedTracks
	for i = 1 to Track.Count
	tName = Track(i).Name
	id3Parts = Split(tName,"-",3)
	Track(i).Show = Trim(id3Parts(0))
	numParts = Split(id3Parts(1),"x",2)
	Track(i).SeasonNumber = numParts(0)
	Track(i).EpisodeNumber = numParts(1)
	Track(i).EpisodeID = Trim(id3Parts(2))
	
	'Track(i).Name = Trim(id3Parts(1))
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
' Show
' SeasonNumber
' EpisodeNumber 
' EpisodeID 