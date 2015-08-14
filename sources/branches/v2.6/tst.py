# wxPython example:
# How to convert mouse clicks to the text clicked on
#
# Author: Brian Okken
#

import wx
import wx.stc

class TextCtrlFrame(wx.Frame):

    def __init__(self, parent):
        wx.Frame.__init__(self, parent)
        self.text = wx.stc.StyledTextCtrl.__init__(self, -1, "", pos= wx.DefaultPosition, size = wx.DefaultSize, style=wx.TE_MULTILINE)
        self.text.Bind(wx.EVT_LEFT_DCLICK, self.on_left)

    def on_left(self, evt):
        position = evt.GetPosition()
        (res,hitpos) = self.text.HitTestPos(position)
        (col,line) = self.text.PositionToXY(hitpos)
        the_line = self.text.GetLineText(line)
        print("on_left:%s" % the_line)

if __name__ == "__main__":
    APP = wx.App(False)
    FRAME = TextCtrlFrame(None)
    FRAME.Show()
    APP.MainLoop()
