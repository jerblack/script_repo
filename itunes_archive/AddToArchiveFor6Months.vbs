on error resume next
dim iTunes, CurTrack, CurPlaylist
set iTunes = CreateObject("iTunes.Application")
Set CurTrack = iTunes.CurrentTrack
set CurPlaylist = CurTrack.Playlist

CurTrack.Comment = DateAdd("d",180,date)
CurTrack.Enabled = False

wscript.sleep 1000
CurPlaylist.PlayFirstTrack

Set CurTrack = nothing
set iTunes = nothing
