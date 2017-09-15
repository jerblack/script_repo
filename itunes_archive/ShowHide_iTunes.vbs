Set iTunes=CreateObject("iTunes.Application")

If iTunes.Windows.Item(1).Minimized=True Then
iTunes.Windows.Item(1).Minimized=False
Else
iTunes.Windows.Item(1).Minimized=True
End If

set iTunes = nothing




