'Option Explicit
On Error Resume Next 
Dim iTunes,Title,Tracks,tName,tArtist,tAlbum,tPlayTimes
Dim tLength,tBitrate,tYear, tTrackNum, tDateAdded, tArt
Dim newFS, File_Name, realRating, tPlaylist
Set iTunes=CreateObject("iTunes.Application")
Set Track=iTunes.CurrentTrack

Set newFS = Createobject("Scripting.FileSystemObject") 
Set File_Name = newFS.OpenTextFile("C:\\xampp\\htdocs\\headerinfo.txt", 2, True, -2) 
if iTunes.PlayerState <> 0 then
	With Track
	  tName = .Name
	  tArtist = .Artist
	End With
	File_Name.WriteLine tName & "||| by: " & tArtist
	File_Name.Close 
else
	File_Name.WriteLine "Music Stopped"
	File_Name.Close 
end if

Set File_Name = Nothing 
Set newFS = Nothing 



