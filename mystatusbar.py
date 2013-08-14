import time
import wx

class CustomStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(2)
	self.SetStatusWidths([-5,200])

        self.SetStatusText("Petri net simulation", 0)
        self.SetStatusText("Developed at UIUC", 1)

        # This was the original checkbox for debug
        # self.cb = wxCheckBox(self, ID_DEBUG, "Debug mode")
        # EVT_CHECKBOX(self, ID_DEBUG, parent.ToggleDebug)
        # self.cb.SetValue(parent.debug)
        # set the initial position of the checkbox
        # self.Reposition()

        # start our timer
        # self.timer = wx.PyTimer(self.Notify)
        # self.timer.Start(1000)
        # self.Notify()


#    # Time-out handler
#    def Notify(self):
#        t = time.localtime(time.time())
#        st = time.strftime("%I:%M:%S %p  %b %d, %Y", t)
#        self.SetStatusText(st, 1)
