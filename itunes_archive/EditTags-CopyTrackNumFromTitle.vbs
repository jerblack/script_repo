on error resume next
' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count
tName = Track(i).Name
id3Parts = Split(tName,"-",2)
Track(i).TrackNumber = Trim(id3Parts(0))
Track(i).Name = Trim(id3Parts(1))

next



' Done; release object
Set Track = nothing
set iTunes = nothing
msgbox "Done!"

rem End of script.
