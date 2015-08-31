#import  keyword

import  wx
import  wx.stc  as  stc
import matplotlib.colors as colors

#import  images



class XmlSTCEditor(stc.StyledTextCtrl):
    
    def __init__(self, parent, ID,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0):


        if wx.Platform == '__WXMSW__':
            self.faces = { 'font-def': 'Times New Roman', 'font-tag': 'Courier New', 'font-attr': 'Arial', 'font-val': 'Comic Sans MS', 'font-dat': 'Doulos SIL','other': 'Arial',
                           'size': 10, 'size-def': 10, 'size-tag': 8, 'size-attr': 8,'size-val': 8, 'size-dat' : 8,
                           'colour': '#000000', 'col-def':'#000000','col-dat':'#000000','col-val':'#7F007F','col-tag':'#00007F','col-attr':'#007F7F',
                           'style-def':'regular','style-dat':'regular','style-val':'italic','style-tag':'bold','style-attr':'bold',
                         }
        elif wx.Platform == '__WXMAC__':
            self.faces = { 'font-def': 'Times New Roman', 'font-tag': 'Monaco', 'font-attr': 'Arial', 'font-val': 'Comic Sans MS', 'font-dat': 'Doulos SIL', 'other': 'Arial',
                           'size': 10, 'size-def': 12, 'size-tag': 10, 'size-attr': 12, 'size-val': 10, 'size-dat': 10,
                           'colour': '#000000', 'col-def':'#000000','col-dat':'#000000','col-val':'#7F007F','col-tag':'#00007F','col-attr':'#007F7F',
                           'style-def':'regular','style-dat':'regular','style-val':'italic','style-tag':'bold','style-attr':'bold',
                         }
        else:
            self.faces = { 'font-def': 'Times', 'font-tag': 'Times', 'font-attr': 'Helvetica', 'font-val': 'new century schoolbook', 'font-dat': 'Doulos SIL', 'other': 'Arial',
                           'size': 10, 'size-def': 12, 'size-tag': 10, 'size-attr'  : 12, 'size-val': 10, 'size-dat' : 12,
                           'colour': '#000000', 'col-def':'#000000','col-dat':'#000000','col-val':'#7F007F','col-tag':'#00007F','col-attr':'#007F7F',
                           'style-def':'regular','style-dat':'regular','style-val':'italic','style-tag':'bold','style-attr':'bold',
                  }



        stc.StyledTextCtrl.__init__(self, parent, ID, pos, size, style)
        self.CmdKeyAssign(ord('B'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), stc.STC_SCMOD_CTRL, stc.STC_CMD_ZOOMOUT)

        self.SetLexer(stc.STC_LEX_XML)
        #self.SetKeyWords(0, " ".join(keyword.kwlist))

        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0,0)

        self.SetViewWhiteSpace(False)
        # Setup a margin to hold fold markers
        self.SetMarginType(2, stc.STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, stc.STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 12)

        self.UsePopUp(1)

        self.Bind(stc.EVT_STC_UPDATEUI, self.OnUpdateUI)
        # Make some styles,  The lexer defines what each style is used for, we
        # just have to define what each style looks like.  This set is adapted from

        # Global default styles for all languages
        # Used for everything not related to XML, like line numbers
        # or = signs.
        self.StyleSetSpecs()


    def StyleSetSpecs(self):

        self.StyleSetSpec(stc.STC_STYLE_DEFAULT,     "fore:%(col-def)s,face:%(font-def)s,size:%(size-def)d,%(style-def)s" % self.faces)
        self.StyleClearAll()
        # Reset all to be like the default

        # Highlighting brackets (may be obsolete)
        self.StyleSetSpec(stc.STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#000000,bold,size:%(size-tag)d" % self.faces)
        self.StyleSetSpec(stc.STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")


        # Xml Element Data (<Element>DATA</Element>)
        self.StyleSetSpec(wx.stc.STC_H_DEFAULT,      "face:%(font-dat)s,fore:%(col-dat)s,size:%(size-dat)d,%(style-dat)s" % self.faces)
        
        # Comments (<!--Blabla-->)
        self.StyleSetSpec(wx.stc.STC_H_COMMENT,      "face:%(other)s,fore:#007F00,italic,face:%(other)s,size:%(size)d" % self.faces)

        # Xml Element Type Value (<Element type="VALUE">)
        self.StyleSetSpec(wx.stc.STC_H_DOUBLESTRING, "face:%(font-val)s,fore:%(col-val)s,size:%(size-val)d,%(style-val)s" % self.faces)
        
        # Xml Element Tag (<ELEMENT_TAG>)
        self.StyleSetSpec(wx.stc.STC_H_TAG,          "face:%(font-tag)s,fore:%(col-tag)s,size:%(size-tag)d,%(style-tag)s" % self.faces)
        
        # Xml Element Attribute(<Element ATTRIBUTE="value">)
        self.StyleSetSpec(wx.stc.STC_H_ATTRIBUTE,    "face:%(font-attr)s,fore:%(col-attr)s,size:%(size-attr)d,%(style-attr)s" % self.faces)

        self.SetCaretForeground("BLACK")
        


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()

        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "<>":
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)

            if charAfter and chr(charAfter) in "<>":
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)
            #pt = self.PointFromPosition(braceOpposite)
            #self.Refresh(True, wxRect(pt.x, pt.y, 5,5))
            #print pt
            #self.Refresh(False)




