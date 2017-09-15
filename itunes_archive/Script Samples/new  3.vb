Option Explicit
sub fixtext()
Dim oRng As Word.Range
Dim bParaAdded As Boolean
Dim pWrap As Integer
Dim pStoryType As Integer

AdvOption = 1

'Me.Hide
Word.Application.ScreenUpdating = False

    MakeHFValid
  For Each oRng In ActiveDocument.StoryRanges
    If oRng.StoryLength >= 2 Then 'Skips empty/near empty storyranges
    pStoryType = oRng.StoryType
    pWrap = 1
    Do
      'Ensure proper paragraph marks
      If oRng.Paragraphs.Count > 1 Then
        ValidateParagraphs oRng, pWrap
        oRng.Paragraphs.Last.Range.Delete
      End If
      oRng.InsertBefore Chr(13)
      pWrap = 1
      bParaAdded = True
      'Call Processor
      Process oRng, pWrap, bParaAdded, pStoryType
      Set oRng = oRng.NextStoryRange
    Loop Until oRng Is Nothing
    End If
  Next
  
	Word.Application.ScreenRefresh
	Word.Application.ScreenUpdating = True
  

end sub

Private Sub Process(ByRef oRng As Range, ByVal pWrap As Integer, _
                    ByVal bParaAdded As Boolean, ByVal pStoryType As Integer)


Dim TextCharArray As Variant
Dim i As Integer
Dim j As Integer
Dim EP As Range
Dim oPara As Paragraph


  With oRng.Find
    .ClearFormatting
    .Replacement.ClearFormatting
    .Forward = True
    .Wrap = pWrap
    .MatchWildcards = True
    For i = 1 To 8
      Select Case i
        Case 1
          .Text = "(^13)( {1,})"
          .Replacement.Text = "\1"
        Case 2
          .Text = "(^l)( {1,})"
          .Replacement.Text = "\1"
        Case 3
          .Text = "( {1,})(^13)"
          .Replacement.Text = "\2"
        Case 4
          .Text = "( {1,})(^l)"
          .Replacement.Text = "\2"
        Case 5
          .Text = "(^13)(^s{1,})"
          .Replacement.Text = "\1"
        Case 6
          .Text = "(^l)(^s{1,})"
          .Replacement.Text = "\1"
        Case 7
          .Text = "(^s{1,})(^13)"
          .Replacement.Text = "\2"
        Case 8
          .Text = "(^s{1,})(^l)"
          .Replacement.Text = "\2"
        Case Else
          Exit For
      End Select
      .Execute Replace:=wdReplaceAll
    Next
  End With


  With oRng.Find
    .ClearFormatting
    .Replacement.ClearFormatting
    .Forward = True
    .Wrap = pWrap
    .MatchWildcards = True
    For i = 1 To 8
      Select Case i
        Case 1
          .Text = "(^13)( {1,})"
          .Replacement.Text = "\1"
        Case 2
          .Text = "(^l)( {1,})"
          .Replacement.Text = "\1"
        Case 3
          .Text = "( {1,})(^13)"
          .Replacement.Text = "\2"
        Case 4
          .Text = "( {1,})(^l)"
          .Replacement.Text = "\2"
        Case 5
          .Text = "(^13)(^s{1,})"
          .Replacement.Text = "\1"
        Case 6
          .Text = "(^l)(^s{1,})"
          .Replacement.Text = "\1"
        Case 7
          .Text = "(^s{1,})(^13)"
          .Replacement.Text = "\2"
        Case 8
          .Text = "(^s{1,})(^l)"
          .Replacement.Text = "\2"
         Case Else
          Exit For
      End Select
      .Execute Replace:=wdReplaceAll
    Next
  End With

'Remove Empty Paragraphs

  With oRng.Find
    .Text = "^13{2,}"
    .Replacement.Text = "^p"
    .Forward = True
    .Wrap = pWrap
    .MatchWildcards = True
    .Execute Replace:=wdReplaceAll
  End With
  If AdvOption = 2 Then
    For Each oPara In oRng.Paragraphs
      If Len(oPara.Range.Text) = 1 Then
        oPara.Range.Delete
      End If
    Next
  Else
  'Call Macro to process empty PMs in tables and nested tables
    ProcessTables oRng, pStoryType
  End If
  If oRng.Paragraphs.Count > 1 Then
    Set EP = ActiveDocument.StoryRanges(pStoryType).Paragraphs.First.Range
    If EP.Text = vbCr Then EP.Delete
    Set EP = ActiveDocument.StoryRanges(pStoryType).Paragraphs.Last.Range
    If EP.Text = vbCr Then EP.Delete
  End If
If bParaAdded = True Then
  oRng.Paragraphs(1).Range.Delete
End If

If oRng.Paragraphs.Last.Range.Characters.Count = 1 Then
   On Error Resume Next
   oRng.Paragraphs.Last.Range.Delete
   On Error GoTo 0
End If
Selection.Collapse Direction:=wdCollapseStart
End Sub

Private Sub ValidateParagraphs(ByVal oRng As Range, pWrap As Integer)
With oRng.Find
  .ClearFormatting
  .Replacement.ClearFormatting
  .Forward = True
  .Wrap = pWrap
  .Text = "^13"
  .Replacement.Text = "^p"
  .Execute Replace:=wdReplaceAll
End With
End Sub
Private Sub MakeHFValid()
Dim lngJunk As Long
lngJunk = ActiveDocument.Sections(1).Headers(1).Range.StoryType
End Sub
Sub ProcessTables(oRng As Range, pStoryType As Integer)
Dim TopTable As Table
Dim ttCell As Word.Cell
Dim Level As Long
Dim Level2Table As Word.Table

