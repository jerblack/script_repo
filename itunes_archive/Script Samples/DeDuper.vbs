' =======
' DeDuper
' =======
' Version 1.0.1.5 - March 15th 2012
' Copyright © Steve MacGuire 2011-2012
' http://samsoft.org.uk/iTunes/DeDuper.vbs
' Please visit http://samsoft.org.uk/iTunes/scripts.asp for updates

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
' Aims to dedupe tracks where more than one logical entry exists for the same physical file
' or more than one physical file has the same metadata

' Written partly in response to this thread in Apple Support Communities
' https://discussions.apple.com/message/16038843#16038843
' Thanks to tcminyard for pointing out a potential problem with "/" vs. "\" in file paths.

' =========
' ChangeLog 
' =========
' Version 1.0.0.1 - Initial version
' Version 1.0.0.2 - Fixed race condition
' Version 1.0.0.3 - Extend to deal with files that have duplicate metadata & the same file size
'                 - Deleted files go to the recycle bin
' Version 1.0.0.4 - Fixed issue arising when there were more than two physical copies of any given file
' Version 1.0.0.5 - Improved distinction between logical and physical duplicates
'                 - Removes any folders emptied as a result of removing duplicates
' Version 1.0.0.6 - Update detection routines to cope with Mac/Linux style file paths that have been imported to the database
'		              - Rewrite recyle routine for clarity
' Version 1.0.1.1 - Updated to common code base with progress bar
' Version 1.0.1.2 - Updated recycle routine for Vista/Windows 7 compatability
' Version 1.0.1.3 - Added feature to ensure playlist membership is preserved
' Version 1.0.1.4 - Extended to allow optional removal of alternate dupes, keeping largest file
' Version 1.0.1.5 - Fixed potential bug when running under UAC


' ==========
' To-do List
' ==========
' Add things to do

' =============================
' Declare constants & variables
' =============================
Option Explicit	        ' Declare all variables before use
Const Kimo=False        ' True if script expects "Keep iTunes Media folder organised" to be disabled
Const Min=2             ' Minimum number of tracks this script should work with
Const Max=0             ' Maximum number of tracks this script should work with, 0 for no limit
Const Warn=500          ' Warning level, require confirmation for procssing above this level
Dim Intro,Outro,Check   ' Manage confirmation dialogs
Dim PB,Prog,Debug       ' Control the progress bar
Dim Clock,T1,T2,Timing  ' The secret of great comedy
Dim Playlist,List       ' Name for any generated playlist, and the object itself
Dim Named,Source        ' Control use on named playlist
Dim iTunes              ' Handle to iTunes application
Dim Tracks              ' A collection of track objects
Dim Count               ' The number of tracks
Dim M,P,S,U,V           ' Counters
Dim nl,tab              ' New line/tab strings
Dim Quit                ' Used to abort script

Dim Title,Summary
Title="DeDuper"
Summary="Scan selected tracks/current playlist for duplicates and optionally remove them." & vbCrLf & vbCrLf _
  & "Plays & skips will be merged, most recent played/skipped dates will be used, and the track" & vbCrLf _
  & "that is preserved will be added to any playlists that the removed tracks were in." & vbCrLf & vbCrLf _
  & "It should help to reduce the overal execution time if you use the iTunes feature to " & vbCrLf _
  & "''Show Exact Duplicates'' and select the displayed tracks before running the script."
  
Dim Paths               ' A dictionary object for comparing paths
Dim DeathRow            ' A dictionary object for tracks to remove
Dim D                   ' Index into death row
Dim FSO                 ' Handle to FileSystemObject
Dim Reg                 ' Handle to Registry object
Dim SH                  ' Handle to Shell application
Dim C1,C2,C3            ' More counters
Dim CheckTypes          ' Check types to delete

' =======================
' Initialise user options
' =======================
Intro=True              ' Set false to skip initial prompts, avoid if non-reversible actions
Outro=True              ' Produce summary report
Check=True              ' Track-by-track confirmation
Prog=True               ' Display progress bar
Debug=False             ' Include any debug messages in progress bar
Timing=True             ' Display running time in summary report
Named=False             ' Force script to process specific playlist rather than current selection or playlist
Source=""               ' Named playlist to process, use "Library" for entire library
CheckTypes=True         ' Confirm which types of dupes are to be removed.


' ============
' Main program
' ============

GetTracks               ' Set things up
DedupeTracks            ' Main process 
Results                 ' Summary

' ===================
' End of main program
' ===================


' ===============================
' Declare subroutines & functions
' ===============================


' Note: The bulk of the code in this script is concerned with making sure that only suitable tracks are processed by
'       the following module and supporting numerous options for track selection, confirmation, progress and results.


