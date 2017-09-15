'Option Explicit
Dim iTunes, TrackPath, ArtPath, track,  Artobj, Art, Format, fso
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
Set iTunes  = CreateObject("iTunes.Application")
Set Track = iTunes.CurrentTrack
TrackPath = "c:\xampp\htdocs\"
Set Artobj = track.Artwork
Set Art = Artobj.Item(1)
Format = Art.Format
ArtPath = fso.BuildPath(TrackPath, "art." & ExtArray (Format))
Art.SaveArtworkToFile(ArtPath)

