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
import wx.richtext as rt
import re
# Set up some button numbers for the menu

class TextPanel(wx.Panel):
    def __init__(self,parent):
        # based on a frame, so set up the frame
        wx.Panel.__init__(self,parent)

        self.control = rt.RichTextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_RICH2 )
        self.control.Bind(wx.EVT_TEXT, self.forceDefaultStyle)
        self.hFontLabel = wx.ITALIC

        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control,1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.sizer.Fit(self)

        # Show it !!!
        self.Show(1)

        self.dirname = ''
        pub.subscribe(self.myListener, "panelListener")
        #self.AddRTCHandlers()


    #def AddRTCHandlers(self):
        # make sure we haven't already added them.
        #if rt.RichTextBuffer.FindHandlerByType(rt.RICHTEXT_TYPE_HTML) is not None:
            #return

        # This would normally go in your app's OnInit method.  I'm
        # not sure why these file handlers are not loaded by
        # default by the C++ richtext code, I guess it's so you
        # can change the name or extension if you wanted...
        #rt.RichTextBuffer.AddHandler(rt.RichTextHTMLHandler())
        #rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler())

        # ...like this
        #rt.RichTextBuffer.AddHandler(rt.RichTextXMLHandler(name="Other XML",
        #                                                   ext="ox",
        #                                                   type=99))

        # This is needed for the view as HTML option since we tell it
        # to store the images in the memory file system.
        #wx.FileSystem.AddHandler(wx.MemoryFSHandler())



    #----------------------------------------------------------------------
    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        print "Received the following message: " + message
        if arg2:
            print "Received another arguments: " + str(arg2)
        self.addAudioSample(message, arg2)

    def getSectionNumber(self, i):
        k=0
        res = -1
        print i
        size = len(self.Sentences)
        while k< size:
            print k, self.Sentences[k]
            if i < self.Sentences[k]:
                if k != 0:
                    res = k-1
                k = size
            k=k+1
        if i > self.Sentences[size-1]:
            res = size-1
        print res
        return res

    def SimplifyAudioLimit(self, num):
        return str(round(float(num), 4))

    def addAudioSample(self, start, end):
        #i = self.control.GetInsertionPoint()
        lineNum = self.control.GetRange( 0, self.control.GetInsertionPoint() ).split("\n")
        #lineText = self.control.GetLineText(lineNum)
        i = len(lineNum) - 1
        section = self.getSectionNumber(i)
        self.doc.TEXT.S[section].AUDIO.start = self.SimplifyAudioLimit(start)
        self.doc.TEXT.S[section].AUDIO.end = self.SimplifyAudioLimit(end)
        #self.doc.xml_write(XML_W)
        self.control.SetValue(self.doc.xml_encode(self.XML_W))
        self.control.SetInsertionPoint(i)
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

    def forceDefaultStyle(self, event):
        hEventObject = event.GetEventObject()
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



    def OnSave(self,e):
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", \
                wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:
            # Grab the content to be saved
            itcontains = self.control.GetValue()

            # Open the file for write, write, close
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
        # Get rid of the dialog to keep things tidy
        dlg.Destroy()

    def onClose(self):
        self.Destroy()
