//need to write a new method to identify all duplicate tracks
//	compare attributes, not spuri
//	artist, track, duration
//	in all shuffle playlists
//		shuffle in name
//
//model after existing dedupe()
//	other dedupes by spuri

function findDupes() {
    var potentialDupes = [];
    var count = 0;

    spls.forEach(function(p){
        for(var i = 0; i < p.tracks.length; i++) {
            count ++;
        };
    })
    console.log(count);
}