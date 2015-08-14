# Get the GUI stuff
import wx
#import wx.richtext
#from StringIO import StringIO
# We're going to be handling files and directories
import os
import amara
from amara import tree
from amara import bindery
from wx.lib.pubsub import pub
from amara.writers import lookup
#import wx.lib.docview
#import wx.lib.pydocview
#import wx.richtext as rt
#import wx.stc as stc
import re
import XmlEditor 
#from lxml import etree

# Set up some button numbers for the menu

class TextPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #self.control = TextCtrl(self, 1, style=wx.TE_MULTILINE | wx.TE_RICH2)
        self.control = XmlEditor.XmlSTCEditor(self, -1, style=wx.TE_MULTILINE)
        self.loaded = 0

        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control,1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.focus = -1

        self.dirname = ''


        pub.subscribe(self.myListener, "panelListener")

    #----------------------------------------------------------------------
    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        if self.loaded == 1:
            print "Received the following message: " + message
            if arg2:
                print "Received another arguments: " + str(arg2)
                self.addAudioSample(message, arg2)
            if message == "prev":
                self.onPrev()
            elif message == "next":
                self.onNext()
            else:
                print "wow"

    def onPrev(self):
        #i = self.control.GetInsertionPoint()
        #j = self.control.LineFromPosition(i)
        #section = self.getSectionNumber(j)
        #print "section = "+str(section)
        #self.Sentences = []
        #if section > 0:
        if self.focus >= 1:
            self.focus = self.focus-1
            audioStart = self.doc.TEXT.S[self.focus].AUDIO.start
            audioEnd   = self.doc.TEXT.S[self.focus].AUDIO.end
            #print audioStart, audioEnd
            pub.sendMessage("panelListener2", message=audioStart, arg2=audioEnd)
            self.reloadText()

    def onNext(self):
        #i = self.control.GetInsertionPoint()
        #j = self.control.LineFromPosition(i)
        #section = self.getSectionNumber(j)
        #print "section = "+str(section)
        self.focus = self.focus+1
        audioStart = self.doc.TEXT.S[self.focus].AUDIO.start
        audioEnd = self.doc.TEXT.S[self.focus].AUDIO.end
        #self.Sentences = []
        #print audioStart, audioEnd
        pub.sendMessage("panelListener2", message=audioStart, arg2=audioEnd)
        self.reloadText()

    def reloadText(self):
        self.scanXMLDocument()
        i = self.control.PositionFromLine(self.Sentences[self.focus] + 1)
        self.control.SetInsertionPoint(i)
        self.control.ShowPosition(i)
        self.Sentences=[]

    def getSectionNumber(self, i):
        self.scanXMLDocument()
        k=0
        res = -1
        size = len(self.Sentences)
        while k< size:
            print k, self.Sentences[k], i
            if i < self.Sentences[k]:
                res = k
                k = size
            elif i > self.Sentences[size-1]:
                res = size-1
                k = size
            k=k+1
        return res
        
    def SimplifyAudioLimit(self, num):
        return str(round(float(num), 4))
    
    def scanXMLDocument(self):
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
        print self.Sentences
        
    def addAudioSample(self, start, end):
        i = self.control.GetInsertionPoint()
        j = self.control.LineFromPosition(i)
        print "line = "+str(j)
        section = self.getSectionNumber(j)
        #print section
        if section != 0:
            self.doc.TEXT.S[section-1].AUDIO.start = self.SimplifyAudioLimit(start)
            self.doc.TEXT.S[section-1].AUDIO.end = self.SimplifyAudioLimit(end)
            self.control.SetValue(self.doc.xml_encode(self.XML_W))
            i = self.control.PositionFromLine(j)
            self.control.SetInsertionPoint(i)
            self.control.ShowPosition(i)
            #self.control.SetSelection(i,i+1)
        self.Sentences=[]
        #self.control.SetValue(self.doc.xml_children[0])
        #self.control.SetInsertionPoint(i)
        #self.control.WriteText("<AUDIO start=\""+str(start)+"\" end=\""+str(end)+"\"/>")

    def parseXMLDocument(self, path):
        i=0
        
        self.XML_W = lookup("xml")
        try:
            self.doc = bindery.parse(path)
        except amara.lib.IriError:
            self.doc = bindery.parse(path, standalone=True)
            
        #self.control.SetText(open(path).read())
        self.control.EmptyUndoBuffer()
        self.control.Colourise(0, -1)

        # line numbers in the margin
        self.control.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.control.SetMarginWidth(1, 25)

        #self.control.BeginTextColour((255,0,0))
        self.control.SetValue(self.doc.xml_encode(self.XML_W).decode("utf-8").replace("&lt;","<").replace("&gt;", ">"))
        #self.control.SetValue(unicode(open(path).read()))
        self.Sentences = []



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
        pub.sendMessage("panelListener2", message= fileName)
        if fileExtension == '.xml':
            self.loaded = 1
            self.parseXMLDocument(path)



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
