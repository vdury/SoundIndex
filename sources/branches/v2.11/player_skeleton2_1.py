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
import scipy.io.wavfile as wf
import math
from wx.lib.pubsub import pub
import wx.lib.platebtn as platebtn
import time

sys.path.append("./")
from wavio import *


dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')



########################################################################


class MediaPanel(wx.Panel):
    """
    class variables:
    -self.frame        : MainPanel of the application, to communicate with parent
    -self.currentVolume: Volume of audio
    -self.currentFolder: Folder of the application
    -self.endmark      : End of the marked audio Sample
    -self.x0           : First click of the marked audio
    -self.x1           : Release of the marked audio
    -self.play         : -1 if no Audio loaded, 0 if on pause, 1 if playing
    -self.edit         : Only used to clear selection (0), otherwise always =1
    -self.pressed      : 1 if left click is pressed, 0 when released
    """

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)

        self.frame = parent
        self.currentVolume = 50
        self.layoutControls()

        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer, self.timer)
        self.timer.Start(1)

        pub.subscribe(self.myListener, "panelListener2")

        #Variable Initialization
        self.endmark = -1
        self.x1 = 0
        self.x0 = 0
        self.play = -1
        self.edit = 1
        self.pressed = 0
        
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
        self.imageMaxHeight= 200


        #drawing a constant function
        self.fig = plt.figure(figsize=((self.imageMaxWidth/10.0), (self.imageMaxHeight/100.0)),frameon=False)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        plt.autoscale(tight=True)
        self.ax.axis('off')
        a = [1,2,3,4,5]
        b = [0,0,0,0,0]


        #transposing the constant function onto a FigureCanvas
        self.imageCtrl = FigureCanvasWxAgg(self, -1, self.fig)
        self.imageCtrl.plot_data = \
            plt.plot(a, b, '-', color='black')[0]
        plt.close()


        #Setting up the scrollbar, with the buttons on each side.
        ScrollSizer = wx.BoxSizer(wx.HORIZONTAL)
        slbtn = platebtn.PlateButton(self, label =u"\u25C0"+u"\u25C0", size=(30,20), style=platebtn.PB_STYLE_DEFAULT)
        srbtn = platebtn.PlateButton(self, label = u"\u25B6"+u"\u25B6", size=(30,20), style=platebtn.PB_STYLE_DEFAULT)

        if (wx.Platform != '__WXMSW__'):
            """
            Left and Right Buttons unnecessary on Windows
            """
            lbtn = platebtn.PlateButton(self, id= wx.ID_ANY, label= u"\u25C0", size = (20, 20), style=platebtn.PB_STYLE_DEFAULT) 
            rbtn = platebtn.PlateButton(self, id= wx.ID_ANY, label= u"\u25B6", size = (20, 20), style=platebtn.PB_STYLE_DEFAULT) 
            lbtn.Bind(wx.EVT_BUTTON, lambda evt, a=-1, b=0: self.ScrollButton(evt, a, b))
            rbtn.Bind(wx.EVT_BUTTON, lambda evt, a=1, b=0: self.ScrollButton(evt, a, b)) 

        self.scrollbar = wx.ScrollBar(self, -1, size= (self.imageMaxWidth - 100, 20),  style=wx.SB_HORIZONTAL)
        self.scrollbar.Bind(wx.EVT_SCROLL, self.OnScroll)

        ScrollSizer.Add(slbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(lbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(self.scrollbar, 1, wx.EXPAND, 5)
        ScrollSizer.Add(rbtn, 0, wx.EXPAND, 5)
        ScrollSizer.Add(srbtn, 0, wx.EXPAND, 5)

        slbtn.Bind(wx.EVT_BUTTON, lambda evt, a=-1, b=1: self.ScrollButton(evt, a, b))
        srbtn.Bind(wx.EVT_BUTTON, lambda evt, a=1, b=1: self.ScrollButton(evt, a, b))

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()

        #Watch to help know what part of the audio is being played
        self.watch = wx.StaticText(self, wx.ID_ANY, label = "0:00/0:00", style = wx.ALIGN_CENTER)
        mainSizer.Add(self.watch, 0, wx.ALL|wx.LEFT, 5)
        mainSizer.Add(ScrollSizer, 0, wx.ALL|wx.CENTER, 5)
        mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        
        hSizer1.Add(audioSizer, 0, wx.ALL|wx.CENTER, 5)
        mainSizer.Add(hSizer1)

        self.SetSizer(mainSizer)
        self.Layout()

    #----------------------------------------------------------------------
    def buildAudioBar(self):
        """
        Builds the audio bar controls and buttons
        """
        audioBarSizer = wx.BoxSizer(wx.HORIZONTAL)
        #Size of buttons
        w = 40
        h = 40
        self.bmpMask = wx.EmptyBitmap(w, h)

        mdc = wx.MemoryDC()
        mdc.SelectObject(self.bmpMask)        
        mdc.SetBackground(wx.Brush("lightgray")) 
        mdc.Clear()
        

        #Play Btn
        mdc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        #Drawing the Triangle
        mdc.DrawPolygon([(w*(9.0/10), h*(1.0/2)), (w*(1.0/10),h*(1.0/10)), (w*(1.0/10),h*(9.0/10))])
        self.playPauseBtn = buttons.GenBitmapButton(self, bitmap=self.bmpMask, name="play")
        self.playPauseBtn.Enable(False)
        self.playPauseBtn.SetInitialSize()
        self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
        audioBarSizer.Add(self.playPauseBtn, 0, wx.EXPAND, 3)


        #Pause Btn
        self.bmpMask = wx.EmptyBitmap(w, h)

        mdc.SelectObject(self.bmpMask)        
        mdc.SetBackground(wx.Brush("lightgray")) 
        mdc.Clear()

        mdc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        #Drawing the the two bars of the pause symbol
        mdc.DrawRectangle(10, 8, 8, 24)
        mdc.DrawRectangle(22, 8, 8, 24)
        self.pauseBtn = buttons.GenBitmapButton(self, bitmap=self.bmpMask, name="pause")
        self.pauseBtn.Enable(False)
        self.pauseBtn.SetInitialSize()
        self.pauseBtn.Bind(wx.EVT_BUTTON, self.onPause)
        audioBarSizer.Add(self.pauseBtn, 0, wx.EXPAND, 3)


        #Stop Btn
        self.bmpMask = wx.EmptyBitmap(w, h)

        mdc.SelectObject(self.bmpMask)        
        mdc.SetBackground(wx.Brush("lightgray")) 
        mdc.Clear()

        mdc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        #Drawing the Rectangle of the stop symbol
        mdc.DrawRectangle(8, 8, 24, 24)
        btn = buttons.GenBitmapButton(self, bitmap=self.bmpMask, name="stop")
        btn.Enable(True)
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, self.onStop)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 3)

        #Zoom In Btn
        btnData = [{'bitmap':'zoom_in.png',
                    'handler':self.zoomIn, 'name':'zoomin'},
                    {'bitmap':'zoom_out.png',
                     'handler':self.zoomOut, 'name':'zoomout'}]
        for btn in btnData:
            self.buildBtn(btn, audioBarSizer)

        #Set Zoom Btn
        btn = buttons.GenButton(self, label="Set Zoom", name="zoom")
        btn.Bind(wx.EVT_BUTTON, self.onZoom)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 3)

        #Prev Btn
        self.bmpMask = wx.EmptyBitmap(23, h)

        mdc.SelectObject(self.bmpMask)        
        mdc.SetBackground(wx.Brush("lightgray")) 
        mdc.Clear()

        mdc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        mdc.DrawRectangle(5, 7, 2, 26)
        mdc.DrawPolygon([(5,20), (18,7), (18,33)])
        btn = buttons.GenBitmapButton(self, bitmap=self.bmpMask, name="prev")
        btn.Enable(True)
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, self.onPrev)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 3)

        #Next Btn
        self.bmpMask = wx.EmptyBitmap(23, h)

        mdc.SelectObject(self.bmpMask)        
        mdc.SetBackground(wx.Brush("lightgray")) 
        mdc.Clear()

        mdc.SetBrush(wx.Brush(wx.BLACK, wx.SOLID))
        mdc.DrawRectangle(18, 7, 2, 26)
        mdc.DrawPolygon([(18,20), (5,7), (5,33)])
        btn = buttons.GenBitmapButton(self, bitmap=self.bmpMask, name="next")
        btn.Enable(True)
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, self.onNext)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 3)

        #Select Btn
        btn = buttons.GenButton(self, label="Select", name="select")
        btn.Bind(wx.EVT_BUTTON, self.onSelect)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 0)
        
        #Clear Selection Btn
        btn = buttons.GenButton(self, label="Clear Selection", name="clselect")
        btn.Bind(wx.EVT_BUTTON, self.onClear)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 0)
        
        #Sync Xml Btn
        btn = buttons.GenButton(self, label="Sync", name="sync")
        btn.Bind(wx.EVT_BUTTON, self.onSync)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 0)
        
        #Mark&Next Btn
        btn = buttons.GenButton(self, label="Sync & Next", name="syncnext")
        btn.Bind(wx.EVT_BUTTON, self.onSyncNext)
        audioBarSizer.Add(btn, 0, wx.EXPAND, 0)

        #Spacer
        audioBarSizer.AddSpacer(50)

        #Showing Sentence nbr Text
        self.sentence = wx.StaticText(self, wx.ID_ANY, size = (400,40), style = wx.ALIGN_CENTER)        
        audioBarSizer.Add(self.sentence, 0, wx.RIGHT, 0)

        #Showing audio time Text
        self.audioRange = wx.StaticText(self, wx.ID_ANY, size = (300,40), style = wx.ALIGN_CENTER)        
        audioBarSizer.Add(self.audioRange, 0, wx.RIGHT, 0)


        mdc.EndDrawing()
        return audioBarSizer

    #----------------------------------------------------------------------
    def onClear(self, event):
        self.edit = 0
        self.Refresh()

    #----------------------------------------------------------------------
    def buildBtn(self, btnDict, sizer):
        """
        Build Zoom In and Zoom out buttons from bitmaps
        """
        bmp = btnDict['bitmap']
        handler = btnDict['handler']
        img = wx.Bitmap(os.path.join(bitmapDir, bmp))
        btn = buttons.GenBitmapButton(self, bitmap=img, name=btnDict['name'])
        btn.SetInitialSize()
        btn.Bind(wx.EVT_BUTTON, handler)
        sizer.Add(btn, 0, wx.EXPAND, 3)


    #----------------------------------------------------------------------
    def OnRelease(self, event):
        """
        When Left Mouse Click is released
        """
        if self.pressed == 1 & self.edit == 1:
            self.pressed = 0
            x,y = self.ScreenToClient(wx.GetMousePosition())
            self.x1 = self.coordsToSeconds(x)
            #self.drawMark(0)
            if self.play != -1:
                self.AudioStart = min(self.x0, self.x1)
                self.AudioEnd   = max(self.x0, self.x1)


    #---------------------------------------------------------------------
    def OnMotion(self, event):
        """
        When Mouse is moving (only active when left mouse is clicked)
        """
        if self.pressed == 1:
            self.Refresh()
            x,y = self.ScreenToClient(wx.GetMousePosition())
            self.x1 = self.coordsToSeconds(x)
            #self.drawMark(0)

    #-----------------------------------------------------------------------
    def drawMark(self, reload):
        """
        is called constantly, reload param is used to know if the scrollbar 
        has to be updated, only in the case of prev and next buttons
        """
        dc = wx.ClientDC(self.imageCtrl)
        dc.BeginDrawing()
        dc.SetBrush(wx.Brush(wx.BLUE, wx.CROSSDIAG_HATCH))
        a, x0 = self.secondsToCoords(self.x0)
        b, x1 = self.secondsToCoords(self.x1)
        
        if (((a != 0) | (b != 0)) & reload == 1):

            if self.zoom < (abs(self.x0 - self.x1) + 2):
                self.zoom = abs(self.x0 - self.x1) + 2
                self.scrollbar.SetScrollbar(0, self.zoom, self.num/self.fs, 2)
            #self.zoom = max(self.zoom, abs(self.x0 - self.x1) + 2)
            
            moment = min(self.x0, self.x1) - 1

            if (moment+self.zoom) > self.length:
                moment = self.length-self.zoom

            self.scrollbar.SetThumbPosition(moment)

            a, x0 = self.secondsToCoords(self.x0)
            b, x1 = self.secondsToCoords(self.x1)
            self.OnScroll(0)

        dc.DrawRectangle(min(x0, x1), 0, abs(x1 - x0), self.imageMaxHeight - 40)
        self.sentence.SetLabel("Marker set from %02d:%02d:%02d to %02d:%02d:%02d" % self.markerLabel(self.x0, self.x1))
        
        self.AudioStart = self.x0
        self.AudioEnd = self.x1

        dc.EndDrawing()
    
    #------------------------------------------------------------------------
    def markerLabel(self, x0, x1):
        """
        Useful to convert seconds into minute/secs/decimals
        """
        y0 = min(x0, x1)
        y1 = max(x0, x1)
        
        y0min = 0
        y1min = 0

        if y0 > 60:
            y0min = y0/60
            y0    = y0 - math.floor(y0min)*60
        y0dec = int((y0 - int(y0))*100)
        y0 = int(y0)
    
        if y1 > 60:
            y1min = y1/60
            y1    = y1 - math.floor(y1min)*60
        y1dec = int((y1 - int(y1))*100)
        y1 = int(y1)

        return y0min, y0, y0dec, y1min, y1, y1dec
    #------------------------------------------------------------------------


    def OnLeftDown(self, event):
        """Left mouse button clicked"""
        x,y = self.ScreenToClient(wx.GetMousePosition())
        self.edit =  1
        if event.ShiftDown():
            self.x1 = self.coordsToSeconds(x)
        else:
            self.x1 = self.coordsToSeconds(x)
            self.x0 = self.x1
        self.pressed = 1




    #----------------------------------------------------------------------
    def loadMusic(self, musicFile):
        """
        Using the wx.Media to read wav File
        """
        if not self.mediaPlayer.Load(musicFile):
            wx.MessageBox("Unable to load %s: Unsupported format?" % musicFile,
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
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
            self.onOpen(path)
        dlg.Destroy()
        
    def onOpen(self, path):
        self.mediaPlayer.Stop()
        self.currentFolder = os.path.dirname(path)
        self.loadMusic(path)
        self.showInitialSoundwave(path)
        self.play = 0
        self.endmark = self.mediaPlayer.Length()
        fileName, fileExtension = os.path.splitext(path)
        pub.sendMessage("panelListener", message = fileName)

    #----------------------------------------------------------------------
    def showInitialSoundwave(self, path):
        """Used to print out the sample's sound wave"""
        fileName, fileExtension = os.path.splitext(path)
        #Extract Raw Audio from Wav File
        if fileExtension == '.mp3':
            #If mp3, subprocess to change it into wav. 
            #Not working (obviously), if mpg123 command not installed.
            #May be obsolete, will be changed into an error message so that
            #Only wav files are accepted
            subprocess.call(["mpg123", "-w", "new.wav", path])
            self.fs, sampwidth, signal, self.length = readwav("new.wav")
        else:
            #Readwav from wavio.py file, using wave library
            #self.fs: frequency (recalculated later because not reliable)
            #signal : audio data
            #self.length: length of audio file
            self.fs, sampwidth, signal, self.length = readwav(path)


        #If Stereo
        if len(signal) == 2:
            signal = signal[:, 1]
        
        #Setting the signal as a numpy array
        self.signal = np.fromstring(signal, str(signal.dtype))
        #Number of points of the signal
        self.num=len(self.signal)

        #Arbitrary zoom, showing 10 seconds of the audio at first
        #Showing all the audio in the beginning is long and unnecessary
        self.zoom =10
        
        #Setting up size and limit of the scrollbar
        self.scrollbar.SetScrollbar(0, self.zoom, self.length, 2)

        #Necessary to recalculate the frequency.
        #Not sure why, but seems to work everytime with it.
        self.fs = self.num/self.length

        #Plotting the signal between 0 and 10 seconds
        self.imageCtrl.plot_data.set_xdata(np.linspace(0,self.zoom, self.zoom*self.fs))
        self.imageCtrl.plot_data.set_ydata(self.signal[0:self.fs*self.zoom])
        self.ax.set_xlim(0.0, self.zoom)
        self.max_y = max(abs(min(self.signal[0:self.fs*self.zoom])), abs(max(self.signal[0:self.fs*self.zoom])))
        self.ax.set_ylim(-self.max_y+1, self.max_y-1)
        self.imageCtrl.draw()
        plt.close()

        #Updating the range indicator
        self.audioRangeUpdate()
        self.Refresh()

        #Associating right click and motion with the functions
        self.imageCtrl.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.imageCtrl.Bind(wx.EVT_LEFT_UP, self.OnRelease)
        self.imageCtrl.Bind(wx.EVT_MOTION, self.OnMotion)

        self.AudioStart = 0
        self.AudioEnd   = self.length
        

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

    #------------------------------------------------------------------
    def OnScroll(self, event):
        """
        When scrolling the signal, recalculates and plots the signal where needed
        """
        if self.play >= 0:
            moment = self.scrollbar.GetThumbPosition()
            if event != 0:
                self.onPause(0)
                if event == 1:
                    self.scrollbar.SetScrollbar(moment, self.zoom, self.length, 2)
                    if (moment+self.zoom) > self.length:
                        moment = self.length-self.zoom
                        self.scrollbar.SetThumbPosition(moment)

            self.imageCtrl.plot_data.set_xdata(np.linspace(moment,self.zoom+moment, self.zoom*self.fs))
            self.imageCtrl.plot_data.set_ydata(self.signal[moment*self.fs:(moment+self.zoom)*self.fs])

            self.max_y = max(abs(min(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])),
                             abs(max(self.signal[moment*self.fs:self.fs*(moment+self.zoom)])))


            self.ax.set_xlim(moment, moment+self.zoom)
            self.ax.set_ylim(-self.max_y+1, self.max_y-1)
            self.imageCtrl.draw()
            self.audioRangeUpdate()
            self.Refresh()

    #----------------------------------------------------------------------

    def onNext(self, event):
        """
        Demands to the Xml file the next audio limits
        """
        if self.play>=0:
            pub.sendMessage("panelListener", message="next")

    #----------------------------------------------------------------------
    def onPrev(self, event):
        """
        Demands to the Xml file the previous audio limits
        """
        if self.play>=0:
            pub.sendMessage("panelListener", message="prev")

    #----------------------------------------------------------------------
    def onPause(self, event):
        """
        Pauses the music
        """
        self.play = 0
        self.mediaPlayer.Pause()
        self.playPauseBtn.Enable(True)
        self.pauseBtn.Enable(False)

    #--------------------------------------------------------------------
    def onSelect(self, event):
        """
        Shows the time sample of the sentence where cursor is
        """
        if self.play >= 0:
            pub.sendMessage("panelListener", message="sentence")
        
    #--------------------------------------------------------------------
    def onSync(self, event):
        """
        Sends audio limits defined by marker to the Xml File,
        To sync them with the Xml
        """
        if self.edit == 0:
            print "Nothing to sync about"
        else:
            pub.sendMessage("panelListener", message=str(self.AudioStart), arg2=str(self.AudioEnd))

    #--------------------------------------------------------------------
    def onSyncNext(self, event):
        """
        Syncs the audio limits and shows the next sentence (if exists and marked)
        """
        if self.edit != 0:
            self.onSync(0)
            self.onNext(0)

    #----------------------------------------------------------------------
    def onZoom(self, event):
        """
        Zoom button, shows ZoomDialog to define how many seconds
        The User wants to display
        """
        if self.play >= 0:
            if self.length > 5:
                self.onPause(0)
                dlg = ZoomDialog(self, -1, 'Zoom', self.zoom, self.length)
                dlg.ShowModal()
                dlg.Destroy()
                self.OnScroll(1)

    def zoomOut(self, event):
        """
        Displays one second more than before
        """
        if self.play >= 0:
            self.zoom = self.zoom + 1
            self.OnScroll(1)

    def zoomIn(self, event):
        """
        Displays one second less than before
        """
        if (self.play >= 0) & (self.zoom >= 2):
            self.zoom = self.zoom - 1
            self.OnScroll(1)

    #----------------------------------------------------------------------
    def audioRangeUpdate(self):
        """
        Updates the text on bottom right showing which part of the
        audio is being displayed
        """
        moment = self.scrollbar.GetThumbPosition()
        end = moment + self.zoom
        momentmin = 0
        endmin = 0
        if moment >= 60:
            momentmin = moment/60
            moment = moment - momentmin*60
        if end >= 60:
            endmin = int(end/60)
            end = end - endmin*60
        self.audioRange.SetLabel("Displaying [%02d:%02d - %02d:%02d]" %(momentmin, moment, endmin, end))

    #----------------------------------------------------------------------

    def onPlay(self, event):
        """
        Plays the music
        """
        self.play = 1
        if not event.GetIsDown():
            self.onPause(0)
            return

        if not self.mediaPlayer.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        elif self.edit == 1:
            offset = min(self.x0, self.x1)
            self.endmark = max(self.x0, self.x1)
            self.mediaPlayer.Seek(offset*1000)
        else:
            self.mediaPlayer.SetInitialSize()
        self.drawCursor()
        event.Skip()
        self.playPauseBtn.Enable(False)
        self.pauseBtn.Enable(True)



    def drawCursor(self):
        """
        Draws a big thin red line where the audio is being played
        """
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

    #----------------------------------------------------------------------
    def onSeek(self, event):
        """
        Seeks the media file according to the amount the slider has
        been adjusted.
        Is not being used at the time, but maybe interesting for future
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
            self.playPauseBtn.Enable(True)
            self.pauseBtn.Enable(False)
    #----------------------------------------------------------------------

    def onTimer(self, event):
        """
        Keeps the player slider updated
        Is being called constantly with a timer
        For various event
        """
        if self.play == -1:
            return
        elif self.mediaPlayer.Tell() == self.mediaPlayer.Length():
            #If audio is finished, stop
            self.onStop(0)
        elif self.mediaPlayer.Tell() >= self.endmark*1000:
            #If audio is finished reading the marker, pause
            self.onPause(0)
        else:
            #draws cursor all the time and keeps chronometer updated
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
            
        if self.edit == 1:
            #Keeps on drawing the marker, because the signal may be refreshed
            #Because of the moving cursor, or the audiobar being updated
            self.drawMark(0)

        if self.play == 1:
            #Refreshes to update the cursor position
            self.Refresh()
        
    def onClose(self):
        #Trying to neaty way to close the panel
        self.onStop(0)
        self.mediaPlayer.Destroy()
        self.Destroy()

    def myListener(self, message, arg2=None):
        #Manages the messages received from Xml
        if self.play >= 0:
            if arg2:
                self.edit = 1
                self.Refresh()
                self.x0 = float(message)
                self.x1 = float(arg2)
                self.drawMark(1)
        elif os.path.exists(message+".wav"):
            self.onOpen(message+".wav")
        else:
            print message+".wav"


    def secondsToCoords(self, x):
        #Translates time values to coordinates on the screen
        a = self.scrollbar.GetThumbPosition()
        b = a +self.zoom
        if x < a:
            return 1, 0
        elif x > b:
            return 1, self.imageMaxWidth
        else:
            return 0, (((x-a)/(b-a))*self.imageMaxWidth)

    def coordsToSeconds(self, x):
        #Translates coordinates on the screen to time values
        return (((x*1.0/self.imageMaxWidth*1.0) * self.zoom) + self.scrollbar.GetThumbPosition())

#----------------------------------------------------------------------------------------

class ZoomDialog(wx.Dialog):
    """
    Creates a Dialog box so the user can personalize how many seconds 
    of the audio sample he wants to display on the screen
    """
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
        self.zoomslider = wx.Slider(self, size=(175,-1), style = wx.SL_MIN_MAX_LABELS|wx.SL_AUTOTICKS)
        self.zoomslider.SetRange(5, length)
        self.zoomslider.SetValue(zoom)
        self.zoomslider.Bind(wx.EVT_SLIDER, self.sliderUpdate)
        topsizer.Add(self.zoomslider)
        topsizer.AddSpacer(15)
        sizer.Add(topsizer, border=5)
        sizer.AddSpacer(20)
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
        """
        Small sentence to show the user how much he selected with the slider
        """
        self.value.SetLabel("Showing %02d seconds of the sound sample" % self.zoomslider.GetValue())

    def onOk(self, event):
        """
        Changes the zoom
        """
        self.parent.zoom = self.zoomslider.GetValue()
        self.Destroy()

    def onCancel(self, event):
        self.Destroy()

