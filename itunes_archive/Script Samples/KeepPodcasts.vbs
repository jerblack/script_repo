Set iTunesApp = CreateObject("iTunes.Application")

Set objLibrary = iTunesApp.LibraryPlaylist
Set colTracks = objLibrary.Tracks
for each item in colTracks
	if item.podcast then
		if item.PlayedCount = 0 then
			item.PlayedCount = 1
			item.PlayedDate = now
		end if
	end if
next