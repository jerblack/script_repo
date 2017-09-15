'VBScript Example
Set WshShell = WScript.CreateObject("WScript.Shell")

strComputer = "."
Set objWMIService = GetObject("winmgmts:" _
    & "{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")

Set colProcessList = objWMIService.ExecQuery _
    ("Select * from Win32_Process Where Name = 'iTunes.exe'")

For Each objProcess in colProcessList
    foobar = split (objProcess.Name, ".")
    WshShell.AppActivate ( foobar(0) )
    WshShell.SendKeys "%(fx)"
Next