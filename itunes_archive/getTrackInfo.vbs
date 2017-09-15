' Variables
dim iTunes, Track, i
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set Track = iTunes.SelectedTracks
for i = 1 to Track.Count

msgbox Track(i).index

next


' Done; release object
Set Track = nothing
set iTunes = nothing


rem End of script.
