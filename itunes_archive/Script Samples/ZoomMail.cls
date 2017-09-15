VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "ThisOutlookSession"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit
Dim WithEvents objInspectors As Outlook.Inspectors
Attribute objInspectors.VB_VarHelpID = -1
Dim WithEvents objOpenInspector As Outlook.Inspector
Attribute objOpenInspector.VB_VarHelpID = -1
Dim WithEvents objMailItem As Outlook.MailItem
Attribute objMailItem.VB_VarHelpID = -1
Private Sub Application_Startup()
Set objInspectors = Application.Inspectors
End Sub

Private Sub Application_Quite()
Set objOpenInspector = Nothing
Set objInspectors = Nothing
Set objMailItem = Nothing
End Sub

Private Sub objInspectors_NewInspector(ByVal Inspector As Inspector)
If Inspector.CurrentItem.Class = olMail Then
Set objMailItem = Inspector.CurrentItem
Set objOpenInspector = Inspector

End If
End Sub
Private Sub objOpenInspector_Close()

Set objMailItem = Nothing
End Sub

Private Sub objOpenInspector_Activate()

Dim wdDoc As Word.Document
Set wdDoc = objOpenInspector.WordEditor
wdDoc.Windows(1).Panes(1).View.Zoom.Percentage = 140

End Sub
