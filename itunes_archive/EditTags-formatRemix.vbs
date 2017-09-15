' Variables
dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tMix
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count
tName = Track(i).Name
id3Parts = Split(tName,"-",2)
tName = Trim(id3Parts(0))
tMix = Trim(id3Parts(1))
tNewName = tName & " (" & tMix & ")"
Track(i).Name = tNewName
next


' Done; release object
Set Track = nothing
set iTunes = nothing
msgbox "Done!"

rem End of script.
