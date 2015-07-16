import wx
import wx.stc

import os

from amara import bindery

def create(parent):
    return Frame1(parent)

[wxID_FRAME1, wxID_FRAME1STYLEDTEXTCTRL1,
] = [wx.NewId() for _init_ctrls in range(2)]

class Frame1(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(504, 196), size=wx.Size(847, 592),
              style=wx.DEFAULT_FRAME_STYLE, title='Frame1')
        self.SetClientSize(wx.Size(831, 556))

        self.styledTextCtrl1 = wx.stc.StyledTextCtrl(id=wxID_FRAME1STYLEDTEXTCTRL1,
              name='styledTextCtrl1', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(831, 556), style=0)
##        self.styledTextCtrl1.SetLexer(wx.stc.STC_LEX_XML)

    def __init__(self, parent):
        self._init_ctrls(parent)
        # replace the file name below
        fileName = 'Musica/crdo-NRU_F4_10_AGRICULTURAL_ACTIVITIES.xml'
        file = os.path.join(os.getcwd(), fileName)
        self.xmlDoc = bindery.parse(file)
       
        self.styledTextCtrl1.AddTextUTF8(self.xmlDoc.xml(indent=u'yes'))

if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop() 
