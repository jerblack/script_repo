' Variables
dim iTunes, CurTrack
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
Set CurTrack = iTunes.CurrentTrack
msgbox CurTrack.Rating
' Do the appropriate thing


' Done; release object
Set CurTrack = nothing
set iTunes = nothing


rem End of script.