For Each TopTable In oRng.Tables
  'Call Macro to process empty PMs between top level tables
  BAITables TopTable, pStoryType
  
  Level = 1
  'Call Macro to process empty PMs in TopTable cells
  ProcessCells TopTable, pStoryType
  
  'Process TopTable for nested tables
  For Each ttCell In TopTable.Range.Cells
    If ttCell.Tables.Count > 0 Then
      Dim j As Integer
      For j = 1 To ttCell.Tables.Count
        Set Level2Table = ttCell.Tables(j)
        Level = 2
        'Process cells in Level2 Tables
        ProcessCells Level2Table, pStoryType
        'Process deep nested Tables
        ProcessNestedTable Level, Level2Table, TopTable, pStoryType
      Next
    End If
  Next ttCell
Next
End Sub
Function ProcessNestedTable(NewLevel As Long, _
    tbl As Word.Table, ByRef tblOuter As Word.Table, pStoryType As Integer)

Dim celNested As Word.Cell
Dim tblNested As Word.Table

For Each celNested In tbl.Range.Cells
  If celNested.Tables.Count > 0 Then
    Set tblNested = celNested.Tables(1)
    NewLevel = tblNested.NestingLevel
    Set tblOuter = tblNested
    ProcessCells tblNested, pStoryType
    ProcessNestedTable NewLevel, tblNested, tblOuter, pStoryType
  End If
Next celNested
End Function
Sub BAITables(oTbl As Table, pStoryType As Integer)

Dim myRange As Range
Dim emptyPara As Boolean

'Remove empty PMs immediate before, after, and between
'top level tables
Set myRange = oTbl.Range 'tbl.Range
myRange.Collapse wdCollapseEnd
If myRange.Paragraphs(1).Range.Text = vbCr Then
  myRange.Collapse wdCollapseEnd
  myRange.Move wdParagraph, 1
  If myRange.Information(wdWithInTable) Then
    'Do nothing.  Issue will be resolve while
    'processing next table.
  Else
    myRange.Move wdParagraph, -1
    myRange.Paragraphs(1).Range.Delete
  End If
End If
Set myRange = oTbl.Range
Do
  myRange.Collapse wdCollapseStart
  myRange.Move wdParagraph, -1
  If myRange.Paragraphs(1).Range.Text = vbCr Then
    myRange.Collapse wdCollapseStart
    If myRange.Start = ActiveDocument.StoryRanges(pStoryType).Start Then
      myRange.Paragraphs(1).Range.Delete
      emptyPara = False
    Else
      myRange.Move wdParagraph, -1
      If myRange.Information(wdWithInTable) Then
        If AdvOption = 3 Then
          myRange.Move wdParagraph, 1
          emptyPara = True
          myRange.Text = TextMark '"****"
        End If
      Else
        myRange.Move wdParagraph, 1
        emptyPara = True
        myRange.Paragraphs(1).Range.Delete
      End If
    End If
  Else
    emptyPara = False
  End If
Loop While emptyPara = True

End Sub
Sub ProcessCells(tbl As Table, ByVal pStoryType As Integer)
Dim oCell As Cell
Dim Counter As Integer
Dim oPara As Paragraph
Dim workingRng As Range
Dim prevTab As Range
Dim k As Integer
Dim emptyPara As Boolean

For Each oCell In tbl.Range.Cells
  If oCell.Tables.Count > 1 Then
    'Process PMs before first table
    Set workingRng = oCell.Tables(1).Range
    Do
      workingRng.Collapse wdCollapseStart
      workingRng.Move wdParagraph, -1
      If workingRng.Paragraphs(1).Range.Text = vbCr Then
        workingRng.Paragraphs(1).Range.Delete
        emptyPara = True
      Else
         emptyPara = False
      End If
    Loop While emptyPara = True
    
    For k = 2 To oCell.Tables.Count
      Set workingRng = oCell.Tables(k).Range
      'Process PM after last table
      If k = oCell.Tables.Count Then
        workingRng.Collapse wdCollapseEnd
        If workingRng.Paragraphs(1).Range.Text = vbCr Then
          workingRng.Paragraphs(1).Range.Delete
        End If
        Set workingRng = oCell.Tables(k).Range
      End If
      'Process PMs preceeding remaining tables
      Set prevTab = oCell.Tables(k - 1).Range
      workingRng.Select
      Do
        workingRng.Collapse wdCollapseStart
        workingRng.Move wdParagraph, -1
        If workingRng.Paragraphs(1).Range.Text = vbCr Then
          workingRng.Collapse wdCollapseStart
          workingRng.Move wdParagraph, -1
          If workingRng.InRange(prevTab) Then
            If AdvOption = 3 Then
              workingRng.Move wdParagraph, 1
              emptyPara = True
              workingRng.Text = TextMark '"****"
            End If
          Else
            workingRng.Move wdParagraph, 1
            emptyPara = True
            workingRng.Paragraphs(1).Range.Delete
          End If
        Else
          emptyPara = False
        End If
      Loop While emptyPara = True
    Next
  Else
    For Each oPara In oCell.Range.Paragraphs
      If oPara.Range.Characters(1).Text = vbCr Then
        oPara.Range.Delete
      End If
    Next
    If Len(oCell.Range.Text) > 2 And _
         Asc(Right$(oCell.Range.Text, 3)) = 13 Then
      oCell.Range.Characters(Len(oCell.Range.Text) - 2).Delete
    End If
  End If
Next
End Sub

