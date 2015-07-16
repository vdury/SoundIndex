#----------------------------------------------------------------------
# player_skeleton2.py
#
# Created: 04/15/2010
#
# Author: Mike Driscoll - mike@pythonlibrary.org
#----------------------------------------------------------------------
import os
import sys
import wx
import wx.media
import wx.lib.buttons as buttons
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import wave
import scipy.io.wavfile as wf
import math


sys.path.append("./")
from wavio import *

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
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(10)
        

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.change_plot(0)

        self.canvas = FigureCanvas(parent, -1, self.figure)

        
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
        
        img = wx.Image('cst.png', wx.BITMAP_TYPE_ANY)
        img.Rescale(self.imageMaxWidth, self.imageMaxHeight)
        
        #img = img.ConvertToBitmap()
        #self.imageCtrl = wx.StaticBitmap(self, -1, img,  (10,5), (self.imageMaxWidth, self.imageMaxHeight))
        
        # Create sizers
        
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()

        mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)
        hSizer1.Add(audioSizer, 0, wx.ALL|wx.CENTER, 5)
        mainSizer.Add(hSizer1)
                
        self.SetSizer(mainSizer)
        self.Layout()
        
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
        self.playPauseBtn = buttons.GenBitmapToggleButton(self, bitmap=img, name="play")
        self.playPauseBtn.Enable(False)
        
        img = wx.Bitmap(os.path.join(bitmapDir, "player_pause.png"))
        self.playPauseBtn.SetBitmapSelected(img)
        self.playPauseBtn.SetInitialSize()
        
        self.playPauseBtn.Bind(wx.EVT_BUTTON, self.onPlay)
        audioBarSizer.Add(self.playPauseBtn, 0, wx.LEFT, 3)
        
        btnData = [{'bitmap':'player_stop.png',
                    'handler':self.onStop, 'name':'stop'},
                    {'bitmap':'player_next.png',
                     'handler':self.onNext, 'name':'next'}]
        for btn in btnData:
            self.buildBtn(btn, audioBarSizer)
            
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
            print path
            self.currentFolder = os.path.dirname(path)
            self.loadMusic(path)
            self.showSoundwave(path)
            self.play = 0
        dlg.Destroy()
            
    
    #----------------------------------------------------------------------
    def showSoundwave(self, path):
        """Used to print out the sample's sound wave"""
        fileName, fileExtension = os.path.splitext(path)
        #Extract Raw Audio from Wav File
        if fileExtension == '.mp3':
            subprocess.call(["mpg123", "-w", "new.wav", path])
            fs, sampwidth, signal = readwav("new.wav")
        else:
            fs, sampwidth, signal = readwav(path)
        
        print "frequence: "+ str(fs)

        #If Stereo
        if len(signal) == 2:
            signal = signal[:, 1]

        signal = np.fromstring(signal, str(signal.dtype))
        
        #length = (len(signal)/10.0)/(fs/10.0)
        #print "length of track: "+str((len(signal)/10.0)/(fs/10.0))
        #print "data type: "+str(signal.dtype)
        print len(signal)
        num=len(signal)
        print num
        Time=np.linspace(0, len(signal)/fs, num)
 
        
        fig = plt.figure(frameon=False, facecolor='blue')
        
        ax = fig.add_axes([0, 0, 1, 1])
        plt.autoscale(tight=True)
        ax.axis('off')
        
        plt.plot(Time, signal, color='black')
        #plt.show()
        plt.savefig('foo.png', facecolor='lightgray')
        plt.close()
        png = wx.Image("foo.png", wx.BITMAP_TYPE_ANY)

        W = png.GetWidth()
        H = png.GetHeight()
        
        """Utile si besoin de changer le format"""
        W3, H3 = self.GetClientSize()

        if W > H:
            NewH = self.imageMaxHeight * H / W
            NewW = self.imageMaxWidth
        else:
            NewH = self.imageMaxHeight
            NewW = self.imageMaxWidth * W / H
        

        print "newW: "+str(NewW)
        png = png.Rescale(NewW,NewH)
        png = png.ConvertToBitmap()
        
        self.imageCtrl.SetBitmap(png)
        self.Refresh()
    #----------------------------------------------------------------------
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
        dc = wx.ClientDC(self.imageCtrl)
        dc.SetPen(wx.Pen(wx.RED, 1.5))
        moment = (self.mediaPlayer.Tell() * self.imageMaxWidth)/self.mediaPlayer.Length()
        dc.DrawLine(moment, 15, moment, self.imageMaxHeight - 15)

    #----------------------------------------------------------------------
    def onPrev(self, event):
        """Same as onStop"""
        self.onStop(event)

    
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
        self.Refresh()
        self.play = 0
        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)
    #----------------------------------------------------------------------
    def onStop2(self):
        """
        Force Stop
        """
        self.Refresh()
        self.play = 0
        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)
        
    #----------------------------------------------------------------------
    def onTimer(self, event):
        """
        Keeps the player slider updated
        """
        if self.play == -1:
            pass
        elif self.mediaPlayer.Tell() == self.mediaPlayer.Length():
            self.onStop2()
        else:
            offset = self.mediaPlayer.Tell()
            self.drawCursor()
            if self.play == 1:
                self.Refresh()

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
class MainFrame(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "SoundIndex_2.0")
        #bSizer1 = wx.BoxSizer( wx.VERTICAL )
        self.player_panel = MediaPanel(self)
        #self.text_panel = TextPanel(self)
        #bSizer1.Add(self.text_panel)
        #bSizer1.Add(self.player_panel)
        self.Maximize(True)
        
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
