import time, subprocess
from win32com.client import Dispatch, pythoncom


def connectSonos():
    pythoncom.CoInitialize()
    airfoilapp = Dispatch("RogueAmoeba.Airfoil")
    speakerBox = airfoilapp.GetSpeakers()
    sonosNum = -1
    while (speakerBox.Count() < 3):
        time.sleep(3)
    for i in range(0, speakerBox.Count()):
        speaker = speakerBox.Item(i)
        if speaker.Name() == "Computer":
            sonosNum = i
    sonos = speakerBox.Item(sonosNum)
    sonos.Connect()
    airfoilapp = None
    pythoncom.CoUninitialize()


def disconnectSonos():
    pythoncom.CoInitialize()
    airfoilapp = Dispatch("RogueAmoeba.Airfoil")
    speakerBox = airfoilapp.GetSpeakers()
    sonosNum = 4
    for i in range(0, speakerBox.Count()):
        speaker = speakerBox.Item(i)
        if speaker.Name() == "Computer":
            sonosNum = i
    sonos = speakerBox.Item(sonosNum)
    sonos.Disconnect()
    airfoilapp = None
    pythoncom.CoUninitialize()

if __name__ == "__main__":
    connectSonos()