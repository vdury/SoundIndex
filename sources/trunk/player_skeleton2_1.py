#----------------------------------------------------------------------
# player_skeleton2.py
#
# Created: 04/15/2010
#
# Author: Mike Driscoll - mike@pythonlibrary.org
#----------------------------------------------------------------------
import matplotlib
matplotlib.use('WXAgg')
    

import os
import sys
import wx
import wx.media
import wx.lib.buttons as buttons
import subprocess
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
import matplotlib.pyplot as plt
import numpy as np
import wave
import scipy.io.wavfile as wf
import math
from wx.lib.pubsub import pub
import wx.lib.platebtn as platebtn

sys.path.append("./")
from wavio import *
from test import *

dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')

########################################################################
class MediaPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        self.frame = parent
        self.currentVolume = 50
        self.layoutControls()

        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        self.play = -1
        self.edit = 0
        self.pressed = 0
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.timer.Start(1)
        

    #----------------------------------------------------------------------
    def layoutControls(self):
        """
        Create and layout the widgets
        """

        try:
            self.mediaPlayer = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
        except NotImplementedError:
            self.Destroy()
            raise

        width, height = wx.DisplaySize()
        self.imageMaxWidth = width
        self.imageMaxHeight= 100



        #draw the cst image
        #img = wx.Image('cst.png', wx.BITMAP_TYPE_ANY)
        #img.Rescale(self.imageMaxWidth, self.imageMaxHeight)
        #img = img.ConvertToBitmap()

        self.fig = plt.figure(figsize=((self.imageMaxWidth/10.0), (self.imageMaxHeight/100.0)),frameon=False)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        plt.autoscale(tight=True)
        self.ax.axis('off')
        a = [1,2,3,4,5]
        b = [0,0,0,0,0]
        #self.imageCtrl = wx.StaticBitmap(self, -1, img,  (10,5), (self.imageMaxWidth, self.imageMaxHeight))
        self.imageCtrl = FigureCanvasWxAgg(self, -1, self.fig)
        self.imageCtrl.plot_data = \
            plt.plot(a, b, '-', color='black')[0]
        plt.close()

        ScrollSizer = wx.BoxSizer(wx.HORIZONTAL)
        slbtn = platebtn.PlateButton(self, label =u"\u25C0"+u"\u25C0", size=(30,20), style=platebtn.PB_STYLE_DEFAULT)
        lbtn = platebtn.PlateButton(self, id= wx.ID_ANY, label= u"\u25C0", size = (20, 20), style=platebtn.PB_STYLE_DEFAULT) 
        rbtn = platebtn.PlateButton(self, id= wx.ID_ANY, label= u"\u25B6", size = (20, 20), style=platebtn.PB_STYLE_DEFAULT) 
        srbtn = platebtn.PlateButton(self, label = u"\u25B6"+u"\u25B6", size=(30,20), style=platebtn.PB_STYLE_DEFAULT)
        

        self.scrollbar = wx.ScrollBar(self, -1, size= (self.imageMaxWidth - 100, 20),  style=wx.SB_HORIZONTAL)
        #self.scrollbar.SetScrollbar(0, 10, 1000, 10)
        #size= (self.imageMaxWidth, 20), 
        self.watch = wx.StaticText(self, wx.ID_ANY, label = "0:00/0:00", style = wx.ALIGN_CENTER)
        self.scrollbar.Bind(wx.EVT_SCROLL, self.OnScroll)
        # Create sizers
        
        ScrollSizer.Add(slbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(lbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(self.scrollbar, 1, wx.EXPAND, 5)
        ScrollSizer.Add(rbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(srbtn, 0, wx.EXPAND, 5)

        slbtn.Bind(wx.EVT_BUTTON, lambda evt, a=-1, b=1: self.ScrollButton(evt, a, b))
        lbtn.Bind(wx.EVT_BUTTON, lambda evt, a=-1, b=0: self.ScrollButton(evt, a, b))
        rbtn.Bind(wx.EVT_BUTTON, lambda evt, a=1, b=0: self.ScrollButton(evt, a, b)) 
        srbtn.Bind(wx.EVT_BUTTON, lambda evt, a=1, b=1: self.ScrollButton(evt, a, b))
        #ScrollSizer.Bind(wx.EVT_LEFT_DOWN, self.OnLeftScroll)
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()

        mainSizer.Add(self.watch, 0, wx.ALL|wx.LEFT, 5)
        mainSizer.Add(ScrollSizer, 0, wx.ALL|wx.CENTER, 5)
        mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        
        hSizer1.Add(audioSizer, 0, wx.ALL|wx.CENTER, 5)
        mainSizer.Add(hSizer1)

        self.SetSizer(mainSizer)
        self.Layout()


    #----------------------------------------------------------------------
    def OnRelease(self, event):
        if self.pressed == 1 & self.edit == 1:
            self.pressed = 0
            x,y = self.ScreenToClient(wx.GetMousePosition())
            dc = wx.ClientDC(self.imageCtrl)
            dc.BeginDrawing()
            dc.SetPen(wx.Pen(wx.BLUE, 3))
            if x-self.x0 > 0:
                dc.DrawRectangle(self.x0, 15, x-self.x0, self.imageMaxHeight - 30)
                if self.play != -1:
                    self.AudioStart = (((self.x0/1.0)/(self.imageMaxWidth/1.0)) * (self.scrollbar.GetThumbPosition() + self.zoom)) + self.scrollbar.GetThumbPosition()
                    self.AudioEnd   = (((x/1.0)/(self.imageMaxWidth/1.0)) * (self.scrollbar.GetThumbPosition() + self.zoom)) + self.scrollbar.GetThumbPosition()
            else:
                dc.DrawRectangle(x, 15, self.x0-x, self.imageMaxHeight - 30)
                if self.play != -1:
                    self.AudioStart = (((x/1.0)/(self.imageMaxWidth/1.0)) * (self.scrollbar.GetThumbPosition() + self.zoom)) + self.scrollbar.GetThumbPosition()
                    self.AudioEnd   = (((self.x0/1.0)/(self.imageMaxWidth/1.0)) * (self.scrollbar.GetThumbPosition() + self.zoom)) + self.scrollbar.GetThumbPosition()
            dc.EndDrawing()

    #---------------------------------------------------------------------
    def OnMotion(self, event):
        if self.pressed == 1:
            self.Refresh()
            x,y = self.ScreenToClient(wx.GetMousePosition())
            dc = wx.ClientDC(self.imageCtrl)
            dc.BeginDrawing()
            dc.SetPen(wx.Pen(wx.BLUE, 3))
            if x-self.x0 > 0:
                dc.DrawRectangle(self.x0, 15, x-self.x0, self.imageMaxHeight - 30)
            else:
                dc.DrawRectangle(x, 15, self.x0-x, self.imageMaxHeight - 30)
            dc.EndDrawing()

    #----------------------------------------------------------------------
    def buildAudioBar(self):
        """
        Builds the audio bar controls
        """
        audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.buildBtn({'bitmap':'player_prev.png', 'handler':self.onPrev,
                       'name':'prev'},
                      audioBarSizer)

        # create play/pause toggle button
        img = wx.Bitmap(os.path.join(bitmapDir, "player_play.png"))
        #self.playPauseBtn = wx.Button(self, id= wx.ID_FORWARD, label="", size = (50,50))
        #u"\u25B6"
        self.playPauseBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="play")
        self.playPauseBtn.Enable(False)

        img = wx.Bitmap(os.path.join(bitmapDir, "player_pause.png"))
        self.playPauseBtn.SetBitmapSelected(img)
        #self.playPauseBtn.SetInitialSize()

        self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
        audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 3)

        btnData = [{'bitmap':'player_stop.png',
                    'handler':self.onStop, 'name':'stop'},
                    {'bitmap':'player_next.png',
                     'handler':self.onNext, 'name':'next'}]
        for btn in btnData:
            self.buildBtn(btn, audioBarSizer)

        btn = wx.Button(self, id= wx.ID_ANY, label = "EDIT")
        btn.Bind(wx.EVT_BUTTON, self.onEdit)
        audioBarSizer.Add(btn, 0, wx.LEFT, 3)

        btn2 = wx.Button(self, id= wx.ID_ANY, label = "SYNC")
        btn2.Bind(wx.EVT_BUTTON, self.onSync)
        audioBarSizer.Add(btn2, 0, wx.LEFT, 3)

        #self.zoomslider = wx.Slider(self, size=(450,-1))
        #self.zoomslider.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        btn3 = wx.Button(self, id= wx.ID_ANY, label = "ZOOM")
        btn3.Bind(wx.EVT_BUTTON, self.onZoom)
        audioBarSizer.Add(btn3, 0, wx.RIGHT, 3)
        #testst = wx.StaticText(self, id= wx.ID_ANY, label = "XXXX")
        #audioBarSizer.Add(testst, 0, wx.LEFT, 3)

        return audioBarSizer

    #----------------------------------------------------------------------
    def buildBtn(self, btnDict, sizer):
        """"""
        bmp = btnDict['bitmap']
        handler = btnDict['handler']

        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self, bitmap=img, name=btnDict['name'])
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.LEFT, 3)

    #----------------------------------------------------------------------
    def createMenu(self):
        """
        Creates a menu
        """
        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        open_file_menu_item = fileMenu.Append(wx.NewId(), "&Open", "Open a File")
        menubar.Append(fileMenu, '&File')
        self.frame.SetMenuBar(menubar)
        self.frame.Bind(wx.EVT_MENU, self.onBrowse, open_file_menu_item)

    #----------------------------------------------------------------------
    def loadMusic(self, musicFile):
        """"""
        if not self.mediaPlayer.Load(musicFile):
            wx.MessageBox("Unable to load %s: Unsupported format?" % pat,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            self.GetSizer().Layout()
            self.playPauseBtn.Enable(True)

    #---------------------------------------------------------------------
    def onBrowse(self, event):
        """
        Opens file dialog to browse for music
        """
        wildcard = "WAV (*.wav)|*.wav|"      \
                   "MP3 (*.mp3)|*.mp3|"      \
                   "All Files  |*.*"


        dlg = wx.FileDialog(
            self, message="Choose a file",
            defaultDir=self.currentFolder,
            defaultFile="",
            wildcard=wildcard,
            style=wx.OPEN | wx.CHANGE_DIR
            )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.currentFolder = os.path.dirname(path)
            self.loadMusic(path)
            self.showInitialSoundwave(path)
            self.play = 0
        dlg.Destroy()




    #----------------------------------------------------------------------
    def showInitialSoundwave(self, path):
        """Used to print out the sample's sound wave"""
        fileName, fileExtension = os.path.splitext(path)
        #Extract Raw Audio from Wav File
        if fileExtension == '.mp3':
            subprocess.call(["mpg123", "-w", "new.wav", path])
            self.fs, sampwidth, signal = readwav("new.wav")
        else:
            self.fs, sampwidth, signal = readwav(path)



        #If Stereo
        if len(signal) == 2:
            signal = signal[:, 1]

        self.signal = np.fromstring(signal, str(signal.dtype))
        #si = np.arange(0, self.fs*10)
        self.num=len(self.signal)
        self.length = self.num/self.fs
        #for i in range (0, min(self.num, self.fs*10)):
        #    si[i] = self.signal[i]
        #pub.sendMessage("WidgetPanel", message=length)
        #Example(None)
        #scrollbar
        self.zoom =10
        self.scrollbar.SetScrollbar(0, self.zoom, self.num/self.fs, 2)

        #signal = self.signal.take((0,10000))
        #print len(self.signal)
        #length = (len(signal)/10.0)/(fs/10.0)
        #print "length of track: "+str((len(signal)/10.0)/(fs/10.0))
        #print "data type: "+str(signal.dtype)
        self.Time=np.linspace(0, self.num/self.fs, self.num)
        #print num/fs
        ratio = self.imageMaxHeight/self.imageMaxWidth
        #self.fig = plt.figure(figsize=((self.imageMaxWidth/100.0), 1),frameon=False)
        self.imageCtrl.plot_data.set_xdata(self.Time[0:self.fs*self.zoom])
        self.imageCtrl.plot_data.set_ydata(self.signal[0:self.fs*self.zoom])
        #self.ax.set_xlim(0.0, 10.0)
        self.ax.set_xlim(0.0, self.zoom)
        self.max_y = max(abs(min(self.signal[0:self.fs*self.zoom])), abs(max(self.signal[0:self.fs*self.zoom])))
        self.ax.set_ylim(-self.max_y+1, self.max_y-1)
        self.imageCtrl.draw()

        plt.close()
        self.Refresh()
        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.imageCtrl.Bind(wx.EVT_MOTION, self.OnMotion)

    #------------------------------------------------------------------
    def ScrollButton(self, event, forward, zoom):
        """
        When scrollbar arrows are pressed
        Changes the position of scrollbar
        And calls the function to recalculate plot
        """
        if self.play >= 0:
            moment = self.scrollbar.GetThumbPosition()
            self.scrollbar.SetThumbPosition(moment+(forward*pow(self.zoom, zoom)))
            self.OnScroll(event)

    #-----------------------------------------------------------------
    def OnLeftScroll(self, event):
        """
        navigate through track
        """
        print "wat"
        x,y = self.ScreenToClient(wx.GetMousePosition())
        print x
            
    #------------------------------------------------------------------
    def OnScroll(self, event):
        #print self.scrollbar.GetThumbPosition()
        if self.play >= 0:
            if event != 0:
                self.onPause()
            moment = self.scrollbar.GetThumbPosition()
            self.imageCtrl.plot_data.set_xdata(self.Time[moment*self.fs:(moment+self.zoom)*self.fs])
            self.imageCtrl.plot_data.set_ydata(self.signal[moment*self.fs:(moment+self.zoom)*self.fs])

            self.max_y = max(abs(min(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])),
                             abs(max(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])))

            self.ax.set_xlim(moment, moment+self.zoom-1)
            self.ax.set_ylim(-self.max_y+1, self.max_y-1)
            self.imageCtrl.draw()
            self.Refresh()
    #----------------------------------------------------------------------
            #self.Refresh()
    def onNext(self, event):
        """
        Not implemented!
        """
        pass

    #----------------------------------------------------------------------
    def onPause(self):
        """
        Pauses the music
        """
        self.play = 0
        self.mediaPlayer.Pause()
        self.playPauseBtn.SetToggle(False)

    #--------------------------------------------------------------------
    def onEdit(self, event):
        """
        Turns on/off Edit mode
        """
        self.edit = (self.edit + 1)%2

    #--------------------------------------------------------------------
    def onSync(self, event):
        if self.edit == 0:
            print "Nothing to sync about"
        else:
            pub.sendMessage("panelListener", message=str(self.AudioStart), arg2=str(self.AudioEnd))

    #----------------------------------------------------------------------
    def onZoom(self, event):
        if self.play >= 0:
            if self.length > 5:
                self.onPause()
                dlg = ZoomDialog(self, -1, 'Zoom', self.zoom, self.length)
                dlg.ShowModal()
                dlg.Destroy()
                self.sliderUpdate()

    #----------------------------------------------------------------------
    def sliderUpdate(self):
        if self.play >= 0:
            moment = self.scrollbar.GetThumbPosition()
            #self.zoom = self.zoomslider.GetValue()
            self.scrollbar.SetScrollbar(0, self.zoom, self.num/self.fs, 2)
            if (moment+self.zoom) > self.length:
                moment = self.length-self.zoom
                self.scrollbar.SetThumbPosition(moment)
            self.imageCtrl.plot_data.set_xdata(self.Time[moment*self.fs:(moment+self.zoom)*self.fs])
            self.imageCtrl.plot_data.set_ydata(self.signal[moment*self.fs:(moment+self.zoom)*self.fs])

            self.max_y = max(abs(min(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])),
                             abs(max(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])))

            self.ax.set_xlim(moment, moment+self.zoom)
            self.ax.set_ylim(-self.max_y+1, self.max_y-1)
            self.imageCtrl.draw()
            self.Refresh()

    #----------------------------------------------------------------------
    def onPlay(self, event):
        """
        Plays the music
        """
        self.play = 1
        if not event.GetIsDown():
            self.onPause()
            return

        if not self.mediaPlayer.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            #self.GetSizer().Layout()
            self.drawCursor()
            #self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
        event.Skip()


    def drawCursor(self):
        mom = self.mediaPlayer.Tell()/1000.0
        if (mom >= self.scrollbar.GetThumbPosition()) & (mom <= (self.scrollbar.GetThumbPosition() + self.zoom)):
            dc = wx.ClientDC(self.imageCtrl)
            dc.BeginDrawing()
            dc.SetPen(wx.Pen(wx.RED, 1.5))
            moment = ((mom-self.scrollbar.GetThumbPosition()) * self.imageMaxWidth)/self.zoom
            dc.DrawLine(moment, 0, moment, self.imageMaxHeight - 15)
            dc.EndDrawing()
        elif (mom > (self.scrollbar.GetThumbPosition() + self.zoom)):
            self.ScrollButton(0, 1, 1)
            #self.scrollbar.SetThumbPosition(self.scrollbar.GetThumbPosition() + self.zoom)
        #elif (mom == (self.scrollbar.GetThumbPosition() + self.zoom)):
            #self.scrollbar.SetThumbPosition(self.scrollbar.GetThumbPosition() + self.zoom)
    #---------------------------------------------------------------------
    #def drawRectangle(self, x, y):
    #    dc = wx.ClientDC(self.imageCtrl)
    #    dc.SetPen(wx.Pen(wx.BLUE, 3))
    #    dc.DrawRectangle(x, 15, 40, self.imageMaxHeight -15)


    #----------------------------------------------------------------------
    def onPrev(self, event):
        """Same as onStop (for now)"""
        self.onStop(0)


    #----------------------------------------------------------------------
    def onSeek(self, event):
        """
        Seeks the media file according to the amount the slider has
        been adjusted.
        """
        offset = self.playbackSlider.GetValue()
        self.mediaPlayer.Seek(offset)
        self.drawCursor()
    #----------------------------------------------------------------------
    def onSetVolume(self, event):
        """
        Sets the volume of the music player
        """
        self.currentVolume = self.volumeCtrl.GetValue()
        print "setting volume to: %s" % int(self.currentVolume)
        self.mediaPlayer.SetVolume(self.currentVolume)

    #----------------------------------------------------------------------
    def onStop(self, event):
        """
        Stops the music and resets the play button
        """
        if self.play >= 0:
            self.scrollbar.SetThumbPosition(0)
            self.OnScroll(0)
            self.Refresh()
            self.play = 0
            self.mediaPlayer.Stop()
            self.playPauseBtn.SetToggle(False)
    #----------------------------------------------------------------------

    def onTimer(self, event):
        """
        Keeps the player slider updated
        """
        #print self.scrollbar.GetThumbPosition()
        if self.play == -1:
            pass
        elif self.mediaPlayer.Tell() == self.mediaPlayer.Length():
            self.onPrev(0)
        else:
            offset = self.mediaPlayer.Tell()
            self.drawCursor()
            moment = math.ceil(self.mediaPlayer.Tell()/1000)
            end = math.ceil(self.mediaPlayer.Length()/1000)
            if moment > 59:
                momentmin = math.floor(moment/60)
                moment -= momentmin*60
            else:
                momentmin = 0

            if end > 59:
                endmin = math.floor(end/60)
                end -= endmin*60
            else:
                endmin = 0

            self.watch.SetLabel("%d:%02d/%d:%02d" % (momentmin, moment, endmin, end))
            if self.play == 1:
                self.Refresh()


    def OnLeftDown(self, event):
        """Left mouse button clicked"""
        x,y = self.ScreenToClient(wx.GetMousePosition())
        if self.edit ==  1:
            self.x0 = x
            self.y0 = y
            self.pressed = 1
        elif self.play != -1:
            self.Refresh()
            self.onPause()
            offset = (((x/1.0)/(self.imageMaxWidth/1.0)) * self.zoom) + self.scrollbar.GetThumbPosition()
            self.mediaPlayer.Seek(offset*1000.0)
            self.drawCursor()
        #elif self.play == 0:
            self.Refresh()

    def onClose(self):
        self.onStop(0)
        self.mediaPlayer.Destroy()
        self.Destroy()