class FontDialog(wx.Dialog):
    def __init__(self, parent, id, title):
        wx.Dialog.__init__(self, parent, id, title, size=(700,300))
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(20)
        self.text = XmlSTCEditor(self, -1, size=(600, 50))
        self.text.SetScrollWidth(500)
        self.text.SetMarginType(1, wx.stc.STC_MARGIN_NUMBER)
        self.text.SetValue("<XML_ELEMENT attribute=\"value\">ABC abc</XML_ELEMENT>")
        self.text.SetReadOnly(1)
        sizer.Add(self.text)
        sizer.AddSpacer(20)
        
        self.rad1 = wx.RadioButton(self, label="Default Text", style = wx.RB_GROUP)
        self.rad2 = wx.RadioButton(self, label="Xml Element and Brackets Text")
        self.rad3 = wx.RadioButton(self, label="Xml Attribute Text")
        self.rad4 = wx.RadioButton(self, label="Xml Attribute Value Text")
        self.rad5 = wx.RadioButton(self, label="Xml Data Text")

        sizer.Add(self.rad1)
        sizer.Add(self.rad2)
        sizer.Add(self.rad3)
        sizer.Add(self.rad4)
        sizer.Add(self.rad5)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)

        fontbtn = wx.Button(self, id=-1, label="Change Font")
        hsizer.Add(fontbtn, wx.EXPAND)
        
        colorbtn = wx.Button(self, id=-1, label="Change Colour")
        hsizer.Add(colorbtn, wx.EXPAND)

        sizer.Add(hsizer)
        fontbtn.Bind(wx.EVT_BUTTON, self.onButtonFont)
        colorbtn.Bind(wx.EVT_BUTTON, self.onButtonColour)

        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)

        okbtn = wx.Button(self, id=wx.ID_OK, label="OK")
        cancelbtn = wx.Button(self, id=wx.ID_CANCEL, label="Cancel")
        
        hsizer2.Add(okbtn, wx.EXPAND)
        hsizer2.Add(cancelbtn, wx.EXPAND)

        sizer.AddSpacer(20)
        sizer.Add(hsizer2)

        cancelbtn.Bind(wx.EVT_BUTTON, self.OnCancel)

        sizer.Layout()
        self.SetSizer(sizer)
        

    def onButtonFont(self, event):
        dialog = wx.FontDialog(None, wx.FontData())
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetFontData()
            font_ = data.GetChosenFont()
            font = font_.GetFaceName()
            size = font_.GetPointSize()
            style= font_.GetStyleString()
            weight = font_.GetWeightString()
            self.changeFontColour((font, size, style, weight))
        dialog.Destroy()


    def onButtonColour(self, event):
        dialog = wx.ColourDialog(self)
        if dialog.ShowModal() == wx.ID_OK:
            data = dialog.GetColourData().GetColour().Get()
            self.changeFontColour('#%02X%02X%02X' % (data), True)
        dialog.Destroy()

        
    def changeFontColour(self, data, colour=False):
        #Getting which radio button is pressed
        prss_btn = self.rad1.GetValue()*1+self.rad2.GetValue()*2+self.rad3.GetValue()*3+self.rad4.GetValue()*4+self.rad5.GetValue()*5

        #Building tab to correspond radiobut to part of the xml
        radToXml = { 1: 'def',
                     2: 'tag',
                     3: 'attr',
                     4: 'val',
                     5: 'dat',
                   }
        a = radToXml.get(prss_btn)

        if colour == True:
            self.text.faces['col-'+a] = data
            self.text.StyleSetSpecs()
        
        else:
            font = data[0]
            size = data[1]
            style = ""
            if data[2] == u'wxFONTSTYLE_ITALIC':
                style = "italic"
            else:
                style = "regular"
            if data[3] == u'wxFONTWEIGHT_BOLD':
                style+= "bold"
            
            self.text.faces['font-'+a] = font
            self.text.faces['size-'+a] = size
            self.text.faces['style-'+a] = style
            self.text.StyleSetSpecs()


    def OnCancel(self, event):
        self.Destroy()
