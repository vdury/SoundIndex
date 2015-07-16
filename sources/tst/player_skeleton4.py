#----------------------------------------------------------------------
# player_skeleton2.py
#
# Created: 04/15/2010
#
# Author: Mike Driscoll - mike@pythonlibrary.org
#----------------------------------------------------------------------

import os
import wx
import wx.media
import wx.lib.buttons as buttons
import subprocess
import matplotlib.pyplot as plt
import numpy as np
import wave
dirName = os.path.dirname(os.path.abspath(__file__))
bitmapDir = os.path.join(dirName, 'bitmaps')
mainSizer = wx.BoxSizer(wx.VERTICAL)
########################################################################
class MediaPanel(wx.Panel):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        
        self.frame = parent
        self.currentVolume = 50
        self.createMenu()
        self.layoutControls()
        
        sp = wx.StandardPaths.Get()
        self.currentFolder = sp.GetDocumentsDir()
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(100)
        
        
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
                
        # create playback slider
        self.playbackSlider = wx.Slider(self, size=wx.DefaultSize)
        #self.Bind(wx.EVT_SLIDER, self.onSeek, self.playbackSlider)
                
        width, height = wx.DisplaySize()
        self.imageMaxWidth = width
        self.imageMaxHeight= 150
        
        img = wx.Image('cst.png', wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.imageCtrl = wx.StaticBitmap(self, -1, img,  (10,5), (self.imageMaxWidth, self.imageMaxHeight))
        mainSizer.Add(self.imageCtrl, 0, wx.ALL|wx.CENTER, 5)

        self.volumeCtrl = wx.Slider(self, -1, 27, 0, 100,
                                    size=(-1, 100),
                                    style=wx.SL_VERTICAL|wx.SL_INVERSE)
        
        self.volumeCtrl.SetRange(0, 100)
        self.volumeCtrl.SetValue(self.currentVolume)
        #     self.volumeCtrl.SetTickFreq(5, 1)
        self.volumeCtrl.Bind(wx.EVT_SLIDER, self.onSetVolume)
        #      self.volumeCtrl.SetDimensions(100, 330, 250, -1)
        

        # Create sizers

        hSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        #hSizer2 = wx.BoxSizer(wx.HORIZONTAL)
        audioSizer = self.buildAudioBar()
        
        # layout widgets
        #mainSizer.Add(self.playbackSlider, 1, wx.ALL|wx.EXPAND, 5)
        hSizer1.Add(audioSizer, 0, wx.ALL|wx.CENTER, 5)
        hSizer1.Add(self.volumeCtrl, 0, wx.ALL, 5)
        
        
        mainSizer.Add(hSizer1)
        #mainSizer.Add(hSizer2)

        
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
            self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
            self.playPauseBtn.Enable(True)
           
    #---------------------------------------------------------------------
    def onBrowse(self, event):
        """
        Opens file dialog to browse for music
        """
        wildcard = "MP3 (*.mp3)|*.mp3|"     \
                   "WAV (*.wav)|*.wav"
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
        dlg.Destroy()
            

    #----------------------------------------------------------------------
    def showSoundwave(self, path):
        """Used to print out the sample's sound wave"""
        subprocess.call(["mpg123", "-w", "new.wav", path])
        spf = wave.open('new.wav','r')
        #Extract Raw Audio from Wav File
        signal = spf.readframes(-1)
        signal = np.fromstring(signal, 'Int16')
        fs = spf.getframerate()
        
        #If Stereo
        if spf.getnchannels() == 2:
            print 'Just mono files'
            sys.exit(0)
            
        Time=np.linspace(0, len(signal)/fs, num=len(signal))
        
        fig = plt.figure(frameon=False, facecolor='blue')
      
        ax = fig.add_axes([0, 0, 1, 1])
        ax.axis('off')
        plt.plot(signal, color='black')
        plt.savefig('foo.jpg', facecolor='lightgray')
        png = wx.Image("foo.jpg", wx.BITMAP_TYPE_ANY)
        #img_bitmap= wx.StaticBitmap(self, -1, png, (10, 5), (png.GetWidth(), png.GetHeight()))
        #mainSizer.Add( img_bitmap, 2, wx.EXPAND) 
        W = png.GetWidth()
        H = png.GetHeight()
        if W > H:
            NewW = self.imageMaxWidth
            NewH = self.imageMaxHeight * H / W
        else:
            NewH = self.imageMaxHeight
            NewW = self.imageMaxWidth * W / H
        png = png.Scale(NewW,NewH)
        png = png.ConvertToBitmap()
        #
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
        self.mediaPlayer.Pause()
    
    #----------------------------------------------------------------------
    def onPlay(self, event):
        """
        Plays the music
        """
        if not event.GetIsDown():
            self.onPause()
            return
        
        if not self.mediaPlayer.Play():
            wx.MessageBox("Unable to Play media : Unsupported format?",
                          "ERROR",
                          wx.ICON_ERROR | wx.OK)
        else:
            self.mediaPlayer.SetInitialSize()
            self.GetSizer().Layout()
            self.playbackSlider.SetRange(0, self.mediaPlayer.Length())
            
        event.Skip()
    
    #----------------------------------------------------------------------
    def onPrev(self, event):
        """
        Not implemented!
        """
        pass
    
    #----------------------------------------------------------------------
    def onSeek(self, event):
        """
        Seeks the media file according to the amount the slider has
        been adjusted.
        """
        offset = self.playbackSlider.GetValue()
        self.mediaPlayer.Seek(offset)
        
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
        self.mediaPlayer.Stop()
        self.playPauseBtn.SetToggle(False)
        
    #----------------------------------------------------------------------
    def onTimer(self, event):
        """
        Keeps the player slider updated
        """
        offset = self.mediaPlayer.Tell()
        self.playbackSlider.SetValue(offset)

########################################################################
class MediaFrame(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Python Music Player")
        panel = MediaPanel(self)
        self.Maximize(True)
        
#----------------------------------------------------------------------
# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MediaFrame()
    frame.Show()
    app.MainLoop()
