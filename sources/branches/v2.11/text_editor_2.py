# Get the GUI stuff
import wx
import os
import amara
#from amara import tree
from amara import bindery
from wx.lib.pubsub import pub
from amara.writers import lookup
import re
import XmlEditor 
import sys

class TextPanel(wx.Panel):
    """
    self.loaded   : 1 when Xml File is loaded
    self.focus    : used for prev and next buttons, keep up with the sentences
    self.readonly : toggle on/off readonly
    self.Sentences: Tabular filled with the line numbers of every beginning of sentence
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.control = XmlEditor.XmlSTCEditor(self, -1, style=wx.TE_MULTILINE)
        self.loaded = 0

        self.sizer=wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.control,1,wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(True)
        self.focus = -1

        self.dirname = ''
        self.readonly = 0

        pub.subscribe(self.myListener, "panelListener")

    #----------------------------------------------------------------------
    def myListener(self, message, arg2=None):
        """
        Listener function
        """
        if self.loaded == 1:
            if arg2:
                self.addAudioSample(message, arg2)
            if message == "prev":
                self.onPrev()
            elif message == "next":
                self.onNext()
            elif message == "sentence":
                self.onSelect()
        elif os.path.exists(message+".xml"):
            self.OnOpen(message+".xml")

    def onSelect(self):
        """
        Getting the section number based on the cursor position
        Finding out the start and end of audio sample concerned
        """
        i = self.control.GetInsertionPoint()
        j = self.control.LineFromPosition(i)
        section = self.getSectionNumber(j)
        if section != 0:
            try:
                audioStart = self.doc.TEXT.S[section-1].AUDIO.start
                audioEnd = self.doc.TEXT.S[section-1].AUDIO.end
                pub.sendMessage("panelListener2", message=audioStart, arg2=audioEnd)
                self.focus = section-1
            except AttributeError:
                return
        return

    def onPrev(self):
        """
        Getting the previous sentence
        """
        if self.focus >= 1:
            self.focus -= 1
            try:
                audioStart = self.doc.TEXT.S[self.focus].AUDIO.start
                audioEnd = self.doc.TEXT.S[self.focus].AUDIO.end
            except AttributeError:
                try:
                    audioEnd = self.doc.Text.S[self.focus+1].AUDIO.start
                    audioStart = str(float(audioEnd) - 5.0)
                except AttributeError:
                    try:
                        audioStart = self.doc.TEXT.S[self.focus-1].AUDIO.end
                        audioEnd = str(float(audioStart) + 5.0)
                    except AttributeError:
                        self.focus += 1
                        return
            pub.sendMessage("panelListener2", message=audioStart, arg2=audioEnd)
            #self.reloadText()

    def onNext(self):
        self.focus += 1
        try:
            try:
                audioStart = self.doc.TEXT.S[self.focus].AUDIO.start
                audioEnd = self.doc.TEXT.S[self.focus].AUDIO.end
            except IndexError:
                self.focus -= 1
                return
        except AttributeError:
            try:
                audioStart = self.doc.TEXT.S[max(self.focus-1, 0)].AUDIO.end
                audioEnd = str(float(audioStart) + 5.0)
            except AttributeError:
                try:
                    audioEnd = self.doc.Text.S[self.focus+1].AUDIO.start
                    audioStart = str(float(audioEnd) - 5.0)
                except AttributeError:
                    self.focus -= 1
                    return
        pub.sendMessage("panelListener2", message=audioStart, arg2=audioEnd)
        self.reloadText()

    def reloadText(self):
        """
        Reload text when changed
        """
        self.scanXMLDocument()
        i = self.control.PositionFromLine(self.Sentences[self.focus])
        self.control.SetInsertionPoint(i)
        line = self.control.LineFromPosition(i)
        self.control.ScrollToLine(line)

    def getSectionNumber(self, i):
        """
        finding out which section is concerned by line i.
        Going through the self.Sentences to compare with each beginning of sentence
        """
        self.scanXMLDocument()
        k=0
        res = -1
        size = len(self.Sentences)
        while k< size:
            if i < self.Sentences[k]:
                res = k
                k = size
            elif i >= self.Sentences[size-1]:
                res = size
                k = size
            k += 1
        return res
        
    def SimplifyAudioLimit(self, num):
        return str(round(float(num), 4))

    def scanXMLDocument(self):
        self.Sentences = []
        for i in range (0, self.control.GetNumberOfLines()):
            Line = self.control.GetLineText(i)
            Line.strip()
            #To remove spaces in the line
            Line = re.sub(r"\s+", "", Line, flags=re.UNICODE)
            if len(Line) >= 3:
                if (Line[0]=='<') & (Line[1]=='S') & (Line[2]=='i'):
                    """
                    Everytime we encouter '<Si' at the beginning
                    of a line, we append the Sentence Tab with
                    the line number
                    """
                    self.Sentences.append(i)
        
    def addAudioSample(self, start, end):
        i = self.control.GetInsertionPoint()
        j = self.control.LineFromPosition(i)
        section = self.getSectionNumber(j)
        line= self.control.GetFirstVisibleLine()


        res=self.testXml()

        if res == 0:
            return

        if section != 0:
            try:
                self.doc.TEXT.S[section-1].AUDIO.start = self.SimplifyAudioLimit(start)
                self.doc.TEXT.S[section-1].AUDIO.end = self.SimplifyAudioLimit(end)
            except AttributeError:
                new_elem = self.doc.xml_element_factory(None, u"AUDIO")
                new_elem.xml_attributes.setnode(new_elem.xml_attribute_factory(None, u"start", self.SimplifyAudioLimit(start)))
                new_elem.xml_attributes.setnode(new_elem.xml_attribute_factory(None, u"end", self.SimplifyAudioLimit(end)))
                self.doc.TEXT.S[section-1].xml_insert(0, new_elem)
            self.control.SetValue(self.doc.xml_encode(self.XML_W).decode("utf-8"))
            i = self.control.PositionFromLine(j)
            self.control.SetInsertionPoint(i)

            self.control.ScrollToLine(line)
            self.focus = section-1

    def testXml(self):
        
        tmp = self.control.GetValue().encode("utf-8")
        
        try:
            self.doc = bindery.parse(tmp)
        except bindery.Error as e:
            line= e.lineNumber
            res = self.errorDialog(line)
            return res
        return 1

    def errorDialog(self, line):
        dial = wx.MessageDialog(None, 'Error with XML parsing at line '+str(line-1)+' \nDo you want to go back to the previous version?\nThe changes you made to the Xml will be erased,\nBut the audio boundaries you marked will be taken into account', 'Error', 
            wx.YES_NO | wx.ICON_ERROR)
        if dial.ShowModal() == wx.ID_YES:
            dial.Destroy()
            return 1
        else:
            dial.Destroy()
            return 0
        
    def onReadOnly(self, event):
        self.readonly = (self.readonly+1)%2
        self.control.SetReadOnly(self.readonly)

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

        self.control.SetValue(self.doc.xml_encode(self.XML_W).decode("utf-8").replace("<S id=","\n <S id=").replace("&lt;", u"\u2039").replace("&gt;", u"\u203A"))




    def OnBrowse(self,e):
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

        path = dlg.GetPath()
        dlg.Destroy()
        self.OnOpen(path)

    def OnOpen(self, path):
        fileName, fileExtension = os.path.splitext(path)
        self.filename = fileName+fileExtension
        pub.sendMessage("panelListener2", message= fileName)
        if fileExtension == '.xml':
            self.loaded = 1
            self.parseXMLDocument(path)
        

    def OnSave(self,e):
        # Save away the edited text
        # Open the file, do an RU sure check for an overwrite!
        
        # Grab the content to be saved
        itcontains = self.control.GetValue().encode("utf-8")
        # Checking if the XML is correct
        try:
            self.doc = bindery.parse(itcontains)
        except bindery.Error as e:
            line = e.lineNumber
            dial = wx.MessageDialog(None, 'Error with XML parsing at line '+str(line-1)+' \nCannot save document, please correct the error', 'Error', 
                            wx.OK | wx.ICON_ERROR)
            if dial.ShowModal() == wx.ID_OK:
                dial.Destroy()
                return
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, self.filename, "*.*", \
                            wx.SAVE | wx.OVERWRITE_PROMPT)
        if dlg.ShowModal() == wx.ID_OK:

                
            # Open the file for write, write, close
            self.filename=dlg.GetFilename()
            self.dirname=dlg.GetDirectory()
            filehandle=open(os.path.join(self.dirname, self.filename),'w')
            filehandle.write(itcontains)
            filehandle.close()
            # Get rid of the dialog to keep things tidy
        dlg.Destroy()

    def FontMenu(self,e):
        dialog = XmlEditor.FontDialog(self, -1, 'Font')
        if dialog.ShowModal() == wx.ID_OK:
            self.control.faces = dialog.text.faces
            self.control.StyleSetSpecs()
            dialog.Destroy()
        #dialog = wx.FontDialog(None, wx.FontData())
        #if dialog.ShowModal() == wx.ID_OK:
        #    data = dialog.GetFontData()
        #    font = data.GetChosenFont()
        #    colour = data.GetColour()
        #dialog.Destroy()
        



    def onClose(self):
        self.Destroy()

