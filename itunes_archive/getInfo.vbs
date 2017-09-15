Option Explicit
On Error Resume Next 
Dim TrackPath, ArtPath, Track, songName, Artobj, Art, Format, fso, noArt
Dim FormatArray(4), ExtArray(4)
Set fso = CreateObject("Scripting.FileSystemObject")
FormatArray(0) = "Unknown"
FormatArray(1) = "JPEG"
FormatArray(2) = "PNG"
FormatArray(3) = "BMP"
ExtArray(0) = "unk"
ExtArray(1) = "jpg"
ExtArray(2) = "png"
ExtArray(3) = "bmp"
Set iTunes = CreateObject("iTunes.Application")
Set Track = iTunes.CurrentTrack
TrackPath = "c:\xampp\htdocs\"
noArt = False
if Track.Artwork.Count <> 0 then
	Set Artobj = Track.Artwork
	Set Art = Artobj.Item(1)
	Format = Art.Format
	ArtPath = fso.BuildPath(TrackPath, "art." & ExtArray (Format))
	Art.SaveArtworkToFile(ArtPath)
else
	noArt = True
End if
Dim iTunes,Title,Tracks,tName,tArtist,tAlbum,tPlayTimes, tDateAdded, tGenre
Dim tLength,tBitrate,tYear, tTrackNum, tRating
Dim newFS, File_Name, realRating, tPlaylist
Set newFS = Createobject("Scripting.FileSystemObject") 
Set File_Name = newFS.OpenTextFile("C:\\xampp\\htdocs\\trackinfo.htm", 2, True) 
With Track
	tName = .Name
	tArtist = .Artist
	tAlbum = .Album
	tRating = .Rating
	tYear = .Year
	tTrackNum = .TrackNumber
	tPlayTimes = .PlayedCount
	tLength = .Time
	tBitrate = .BitRate
	tGenre = .Genre
	tDateAdded = .DateAdded
	tPlaylist = .Playlist.Name
  End With

 if tRating = 0 then
	realRating = "Not Rated"
elseif tRating = 20 then
	realRating = "1 Star"
elseif tRating = 40 then
	realRating = "2 Stars"
elseif tRating = 60 then
	realRating = "3 Stars"
elseif tRating = 80 then
	realRating = "4 Stars"
elseif tRating = 100 then
	realRating = "5 Stars"
end if

if iTunes.PlayerState <> 0 then
File_Name.WriteLine "<html><head><title>PoleyMote</title>"
File_Name.WriteLine "<meta name = ""viewport"" content = ""width=device-width,user-scalable=no""><META HTTP-EQUIV=""Pragma"" CONTENT=""no-cache""><META HTTP-EQUIV=""Expires"" CONTENT=""-1"">"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-capable"" content=""yes"" >"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-status-bar-style"" content=""black"" >"
File_Name.WriteLine "<link href=""iphone.css"" type=""text/css"" rel=""stylesheet"">"
File_Name.WriteLine "</head><body>"
File_Name.WriteLine "<div style=""height:10px;""></div>"
File_Name.WriteLine "<p id=""trackInfoHead"">[artist]</p>"
File_Name.WriteLine "<p id=""trackInfo"">" & tArtist & "</p>"
File_Name.WriteLine "<p id=""trackInfoHead"">[album]</p>"	
File_Name.WriteLine "<p id=""trackInfo"">" & tAlbum & "</p>"
File_Name.WriteLine "<p id=""trackInfoHead"">[title]</p>"
File_Name.WriteLine "<p id=""trackInfo"">" & tName & "</p>"
File_Name.WriteLine "<input style=""border-top-width:1px;margin-top:10px;"" id=""button"" value=""Return Home"" type=""button"" onclick=""window.location='/';"" >"
if noArt = False then
	if Format = 0 then
		'unknown
		'do nothing
	elseIf Format = 1 then 
		'jpg
		File_Name.WriteLine "<img id=""art"" src=""art.jpg"">"
	elseIf Format = 2 then 
		'png
		File_Name.WriteLine "<img id=""art"" src=""art.png"">"
	elseIf Format = 3 then 
		'bmp
		File_Name.WriteLine "<img id=""art"" src=""art.bmp"">"
	end If 
	Else
	File_Name.WriteLine "<img id=""art"" src=""NoArt.jpg"">"
end if
File_Name.WriteLine "<hr/ style=""color:#0099CC;background-color:#0099CC;height:1px;border:none;margin-top:5px;""><div style=""margin:30px;"">"
File_Name.WriteLine "<table >"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Rating:</td><td><p id=""trackDetails"">" & realRating & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Year:</td><td><p id=""trackDetails"">" & tYear & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Length:</td><td><p id=""trackDetails"">" & tLength & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">#Plays:</td><td><p id=""trackDetails"">" & tPlayTimes & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Track#:</td><td><p id=""trackDetails"">" & tTrackNum & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Bitrate:</td><td><p id=""trackDetails"">" & tBitrate & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Genre:</td><td><p id=""trackDetails"">" & tGenre & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Playlist:</td><td><p id=""trackDetails"">" & tPlaylist & "</p></td></tr>"
File_Name.WriteLine "<tr><td><p id=""trackDetails"">Added:</td><td><p id=""trackDetails"">" & tDateAdded & "</p></td></tr></table></div>"
File_Name.WriteLine "</body></html>"
File_Name.Close 
else
File_Name.WriteLine "<html><head><title>PoleyMote</title>"
File_Name.WriteLine "<meta name = ""viewport"" content = ""width=device-width,user-scalable=no"">"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-capable"" content=""yes"" >"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-status-bar-style"" content=""black"" >"
File_Name.WriteLine "<link href=""iphone.css"" type=""text/css"" rel=""stylesheet"">"
File_Name.WriteLine "</head><body>"
File_Name.WriteLine "<p id=""trackInfoHead"">Stopped</p>"
File_Name.WriteLine "<p id=""trackInfo"">No Music Playing</p>"
File_Name.WriteLine "<input style=""border-top-width:1px;margin-top:10px;"" id=""button"" value=""Return Home"" type=""button"" onclick=""window.location='/';"" >"
File_Name.WriteLine "</body></html>"
File_Name.Close 
end if
Set File_Name = Nothing 
Set newFS = Nothing 



