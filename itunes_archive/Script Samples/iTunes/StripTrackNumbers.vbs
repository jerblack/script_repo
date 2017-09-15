' =================
' StripTrackNumbers
' =================

' Version 1.0.1.2 - October 3rd 2010
' Copyright © Steve MacGuire 2010


' =======
' Licence
' =======

' This program is free software: you can redistribute it and/or modify it under the terms
' of the GNU General Public License as published by the Free Software Foundation, either
' version 3 of the License, or (at your option) any later version.

' This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
' without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
' See the GNU General Public License for more details.

' Please visit http://www.gnu.org/licenses/gpl-3.0-standalone.html to view the GNU GPLv3 licence.


' ===========
' Description
' ===========

' A VBScript for iTunes to strip leading track & disk numbers from filenames.

' Note iTunes has two boolean options create-filenames-with-disknumber & create-filenames-with-tracknumber
' However create-filenames-with-disknumber appears to be ignored with tracks getting both track & disc numbers
' or neither depending on the setting of create-filenames-with-tracknumber
 

' =========
' ChangeLog
' =========

' Version 1.0.0.1 - Initial version
' Version 1.0.1.1 - New filename construction algorithm to prevent issues where track names have leading numeric characters
'		  - Use common base code for the related scripts: AddDisk&TrackNumbers, AddTrackNumbers, StripTrackNumbers
' Version 1.0.0.2 - Test for iTunes version, won't work with iTunes 10.0.0.68 due to bug in that version


' Visit http://samsoft.org.uk/iTunes/scripts.asp for updates


' ==========
' To-do List
' ==========

' Handle potential clash where renaming would create a duplicate filename


' =============================
' Declare constants & variables
' =============================

Option Explicit
Const Min=1		' Minimum number of tracks this script should work with
Const Max=0		' Maximum number of tracks this script should work with, 0 for no limit
'Dim CD			' Handle to CommonDialog object
Dim FSO 		' Handle to FileSystemObject
Dim iTunes		' Handle to iTunes application
'Dim SH			' Handle to Shell application
Dim nl			' New line string for messages
Dim Title		' Message box title
Dim Tracks		' A collection of track objects
Dim Count		' The number of tracks
Dim P,S,U		' Counters
Dim Q			' Global flag
Dim Dbg			' Manage debugging output
Dim Opt			' Script options
Dim DiscNum		' True to include disc numbers, false to remove
Dim TrackNum		' True to include track numbers, false to remove
Dim Custom		' True to use custom character replacements and long file/folder names, false for iTunes standard


' =======================
' Initialise user options
' =======================

' N.B. Edit Opt value to suit your needs.

' Control options, add bit values (x) for selective actions
' Bit 0 = Suppress dialog box for previews, just process tracks					(1)
' Bit 1 = Suppress summary report								(2)
' Bit 2 = Process entire library, otherwise try to restict to current playlist			(4)

Opt=4

' Debug/report options, add bit values (x) for selective actions, initial value may be modified during run
' Bit 0 = Confirm actions									(1)

Dbg=0

' Set disc number, track number and file naming options

DiscNum  =False		' DiscNum=True also sets TrackNum=True, can't have disc numbers unless track numbers present
TrackNum =False		
Custom   =False


' ============
' Main program
' ============

Init			' Set things up
ProcessTracks		' Main process 
Report			' Summary

' ===================
' End of main program
' ===================


' ===============================
' Declare subroutines & functions
' ===============================