#----------------------------------------------------------------------------------------

class ZoomDialog(wx.Dialog):
    def __init__(self, parent, id, title, zoom, length):
        wx.Dialog.__init__(self, parent, id, title, size=(400,200))
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.AddSpacer(10)
        topsizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(self, wx.ID_ANY, label = "Seconds per frame:", style = wx.ALIGN_CENTER)
        topsizer.AddSpacer(15)
        topsizer.Add(text)
        topsizer.AddSpacer(20)
        self.zoomslider = wx.Slider(self, size=(175,-1), style = wx.SL_INVERSE|wx.SL_MIN_MAX_LABELS|wx.SL_AUTOTICKS)
        self.zoomslider.SetRange(5, length)
        self.zoomslider.SetValue(zoom)
        self.zoomslider.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        topsizer.Add(self.zoomslider)
        topsizer.AddSpacer(15)
        sizer.Add(topsizer, border=5)
        sizer.AddSpacer(20)
        #topSizer.Add(wx.StaticLine(self.panel,), 0, wx.ALL|wx.EXPAND, 5)
        self.value = wx.StaticText(self, wx.ID_ANY, label = "Showing %02d seconds of the sound sample" % zoom, style = wx.ALIGN_CENTER)
        sizer.Add(self.value, 0, wx.ALIGN_CENTER_HORIZONTAL, 5)
        sizer.AddSpacer(30)
        
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        btn = wx.Button(self, id= wx.ID_ANY, label = "OK")
        btn.Bind(wx.EVT_BUTTON, self.onOk)
        btn2 = wx.Button(self, id= wx.ID_ANY, label = "CANCEL")
        btn2.Bind(wx.EVT_BUTTON, self.onCancel)
        buttonSizer.Add(btn2, 0, wx.ALL|wx.ALIGN_LEFT, 35)
        buttonSizer.Add(btn, 0, wx.ALL|wx.ALIGN_RIGHT, 35)

        sizer.Add(buttonSizer, 0, wx.ALL|wx.EXPAND, 5)
        sizer.Layout()
        self.SetSizer(sizer)
        sizer.Fit(self)

    def sliderUpdate(self, event):
        self.value.SetLabel("Showing %02d seconds of the sound sample" % self.zoomslider.GetValue())

    def onOk(self, event):
        self.parent.zoom = self.zoomslider.GetValue()
        self.Destroy()

    def onCancel(self, event):
        self.Destroy()

########################################################################
#class MediaFrame(wx.Frame):

    #----------------------------------------------------------------------
    #def __init__(self):
    #    wx.Frame.__init__(self, None, wx.ID_ANY, wx.EmptyString)
    #    panel = MediaPanel(self)
    #    self.Maximize(True)

#----------------------------------------------------------------------
# Run the program
#if __name__ == "__main__":
#    app = wx.App(False)
#    frame = MediaFrame()
#    frame.Show()
#    app.MainLoop()
#class MainFrame(wx.Frame):

    #----------------------------------------------------------------------
#    def __init__(self):
#        wx.Frame.__init__(self, None, wx.ID_ANY, "SoundIndex_2.0")
        #bSizer1 = wx.BoxSizer( wx.VERTICAL )
#        self.player_panel = MediaPanel(self)
        #self.text_panel = TextPanel(self)
        #bSizer1.Add(self.text_panel)
        #bSizer1.Add(self.player_panel)
#        self.Maximize(True)

#----------------------------------------------------------------------
# Run the program
#if __name__ == "__main__":
#    app = wx.App(False)
#    frame = MainFrame()
#    frame.Show()
#    app.MainLoop()
