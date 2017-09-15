
Dim iTunes 'As iTunes
Dim ArgPlaylist 'As String
Dim ArgPlaylistLcase 'As String
Dim Playlist 'As IITPlaylist
Dim TempPlaylist 'As IITPlaylist
Dim SyntaxErr 'As Boolean
Dim Msg 'As String


' Init
ArgPlaylist = "Jeremy's Bookmarks"
Set Playlist = Nothing

' Special support: if they provide exactly one unnamed argument, then
' assume that it's the playlist name (assuming /playlist hasn't been specified)
If (ArgPlaylist = "") And (Wscript.Arguments.Unnamed.Count = 1) Then
	' Use it!
	ArgPlaylist = Wscript.Arguments.Unnamed.Item(0)
End If


' Connect to iTunes app
Set iTunes = Wscript.CreateObject("iTunes.Application")


' Find the specified playlist
Set Playlist = Nothing
ArgPlaylistLcase = LCase(ArgPlaylist)
For Each TempPlaylist In iTunes.LibrarySource.Playlists
    If LCase(TempPlaylist.Name) = ArgPlaylistLcase Then
        ' Match!
        Set Playlist = TempPlaylist
        Exit For
    End If
Next 'TempPlaylist

' Did we find one?
If Playlist Is Nothing Then
    Wscript.echo "The playlist """ + ArgPlaylist + """ could not be found."
    Wscript.Quit
Else
	' Start playing the playlist
	Playlist.PlayFirstTrack
End If


' Done; clean up
Set Playlist = Nothing
Set iTunes = Nothing


Rem End of script.
