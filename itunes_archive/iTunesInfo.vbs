

' ===========
' Description
' ===========
' Reads & displays miscellaneous information from iTunes.
' Modify to read any other data of interest that cannot be read in the iTunes interface.


Option Explicit
Dim Count,iTunes,nl,T,tab,Tracks
Dim I,L,Lists,FP,NP,SP
nl=vbCrLf
tab=Chr(9)
Set iTunes=CreateObject("iTunes.Application")

Set Tracks=iTunes.SelectedTracks
If Tracks is Nothing Then
  Count=0
Else 
  Count=Tracks.Count
End If

FP=0
NP=0
SP=0
' Loop through playlists
Set Lists=iTunes.Sources.Item(1).Playlists
For I=Lists.Count To 1 Step -1
  Set L=Lists.Item(I)
  If L.Kind=2 Then
    If L.SpecialKind=4 Then
      FP=FP+1
    ElseIf L.Smart Then
      SP=SP+1
    Else
      NP=NP+1
    End If
  End If
Next  

' Set values here as required
' Refer to iTunes COM SDK to see what can be controlled via script commands
' iTunes.ForceToForegroundOnDialog=False

' List out iTunes properties
T="iTunes version" & tab & tab & tab & iTunes.Version & nl
T=T & "XML location" & tab & tab & tab & iTunes.LibraryXMLPath & nl
T=T & "Selected playlist" & tab & tab & tab & iTunes.BrowserWindow.SelectedPlaylist.Name & nl
T=T & "Current source" & tab & tab & tab & iTunes.BrowserWindow.SelectedPlaylist.Source.Name & nl
T=T & "Current encoder" & tab & tab & tab & iTunes.CurrentEncoder.Name & nl
T=T & "AppCommandMessageProcessing" & tab & iTunes.AppCommandMessageProcessingEnabled & nl
T=T & "Force dialogs to foreground" & tab & tab & iTunes.ForceToForegroundOnDialog & nl
T=T & "Process media keys" & tab & tab & tab & iTunes.AppCommandMessageProcessingEnabled & nl & nl
T=T & "Total number of items in the library" & tab & iTunes.LibraryPlaylist.Tracks.Count & nl
T=T & "Regular playlists " & tab & tab & tab & NP & nl
T=T & "Smart playlists" & tab & tab & tab & SP & nl
T=T & "Playlist folders" & tab & tab & tab & FP & nl & nl
If Count=0 Then
  T=T & "There are no tracks currently selected."
ElseIf Count=1 Then
  T=T & "There is 1 track currently selected."
Else
  T=T & "There are " & Count & " tracks currently selected."
End If
MsgBox T,0,"iTunes Info"