' Initialise track selections, quit script if track selection is out of bounds or user aborts
Sub Init
  Dim R,T
  ' Initialise global variables
  P=0
  S=0
  U=0
  Q=False
  nl=vbCr & vbLf
  If DiscNum Then
    Title="Add Disc & Track Numbers"
    TrackNum=True
  ElseIf TrackNum Then
    Title="Add Track Numbers, No Disc Numbers"
  Else
    Title="Strip Track Numbers"
  End If
  ' Initialise global objects
  ' Set CD=CreateObject("UserAccounts.CommonDialog")
  Set FSO=CreateObject("Scripting.FileSystemObject")
  Set iTunes=CreateObject("iTunes.Application")
  ' Set SH=CreateObject("Shell.Application") 

  If iTunes.Version="10.0.0.68" Then
    MsgBox "This script will not work properly owing to a bug in iTunes 10.0.0.68" & nl & _
      "Please upgrade to version 10.0.1.22 or later.",0,Title
    WScript.Quit
  End If


  Set Tracks=iTunes.SelectedTracks
  If Tracks is Nothing Then
    If (Opt AND 4) OR iTunes.BrowserWindow.SelectedPlaylist.Source.Name<>"Library" Then
      Set Tracks=iTunes.LibraryPlaylist.Tracks
    Else
      Set Tracks=iTunes.BrowserWindow.SelectedPlaylist.Tracks
    End If
  End If
  Count=Tracks.Count
  ' Check there is a suitable number of suitable tracks to work with
  IF Count<Min Or (Count>Max And Max>0) Then
    If Max=0 Then
      MsgBox "Please select " & Min & " or more tracks in iTunes before calling this script!",0,Title
      WScript.Quit
    Else 
      MsgBox "Please select between " & Min & " and " & Max & " tracks in iTunes before calling this script!",0,Title
      WScript.Quit
    End If
  End If
  ' Check if the user wants to proceed and how
  If (Opt AND 1)=0 Then
    T="Process " & Count & " track" & Plural(Count,"s","") & "?" & nl & nl
    T=T & "Yes : Process track" & Plural(Count,"s","") & " automatically" & nl
    T=T & "No : Preview & confirm each action" & nl
    T=T & "Cancel : Abort script"
    T=T & nl & nl & "NB: Disable ''Keep iTunes Media folder organised'' preference before use."
    R=MsgBox(T,vbYesNoCancel+vbQuestion,Title)
    If R=vbCancel Then WScript.Quit
    If R=vbYes Then
      Dbg=0
    Else
      Dbg=Dbg OR 1
    End If
  End If
  
End Sub


' Return relevant string depending on whether value is plural or singular
Function Plural(V,P,S)
  If V=1 Then Plural=S ELSE Plural=P
End Function


' Loop through track selection processing suitable items
Sub ProcessTracks
Dim I,T
  For I=Count To 1 Step -1		' Work backwards in case edit remomves item from selection
    P=P+1				
    IF Tracks.Item(I).Kind=1 Then	' Only modify "File" tracks
      SetFilename Tracks.Item(I)
      IF Q Then Exit Sub
    End If
  Next
End Sub


