' rateAllByArtist1Star
' Rate all tracks by currently playing artist with 1 star (marking them for deletion that night)

' Declare variables for itunes to get current track
dim iTunes, CurTrack, CurPlaylist, i

' Declare variable for artist from current track
Dim artistToFind

' Declare variable to get main iTunes library
Dim sources, objSource, colPlaylists, libPlaylist, TrackCount, CurArtist, checkedTracks, checkedTrack


' Read artist into variable
Set iTunes = CreateObject("iTunes.Application")
Set CurTrack = iTunes.CurrentTrack
set CurPlaylist = CurTrack.Playlist
artistToFind = LCase(CurTrack.Artist)

' rate current track 1 star
CurTrack.Rating = 20

' resume playing music
wscript.sleep 1000
CurPlaylist.PlayFirstTrack

' get main music library
set sources = iTunes.Sources
set objSource = sources.ItemByName("Library")
set colPlaylists = objSource.Playlists
set libPlaylist = colPlaylists.ItemByName("Music")
'MsgBox(LCase(artistToFind))
Set checkedTracks = libPlaylist.Tracks
TrackCount = checkedTracks.Count
'Set checkedTrack  = checkedTracks.Item(1)
'MsgBox(checkedTrack.Artist)
' use for loop to iterate through all tracks
For i = 1 To TrackCount
	Set checkedTrack  = checkedTracks.Item(i)
' check each track to see if artist ifs the one we are looking For
	CurArtist = LCase(checkedTrack.Artist)
	If CurArtist = artistToFind Then
		If checkedTrack.Rating = 0 Then
			checkedTrack.Rating = 20
		End If 
	End If
' if so, rate the track with 1 star
Next


