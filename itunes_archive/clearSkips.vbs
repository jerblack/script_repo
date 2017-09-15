on error resume next
dim iTunes, i, Track
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
	Set Track = iTunes.SelectedTracks
Do 
	for i = 1 to Track.Count
		Track(i).SkippedDate = 0
		Track(i).SkippedCount = 0
	next
Loop while Track.Count <> 0

set Track = nothing
set iTunes = nothing



