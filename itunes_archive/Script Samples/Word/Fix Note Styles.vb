Sub SetFMI()

    With ActiveDocument.Content.Find
        .ClearFormatting
        .Font.Bold = True
        Do While .Execute(FindText:="For More Information", Forward:=True, Format:=True) = True
          .Parent.Style = ActiveDocument.Styles("Tip")
        Loop
    End With
      
    With ActiveDocument.Content.Find
        .ClearFormatting
        .Style = ActiveDocument.Styles("Note")
    Do While .Execute(FindText:="tip", Forward:=True, Format:=True) = True
        .Parent.Bold = True
        .Parent.Style = ActiveDocument.Styles("Tip")
    Loop
    Do While .Execute(FindText:="caution", Forward:=True, Format:=True) = True
        .Parent.Bold = True
        .Parent.Style = ActiveDocument.Styles("Warning")
    Loop
    Do While .Execute(FindText:="warning", Forward:=True, Format:=True) = True
        .Parent.Bold = True
        .Parent.Style = ActiveDocument.Styles("Warning")
    Loop
    Do While .Execute(FindText:="important", Forward:=True, Format:=True) = True
        .Parent.Bold = True
        .Parent.Style = ActiveDocument.Styles("Important")
    Loop
    End With
End Sub
