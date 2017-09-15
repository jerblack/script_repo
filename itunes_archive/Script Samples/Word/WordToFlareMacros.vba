Sub AutoOpen()
    Application.TaskPanes(wdTaskPaneFormatting).Visible = True
    Application.TaskPanes(wdTaskPaneNav).Visible = True
    Application.TaskPanes(wdTaskPaneStyleInspector).Visible = True
    CopyStylesFromTemplate
End Sub

Sub applyHead1(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 1")
End Sub

Sub applyHead2(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 2")
End Sub

Sub applyHead3(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 3")
End Sub

Sub applyHead4(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 4")
End Sub

Sub applyHead5(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 5")
End Sub

Sub applyHead6(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Heading 6")
End Sub

Sub applyCode(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("code")
End Sub

Sub applyParagraph(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Paragraph Text")
End Sub

Sub applyParaIndent(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Paragraph Indent")
End Sub

Sub applyCaption(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Caption")
End Sub

Sub applyNote(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Note")
End Sub

Sub applyTip(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Tip")
End Sub

Sub applyWarning(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Warning")
End Sub

Sub applyImportant(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Important")
End Sub

Sub applyNum1(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Number")
End Sub

Sub applyNum2(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Number 2")
End Sub

Sub applyNum3(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Number 3")
End Sub

Sub applyBullet1(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Bullet")
End Sub

Sub applyBullet2(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Bullet 2")
End Sub

Sub applyBullet3(control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Bullet 3")
End Sub

Sub fixHyperlinkPara(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Hyperlink")
    Selection.Style = ActiveDocument.Styles("Paragraph Text")
End Sub

Sub fixHyperlinkList(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("Hyperlink")
    Selection.Style = ActiveDocument.Styles("Paragraph Indent")
End Sub

Sub applyGraphic(ByVal control As IRibbonControl)
    Selection.Paragraphs(1).Range.Select
    Selection.Style = ActiveDocument.Styles("Graphic")
    Selection.InsertCaption Label:="Figure", TitleAutoText:="InsertCaption1", Title:=" ", _
        Position:=wdCaptionPositionBelow, ExcludeLabel:=0
End Sub

Sub applyGraphicStyle(ByVal control As IRibbonControl)
    Selection.Paragraphs(1).Range.Select
    Selection.Style = ActiveDocument.Styles("Graphic")
End Sub

Sub TableCleanup(ByVal control As IRibbonControl)
On Error Resume Next
Dim cellText, cellLetter As String
Dim numRows, i As Integer
    With Selection.Tables(1)
        .Borders(wdBorderLeft).LineStyle = wdLineStyleSingle
        .Borders(wdBorderLeft).LineWidth = wdLineWidth075pt
        .Borders(wdBorderLeft).Color = wdColorBlack
        .Borders(wdBorderRight).LineStyle = wdLineStyleSingle
        .Borders(wdBorderRight).LineWidth = wdLineWidth075pt
        .Borders(wdBorderRight).Color = wdColorBlack
        .Borders(wdBorderTop).LineStyle = wdLineStyleSingle
        .Borders(wdBorderTop).LineWidth = wdLineWidth075pt
        .Borders(wdBorderTop).Color = wdColorBlack
        .Borders(wdBorderBottom).LineStyle = wdLineStyleSingle
        .Borders(wdBorderBottom).LineWidth = wdLineWidth075pt
        .Borders(wdBorderBottom).Color = wdColorBlack
        .Borders(wdBorderHorizontal).LineStyle = wdLineStyleSingle
        .Borders(wdBorderHorizontal).LineWidth = wdLineWidth075pt
        .Borders(wdBorderHorizontal).Color = wdColorBlack
        .Borders(wdBorderVertical).LineStyle = wdLineStyleSingle
        .Borders(wdBorderVertical).LineWidth = wdLineWidth075pt
        .Borders.Shadow = False
        .Shading.Texture = wdTextureNone
        .Shading.ForegroundPatternColor = wdColorAutomatic
        .Shading.BackgroundPatternColor = wdColorAutomatic
        .AllowAutoFit = True
        .Rows.LeftIndent = InchesToPoints(0.5)
        .Rows(1).HeadingFormat = False
    End With
    Selection.Paragraphs.IndentCharWidth -1
    
    cellText = Selection.Tables(1).Cell(1, 1).Range.Text
    cellLetter = Left(cellText, 1)
    If cellLetter <> "1" Then
        Selection.Tables(1).Rows(1).Range.Font.Bold = True
    Else
        numRows = Selection.Tables(1).Rows.Count
        For i = 1 To numRows
            Selection.Tables(1).Cell(i, 1).Range.Font.Bold = True
        Next i
             
    End If
    
End Sub

Sub cleanupAllTablesButton(ByVal control As IRibbonControl)
cleanupAllTables
End Sub

Sub cleanupAllTables()
On Error Resume Next

Dim cellText, cellLetter As String
For Each aTable In ActiveDocument.Tables
    With aTable
        .Borders(wdBorderLeft).LineStyle = wdLineStyleSingle
        .Borders(wdBorderLeft).LineWidth = wdLineWidth075pt
        .Borders(wdBorderLeft).Color = wdColorBlack
        .Borders(wdBorderRight).LineStyle = wdLineStyleSingle
        .Borders(wdBorderRight).LineWidth = wdLineWidth075pt
        .Borders(wdBorderRight).Color = wdColorBlack
        .Borders(wdBorderTop).LineStyle = wdLineStyleSingle
        .Borders(wdBorderTop).LineWidth = wdLineWidth075pt
        .Borders(wdBorderTop).Color = wdColorBlack
        .Borders(wdBorderBottom).LineStyle = wdLineStyleSingle
        .Borders(wdBorderBottom).LineWidth = wdLineWidth075pt
        .Borders(wdBorderBottom).Color = wdColorBlack
        .Borders(wdBorderHorizontal).LineStyle = wdLineStyleSingle
        .Borders(wdBorderHorizontal).LineWidth = wdLineWidth075pt
        .Borders(wdBorderHorizontal).Color = wdColorBlack
        .Borders(wdBorderVertical).LineStyle = wdLineStyleSingle
        .Borders(wdBorderVertical).LineWidth = wdLineWidth075pt
        .Borders.Shadow = False
        .Shading.Texture = wdTextureNone
        .Shading.ForegroundPatternColor = wdColorAutomatic
        .Shading.BackgroundPatternColor = wdColorAutomatic
        .AllowAutoFit = True
        .Rows.LeftIndent = InchesToPoints(0.5)
        aTable.Rows(1).HeadingFormat = False
    End With
     aTable.Range.Paragraphs.IndentCharWidth -1
   
    cellText = aTable.Cell(1, 1).Range.Text
    cellLetter = Left(cellText, 1)
    If cellLetter <> "1" Then
        aTable.Rows(1).Range.Font.Bold = True
    Else
        numRows = aTable.Rows.Count
        For i = 1 To numRows
            aTable.Cell(i, 1).Range.Font.Bold = True
        Next i
        
    End If


Next aTable
MsgBox ("Finished formatting all tables.")
End Sub

Sub captionAllTablesButton(ByVal control As IRibbonControl)
captionAllTables
End Sub


Sub captionAllTables()
On Error Resume Next
Dim prevText, tableText, captionDetail As String
Dim Position, noDesc As Integer
noDesc = 0
For Each aTable In ActiveDocument.Tables
    tableText = "Table "
    prevText = aTable.Cell(1, 1).Range.Paragraphs(1).Previous.Range.Text
    If InStr(prevText, tableText) <> 0 Then
        If InStr(prevText, ":") <> 0 Then
            Position = InStr(prevText, ":")
            captionDetail = Trim(Mid(prevText, Position + 1))
    
        ElseIf InStr(prevText, "-") <> 0 Then
            Position = InStr(prevText, "-")
            captionDetail = Trim(Mid(prevText, Position + 1))
        Else
            captionDetail = ""
        End If
        aTable.Cell(1, 1).Range.Paragraphs(1).Previous.Range.Delete
        aTable.Cell(1, 1).Range.Paragraphs(1).Previous.Range.Delete
    End If
    
    If Len(captionDetail) < 2 Then
        noDesc = noDesc + 1
    End If
    

    aTable.Range.InsertCaption Label:="Table", _
        TitleAutoText:="InsertCaption1", _
        Title:=": " + captionDetail, _
        Position:=wdCaptionPositionAbove, _
        ExcludeLabel:=0
    captionDetail = ""
Next aTable
'MsgBox (noDesc)
MsgBox ("Finished adding captions to the tables. There are currently " + CStr(noDesc) _
    + " table captions with no description")
End Sub

Sub captionSelectedTableButton(ByVal control As IRibbonControl)
captionSelectedTable
End Sub

Sub captionSelectedTable()

On Error GoTo ErrHandler:
Dim prevText, tableText, captionDetail As String
Dim Position As Integer
tableText = "Table "
prevText = Selection.Tables(1).Cell(1, 1).Range.Paragraphs(1).Previous.Range.Text

If InStr(prevText, tableText) <> 0 Then
    If InStr(prevText, "-") <> 0 Then
        Position = InStr(prevText, "-")
        captionDetail = Trim(Mid(prevText, Position + 1))

    ElseIf InStr(prevText, ":") <> 0 Then
        Position = InStr(prevText, ":")
        captionDetail = Trim(Mid(prevText, Position + 1))
    Else
        captionDetail = ""
    End If
    Selection.Tables(1).Cell(1, 1).Range.Paragraphs(1).Previous.Range.Delete
    Selection.Tables(1).Cell(1, 1).Range.Paragraphs(1).Previous.Range.Delete
End If

Selection.Tables(1).Range.InsertCaption Label:="Table", _
    TitleAutoText:="InsertCaption1", _
    Title:=": " + captionDetail, _
    Position:=wdCaptionPositionAbove, _
    ExcludeLabel:=0

ErrHandler:
    If Err.Number = 5941 Then
        MsgBox ("Please select a table first.")
        Exit Sub
    Else
        Resume Next
    End If
End Sub

Sub captionSelectedImageButton(ByVal control As IRibbonControl)
captionSelectedImage
End Sub


Sub captionSelectedImage()
On Error GoTo ErrHandler:
    Dim nextText, figureText, captionDetail As String
    Dim Position As Integer
    figureText = "Figure "
    nextText = Selection.Range.Paragraphs(1).Next.Range.Text

If InStr(nextText, figureText) <> 0 Then
    If InStr(nextText, "-") <> 0 Then
        Position = InStr(nextText, "-")
        captionDetail = Trim(Mid(nextText, Position + 1))

    ElseIf InStr(nextText, ":") <> 0 Then
        Position = InStr(nextText, ":")
        captionDetail = Trim(Mid(nextText, Position + 1))
    Else
        captionDetail = ""
    End If
    
    Selection.Range.Paragraphs(1).Next.Range.Delete
End If
   
    Selection.Range.Next.InsertCaption Label:="Figure", _
        TitleAutoText:="InsertCaption1", _
        Title:=": " + captionDetail, _
        Position:=wdCaptionPositionBelow, _
        ExcludeLabel:=0
        
ErrHandler:
    If Err.Number = 5941 Then
        MsgBox ("Please select an image first.")
        Exit Sub
    Else
        Resume Next
    End If
End Sub

Sub captionAllImagesButton(ByVal control As IRibbonControl)
captionAllImages
End Sub

Sub captionAllImages()
'On Error Resume Next
Dim prevText, figureText, captionDetail As String
Dim Position, noDesc As Integer
noDesc = 0
For Each img In ActiveDocument.InlineShapes
    captionDetail = ""
    figureText = "Figure "
    nextText = img.Range.Paragraphs(1).Next.Range.Text
    'MsgBox (nextText)
    
    If InStr(nextText, figureText) <> 0 Then
        If InStr(nextText, "-") <> 0 Then
            Position = InStr(nextText, "-")
            captionDetail = Trim(Mid(nextText, Position + 1))
    
        ElseIf InStr(nextText, ":") <> 0 Then
            Position = InStr(nextText, ":")
            captionDetail = Trim(Mid(nextText, Position + 1))
        Else
            captionDetail = ""
        End If
        img.Range.Paragraphs(1).Next.Range.Delete
        
        If Len(captionDetail) < 2 Then
            noDesc = noDesc + 1
        End If
        
        Else
        noDesc = noDesc + 1
        
    End If
   
    img.Range.InsertCaption Label:="Figure", TitleAutoText:="InsertCaption1", Title:=": " + captionDetail, Position:=wdCaptionPositionBelow, ExcludeLabel:=0
Next img
    
For Each oshp In ActiveDocument.Shapes
    oshp.ConvertToInlineShape
Next oshp


MsgBox ("Finished adding captions to the images. There are currently " + CStr(noDesc) _
    + " image captions with no description")
End Sub

Sub SendToPowerPoint(ByVal control As IRibbonControl)
    If MsgBox("You should save your work before exporting headings. " _
        + "When finished, close Word and reset slide formatting in PowerPoint. Do you want to continue?" _
        , vbYesNo, "Caution") _
        = 6 _
        Then
        SendToPowerPointWork
    Else
    End If

End Sub


Sub SendToPowerPointWork()

    'Move to the top of the document, in case we are not at the top.
    Selection.TypeParagraph
    Selection.MoveUp Unit:=wdLine, Count:=1

    'Create a TOC, which will form the basis of our exported headers.
    With ActiveDocument
        .TablesOfContents.Add Range:=Selection.Range, RightAlignPageNumbers:= _
            True, UseHeadingStyles:=True, UpperHeadingLevel:=1, _
            LowerHeadingLevel:=5, IncludePageNumbers:=False, AddedStyles:="", _
            UseHyperlinks:=False, HidePageNumbersInWeb:=True, UseOutlineLevels:= _
            False
        .TablesOfContents(1).TabLeader = wdTabLeaderDots
        .TablesOfContents.Format = wdIndexIndent
    End With

    'Select and delete everything in the document after the TOC.
    Selection.EndKey Unit:=wdStory, Extend:=wdExtend
    Selection.Delete Unit:=wdCharacter, Count:=1

    'Back to the top, then unlink the field for the TOC.
    Selection.HomeKey Unit:=wdStory, Extend:=wdExtend
    Selection.Fields.Unlink
    With Selection.Font
        .Name = ""
        .Bold = False
        .Italic = False
    End With

    'Replacing TOC heading formatting with the normal heading styles.
    Selection.Find.ClearFormatting
    Selection.Find.Style = ActiveDocument.Styles("TOC 1")
    Selection.Find.Replacement.Style = ActiveDocument.Styles("Heading 1")

    With Selection.Find
        .Text = ""
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Style = ActiveDocument.Styles("TOC 2")
    Selection.Find.Replacement.Style = ActiveDocument.Styles("Heading 1")

    With Selection.Find
        .Text = ""
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue
    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Style = ActiveDocument.Styles("TOC 3")
    Selection.Find.Replacement.Style = ActiveDocument.Styles("Heading 2")

    With Selection.Find
        .Text = ""
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue

    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    Selection.Find.ClearFormatting
    Selection.Find.Style = ActiveDocument.Styles("TOC 4")
    Selection.Find.Replacement.Style = ActiveDocument.Styles("Heading 3")

    With Selection.Find
        .Text = ""
        .Replacement.Text = ""
        .Forward = True
        .Wrap = wdFindContinue

    End With
    Selection.Find.Execute Replace:=wdReplaceAll

    'Send the remaining document contents (headings only) to PowerPoint.
    ActiveDocument.PresentIt

    'Close the modified document without saving.
    ActiveDocument.Close SaveChanges:=wdDoNotSaveChanges

End Sub

Sub removeExcessStyles(ByVal control As IRibbonControl)
    On Error Resume Next

    ActiveDocument.Styles("BulletIndent").Delete
    ActiveDocument.Styles("BulletListT1").Delete
    ActiveDocument.Styles("BulletListT2").Delete
    ActiveDocument.Styles("BulletList1").Delete
    ActiveDocument.Styles("BulletList2").Delete
    ActiveDocument.Styles("BulletList3").Delete
    ActiveDocument.Styles("BulletList4").Delete
    ActiveDocument.Styles("NumberListT1").Delete
    ActiveDocument.Styles("NumberListT2").Delete
    ActiveDocument.Styles("NumberListT3").Delete
    ActiveDocument.Styles("NumberList1").Delete
    ActiveDocument.Styles("NumberList2").Delete
    ActiveDocument.Styles("NumberList3").Delete
    ActiveDocument.Styles("NumberList4").Delete
    ActiveDocument.Styles("code Table").Delete
    ActiveDocument.Styles("FlareTOC1").Delete
    ActiveDocument.Styles("Graphic Table").Delete
    ActiveDocument.Styles("Graphic Large").Delete
    ActiveDocument.Styles("GraphicLarge").Delete
    ActiveDocument.Styles("Lesson Title").Delete
    ActiveDocument.Styles("Note Table").Delete
    ActiveDocument.Styles("Paragraph Text Table Bold").Delete
    ActiveDocument.Styles("Paragraph Text Table").Delete
    ActiveDocument.Styles("Table Text").Delete
    ActiveDocument.Styles("Notes_Course").Delete
    ActiveDocument.Styles("Notes_Course Label").Delete
    ActiveDocument.Styles("idtext").Delete
    ActiveDocument.Styles("NumberList.1").Delete
    ActiveDocument.Styles("NumberList.2").Delete
    ActiveDocument.Styles("NumberList.3").Delete
    ActiveDocument.Styles("ParaTextTable").Delete
    ActiveDocument.Styles("Unordered List").Delete
    ActiveDocument.Styles("Default").Delete
    ActiveDocument.Styles("Body Text PSS").Delete
    ActiveDocument.Styles("readeraidtitle").Delete
    ActiveDocument.Styles("Activity Heading").Delete
    ActiveDocument.Styles("CPBA Heading 1").Delete
    ActiveDocument.Styles("keywordhighlight1").Delete
    ActiveDocument.Styles("Style1").Delete
    ActiveDocument.Styles("Style2").Delete
    ActiveDocument.Styles("Le").Delete
    ActiveDocument.Styles("NoBulletIndent").Delete
    ActiveDocument.Styles("Paragrph Text Table Bold").Delete
    ActiveDocument.Styles("String (finalized)").Delete
    ActiveDocument.Styles("G_Large").Delete
    ActiveDocument.Styles("Primary List Style").Delete

End Sub
Sub fixAttachedTemplate(ByVal control As IRibbonControl)
    ActiveDocument.AttachedTemplate = "Word to Flare Template.dotm"
End Sub


Sub fixImagesSizes(ByVal control As IRibbonControl)
    'Resize all regular images to 100% and large images to 70%

    Dim PercentSize As Integer
    Dim MyStyle As String
    Dim oIshp As InlineShape
    Dim oshp As Shape
    PercentSize = 100
    With ActiveDocument
        For Each oIshp In .InlineShapes
            With oIshp
                    .ScaleHeight = PercentSize
                    .ScaleWidth = PercentSize
            End With
            oIshp.Range.Style = ActiveDocument.Styles("Graphic")
        Next oIshp
        For Each oshp In .Shapes
            With oshp
                    .ScaleHeight Factor:=(PercentSize / 100), RelativeToOriginalSize:=msoCTrue
                    .ScaleWidth Factor:=(PercentSize / 100), RelativeToOriginalSize:=msoCTrue
            End With
            oshp.Parent.Style = ActiveDocument.Styles("Graphic")
        Next oshp
    End With
    
    PercentSize = 70
    With ActiveDocument
        For Each oIshp In .InlineShapes
            With oIshp
                If .Width > InchesToPoints(8) Then
                    .ScaleHeight = PercentSize
                    .ScaleWidth = PercentSize
                End If
            End With
        Next oIshp
        For Each oshp In .Shapes
            With oshp
                If .Anchor.Paragraphs(1).Style = MyStyle Then
                    .ScaleHeight Factor:=(PercentSize / 100), RelativeToOriginalSize:=msoCTrue
                    .ScaleWidth Factor:=(PercentSize / 100), RelativeToOriginalSize:=msoCTrue
                End If
            End With
        Next oshp
    End With
    MsgBox ("Finished formatting images.")
End Sub

Sub fixNoteBoxes(ByVal control As IRibbonControl)
    'Fix Note styles. Warning, Caution get Warning Style. Important, Tip, and Note all have their own styles.
    'Styles are used in Flare to determine icon that appears next to it

    With ActiveDocument.Content.Find
        .ClearFormatting
        Do While .Execute(FindText:="Note:", Forward:=True, Format:=True) = True
            .Parent.Bold = True
            .Parent.Style = ActiveDocument.Styles("Note")
        Loop
    End With

    With ActiveDocument.Content.Find
        .ClearFormatting
        Do While .Execute(FindText:="Tip:", Forward:=True, Format:=True) = True
            .Parent.Bold = True
            .Parent.Style = ActiveDocument.Styles("Tip")
        Loop
    End With
    With ActiveDocument.Content.Find
        .ClearFormatting
        Do While .Execute(FindText:="Caution:", Forward:=True, Format:=True) = True
            .Parent.Bold = True
            .Parent.Style = ActiveDocument.Styles("Warning")
        Loop
    End With
    With ActiveDocument.Content.Find
        .ClearFormatting
        Do While .Execute(FindText:="Warning:", Forward:=True, Format:=True) = True
            .Parent.Bold = True
            .Parent.Style = ActiveDocument.Styles("Warning")
        Loop
    End With
    With ActiveDocument.Content.Find
        .ClearFormatting
        Do While .Execute(FindText:="Important:", Forward:=True, Format:=True) = True
            .Parent.Bold = True
            .Parent.Style = ActiveDocument.Styles("Important")
        Loop
        .ClearFormatting
    End With
MsgBox ("Finished applying note box styles.")
End Sub

Sub deleteTitle(ByVal control As IRibbonControl)
    'Delete text with Title Style (delete titles from beginning of module)

    With ActiveDocument.Content.Find
        .ClearFormatting
        .Style = ActiveDocument.Styles("Title")
        Do While .Execute(FindText:="", Forward:=True, Format:=True) = True
            .Parent.Delete
        Loop
    End With
End Sub

Sub insertTOCtoH2(ByVal control As IRibbonControl)
    'Delete existing TOC and replace with new TOC to Heading 2
    With ActiveDocument
        If .TablesOfContents.Count > 0 Then .TablesOfContents(1).Delete
        .TablesOfContents.Add Range:=ActiveDocument.Paragraphs(2).Range, _
            RightAlignPageNumbers:=True, UseHeadingStyles:=False, UpperHeadingLevel:=1, _
            LowerHeadingLevel:=2, IncludePageNumbers:=True, HidePageNumbersInWeb:=False
    End With
End Sub


Sub insertTOCtoH3(ByVal control As IRibbonControl)
    'Delete existing TOC and replace with new TOC to Heading 2
    With ActiveDocument
        If .TablesOfContents.Count > 0 Then .TablesOfContents(1).Delete
        .TablesOfContents.Add Range:=ActiveDocument.Paragraphs(2).Range, _
            RightAlignPageNumbers:=True, UseHeadingStyles:=False, UpperHeadingLevel:=1, _
            LowerHeadingLevel:=3, IncludePageNumbers:=True, HidePageNumbersInWeb:=False
    End With
End Sub

Sub newBulletList(ByVal control As IRibbonControl)
    Selection.Style = ActiveDocument.Styles("List Bullet")
Dim t As ListTemplate
Set t = ActiveDocument.Styles("Primary Bullet List").ListTemplate
t.ListLevels(1).ResetOnHigher = True
Selection.Range.ListFormat.ApplyListTemplate t, False, wdListApplyToWholeList
End Sub

Sub newNumberList(ByVal control As IRibbonControl)

    Selection.Style = ActiveDocument.Styles("List Number")
Dim t As ListTemplate
Set t = ActiveDocument.Styles("Primary Number List").ListTemplate
t.ListLevels(1).ResetOnHigher = True
Selection.Range.ListFormat.ApplyListTemplate t, False, wdListApplyToWholeList

End Sub



Sub FixLists()
' be careful, behavior is not consistent for all docs
    On Error Resume Next
    Dim lList As Long
    Dim Level As Integer
    Dim myPara As Paragraph
    Dim tn As ListTemplate
    Dim tb As ListTemplate
    Set tn = ActiveDocument.Styles("Primary Number List").ListTemplate
    Set tb = ActiveDocument.Styles("Primary Bullet List").ListTemplate
    tn.ListLevels(1).ResetOnHigher = True
    tb.ListLevels(1).ResetOnHigher = True
    For Each myPara In ActiveDocument.ListParagraphs
    Level = myPara.Range.ListFormat.ListLevelNumber
    If (myPara.Range.ListFormat.ListType = wdListListNumOnly Or _
        myPara.Range.ListFormat.ListType = wdListMixedNumbering Or _
        myPara.Range.ListFormat.ListType = wdListSimpleNumbering Or _
        myPara.Range.ListFormat.ListType = wdListOutlineNumbering) Then
        Select Case Level
            Case 1
                myPara.Range.Style = ActiveDocument.Styles("List Number")
            Case 2
                myPara.Range.Style = ActiveDocument.Styles("List Number 2")
            Case 3
                myPara.Range.Style = ActiveDocument.Styles("List Number 3")
            Case 4
                myPara.Range.Style = ActiveDocument.Styles("List Number 4")
        End Select
        myPara.Range.ListFormat.ApplyListTemplate tn, True, wdListApplyToSelection
    Else
        Select Case Level
            Case 1
                myPara.Range.Style = ActiveDocument.Styles("List Bullet")
            Case 2
                myPara.Range.Style = ActiveDocument.Styles("List Bullet 2")
            Case 3
                myPara.Range.Style = ActiveDocument.Styles("List Bullet 3")
            Case 4
                myPara.Range.Style = ActiveDocument.Styles("List Bullet 4")
        End Select
        myPara.Range.ListFormat.ApplyListTemplate tb, True, wdListApplyToSelection
    End If
        ' Continue Numbering
    If myPara.Style = ActiveDocument.Styles("List Number") Then
            If (myPara.Previous.Style <> ActiveDocument.Styles("List Number") And _
                    myPara.Previous.Style <> ActiveDocument.Styles("List Number 2") And _
                    myPara.Previous.Style <> ActiveDocument.Styles("List Number 3") And _
                    myPara.Previous.Style <> ActiveDocument.Styles("List Number 4")) Then
                myPara.Range.Select
                Selection.Paragraphs(1).SelectNumber
                Selection.Style = ActiveDocument.Styles("Primary Number List")
            End If
        End If
    Next myPara
    Beep
End Sub

Sub fixContinueNumbering()
    On Error Resume Next
    Dim lList As Long
    Dim Level As Integer
    Dim myPara As Paragraph
    Dim tn As ListTemplate
    Set tn = ActiveDocument.Styles("Primary Number List").ListTemplate
    For Each myPara In ActiveDocument.ListParagraphs
        ' Continue Numbering
        If myPara.Style = ActiveDocument.Styles("List Number") Then
            If (myPara.Previous.Style <> ActiveDocument.Styles("List Number") And _
                myPara.Previous.Style <> ActiveDocument.Styles("List Number 2") And _
                myPara.Previous.Style <> ActiveDocument.Styles("List Number 3") And _
                myPara.Previous.Style <> ActiveDocument.Styles("List Number 4")) Then
                myPara.Range.Select
                Selection.Paragraphs(1).SelectNumber
                Selection.Style = ActiveDocument.Styles("Primary Number List")
            End If
        End If
    Next myPara
    Beep
End Sub

Sub refreshStyles(ByVal control As IRibbonControl)
CopyStylesFromTemplate
MsgBox ("Finished copying all template styles into the document.")
End Sub

Sub CopyStylesFromTemplate()
    On Error Resume Next
    ActiveDocument.AttachedTemplate = "Word to Flare Template.dotm"
    Dim tStyle As Style
    For Each tStyle In ActiveDocument.AttachedTemplate.Styles
        Application.OrganizerCopy _
            Source:=ActiveDocument.AttachedTemplate.FullName, _
            Destination:=ActiveDocument.FullName, _
            Name:=tStyle, _
            Object:=wdOrganizerObjectStyles
    Next tStyle
End Sub

Sub reapplyStylesButton(ByVal control As IRibbonControl)
reapplyStyles
MsgBox ("Finished re-applying document styles to relevant paragraphs.")
End Sub

Sub reapplyStyles()
' reapply all document styles to relevant paragraphs
    Dim txt As String
    Dim p As Paragraph
    For Each p In ActiveDocument.Paragraphs
            p.Style = p.Style
    Next p
End Sub

Sub updateAllFields()
' updates TOC and caption numbering
    Dim myRange
    Set myRange = Selection.Range
    Selection.WholeStory
    Selection.Fields.Update
    myRange.Select
End Sub
