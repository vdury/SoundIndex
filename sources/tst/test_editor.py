#!/usr/bin/env python
from StringIO import StringIO
import wx
import wx.html
import wx.richtext

class TextFormatToolBar(wx.ToolBar):
    def __init__(self, *args, **kwds):
        self.text_ctrl = kwds.pop('text_ctrl')
        kwds["style"] = wx.TB_FLAT|wx.TB_3DBUTTONS
        wx.ToolBar.__init__(self, *args, **kwds)
        self.AddLabelTool(wx.ID_CUT, "Cut", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "Cut selection", "")
        self.AddLabelTool(wx.ID_COPY, "Copy", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddLabelTool(wx.ID_PASTE, "Paste", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddSeparator()
        self.AddLabelTool(wx.ID_UNDO, "Undo", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddLabelTool(wx.ID_REDO, "Redo", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddSeparator()
        self.AddLabelTool(wx.ID_BOLD, "Bold", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddLabelTool(wx.ID_ITALIC, "Italic", wx.Bitmap("bitmaps/player_prev.png", wx.BITMAP_TYPE_ANY), 
wx.NullBitmap, wx.ITEM_NORMAL, "", "")
        self.AddLabelTool(wx.ID_UNDERLINE, "Underline", wx.Bitmap("bitmaps/player_prev.png", 
wx.BITMAP_TYPE_ANY), wx.NullBitmap, wx.ITEM_NORMAL, "", "")

        self.Realize()

        self.Bind(wx.EVT_TOOL, self.handle_bold, id=wx.ID_BOLD)
        self.Bind(wx.EVT_TOOL, self.handle_italic, id=wx.ID_ITALIC)
        self.Bind(wx.EVT_TOOL, self.handle_underline, id=wx.ID_UNDERLINE)
        self.Bind(wx.EVT_TOOL, self.handle_paste, id=wx.ID_PASTE)
        self.Bind(wx.EVT_TOOL, self.handle_copy, id=wx.ID_COPY)
        self.Bind(wx.EVT_TOOL, self.handle_cut, id=wx.ID_CUT)
        self.Bind(wx.EVT_TOOL, self.handle_undo, id=wx.ID_UNDO)
        self.Bind(wx.EVT_TOOL, self.handle_redo, id=wx.ID_REDO)

    def handle_bold(self, event):
        self.text_ctrl.ApplyBoldToSelection()

    def handle_italic(self, event):
        self.text_ctrl.ApplyItalicToSelection()

    def handle_underline(self, event):
        self.text_ctrl.ApplyUnderlineToSelection()

    def handle_paste(self, event):
        self.text_ctrl.Paste()
        
    def handle_copy(self, event):
        self.text_ctrl.Copy()
        
    def handle_cut(self, event):
        self.text_ctrl.Cut()
        
    def handle_undo(self, event):
        self.text_ctrl.Undo()
        
    def handle_redo(self, event):
        self.text_ctrl.Redo()


class TopFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, *args, **kwargs)
        self.Freeze()
        sizer = wx.BoxSizer(wx.VERTICAL)
        rt = wx.richtext.RichTextCtrl(self, -1)
        toolbar = TextFormatToolBar(self, text_ctrl=rt)
        rt.SetMinSize((300,200))
        htmlwindow = wx.html.HtmlWindow(self)
        htmlwindow.SetMinSize((300,200))
        save_button = wx.Button(self, label="Save")
        load_button = wx.Button(self, label="Load")
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        btn_sizer.Add(load_button, 0, wx.EXPAND|wx.ALL, 6)
        btn_sizer.Add(save_button, 0, wx.EXPAND|wx.ALL, 6)
        self.Bind(wx.EVT_BUTTON, self.handle_save, save_button)
        self.Bind(wx.EVT_BUTTON, self.handle_load, load_button)
        sizer.Add(toolbar, 0, wx.EXPAND|wx.ALL, 6)
        sizer.Add(rt, 1, wx.EXPAND|wx.ALL, 6)
        sizer.Add(htmlwindow, 1, wx.EXPAND|wx.ALL, 6)
        sizer.Add(btn_sizer)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.Thaw()
        self.rt = rt
        self.htmlwindow = htmlwindow
        
    def handle_save(self, event):
        out = StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.rt.GetBuffer()
        handler.SaveStream(buffer, out)
        out.seek(0)
        self.content = out.read()
        
    def handle_load(self, event):
        out = StringIO()
        handler = wx.richtext.RichTextXMLHandler()
        buffer = self.rt.GetBuffer()
        buffer.AddHandler(handler)
        out.write(self.content)
        out.seek(0)
        handler.LoadStream(buffer, out)
        self.rt.Refresh()
        
        cio = StringIO()
        cio.write(self.content)
        cio.seek(0)
        cout = StringIO()
        
        xmlhandler = wx.richtext.RichTextXMLHandler()
        htmlhandler = wx.richtext.RichTextHTMLHandler()
        newbuff = wx.richtext.RichTextBuffer()
        newbuff.AddHandler(htmlhandler)
        
        xmlhandler.LoadStream(newbuff, cio) #load xml into buffer
        newbuff.SaveStream(cout, wx.richtext.RICHTEXT_TYPE_HTML)
        cout.seek(0)
        self.htmlwindow.SetPage(cout.read())


class MyApp(wx.App):

    def OnInit(self):
        wx.InitAllImageHandlers()
        frame = TopFrame(None, - 1, "")
        self.SetTopWindow(frame)
        
        frame.Show()
        return 1
    

def start():
    app = MyApp(0)
    app.MainLoop()
    
if __name__ == "__main__":
    start()
