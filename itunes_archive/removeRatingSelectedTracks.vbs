' Variables
dim iTunes, CurTrack, i
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count
Track(i).AlbumRating = 0
Track(i).Rating = 0
next
' Do the appropriate thing


' Done; release object
Set Track = nothing
set iTunes = nothing


rem End of script.
