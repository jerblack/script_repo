' Variables
dim iTunes, CurTrack
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")

Set CurTrack = iTunes.CurrentTrack
CurTrack.Rating = 100

' Done; release object
Set CurTrack = nothing
set iTunes = nothing


rem End of script.
