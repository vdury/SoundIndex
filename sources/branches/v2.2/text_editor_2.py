# Get the GUI stuff
import wx
import wx.richtext
from StringIO import StringIO
# We're going to be handling files and directories
import os
import amara
from amara import tree
from amara import bindery
from wx.lib.pubsub import pub
from amara.writers import lookup
import wx.lib.docview
import wx.lib.pydocview
import wx.richtext as rt
import wx.stc
import re
# Set up some button numbers for the menu

class TextPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.control = TextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_RICH2)

        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control,1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        # Show it !!!
        self.Show(1)

        self.dirname = ''


        pub.subscribe(self.myListener, "panelListener")

    #----------------------------------------------------------------------
    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        print "Received the following message: " + message
        if arg2:
            print "Received another arguments: " + str(arg2)
        #self.addAudioSample(message, arg2)

    #def getSectionNumber(self, i):
        #k=0
        #res = -1
        #print i
        #size = len(self.Sentences)
        #while k< size:
        #    print k, self.Sentences[k]
        #    if i < self.Sentences[k]:
        #        if k != 0:
        #            res = k-1
        #        k = size
        #    k=k+1
        #if i > self.Sentences[size-1]:
        #    res = size-1
        #print res
        #return res
        #
    #def SimplifyAudioLimit(self, num):
    #    return str(round(float(num), 4))
    #
    #def addAudioSample(self, start, end):
        #i = self.control.GetInsertionPoint()
    #    lineNum = self.control.GetRange( 0, self.control.GetInsertionPoint() ).split("\n")
        #lineText = self.control.GetLineText(lineNum)
    #    i = len(lineNum) - 1
    #    section = self.getSectionNumber(i)
    #    self.doc.TEXT.S[section].AUDIO.start = self.SimplifyAudioLimit(start)
    #    self.doc.TEXT.S[section].AUDIO.end = self.SimplifyAudioLimit(end)
        #self.doc.xml_write(XML_W)
    #    self.control.SetValue(self.doc.xml_encode(self.XML_W))
    #    self.control.SetInsertionPoint(i)
        #self.control.SetValue(self.doc.xml_children[0])
        #self.control.SetInsertionPoint(i)
        #self.control.WriteText("<AUDIO start=\""+str(start)+"\" end=\""+str(end)+"\"/>")

    def scanXMLDocument(self, path):
        i=0
        
        self.XML_W = lookup("xml")
        self.doc = bindery.parse(path)

        #self.control.BeginTextColour((255,0,0))
        self.control.SetValue(self.doc.xml_encode(self.XML_W))
        self.Sentences = []

        for i in range (0, self.control.GetNumberOfLines()):
            Line = self.control.GetLineText(i)
            Line.strip()

        #To remove spaces in the line
        Line = re.sub(r"\s+", "", Line, flags=re.UNICODE)

        if (Line[0]=='<') & (Line[1]=='S') & (Line[2]=='i'):
            """
            Everytime we encouter '<Si' at the beginning
            of a line, we append the Sentence Tab with
            the line number
            """
            self.Sentences.append(i)

    #def layout(self):
    #    for i in range (0, self.control.GetNumberOfLines()):
    #        Line = self.control.GetLineText(i)
    #        count = self.control.GetLineLength(i)
    #        for j in range (0, len(Line)):
    #            if Line[j] = "<":
    #                k = j
    #                while Line[j] != "\s":
    #                    j = j+1
    #                    self.control.SetSelection(k, j)

    #def forceDefaultStyle(self, event):
    #    hEventObject = event.GetEventObject()
        #hEventObject.SetStyle(0, len(self.control.GetValue()), wx.TextAttr(wx.RED))
        #hEventObject.SetFont(self.hFontLabel)


    def OnOpen(self,e):
        # In this case, the dialog is created within the method becausea
        # the directory name, etc, may be changed during the running of the
        # application. In theory, you could create one earlier, store it in
        # your frame object and change it when it was called to reflect
        # current parameters / values
        wildcard = "XML (*.xml)|*.xml|"    \
                   "All Files  |*.*"

        dlg = wx.FileDialog(self, "Choose a file",
                            defaultDir=self.dirname,
                            defaultFile="",
                            wildcard = wildcard,
                            style= wx.OPEN)

        if dlg.ShowModal() == wx.ID_OK:
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()

            # Open the file, read the contents and set them into
            # the text edit window
            #filehandle=open(os.path.join(self.dirname, self.filename),'r')


            # Report on name of latest file read
            #self.SetTitle("Editing ... "+self.filename)
            # Later - could be enhanced to include a "changed" flag whenever
            # the text is actually changed, could also be altered on "save" ...
        path = dlg.GetPath()
        dlg.Destroy()
        fileName, fileExtension = os.path.splitext(path)
        if fileExtension == '.xml':
            self.scanXMLDocument(path)



    #def OnSave(self,e):
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
    #    dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", \
    #            wx.SAVE | wx.OVERWRITE_PROMPT)
    #    if dlg.ShowModal() == wx.ID_OK:
    #        # Grab the content to be saved
    #        itcontains = self.control.GetValue()

            # Open the file for write, write, close
    #        self.filename=dlg.GetFilename()
    #        self.dirname=dlg.GetDirectory()
    #        filehandle=open(os.path.join(self.dirname, self.filename),'w')
    #        filehandle.write(itcontains)
    #        filehandle.close()
        # Get rid of the dialog to keep things tidy
    #    dlg.Destroy()

    def onClose(self):
        self.Destroy()

