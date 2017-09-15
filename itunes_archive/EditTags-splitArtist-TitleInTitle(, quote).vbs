dim iTunes, CurTrack, i, tName, id3Parts , tNewName, tArtist
set iTunes = CreateObject("iTunes.Application")
on error resume next
Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count
tName = Track(i).Name
id3Parts = Split(tName,", '",2)
Track(i).Artist = Trim(id3Parts(0))
Track(i).Name = Replace(Trim(id3Parts(1)),"'","")
next
Set Track = nothing
Set iTunes = nothing
MsgBox "Done!"
rem End of script.
