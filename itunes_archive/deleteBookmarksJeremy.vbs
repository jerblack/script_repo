dim iTunes, Track, colSources, objSource, colPlaylists, objPlaylist, i ,fakeIndex

Set iTunes = CreateObject("iTunes.Application")
Set colSources = iTunes.Sources
Set objSource = colSources.ItemByName("Library")
Set colPlaylists = objSource.Playlists
Set objPlaylist = colPlaylists.ItemByName("Jeremy's Bookmarks")


objPlaylist.Delete
iTunes.CreatePlaylist("Jeremy's Bookmarks")



set iTunes = nothing
set colSources = nothing
set objSource = nothing
set colPlaylists = nothing
set objPlaylist = nothing