class TextCtrl(wx.stc.StyledTextCtrl):

    def __init__(self, parent, id=-1, style=wx.NO_FULL_REPAINT_ON_RESIZE):
        wx.stc.StyledTextCtrl.__init__(self, parent, id, style=style)

        self.SetLexer(wx.stc.STC_LEX_XML)
        self.SetProperty("fold.html", "1")

        #if isinstance(parent, wx.gizmos.DynamicSashWindow):
        #    self._dynSash = parent
        #    self.SetupDSScrollBars()
        #    self.Bind(wx.gizmos.EVT_DYNAMIC_SASH_SPLIT, self.OnDSSplit)
        #    self.Bind(wx.gizmos.EVT_DYNAMIC_SASH_UNIFY, self.OnDSUnify)

        self._font = None
        self._fontColor = None

        self.SetVisiblePolicy(wx.stc.STC_VISIBLE_STRICT,1)

        self.CmdKeyClear(wx.stc.STC_KEY_ADD, wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyClear(wx.stc.STC_KEY_SUBTRACT, wx.stc.STC_SCMOD_CTRL)
        self.CmdKeyAssign(wx.stc.STC_KEY_PRIOR, wx.stc.STC_SCMOD_CTRL, wx.stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(wx.stc.STC_KEY_NEXT, wx.stc.STC_SCMOD_CTRL, wx.stc.STC_CMD_ZOOMOUT)
        self.Bind(wx.stc.EVT_STC_ZOOM, self.OnUpdateLineNumberMarginWidth)  # auto update line num width on zoom
        wx.EVT_KEY_DOWN(self, self.OnKeyPressed)
        wx.EVT_KILL_FOCUS(self, self.OnKillFocus)
        wx.EVT_SET_FOCUS(self, self.OnFocus)
        self.SetMargins(0,0)

        self.SetUseTabs(0)
        self.SetTabWidth(4)
        self.SetIndent(4)

        self.SetViewWhiteSpace(False)
        self.SetEOLMode(wx.stc.STC_EOL_LF)
        self.SetEdgeMode(wx.stc.STC_EDGE_NONE)
        self.SetEdgeColumn(78)

        self.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, self.EstimatedLineNumberMarginWidth())
        self.UpdateStyles()

        self.SetCaretForeground("BLACK")

        self.SetViewDefaults()
        font, color = self.GetFontAndColorFromConfig()
        self.SetFont(font)
        self.SetFontColor(color)
        self.MarkerDefineDefault()

        # for multisash initialization
        #if isinstance(parent, wx.lib.multisash.MultiClient):
        #    while parent.GetParent():
        #        parent = parent.GetParent()
        #        if hasattr(parent, "GetView"):
        #            break
        #    if hasattr(parent, "GetView"):
        #        textEditor = parent.GetView()._textEditor
        #        if textEditor:
        #            doc = textEditor.GetDocPointer()
        #            if doc:
        #                self.SetDocPointer(doc)


    def OnFocus(self, event):
        # wxBug: On Mac, the STC control may fire a focus/kill focus event
        # on shutdown even if the control is in an invalid state. So check
        # before handling the event.
        if self.IsBeingDeleted():
            return

        self.SetSelBackground(1, "BLUE")
        self.SetSelForeground(1, "WHITE")
        if hasattr(self, "_dynSash"):
            self._dynSash._view.SetCtrl(self)
        event.Skip()


    def OnKillFocus(self, event):
        # wxBug: On Mac, the STC control may fire a focus/kill focus event
        # on shutdown even if the control is in an invalid state. So check
        # before handling the event.
        if self.IsBeingDeleted():
            return
        self.SetSelBackground(0, "BLUE")
        self.SetSelForeground(0, "WHITE")
        self.SetSelBackground(1, "#C0C0C0")
        # Don't set foreground color, use syntax highlighted default colors.
        event.Skip()


    def SetViewDefaults(self, configPrefix="Text", hasWordWrap=True, hasTabs=False, hasFolding=False):
        config = wx.ConfigBase_Get()
        self.SetViewWhiteSpace(config.ReadInt(configPrefix + "EditorViewWhitespace", False))
        self.SetViewEOL(config.ReadInt(configPrefix + "EditorViewEOL", False))
        self.SetIndentationGuides(config.ReadInt(configPrefix + "EditorViewIndentationGuides", False))
        self.SetViewRightEdge(config.ReadInt(configPrefix + "EditorViewRightEdge", False))
        self.SetViewLineNumbers(config.ReadInt(configPrefix + "EditorViewLineNumbers", True))
        if hasFolding:
            self.SetViewFolding(config.ReadInt(configPrefix + "EditorViewFolding", True))
        if hasWordWrap:
            self.SetWordWrap(config.ReadInt(configPrefix + "EditorWordWrap", False))
        if hasTabs:  # These methods do not exist in STCTextEditor and are meant for subclasses
            self.SetUseTabs(config.ReadInt(configPrefix + "EditorUseTabs", False))
            self.SetIndent(config.ReadInt(configPrefix + "EditorIndentWidth", 4))
            self.SetTabWidth(config.ReadInt(configPrefix + "EditorIndentWidth", 4))
        else:
            self.SetUseTabs(True)
            self.SetIndent(4)
            self.SetTabWidth(4)


    def GetDefaultFont(self):
        """ Subclasses should override this """
        return wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL)


    def GetDefaultColor(self):
        """ Subclasses should override this """
        return wx.BLACK


    def GetFontAndColorFromConfig(self, configPrefix = "Text"):
        font = self.GetDefaultFont()
        config = wx.ConfigBase_Get()
        fontData = config.Read(configPrefix + "EditorFont", "")
        if fontData:
            nativeFont = wx.NativeFontInfo()
            nativeFont.FromString(fontData)
            font.SetNativeFontInfo(nativeFont)
        color = self.GetDefaultColor()
        colorData = config.Read(configPrefix + "EditorColor", "")
        if colorData:
            red = int("0x" + colorData[0:2], 16)
            green = int("0x" + colorData[2:4], 16)
            blue = int("0x" + colorData[4:6], 16)
            color = wx.Colour(red, green, blue)
        return font, color


    def GetFont(self):
        return self._font


    def SetFont(self, font):
        self._font = font
        self.StyleSetFont(wx.stc.STC_STYLE_DEFAULT, self._font)


    def GetFontColor(self):
        return self._fontColor


    def SetFontColor(self, fontColor = wx.BLACK):
        self._fontColor = fontColor
        self.StyleSetForeground(wx.stc.STC_STYLE_DEFAULT, "#%02x%02x%02x" % (self._fontColor.Red(), self._fontColor.Green(), self._fontColor.Blue()))


    def UpdateStyles(self):
        self.StyleClearAll()

        if not self.GetFont():
            return

        print "bla"
        faces = { 'font' : self.GetFont().GetFaceName(),
                  'size' : self.GetFont().GetPointSize(),
                  'size2': self.GetFont().GetPointSize() - 2,
                  'color' : "%02x%02x%02x" % (self.GetFontColor().Red(), self.GetFontColor().Green(), self.GetFontColor().Blue())
                  }

        # White space
        self.StyleSetSpec(wx.stc.STC_H_DEFAULT, "face:%(font)s,fore:#000000,face:%(font)s,size:%(size)d" % faces)
        # Comment
        self.StyleSetSpec(wx.stc.STC_H_COMMENT, "face:%(font)s,fore:#007F00,italic,face:%(font)s,size:%(size)d" % faces)
        # Number
        self.StyleSetSpec(wx.stc.STC_H_NUMBER, "face:%(font)s,fore:#007F7F,size:%(size)d" % faces)
        # String
        self.StyleSetSpec(wx.stc.STC_H_SINGLESTRING, "face:%(font)s,fore:#7F007F,face:%(font)s,size:%(size)d" % faces)
        self.StyleSetSpec(wx.stc.STC_H_DOUBLESTRING, "face:%(font)s,fore:#7F007F,face:%(font)s,size:%(size)d" % faces)
        # Tag
        self.StyleSetSpec(wx.stc.STC_H_TAG, "face:%(font)s,fore:#00007F,bold,size:%(size)d" % faces)
        # Attributes
        self.StyleSetSpec(wx.stc.STC_H_ATTRIBUTE, "face:%(font)s,fore:#007F7F,bold,size:%(size)d" % faces)
        return


    def EstimatedLineNumberMarginWidth(self):
        MARGIN = 4
        baseNumbers = "000"
        lineNum = self.GetLineCount()
        lineNum = lineNum/100
        while lineNum >= 10:
            lineNum = lineNum/10
            baseNumbers = baseNumbers + "0"

        return self.TextWidth(wx.stc.STC_STYLE_LINENUMBER, baseNumbers) + MARGIN


    def OnUpdateLineNumberMarginWidth(self, event):
        self.UpdateLineNumberMarginWidth()


    def UpdateLineNumberMarginWidth(self):
        if self.GetViewLineNumbers():
            self.SetMarginWidth(1, self.EstimatedLineNumberMarginWidth())

    def MarkerDefineDefault(self):
        """ This must be called after the textcontrol is instantiated """
        #self.MarkerDefine(TextView.MARKER_NUM, wx.stc.STC_MARK_ROUNDRECT, wx.BLACK, wx.BLUE)
        pass

    def OnClear(self):
        # Used when Delete key is hit.
        sel = self.GetSelection()

        # Delete the selection or if no selection, the character after the caret.
        if sel[0] == sel[1]:
            self.SetSelection(sel[0], sel[0] + 1)
        else:
            # remove any folded lines also.
            startLine = self.LineFromPosition(sel[0])
            endLine = self.LineFromPosition(sel[1])
            endLineStart = self.PositionFromLine(endLine)
            if startLine != endLine and sel[1] - endLineStart == 0:
                while not self.GetLineVisible(endLine):
                    endLine += 1
                self.SetSelectionEnd(self.PositionFromLine(endLine))

        self.Clear()


    def OnPaste(self):
        # replace any folded lines also.
        sel = self.GetSelection()
        startLine = self.LineFromPosition(sel[0])
        endLine = self.LineFromPosition(sel[1])
        endLineStart = self.PositionFromLine(endLine)
        if startLine != endLine and sel[1] - endLineStart == 0:
            while not self.GetLineVisible(endLine):
                endLine += 1
            self.SetSelectionEnd(self.PositionFromLine(endLine))

        self.Paste()


    def OnKeyPressed(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_NUMPAD_ADD:  #wxBug: For whatever reason, the key accelerators for numpad add and subtract with modifiers are not working so have to trap them here
            if event.ControlDown():
                self.ToggleFoldAll(expand = True, topLevelOnly = True)
            elif event.ShiftDown():
                self.ToggleFoldAll(expand = True)
            else:
                self.ToggleFold(self.GetCurrentLine())
        elif key == wx.WXK_NUMPAD_SUBTRACT:
            if event.ControlDown():
                self.ToggleFoldAll(expand = False, topLevelOnly = True)
            elif event.ShiftDown():
                self.ToggleFoldAll(expand = False)
            else:
                self.ToggleFold(self.GetCurrentLine())
        else:
            event.Skip()


    #----------------------------------------------------------------------------
    # View Text methods
    #----------------------------------------------------------------------------

    def GetViewRightEdge(self):
        return self.GetEdgeMode() != wx.stc.STC_EDGE_NONE


    def SetViewRightEdge(self, viewRightEdge):
        if viewRightEdge:
            self.SetEdgeMode(wx.stc.STC_EDGE_LINE)
        else:
            self.SetEdgeMode(wx.stc.STC_EDGE_NONE)


    def GetViewLineNumbers(self):
        return self.GetMarginWidth(1) > 0


    def SetViewLineNumbers(self, viewLineNumbers = True):
        if viewLineNumbers:
            self.SetMarginWidth(1, self.EstimatedLineNumberMarginWidth())
        else:
            self.SetMarginWidth(1, 0)


    def GetViewFolding(self):
        return self.GetMarginWidth(2) > 0


    def SetViewFolding(self, viewFolding = True):
        if viewFolding:
            self.SetMarginWidth(2, 12)
        else:
            self.SetMarginWidth(2, 0)


    def CanWordWrap(self):
        return True


    def GetWordWrap(self):
        return self.GetWrapMode() == wx.stc.STC_WRAP_WORD


    def SetWordWrap(self, wordWrap):
        if wordWrap:
            self.SetWrapMode(wx.stc.STC_WRAP_WORD)
        else:
            self.SetWrapMode(wx.stc.STC_WRAP_NONE)


    #----------------------------------------------------------------------------
    # DynamicSashWindow methods
    #----------------------------------------------------------------------------

    def SetupDSScrollBars(self):
        # hook the scrollbars provided by the wxDynamicSashWindow
        # to this view
        v_bar = self._dynSash.GetVScrollBar(self)
        h_bar = self._dynSash.GetHScrollBar(self)
        v_bar.Bind(wx.EVT_SCROLL, self.OnDSSBScroll)
        h_bar.Bind(wx.EVT_SCROLL, self.OnDSSBScroll)
        v_bar.Bind(wx.EVT_SET_FOCUS, self.OnDSSBFocus)
        h_bar.Bind(wx.EVT_SET_FOCUS, self.OnDSSBFocus)

        # And set the wxStyledText to use these scrollbars instead
        # of its built-in ones.
        self.SetVScrollBar(v_bar)
        self.SetHScrollBar(h_bar)


    def OnDSSplit(self, evt):
        newCtrl = self._dynSash._view.GetCtrlClass()(self._dynSash, -1, style=wx.NO_BORDER)
        newCtrl.SetDocPointer(self.GetDocPointer())     # use the same document
        self.SetupDSScrollBars()
        if self == self._dynSash._view.GetCtrl():  # originally had focus
            wx.CallAfter(self.SetFocus)  # do this to set colors correctly.  wxBug:  for some reason, if we don't do a CallAfter, it immediately calls OnKillFocus right after our SetFocus.


    def OnDSUnify(self, evt):
        self.SetupDSScrollBars()
        self.SetFocus()  # do this to set colors correctly


    def OnDSSBScroll(self, evt):
        # redirect the scroll events from the _dynSash's scrollbars to the STC
        self.GetEventHandler().ProcessEvent(evt)


    def OnDSSBFocus(self, evt):
        # when the scrollbar gets the focus move it back to the STC
        self.SetFocus()


    def DSProcessEvent(self, event):
        # wxHack: Needed for customized right mouse click menu items.
        if hasattr(self, "_dynSash"):
            if event.GetId() == wx.ID_SELECTALL:
                # force focus so that select all occurs in the window user right clicked on.
                self.SetFocus()

            return self._dynSash._view.ProcessEvent(event)
        return False


    def DSProcessUpdateUIEvent(self, event):
        # wxHack: Needed for customized right mouse click menu items.
        if hasattr(self, "_dynSash"):
            id = event.GetId()
            if (id == wx.ID_SELECTALL  # allow select all even in non-active window, then force focus to it, see above ProcessEvent
            or id == wx.ID_UNDO
            or id == wx.ID_REDO):
                pass  # allow these actions even in non-active window
            else:  # disallow events in non-active windows.  Cut/Copy/Paste/Delete is too confusing user experience.
                if self._dynSash._view.GetCtrl() != self:
                     event.Enable(False)
                     return True

            return self._dynSash._view.ProcessUpdateUIEvent(event)
        return False
