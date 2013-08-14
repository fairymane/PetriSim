#!/usr/bin/env python
#from DrawingBoard import *
import wx
from GUI import *
#from subnet import *

class PetriNet(wx.App):
    def OnInit(self):
        frame = MyFrame(None, -1, "PetriSim!")
        frame.Show(True)
        self.SetTopWindow(frame)
        return True
        
if __name__ == "__main__":
    app = PetriNet(0)
    app.MainLoop()

