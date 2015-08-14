#! /usr/bin/env python

from player_skeleton2_1 import *
dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')
mainSizer = wx.BoxSizer(wx.VERTICAL)

sys.path.append("./")
from text_editor_2 import *


sys.path.append(os.path.abspath(__file__))


######################################################################"
class MainPanel(wx.Panel):
    #------------------------------------------------------------------
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.frame = parent
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.onClose)
        topSplitter = wx.SplitterWindow(self)
        vSplitter = wx.SplitterWindow(topSplitter)

        self.panelOne = TextPanel(topSplitter)
        self.panelTwo = MediaPanel(topSplitter)
        #self.panelThree = RandomPanel(vSplitter, "red")

        #vSplitter.SplitVertically(self.panelOne, self.panelThree)
        #vSplitter.SetSashGravity(0.75)


        topSplitter.SplitHorizontally(self.panelOne, self.panelTwo)
        topSplitter.SetSashGravity(0.58)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(topSplitter, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.createMenu()


    def createMenu(self):
        menubar = wx.MenuBar()

        openmenu = wx.Menu()
        open_audio_menu_item = openmenu.Append(wx.NewId(), "&Open an Audio File", "Open an Audio file")
        self.frame.Bind(wx.EVT_MENU, self.panelTwo.onBrowse, open_audio_menu_item)
        open_text_menu_item = openmenu.Append(wx.NewId(), "&Open an XML file", "Open an XML file")
        menubar.Append(openmenu, '&Open')
        self.frame.Bind(wx.EVT_MENU, self.panelOne.OnBrowse, open_text_menu_item)


        savemenu = wx.Menu()
        save_text_menu_item = savemenu.Append(wx.NewId(), "&Save the XML file", "Saveit")
        self.frame.Bind(wx.EVT_MENU, self.panelOne.OnSave, save_text_menu_item)
        menubar.Append(savemenu, "&Save")


        self.frame.SetMenuBar(menubar)

    def onClose(self, event):
        dialog = wx.MessageDialog(self, message = "Are you sure you want to quit?", caption = "Caption", style = wx.YES_NO, pos = wx.DefaultPosition)
        response = dialog.ShowModal()
        self.panelOne.onClose()
        self.panelTwo.onClose()


#######################################################################

class MainFrame(wx.Frame):
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "SoundIndex_2.0")
        panel = MainPanel(self)
        self.Maximize(True)

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
