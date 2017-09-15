' pm_cli.vbs <command>
' playpause, thumbsup, thumbsdown, skipback, nexttrack, playshuffleplaylists
' playstarred, deletelater, canceldeletelater, deleteartist, deletealbum

Dim arg, pm_ip
pm_ip = "192.168.0.50"
arg = Wscript.Arguments.Item(0)

' WScript.Echo arg

Dim o
Set o = CreateObject("MSXML2.XMLHTTP")
o.open "GET", "http://" + pm_ip + "/cmd/spotify/" + arg, False
o.send 