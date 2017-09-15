/* 	Rename me to FindDeadTracks.js
	Double Click in Explorer to run

Script by Otto - http://ottodestruct.com       */

var ITTrackKindFile	= 1;
var	iTunesApp = WScript.CreateObject("iTunes.Application");
var	deletedTracks = 0;
var	mainLibrary = iTunesApp.LibraryPlaylist;
var	tracks = mainLibrary.Tracks;
var	numTracks = tracks.Count;
var	i;


while (numTracks != 0)
{
	var	currTrack = tracks.Item(numTracks);
	
	// is this a file track?
	if (currTrack.Kind == ITTrackKindFile)
	{
		// yes, does it have an empty location?
		if (currTrack.Rating == "40")
		{
			// write info about the track to a file
			currTrack.Delete();
			deletedTracks++;
		}
		else if (currTrack.Rating == "20")
		{
			// write info about the track to a file
			currTrack.Delete();
			deletedTracks++;
		}
	}
	
	numTracks--;
}