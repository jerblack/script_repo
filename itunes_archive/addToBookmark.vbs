'Option Explicit
On Error Resume Next 
Dim iTunes,Title,Tracks,tName,tArtist,tAlbum,tPlayTimes
Dim tLength,tBitrate,tYear, tTrackNum, tDateAdded, tArt
Dim newFS, File_Name, realRating, tPlaylist
Set iTunes=CreateObject("iTunes.Application")
Set Track=iTunes.CurrentTrack

Set newFS = Createobject("Scripting.FileSystemObject") 
Set File_Name = newFS.OpenTextFile("C:\\xampp\\htdocs\\BookmarkMaria.txt", 8, True) 
if iTunes.PlayerState <> 0 then
	With Track
	  tName = .Name
	  tArtist = .Artist
      tAlbum = .Album
	End With
	File_Name.WriteLine tName & "||| by: " & tArtist & "||| on: " & tAlbum
	File_Name.Close 
else
	File_Name.Close 
end if

Set File_Name = Nothing 
Set newFS = Nothing 



