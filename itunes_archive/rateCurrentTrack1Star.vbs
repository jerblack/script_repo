' Variables
dim iTunes, CurTrack, CurPlaylist
' Connect to iTunes app
set iTunes = CreateObject("iTunes.Application")
set CurTrack = iTunes.CurrentTrack
set CurPlaylist = CurTrack.Playlist

'msgbox CurPlaylist
CurTrack.Rating = 20

wscript.sleep 1000
CurPlaylist.PlayFirstTrack


set CurTrack = nothing
set iTunes = nothing


rem End of script.
