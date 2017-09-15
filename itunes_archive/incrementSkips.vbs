
dim iTunes, i, CurTrack
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
Set CurTrack = iTunes.CurrentTrack

CurTrack.SkippedDate = Now
CurTrack.SkippedCount = CurTrack.SkippedCount + 1


set Track = nothing
set iTunes = nothing