' Renames file adding or removing track & disc numbers according to options
Sub SetFilename(Track)
  Dim E,Ext,F,Folder,L,NewPath,Path,R,T
  With Track
    Path=.Location
    IF Path<>"" Then			' Can't move files we can't find
      E=InStrRev(Path,".")
      Ext=Mid(Path,E)
      L=InStrRev(Path,"\")
      Folder=Left(Path,L)

      NewPath=.Name
      If TrackNum Then
        If .TrackNumber>0 Then
          NewPath=.TrackNumber & " " & NewPath
          If .TrackNumber<10 Then NewPath="0" & NewPath
          If Custom And .TrackNumber<100 And .TrackCount>99 Then NewPath="0" & NewPath
          If DiscNum Then
            If .DiscNumber>1 Or (.DiscNumber=1 And .DiscCount>1) Then NewPath=.DiscNumber & "-" & NewPath
            If Custom And .DiscNumber<10 And .DiscCount>9 Then NewPath="0" & NewPath
          End If
        End If
      End If

      IF Custom Then
        NewPath=Folder & ValidName(NewPath,Ext)
      Else
        NewPath=Folder & ValidiTunes(NewPath,Ext)
      End If

      If NewPath<>Path Then		' Don't update files that don't need changing
        R=True
        If Dbg=1 Then
          T="Rename " & Path & nl & "as " & NewPath
          R=MsgBox(T,vbYesNoCancel+vbQuestion,Title)
          If R=vbCancel Then Q=True : Exit Sub
          If R=vbYes Then
            R=True
          Else
            If R=vbNo Then S=S+1
            R=False
          End If
        End If
        If R Then
          ' Test for clash on rename, either don't do it or add " 2", " 3" etc. as iTunes does
          IF FSO.FileExists(NewPath) Then
            MsgBox "Cannot rename file as there is already a file with the target name."
            S=S+1
          Else
            Set F=FSO.GetFile(Path)
            F.Move NewPath
            .Location=NewPath
            U=U+1
          End If
        End If
      End If
    End If
  End With
End Sub


' Output report

Sub Report
  If (Opt AND 2) Then Exit Sub
  Dim T
  T=P & " track" & Plural(P,"s","")
  If P<Count Then T=T & " of " & count
  T=T & Plural(P," were"," was") & " processed of which " & nl
  T=T & U & Plural(U," were"," was") & " updated"
  IF S>0 Then T=T & " and " & nl & S & Plural(S," were"," was") & " skipped"
  T=T & "."
  MsgBox T,vbInformation,Title
End Sub


' Replace invalid filename characters: \ / : * ? " < > | and also ; with underscores
' Replace leading space or period, strip trailing spaces, trailing periods allowed except for folders
' File names (inclusive of extention) & folder names limited to 40 characters
' A name consisting only of spaces has the leading space changed to an underscore
' Pass name and extention, extention="" for folders

Function ValidiTunes(N,E)
  N=Left(N,40-Len(E))
  N=Replace(N,"\","_")
  N=Replace(N,"/","_")
  N=Replace(N,":","_")
  N=Replace(N,"*","_")
  N=Replace(N,"?","_")
  N=Replace(N,"""","_")
  N=Replace(N,"<","_")
  N=Replace(N,">","_")
  N=Replace(N,"|","_")
  N=Replace(N,";","_")
  IF N=String(Len(N)," ") Then
    N=N="_" & Mid(N,2)
  Else
    Do While Right(N,1)=" "
      N=Left(N,Len(N)-1)
    Loop 
    If Left(N,1)=" " Or Left(N,1)="." Then N="_" & Mid(N,2)
    If E="" And Right(N,1)="." Then N=Left(N,Len(N)-1) & "_"
  End If
  ValidiTunes=N & E
End Function


' Replace invalid filename characters: \ / : * ? " < > | per http://support.microsoft.com/kb/177506
' Strip leading/trailing spaces & leading periods, trailing periods allowed except for folders
' Change the replacement characters on the right for other valid characters if required
' A name consisting only of spaces or periods is changed to a single underscore
' Pass name and extention, extention="" for folders

Function ValidName(N,E)
  N=Replace(N,"\","-")
  N=Replace(N,"/","-")
  N=Replace(N,":",";")
  N=Replace(N,"*","-")
  N=Replace(N,"?","")
  N=Replace(N,"""","''")
  N=Replace(N,"<","{")
  N=Replace(N,">","}")
  N=Replace(N,"|","!")
  Do While (Left(N,1)=" " Or Left(N,1)=".")
    N=Mid(N,2)
    If N=" " Or N="." Then N="_" ' Prevent name from vanishing
  Loop 
  Do While Right(N,1)=" " Or (E="" And Right(N,1)=".")
    N=Left(N,Len(N)-1)
    If N=" " Or N="." Then N="_" ' Prevent name from vanishing
  Loop 
  ValidName=N & E
End Function


' Moves any leading "The " to the end of the string so folder order matches
' iTunes sorting (more or less) while still showing the full title.
Function TheValidName(N,E)
  If Left(N,4)="The " Then N=Mid(N,5) & ", The"
  TheValidName=VaildName(N,E)
End Function


' ==============
' End of listing
' ==============