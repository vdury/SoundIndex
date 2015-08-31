#! /usr/bin/env python

from player_skeleton2_1 import *
#dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')
mainSizer = wx.BoxSizer(wx.VERTICAL)

sys.path.append("./")
from text_editor_2 import *

from wx.lib.wordwrap import wordwrap

#sys.path.append(os.path.abspath(__file__))


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

        width, height = wx.DisplaySize()

        topSplitter.SplitHorizontally(self.panelOne, self.panelTwo)
        topSplitter.SetSashGravity(0.67)

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

        viewmenu = wx.Menu()
        font_item = viewmenu.Append(wx.NewId(), "&Change the XML font", "Xml Font")
        readonly_item = viewmenu.Append(wx.NewId(), "&Set the XML to Read Only", "ReadOnly", wx.ITEM_CHECK)

        helpmenu = wx.Menu()
        about_item = helpmenu.Append(wx.NewId(), '&About', 'About')
        help_item = helpmenu.Append(wx.NewId(), '&Help', 'Help')
        menubar.Append(savemenu, "&Save")
        menubar.Append(viewmenu, '&View')
        menubar.Append(helpmenu, '&Help')

        self.frame.Bind(wx.EVT_MENU, self.panelOne.FontMenu, font_item)
        self.frame.Bind(wx.EVT_MENU, self.panelOne.onReadOnly, readonly_item)
        self.frame.Bind(wx.EVT_MENU, self.onAbout, about_item)
        self.frame.Bind(wx.EVT_MENU, self.onHelp, help_item)
        self.frame.SetMenuBar(menubar)

    def onHelp(self, event):
        dlg = HelpDialog(self, -1, 'Help')
        dlg.ShowModal()


    def onAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = "SoundIndex"
        info.Version = "2.0.1"
        info.Description = wordwrap(
            "This is an application that helps indexing sound "
            "from an audio file to an xml file",
            350, wx.ClientDC(self))
        info.Developers = ["Victor Dury"]
        info.License = wordwrap("Completely and totally open source!", 500,
                                wx.ClientDC(self))
        # Show the wx.AboutBox
        wx.AboutBox(info)


    def onClose(self, event):
        #rint "close"
        #ialog = wx.MessageDialog(self, message = "Are you sure you want to quit?", caption = "Caption", style = wx.YES_NO, pos = wx.DefaultPosition)
        #esponse = dialog.ShowModal()
        #elf.panelOne.onClose()
        #self.panelTwo.onClose()
        self.panelTwo.timer.Stop()
        self.frame.Destroy()
        sys.exit()


class HelpDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(700,700), style = wx.DEFAULT_DIALOG_STYLE)
        nb = wx.Notebook(self, -1)

        PlayerPage = wx.Panel(nb, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(PlayerPage, -1, "This is help for the player section"), 0, wx.ALIGN_CENTER|wx.ALL, 10)
        sizer.Add(wx.StaticText(PlayerPage, -1, "To open an audio file, go into the \"Open\" menu tab,\nAnd click on the \"Open an Audio file\" item. \nThen browse into your folders and open the audio file you want. \nAttention: .mp3 audio files are not supported. \nIf you want to open a .mp3 file, you will have to transform it into a .wav file first."), 0, wx.ALIGN_LEFT|wx.ALL, 10)
        sizer.Add(wx.StaticText(PlayerPage, -1, "Once loaded, you can play the audio file by pressing the triangle button.\nYou can pause using the pause button, and stop using the stop button.\nYou can zoom in and out using the two magnifying glasses (+ for zoom in, - for zoom out)\nUsing the \"Set Zoom button\", you can adjust how many seconds you want to display at once on the screen.\nIf an Xml file is loaded, the previous and next symboled buttons will highlight in the music player the different sentences.\nThe select button will highlight the time frames corresponding to the the sentence in which your cursor is positionned (in the XML part)\nThe \"clear selection\" button will make the marker disappear.\nThe Sync button only works if a marker is drawn. It will take into account the time frame you have selected with your marker,\nAnd change the Xml Audio Element for the sentence where your cursor is positionned.\nThe \"Sync And Next\" button acts like a \"Sync\" Button.\n Then, it highlights the next sentence (if there is an audio element for the next sentence in the Xml)."), 0, wx.ALIGN_LEFT|wx.ALL, 10)
        sizer.Add(wx.StaticText(PlayerPage, -1, "Once you have the audio loaded, if you click on the sound wave, you will draw a marker. \nJust use your mouse to calibrate the time frame you want.\nOnce the marker is set, you can press play to listen to the time frame only.\nYou can use CTRL+Right Click in order to only change the ending of the time frame you selected."), 0, wx.ALIGN_LEFT|wx.ALL, 10)
        PlayerPage.SetSizer(sizer)
        nb.AddPage(PlayerPage, "Audio Player")

        XmlPage = wx.Panel(nb, -1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(XmlPage, -1, "This is help for the XML section"), 0, wx.ALIGN_CENTER|wx.ALL, 10)
        sizer.Add(wx.StaticText(XmlPage, -1, "To open a Xml file, go into the \"Open\" menu tab,\nAnd click on the \"Open an XML file\" item.\nNote that, if you have already opened an audio file, the program will try to open a Xml file which shares the same name, and is located in the same directory. "), 0, wx.ALIGN_LEFT|wx.ALL, 10)
        sizer.Add(wx.StaticText(XmlPage, -1, "You can change the font of the Xml if you go into \"View\" menu tab,\nAnd click on the \"Change the Xml Font\". There, you will be able to change the font and color of any part of the xml.\nNote that editing the Xml manually is permitted, but if the xml is not valid anymore, you won't be able to save or sync anything.\nTo be sure to not make any mistakes with the xml, you can tick the \"Set the Xml to Read Only\" option, in the \"View\" menu tab"), 0, wx.ALIGN_LEFT|wx.ALL, 10)
        sizer.Add(wx.StaticText(XmlPage, -1, "To save the Xml document, just go in the \"Save\" menu item, and click \"Save the Xml Document\"."), 0, wx.ALIGN_LEFT|wx.ALL, 10)

        XmlPage.SetSizer(sizer)
        nb.AddPage(XmlPage, "XML Text Editor")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(nb, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        btn = wx.Button(self, wx.ID_OK)
        sizer.Add(btn, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        self.SetSizer(sizer)
        self.Layout()
        self.Fit()
        #self.Show()
#######################################################################

class MainFrame(wx.Frame):
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "SoundIndex_2.0")
        panel = MainPanel(self)
        self.Maximize(True)
        self.icon = wx.Icon("myIcon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)

#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
