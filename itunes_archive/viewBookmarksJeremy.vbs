on error resume next 
dim iTunes, Track, colSources, objSource, colPlaylists, objPlaylist, i, newFS, File_Name
Set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Jeremy's Bookmarks")
Set newFS = Createobject("Scripting.FileSystemObject")

Set File_Name = newFS.OpenTextFile("C:\\xampp\\htdocs\\jeremy.htm", 2, True, -1)

File_Name.WriteLine "<html><head><title>PoleyMote</title>"
File_Name.WriteLine "<meta name = ""viewport"" content = ""width=device-width,user-scalable=no""><META HTTP-EQUIV=""Pragma"" CONTENT=""no-cache""><META HTTP-EQUIV=""Expires"" CONTENT=""-1"">"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-capable"" content=""yes"" >"
File_Name.WriteLine "<meta name=""apple-mobile-web-app-status-bar-style"" content=""black"" >"
File_Name.WriteLine "<link href=""iphone.css"" type=""text/css"" rel=""stylesheet"">"
File_Name.WriteLine "<script> function confirmDelete() {  if (confirm(""Are you sure you want to clear your bookmarks?"")) { window.location = '/scripts/deleteBookmarksJeremy.php';  }}</script>"
File_Name.WriteLine "</head><body>"

File_Name.WriteLine "<input style=""border-top-width:0px;margin-top:0px;"" id=""button"" value=""Return Home"" type=""button"" onclick=""window.location='/';"" >"
File_Name.WriteLine "<hr/ style=""color:#0099CC;background-color:#0099CC;height:1px;border:none;padding:0px;"">"


Set Track = objPlaylist.Tracks
for i = 1 to Track.Count
File_Name.WriteLine "<p id=""trackInfo"" style=""padding-left:25px;padding-right:8px;padding-top:0px;"">" & Track(i).Name & "</p>"

File_Name.WriteLine "<p id=""trackInfoHead""> -by- " & Track(i).Artist & "</p>"
File_Name.WriteLine "<p id=""trackInfoHead""> -on- " & Track(i).Album & "</p>"
	if Track.Count <> Track(i).PlayOrderIndex then
		File_Name.WriteLine "<hr/ style=""color:#0099CC;background-color:#0099CC;height:1px;border:none;margin-top:5px;"">"
	end if
Next

File_Name.WriteLine "<input style=""background-color:maroon;color:black;border-top-width:0px;margin-top:20px;"" id=""button"" value=""Clear Bookmarks :("" type=""button"" onclick=""confirmDelete();"" >"

File_Name.WriteLine "</body></html>"
File_Name.Close

set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing
