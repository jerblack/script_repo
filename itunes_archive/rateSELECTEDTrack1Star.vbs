' Variables
dim iTunes, CurTrack, i
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count
Track(i).Rating = 20
next
' Do the appropriate thing


' Done; release object
Set Track = nothing
set iTunes = nothing


rem End of script.
