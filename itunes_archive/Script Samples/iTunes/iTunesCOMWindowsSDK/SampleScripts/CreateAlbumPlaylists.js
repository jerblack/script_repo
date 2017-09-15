/* 
    File: CreateAlbumPlaylists.js
     
    Version: 1.0 



    Copyright © 2004 Apple Computer, Inc., All Rights Reserved 
*/ 


var	iTunesApp = WScript.CreateObject("iTunes.Application");
var	mainLibrary = iTunesApp.LibraryPlaylist;
var	mainLibrarySource = iTunesApp.LibrarySource;
var	tracks = mainLibrary.Tracks;
var	numTracks = tracks.Count;
var numPlaylistsCreated = 0;
var	i;

// FIXME take a -v parameter eventually
var verbose = false;

// first, make an array indexed by album name
var	albumArray = new Array();

for (i = 1; i <= numTracks; i++)
{
	var	currTrack = tracks.Item(i);
	var	album = currTrack.Album;
	
	if ((album != undefined) && (album != ""))
	{
		if (albumArray[album] == undefined)
		{
			if (verbose)
				WScript.Echo("Adding album " + album);
			albumArray[album] = new Array();
		}
		
		// add the track to the entry for this album
		albumArray[album].push(currTrack);
	}
}

for (var albumNameKey in albumArray)
{
	var albumPlayList;
	var trackArray = albumArray[albumNameKey];

	if (verbose)
		WScript.Echo("Creating playlist " + albumNameKey);
	
	numPlaylistsCreated++;
	
	albumPlaylist = iTunesApp.CreatePlaylist(albumNameKey);
	
	for (var trackIndex in trackArray)
	{
		var		currTrack = trackArray[trackIndex];
		
		if (verbose)
			WScript.Echo("   Adding " + currTrack.Name);
		
		albumPlaylist.AddTrack(currTrack);
	}
}

if (numPlaylistsCreated == 0)
{
	WScript.Echo("No playlists created.");
}
else if (numPlaylistsCreated == 1)
{
	WScript.Echo("Created 1 playlist.");
}
else
{
	WScript.Echo("Created " + numPlaylistsCreated + " playlists.");
}