' Loop through track selection processing suitable items
' Modified 2012-03-10
Sub DedupeTracks
  Dim A,C,D,F,I,N,O,Q,R,T
  Set FSO=CreateObject("Scripting.FileSystemObject")
  Set SH=CreateObject("Shell.Application")
  Set Reg=GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\default:StdRegProv") 	' Use . for local computer, otherwise could be computer name or IP address
  Set Paths=CreateObject("Scripting.Dictionary")
  Set DeathRow=CreateObject("Scripting.Dictionary")

  If Prog Then                  ' Create ProgessBar
    Set PB=New ProgBar
    PB.Title=Title
    PB.Show
  End If
  Clock=0
  StartTimer
  
  ' Pass 1, identify logical dupes, keep earliest added

  C=0 : N=0
  If Prog Then PB.SetInfo "Scanning for logical duplicates"
  For I=Count To 1 Step -1	    ' Work backwards in case edit removes item from selection
    If Prog Then
      N=N+1    
      PB.SetStatus "Processing " & N & " of " & Count
      PB.Progress N-1,Count
    End If
    Set T=Tracks.Item(I)
    If T.Kind=1 Then		        ' Only process "File" tracks
      If T.Location="" Then     ' Ignore missing tracks
        M=M+1
      Else 
        A=LCase(Replace(T.Location,"/","\"))
        ' If A<>T.Location Then T.Location=A    ' Fix invalid path names
        If Paths.Exists(A) Then
	        ' MsgBox "Match found with item " & Paths.Item(A) & " which should be merged with item " & I
          Merge A,1,I,Paths.Item(A)
          C=C+1
        Else
          ' MsgBox "Adding track " & I & " = " & A
          Paths.Add A,I
        End If
      End If
      If Quit Then StopTimer : Exit Sub	' Abort loop on user request
    End If
    P=P+1                       ' Increment processed tracks
  Next
  C1=C                          ' Logical duplicates identified
  
  ' Pass 2, identify physical dupes, same sizes, keep earliest added
  
  Paths.RemoveAll               ' Reset list of items to match
  C=0 : N=0
  If Prog Then PB.SetInfo "Scanning for physical duplicates"
  For I=Count To 1 Step -1      ' Work backwards in case edit removes item from selection
    If Prog Then
      N=N+1    
      PB.SetStatus "Processing " & N & " of " & Count
      PB.Progress N-1,Count
    End If
    Set T=Tracks.Item(I)
    D=iTunes.ITObjectPersistentIDHigh(T) & iTunes.ITObjectPersistentIDLow(T)
    If Not DeathRow.Exists(D) Then	  ' Ignore logical dupes found in previous pass
      With T
        If .Kind=1 Then         ' Only process "File" tracks
          If Not .Location="" Then
  	        A=LCase(.Artist & "\" & .Album & "\" & .DiscNumber & "." & .TrackNumber & " " & .Name & "=" & .Size)
            If Paths.Exists(A) Then
              ' MsgBox "Match found with item " & Paths.Item(A) & " which should be merged with item " & I
              Merge A,2,I,Paths.Item(A)
              C=C+1
            Else
              ' MsgBox "Adding track " & I & " = " & A
              Paths.Add A,I
            End If
          End If   
        End If
      End With     
    End If
    If Quit Then StopTimer : Exit Sub ' Abort loop on user request
  Next
  C2=C                          ' Physical duplicates identified
  
    ' Pass 3, identify alternate dupes, same track but different sizes, keep largest
  
  Paths.RemoveAll               ' Reset list of items to match
  C=0 : N=0
  If Prog Then PB.SetInfo "Scanning for duplicates of different sizes"
  For I=Count To 1 Step -1      ' Work backwards in case edit removes item from selection
    If Prog Then
      N=N+1    
      PB.SetStatus "Processing " & N & " of " & Count
      PB.Progress N-1,Count
    End If
    Set T=Tracks.Item(I)
    D=iTunes.ITObjectPersistentIDHigh(T) & iTunes.ITObjectPersistentIDLow(T)
    If Not DeathRow.Exists(D) Then	  ' Ignore logical/physical dupes found in previous passes
      With T
        If .Kind=1 Then         ' Only process "File" tracks
          If Not .Location="" Then
  	        A=LCase(.Artist & "\" & .Album & "\" & .DiscNumber & "." & .TrackNumber & " " & .Name)
            If Paths.Exists(A) Then
              ' MsgBox "Match found with item " & Paths.Item(A) & " which should be merged with item " & I
              Merge A,3,I,Paths.Item(A)
              C=C+1
            Else
              ' MsgBox "Adding track " & I & " = " & A
              Paths.Add A,I
            End If
          End If   
        End If
      End With     
    End If
    If Quit Then Exit Sub       ' Abort loop on user request
  Next
  C3=C                          ' Alternate duplicates identified

  If Check Then
    If Prog Then 
      PB.Close                  ' Hide progress bar during track-by-track confirmation
      Prog=False
    End If
  End If
  
  C=C1+C2+C3
  F=True  

  If C>0 And (Check Or CheckTypes) Then
    If C=1 Then
      O=3
      If C1=1 Then Q="logical"
      If C2=1 Then Q="physical"
      If C3=1 Then Q="alternate"
      Q="One " & Q & " duplicate was found." & nl & nl & "Would you like to delete it?"
      StopTimer           ' Don't time user inputs
      R=MsgBox(Q,vbOKCancel,Title)
      StartTimer          ' Don't time user inputs
      If R=vbOK Then O=3 Else F=False
    Else
      Q="There were " & C & " duplicates found:" & nl
      If C1>0 Then Q=Q & nl & C1 & " logical (multiple entries for same file)"
      If C2>0 Then Q=Q & nl & C2 & " physical (multiple copies of same file)"
      If C3>0 Then Q=Q & nl & C3 & " alternate (multiple formats/bitrates of same track)"
      Q=Q & "." & nl & nl 
      If Check Then
        Q=Q & "Would you like to delete them with track by track-by-track confirmation?"
      Else
        Q=Q & "Would you like to delete them?"
      End If
      Q=Q & nl & nl 
      Q=Q & "Yes" & tab & ": Delete all duplicate tracks"
      If Not Check Then Q=Q & " automatically"
      Q=Q & nl & "No" & tab & ": Just delete logical & physical dupes (safer)" & nl
      Q=Q & "Cancel" & tab & ": Abort script"
      StopTimer           ' Don't time user inputs
      R=MsgBox(Q,vbYesNoCancel,Title)
      StartTimer          ' Don't time user inputs
      If R=vbYes Then
        O=3
      ElseIf R=vbNo Then
        O=2
      Else 
        F=False
      End If
    End If  
  End If  
  
  ' Pass 4, delete all dupes

  If F=True And C>0 Then        ' Delete any dupes if found, unless cancelling
    N=0
    If Prog Then PB.SetInfo "Removing duplicates"
    For I=Count To 1 Step -1    ' Work backwords in case edit removes item from selection
      If Prog Then
        N=N+1    
        PB.SetStatus "Processing " & N & " of " & Count
        PB.Progress N-1,Count
      End If
      Set T=Tracks.Item(I)
      If T.Kind=1 Then		      ' Only process "File" tracks
        D=iTunes.ITObjectPersistentIDHigh(T) & iTunes.ITObjectPersistentIDLow(T)
        If DeathRow.Exists(D) Then
          F=True
          If Check And (DeathRow.Item(D)<=O) Then
            Select Case DeathRow.Item(D)
            Case 1
              Q="Delete logical duplicate connected to file: " & nl & Tracks.Item(I).Location & "?"
            Case 2
              Q="Delete physical duplicate file: " & nl & Tracks.Item(I).Location & "?"
            Case 3
              Q="Delete alternate duplicate file: " & nl & Tracks.Item(I).Location & "?"
            End Select            
            StopTimer           ' Don't time user inputs
            R=MsgBox(Q,vbYesNoCancel+vbQuestion,Title)
            If R=vbCancel Then Quit=True : Exit Sub
            StartTimer          ' Don't time user inputs
            If R=vbNo Then
              S=S+1             ' Increment skipped count
              F=False
            End If            
          ElseIf DeathRow.Item(D)=3 And O=2 Then
            F=False
            S=S+1
          End If
          If F Then
            ' Comment out next two lines to test script without removing tracks
            If DeathRow.Item(D)>1	Then Recycle Replace(Tracks(I).Location,"/","\")
            DeleteTrack I
            DeathRow.Remove D   ' Superfluous?
            U=U+1               ' Increment update count
          End If
        End If
        If Quit Then Exit Sub	  ' Abort loop on user request
      End If
    Next
  End If

  StopTimer
  If Prog Then
    PB.SetStatus "Finished!"
    PB.Progress Count,Count
    WScript.Sleep 1000
    PB.Close
  End If
  
End Sub


' Delete a track from iTunes, leave the file
' Modified 2011-09-27
Sub DeleteTrack(I)
  Dim H,L,T
  H=iTunes.ITObjectPersistentIDHigh(Tracks(I))
  L=iTunes.ITObjectPersistentIDLow(Tracks(I))
  Set T=iTunes.LibraryPlaylist.Tracks.ItemByPersistentID(H,L)
  T.Delete
End Sub


' Merge metadata for two tracks, preserve the oldest one and prepare to delete the newest
' Modified 2012-03-06
Sub Merge(A,W,X,Y)
  Dim I,J,K,L,Playlists
  Set Playlists=CreateObject("Scripting.Dictionary")
  If W=3 Then
    ' Keep largest file
    If Tracks(X).Size>Tracks(Y).Size Then
      I=X
      J=Y
    Else
      I=Y
      J=X
    End If
  Else
    ' Keep oldest file
    If Tracks(X).DateAdded<=Tracks(Y).DateAdded Then
      I=X
      J=Y
    Else
      I=Y
      J=X
    End If
  End If
  ' Find all playlists track I is a member of
  For L=1 To Tracks(I).Playlists.Count
    If Tracks(I).Playlists.Item(L).Kind=2 And Tracks(I).Playlists.Item(L).Smart=False Then
      K=iTunes.ITObjectPersistentIDHigh(Tracks(I).Playlists.Item(L)) & "-" & iTunes.ITObjectPersistentIDLow(Tracks(I).Playlists.Item(L))
      Playlists.Add K,1
    End If
  Next
  ' Add track I to any playlists that J is in
  For L=1 To Tracks(J).Playlists.Count
    If Tracks(J).Playlists.Item(L).Kind=2 And Tracks(J).Playlists.Item(L).Smart=False Then
      K=iTunes.ITObjectPersistentIDHigh(Tracks(J).Playlists.Item(L)) & "-" & iTunes.ITObjectPersistentIDLow(Tracks(J).Playlists.Item(L))
      If Playlists.Exists(K)=False Then Tracks(J).Playlists.Item(L).AddTrack(Tracks(I))
    End If
  Next
  ' Consolidate played & skipped info
  If Tracks(J).PlayedCount>0 Then
    If Tracks(J).PlayedDate>Tracks(I).PlayedDate Then Tracks(I).PlayedDate=Tracks(J).PlayedDate
    Tracks(I).PlayedCount=Tracks(I).PlayedCount+Tracks(J).PlayedCount
    Tracks(J).PlayedCount=0     ' In case we don't end up deleting this item
  End If
  If Tracks(J).SkippedCount>0 Then
    If Tracks(J).SkippedDate>Tracks(I).SkippedDate Then Tracks(I).SkippedDate=Tracks(J).SkippedDate
    Tracks(I).SkippedCount=Tracks(I).SkippedCount+Tracks(J).SkippedCount
    Tracks(J).SkippedCount=0    ' In case we don't end up deleting this item
  End If
  ' Take the highest rating
  If Tracks(J).RatingKind=0 And Tracks(J).Rating>Tracks(I).Rating Then Tracks(I).Rating=Tracks(J).Rating
  Paths.Item(A)=I               ' Make sure key now matches item we are keeping
  DeathRow.Add iTunes.ITObjectPersistentIDHigh(Tracks(J)) & iTunes.ITObjectPersistentIDLow(Tracks(J)),W       ' Discard the other item
End Sub


' Recycled from http://gallery.technet.microsoft.com/scriptcenter/191eb207-3a7e-4dbc-884d-5f4498440574
' Modified to recursively remove any emptied folders. Rewritten to simplify and use global objects/declarations
' Needs FSO,Reg,SH objects

' Send file or folder to recycle bin, return status
' Modified 2011-12-01
Function Recycle(FilePath)
  Const HKEY_CURRENT_USER=&H80000001 
  Const KeyPath="Software\Microsoft\Windows\CurrentVersion\Explorer" 
  Const KeyName="ShellState" 
  Dim File,FileName,Folder,FolderName,I,Parent,State,Value
  Recycle=False
  If Not(FSO.FileExists(FilePath) Or FSO.FolderExists(FilePath)) Then Exit Function     ' Can't delete something that isn't there
  ' Make sure recycle bin properties are set to NOT display request for delete confirmation 
  Reg.GetBinaryValue HKEY_CURRENT_USER,KeyPath,KeyName,Value			' Get current shell state 
  State=Value(4)	 							' Preserve current option
  Value(4)=39									  ' Set new option 
  Reg.SetBinaryValue HKEY_CURRENT_USER,KeyPath,KeyName,Value			' Update shell state
 
  ' Use the Shell to send the file to the recycle bin 
  FileName=FSO.GetFileName(FilePath)
  FolderName=FSO.GetParentFolderName(FilePath)
  Set Folder=SH.NameSpace(FolderName)
  Set File=Folder.ParseName(FileName)

  'File.InvokeVerb("&Delete")		' Delete file, sending to recycle bin - fails for Vista/Windows 7
  I=File.Verbs.Count            ' Use DoIt instead of InvokeVerb - http://forums.wincustomize.com/322016
  Do
    I=I-1
    If File.Verbs.Item(I)="&Delete" Then File.Verbs.Item(I).DoIt() : Exit Do
  Loop Until I=0

  If FSO.FileExists(FilePath) Then
    MsgBox "There was a problem deleting the file:" & nl & FilePath,vbCritical,Title
  Else
    Recycle=True
    ' Delete folder using FileSystem if now empty, repeat for parent folders
    Set Folder=FSO.GetFolder(FolderName)
    While Folder.Files.Count=0 And Folder.SubFolders.Count=0
      Set Parent=Folder.ParentFolder
      Folder.Delete
      Set Folder=Parent
    Wend
  End If

  ' Restore the user's property settings for the Recycle Bin 
  Value(4)=State								' Restore option
  Reg.SetBinaryValue HKEY_CURRENT_USER,KeyPath,KeyName,Value			' Update shell state 

End Function


' Output report
' Modified 2012-03-10
Sub Results
  Dim C
  C=C1+C2+C3
  If Not Outro Then Exit Sub
  Dim T
  If Quit Then T="Script aborted!" & nl & nl Else T=""
  If C=0 Then T=T & "No" Else T=T & C 
  T=T & " duplicate" & Plural(C,"s were"," was") & " found from" & nl
  T=T & P & " processed track" & Plural(P,"s.",".")
  If C>0 Then T=T & nl & nl & "There " & Plural(C,"were:","was:")
  If C1>0 Then
    T=T & nl 
    T=T & C1 & " logical duplicate" & Plural(C1,"s","")
    If (C2>0 And C3=0) Or (C2=0 And C3>0) Then T=T & " and"
  End If
  If C2>0 Then
    T=T & nl
    T=T & C2 & " physical duplicate" & Plural(C2,"s","")
    If C3>0 Then T=T & " and"
  End If
  If C3>0 Then
    T=T & nl
    T=T & C3 & " alternate duplicate" & Plural(C3,"s","")
  End If
  If C>0 Then
    T=T & "." & nl & nl
    If U=0 Then T=T & "No" Else T=T & U
    T=T & " duplicate" & Plural(U,"s were"," was") & " removed"
    If M>0 And S=0 Then T=T & " and"
  End If
  If S>0 Then
    If M=0 And U>0 Then T=T & " and" & nl Else T=T & nl
    T=T & S & Plural(S," were"," was") & " skipped"
    If M>0 Then T=T & " and"
  End If
  If M>0 Then T=T & nl & M & Plural(M," tracks were"," track was") & " missing"
  T=T & "."
  If Timing Then 
    T=T & nl & nl
    T=T & "Processing time: " & FormatTime(Clock)
  End If
  MsgBox T,vbInformation,Title
End Sub


' ============================================
' Reusable Library Routines for iTunes Scripts
' ============================================
' Modified 2011-11-13


' Format time interval from x.xxx seconds to hh:mm:ss
' Modified 2011-11-07
Function FormatTime(T)
  If T<0 Then T=T+86400         ' Watch for timer running over midnight
  If T<2 Then
    FormatTime=FormatNumber(T,3) & " seconds"
  ElseIf T<10 Then
    FormatTime=FormatNumber(T,2) & " seconds"
  ElseIf T<60 Then
    FormatTime=Int(T) & " seconds"
  Else
    Dim H,M,S
    S=T Mod 60
    M=(T\60) Mod 60             ' \ = Div operator for integer division
    'S=Right("0" & (T Mod 60),2)
    'M=Right("0" & ((T\60) Mod 60),2)  ' \ = Div operator for integer division
    H=T\3600
    If H>0 Then
      FormatTime=H & Plural(H," hours "," hour ") & M & Plural(M," mins"," min")
      'FormatTime=H & ":" & M & ":" & S
    Else
      FormatTime=M & Plural(M," mins "," min ") & S & Plural(S," secs"," sec")
      'FormatTime=M & " :" & S
      'If Left(FormatTime,1)="0" Then FormatTime=Mid(FormatTime,2)
    End If
  End If
End Function


' Initialise track selections, quit script if track selection is out of bounds or user aborts
' Modified 2011-11-13
Sub GetTracks
  Dim Q,R
  ' Initialise global variables
  nl=vbCrLf : tab=Chr(9) : Quit=False
  M=0 : P=0 : S=0 : U=0 : V=0
  ' Initialise global objects
  Set iTunes=CreateObject("iTunes.Application")
  Set Tracks=iTunes.SelectedTracks      ' Get current selection
  If iTunes.BrowserWindow.SelectedPlaylist.Source.Kind<>1 And Source="" Then Source="Library" : Named=True      ' Ensure section is from the library source
  'If iTunes.BrowserWindow.SelectedPlaylist.Name="Ringtones" And Source="" Then Source="Library" : Named=True    ' and not ringtones (which cannot be processed as tracks???)
  If iTunes.BrowserWindow.SelectedPlaylist.Name="Radio" And Source="" Then Source="Library" : Named=True        ' or radio stations (which cannot be processed as tracks)
  If iTunes.BrowserWindow.SelectedPlaylist.Name=Playlist And Source="" Then Source="Library" : Named=True       ' or a playlist that will be regenerated by this script
  If Named Or Tracks Is Nothing Then    ' or use a named playlist
    If Source<>"" Then Named=True
    If Source="Library" Then            ' Get library playlist...
      Set Tracks=iTunes.LibraryPlaylist.Tracks
    Else                                ' or named playlist
      On Error Resume Next              ' Attempt to fall back to current selection for non-existent source
      Set Tracks=iTunes.LibrarySource.Playlists.ItemByName(Source).Tracks
      On Error Goto 0
      If Tracks is Nothing Then         ' Fall back
        Named=False
        Source=iTunes.BrowserWindow.SelectedPlaylist.Name
        Set Tracks=iTunes.SelectedTracks
        If Tracks is Nothing Then
          Set Tracks=iTunes.BrowserWindow.SelectedPlaylist.Tracks
        End If
      End If
    End If
  End If  
  If Named And Tracks.Count=0 Then      ' Quit if no tracks in named source
    If Intro Then MsgBox "The playlist " & Source & " is empty, there is nothing to do.",vbExclamation,Title
    WScript.Quit
  End If
  If Tracks.Count=0 Then Set Tracks=iTunes.LibraryPlaylist.Tracks
  If Tracks.Count=0 Then                ' Can't select ringtones as tracks?
    MsgBox "This script cannot process " & iTunes.BrowserWindow.SelectedPlaylist.Name & ".",vbExclamation,Title
    WScript.Quit
  End If
  ' Check there is a suitable number of suitable tracks to work with
  Count=Tracks.Count
  If Count<Min Or (Count>Max And Max>0) Then
    If Max=0 Then
      MsgBox "Please select " & Min & " or more tracks in iTunes before calling this script!",0,Title
      WScript.Quit
    Else
      MsgBox "Please select between " & Min & " and " & Max & " tracks in iTunes before calling this script!",0,Title
      WScript.Quit
    End If
  End If
  ' Check if the user wants to proceed and how
  Q=Summary
  If Q<>"" Then Q=Q & nl & nl
  If Warn>0 And Count>Warn Then
    Intro=True
    Q=Q & "WARNING!" & nl & "Are you sure you want to process " & Count & " tracks"
    If Named Then Q=Q & nl
  Else
    Q=Q & "Process " & Count & " track" & Plural(Count,"s "," ")
  End If
  If Named Then Q=Q & "from the " & Source & " playlist"
  Q=Q & "?"
  If Intro Or (Prog And UAC) Then
    If Check Then
      Q=Q & nl & nl 
      Q=Q & "Yes" & tab & ": Process track" & Plural(Count,"s","") & " automatically" & nl
      Q=Q & "No" & tab & ": Preview & confirm each action" & nl
      Q=Q & "Cancel" & tab & ": Abort script"
    End If
    If Kimo Then Q=Q & nl & nl & "NB: Disable ''Keep iTunes Media folder organised'' preference before use."
    If Prog And UAC Then
      Q=Q & nl & nl & "NB: Disable User Access Control to allow progess bar to operate" & nl
      Q=Q & "or change the declaration ''Prog=True'' to ''Prog=False''."
      Prog=False
    End If
    If Check Then
      R=MsgBox(Q,vbYesNoCancel+vbQuestion,Title)
    Else
      R=MsgBox(Q,vbOKCancel+vbQuestion,Title)
    End If
    If R=vbCancel Then WScript.Quit
    If R=vbYes or R=vbOK Then
      Check=False
    Else
      Check=True
    End If
  End If 
  If Check Then Prog=False      ' Suppress progress bar if prompting for user input
End Sub


' Return relevant string depending on whether value is plural or singular
' Modified 2011-10-04
Function Plural(V,P,S)
  If V=1 Then Plural=S Else Plural=P
End Function


' Loop through track selection processing suitable items
' Modified 2011-11-06
Sub ProcessTracks
  Dim C,I,N,Q,R,T
  N=0
  If Prog Then                  ' Create ProgessBar
    Set PB=New ProgBar
    PB.SetTitle Title
    PB.Show
  End If
  Clock=0 : StartTimer
  For I=Count To 1 Step -1      ' Work backwards in case edit removes item from selection
    N=N+1                 
    If Prog Then
      PB.SetStatus Status(N)
      PB.Progress N-1,Count
    End If
    Set T=Tracks.Item(I)
    If Prog Then PB.SetInfo Info(T)
    If T.Kind=1 Then            ' Ignore tracks which can't change
      If Updateable(T) Then     ' Ignore tracks which won't change
        If Check Then           ' Track by track confirmation
          Q=Prompt(T)
          StopTimer             ' Don't time user inputs 
          R=MsgBox(Q,vbYesNoCancel+vbQuestion,Title)
          StartTimer
          Select Case R
          Case vbYes
            C=True
          Case vbNo
            C=False
            S=S+1               ' Increment skipped tracks
          Case Else
            Quit=True
            Exit For
          End Select          
        Else
          C=True
        End If
        If C Then               ' We have a valid track, now do something with it
          Action T
        End If
      Else
        If T.Location<>"" Then V=V+1    ' Increment unchanging tracks, exclude missing ones
      End If
    End If 
    P=P+1                       ' Increment processed tracks
    If Quit Then Exit For       ' Abort loop on user request
  Next
  StopTimer
  If Prog And Not Quit Then
    PB.Progress Count,Count
    WScript.Sleep 500
    PB.Close
  End If
End Sub


' Output report
' Modified 2011-10-24
Sub Report
  If Not Outro Then Exit Sub
  Dim T
  If Quit Then T="Script aborted!" & nl & nl Else T=""
  T=T & P & " track" & Plural(P,"s","")
  If P<Count Then T=T & " of " & count
  T=T & Plural(P," were"," was") & " processed of which " & nl
  If V>0 Then
    T=T & V & " did not need updating"
    If (U>0)+(S>0)+(M>0)<-1 Then
      T=T & "," & nl
    ElseIf (U>0)+(S>0)+(M>0)=-1 Then
      T=T & " and" & nl
    End If
  End If
  If U>0 Or V=0 Then
    T=T & U & Plural(U," were"," was") & " updated"
    If (S>0)+(M>0)<-1 Then
      T=T & "," & nl
    ElseIf (S>0)+(M>0)=-1 Then
      T=T & " and" & nl
    End If
  End If
  If S>0 Then
    T=T & S & Plural(S," were"," was") & " skipped"
    If M>0 Then T=T & " and" & nl
  End If
  If M>0 Then T=T & M & Plural(M," were"," was") & " missing"
  T=T & "."
  If Timing Then 
    T=T & nl & nl
    If Check Then T=T & "Processing" Else T=T & "Running"
    T=T & " time: " & FormatTime(Clock)
  End If
  MsgBox T,vbInformation,Title
End Sub


' Start timing event
' Modified 2011-10-08
Sub StartEvent
  T2=Timer
End Sub


' Start timing session
' Modified 2011-10-08
Sub StartTimer
  T1=Timer
End Sub


' Stop timing event and display elapsed time in debug section of Progress Bar
' Modified 2011-11-07
Sub StopEvent
  If Prog Then
    T2=Timer-T2
    If T2<0 Then T2=T2+86400    ' Watch for timer running over midnight
    If Debug Then PB.SetDebug "<br>Last iTunes call took " & FormatTime(T2) 
  End If  
End Sub


' Stop timing session and add elapased time to running clock
' Modified 2011-10-08
Sub StopTimer
  Clock=Clock+Timer-T1
  If Clock<0 Then Clock=Clock+86400     ' Watch for timer running over midnight
End Sub


' Detect if User Access Control is enabled, UAC prevents use of progress bar
' Modified 2011-10-18
Function UAC
  Const HKEY_LOCAL_MACHINE=&H80000002
  Const KeyPath="Software\Microsoft\Windows\CurrentVersion\Policies\System"
  Const KeyName="EnableLUA"
  Dim Reg,Value
  Set Reg=GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\default:StdRegProv") 	  ' Use . for local computer, otherwise could be computer name or IP address
  Reg.GetDWORDValue HKEY_LOCAL_MACHINE,KeyPath,KeyName,Value	  ' Get current property
  If IsNull(Value) Then UAC=False Else UAC=(Value<>0)
End Function


' ==================
' Progress Bar Class
' ==================

' Progress/activity bar for vbScript implemented via IE automation
' Can optionally rebuild itself if closed or abort the calling script
' Modified 2011-10-18
Class ProgBar
  Public Cells,Height,Width,Respawn,Title,Version
  Private Active,Blank,Dbg,Filled(),FSO,IE,Info,NextOn,NextOff,Status,SHeight,SWidth,Temp

' User has closed progress bar, abort or respwan?
' Modified 2011-10-09
  Public Sub Cancel()
    If Respawn And Active Then
      Active=False
      If Respawn=1 Then
        Show                    ' Ignore user's attempt to close and respawn
      Else
        Dim R
        StopTimer               ' Don't time user inputs 
        R=MsgBox("Abort Script?",vbExclamation+vbYesNoCancel,Title)
        StartTimer
        If R=vbYes Then
          On Error Resume Next
          CleanUp
          Respawn=False
          Quit=True             ' Global flag allows main program to complete current task before exiting
        Else
          Show                  ' Recreate box if closed
        End If  
      End If        
    End If
  End Sub

' Delete temporary html file  
' Modified 2011-10-04
  Private Sub CleanUp()
    FSO.DeleteFile Temp         ' Delete temporary file
  End Sub
  
' Close progress bar and tidy up
' Modified 2011-10-04
  Public Sub Close()
    On Error Resume Next        ' Ignore errors caused by closed object
    If Active Then
      Active=False              ' Ignores second call as IE object is destroyed
      IE.Quit                   ' Remove the progess bar
      CleanUp
    End If    
 End Sub
 
' Initialize object properties
' Modified 2011-10-16
  Private Sub Class_Initialize()
    Dim I,Items,strComputer,WMI
    ' Get width & height of screen for centering ProgressBar
    strComputer="."
    Set WMI=GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
    Set Items=WMI.ExecQuery("Select * from Win32_OperatingSystem",,48)
    'Get the OS version number (first two)
    For Each I in Items
      Version=Left(I.Version,3)
    Next
    Set Items=WMI.ExecQuery ("Select * From Win32_DisplayConfiguration")
    For Each I in Items
      SHeight=I.PelsHeight
      SWidth=I.PelsWidth
    Next
    If Debug Then
      Height=140                ' Height of containing div
    Else
      Height=100                ' Reduce height if no debug area
    End If
    Width=300                   ' Width of containing div
    Respawn=True                ' ProgressBar will attempt to resurect if closed
    Blank=String(50,160)        ' Blanks out "Internet Explorer" from title
    Cells=25                    ' No. of units in ProgressBar, resize window if using more cells
    ReDim Filled(Cells)         ' Array holds current state of each cell
    For I=0 To Cells-1
      Filled(I)=False
    Next
    NextOn=0                    ' Next cell to be filled if busy cycling
    NextOff=Cells-5             ' Next cell to be cleared if busy cycling
    Dbg="&nbsp;"                ' Initital value for debug text
    Info="&nbsp;"               ' Initital value for info text
    Status="&nbsp;"             ' Initital value for status text
    Title="Progress Bar"        ' Initital value for title text
    Set FSO=CreateObject("Scripting.FileSystemObject")          ' File System Object
    Temp=FSO.GetSpecialFolder(2) & "\ProgBar.htm"               ' Path to Temp file
  End Sub

' Tidy up if progress bar object is destroyed
' Modified 2011-10-04
  Private Sub Class_Terminate()
    Close
  End Sub
 
' Display the bar filled in proportion X of Y
' Modified 2011-10-18
  Public Sub Progress(X,Y)
    Dim F,I,L,S,Z
    If X<0 Or X>Y Or Y<=0 Then
      MsgBox "Invalid call to ProgessBar.Progress, variables out of range!",vbExclamation,Title
      Exit Sub
    End If
    Z=Int(X/Y*(Cells))
    If Z=NextOn Then Exit Sub
    If Z=NextOn+1 Then
      Step False
    Else
      If Z>NextOn Then
        F=0 : L=Cells-1 : S=1
      Else
        F=Cells-1 : L=0 : S=-1
      End If
      For I=F To L Step S
        If I>=Z Then
          SetCell I,False
        Else
          SetCell I,True
        End If
      Next
      NextOn=Z
    End If
  End Sub

' Clear progress bar ready for reuse  
' Modified 2011-10-16
  Public Sub Reset
    Dim C
    For C=Cells-1 To 0 Step -1
      IE.Document.All.Item("P",C).classname="empty"
      Filled(C)=False
    Next
    NextOn=0
    NextOff=Cells-5   
  End Sub
  
' Directly set or clear a cell
' Modified 2011-10-16
  Public Sub SetCell(C,F)
    On Error Resume Next        ' Ignore errors caused by closed object
    If F And Not Filled(C) Then
      Filled(C)=True
      IE.Document.All.Item("P",C).classname="filled"
    ElseIf Not F And Filled(C) Then
      Filled(C)=False
      IE.Document.All.Item("P",C).classname="empty"
    End If
  End Sub 
 
' Set text in the Dbg area
' Modified 2011-10-04
  Public Sub SetDebug(T)
    On Error Resume Next        ' Ignore errors caused by closed object
    Dbg=T
    IE.Document.GetElementById("Debug").InnerHTML=T
  End Sub

' Set text in the info area
' Modified 2011-10-04
  Public Sub SetInfo(T)
    On Error Resume Next        ' Ignore errors caused by closed object
    Info=T
    IE.Document.GetElementById("Info").InnerHTML=T
  End Sub

' Set text in the status area
' Modified 2011-10-04
  Public Sub SetStatus(T)
    On Error Resume Next        ' Ignore errors caused by closed object
    Status=T
    IE.Document.GetElementById("Status").InnerHTML=T
  End Sub

' Set title text
' Modified 2011-10-04
  Public Sub SetTitle(T)
    On Error Resume Next        ' Ignore errors caused by closed object
    Title=T
    IE.Document.Title=T & Blank
  End Sub
  
' Create and display the progress bar  
' Modified 2011-10-17
  Public Sub Show()
    Const HKEY_CURRENT_USER=&H80000001
    Const KeyPath="Software\Microsoft\Internet Explorer\Main\FeatureControl\FEATURE_LOCALMACHINE_LOCKDOWN"
    Const KeyName="iexplore.exe"
    Dim File,I,Reg,State,Value
    Set Reg=GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\default:StdRegProv") 	' Use . for local computer, otherwise could be computer name or IP address
    'On Error Resume Next        ' Ignore possible errors
    ' Make sure IE is set to allow local content, at least while we get the Progress Bar displayed
    Reg.GetDWORDValue HKEY_CURRENT_USER,KeyPath,KeyName,Value	' Get current property
    State=Value	 							  ' Preserve current option
    Value=0		    							' Set new option 
    Reg.SetDWORDValue HKEY_CURRENT_USER,KeyPath,KeyName,Value	' Update property
    'If Version<>"5.1" Then Prog=False : Exit Sub      ' Need to test for Vista/Windows 7 with UAC
    Set IE=WScript.CreateObject("InternetExplorer.Application","Event_")
    Set File=FSO.CreateTextFile(Temp, True)
    With File
      .WriteLine "<!doctype html>"
      .WriteLine "<html><head><title>" & Title & Blank & "</title>"
      .WriteLine "<style type='text/css'>"
      .WriteLine ".border {border: 5px solid #DBD7C7;}"
      .WriteLine ".debug {font-family: Tahoma; font-size: 8.5pt;}"
      .WriteLine ".empty {border: 2px solid #FFFFFF; background-color: #FFFFFF;}"
      .WriteLine ".filled {border: 2px solid #FFFFFF; background-color: #00FF00;}"
      .WriteLine ".info {font-family: Tahoma; font-size: 8.5pt;}"
      .WriteLine ".status {font-family: Tahoma; font-size: 10pt;}"
      .WriteLine "</style>"
      .WriteLine "</head>"
      .WriteLine "<body scroll='no' style='background-color: #EBE7D7'>"
      .WriteLine "<div style='display:block; height:" & Height & "px; width:" & Width & "px; overflow:hidden;'>"
      .WriteLine "<table border-width='0' cellpadding='2' width='" & Width & "px'><tr>"
      .WriteLine "<td id='Status' class='status'>" & Status & "</td></tr></table>"
      .WriteLine "<table class='border' cellpadding='0' cellspacing='0' width='" & Width & "px'><tr>"
      ' Write out cells
      For I=0 To Cells-1
	      If Filled(I) Then
          .WriteLine "<td id='p' class='filled'>&nbsp;</td>"
        Else
          .WriteLine "<td id='p' class='empty'>&nbsp;</td>"
        End If
      Next
	    .WriteLine "</tr></table>"
      .WriteLine "<table border-width='0' cellpadding='2' width='" & Width & "px'><tr><td>"
      .WriteLine "<span id='Info' class='info'>" & Info & "</span><br>"
      .WriteLine "<span id='Debug' class='debug'>" & Dbg & "</span></td></tr></table>"
      .WriteLine "</div></body></html>"
    End With
    ' Create IE automation object with generated HTML
    With IE
      .width=Width+30           ' Increase if using more cells
      .height=Height+55         ' Increase to allow more info/debug text
      If Version>"5.1" Then     ' Allow for bigger border in Vista/Widows 7
        .width=.width+10
        .height=.height+10
      End If        
      .left=(SWidth-.width)/2
      .top=(SHeight-.height)/2
      .navigate "file://" & Temp
      '.navigate "http://samsoft.org.uk/progbar.htm"
      .addressbar=False
      .menubar=False
      .resizable=False
      .toolbar=False
      On Error Resume Next      
      .statusbar=False          ' Causes error on Windows 7 or IE 9
      On Error Goto 0
      .visible=True             ' Causes error if UAC is active
    End With
    Active=True
    ' Restore the user's property settings for the registry key
    Value=State		    					' Restore option
    Reg.SetDWORDValue HKEY_CURRENT_USER,KeyPath,KeyName,Value	  ' Update property 
    Exit Sub
  End Sub
 
' Increment progress bar, optionally clearing a previous cell if working as an activity bar
' Modified 2011-10-05
  Public Sub Step(Clear)
    SetCell NextOn,True : NextOn=(NextOn+1) Mod Cells
    If Clear Then SetCell NextOff,False : NextOff=(NextOff+1) Mod Cells
  End Sub

' Self-timed shutdown
' Modified 2011-10-05 
  Public Sub TimeOut(S)
    Dim I
    Respawn=False                ' Allow uninteruppted exit during countdown
    For I=S To 2 Step -1
      SetDebug "<br>Closing in " & I & " seconds" & String(I,".")
      WScript.sleep 1000
    Next
      SetDebug "<br>Closing in 1 second."
      WScript.sleep 1000
    Close
  End Sub 
    
End Class


' Fires if progress bar window is closed, can't seem to wrap up the handler in the class
' Modified 2011-10-04
Sub Event_OnQuit()
  PB.Cancel
End Sub


' ==============
' End of listing
' ==============