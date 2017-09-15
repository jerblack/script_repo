Set iTunes=CreateObject("iTunes.Application")
F=iTunes.AppCommandMessageProcessingEnabled
T="The current value of the iTunes.AppCommandMessageProcessingEnabled propery is """
If F Then
  T=T & "True"""
Else
  T=T & "False"""
End If
T=T & vbCrLf & vbCrLf & "Change the value?"
R=MsgBox(T,vbYesNoCancel+vbQuestion,"Media Key Processing")
If R=vbYes Then iTunes.AppCommandMessageProcessingEnabled=Not F