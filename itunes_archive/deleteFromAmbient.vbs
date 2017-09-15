'on error resume next
dim iTunes, colSources, objSource, colPlaylists, objPlaylist, libPlaylist, Track, mainTrack, trackInLib
set iTunes = CreateObject("iTunes.Application")
set colSources = iTunes.Sources
set objSource = colSources.ItemByName("Library")
set colPlaylists = objSource.Playlists
set objPlaylist = colPlaylists.ItemByName("Ambient")
set libPlaylist = colPlaylists.ItemByName("Music")

' get all tracks in the playlist
set Track = objPlaylist.Tracks

'Delete first track in playlist until playlist is empty
'Do until Track.Count = 0
'	Track(1).delete
'Loop
Do until Track.Count = 0

set mainTrack = Track(1)
set trackInLib = libPlaylist.Tracks.ItemByPersistentID(iTunes.ITObjectPersistentIDHigh(mainTrack), iTunes.ITObjectPersistentIDLow(mainTrack))
trackInLib.delete
 
 Loop

set Track = nothing
set iTunes = nothing
set colSources = nothing
set libPlaylist = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing

