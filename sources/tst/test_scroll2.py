import numpy as np

import matplotlib
from matplotlib.ticker import NullLocator
from matplotlib.patches import Rectangle
matplotlib.use('WXAgg')
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg
from matplotlib.figure import Figure

import wx
import re

class Struct(object):
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    colors = ['red', 'orange', 'blue', 'green', 'black', 'yellow', 'violet', 'brown', 'pink']
    inputFilePath=""

class MyFrame(wx.Frame):
    def __init__(self, parent, id, fPath):
        wx.Frame.__init__(self,parent, id, 'scrollable plot',
                          style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER,
                          size=(1024, 768))
        self.panel = wx.Panel(self, -1)
        
        self.fig = Figure((5, 4), 75)
        self.canvas = FigureCanvasWxAgg(self.panel, -1, self.fig)
        self.scroll_range = 768
        self.canvas.SetScrollbar(wx.HORIZONTAL, 0, 5,
                                 self.scroll_range)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.canvas, -1, wx.EXPAND)
        
        self.panel.SetSizer(sizer)
        self.panel.Fit()

        self.init_data(dataFilePath=fPath)
        self.init_plot()
        
        self.canvas.Bind(wx.EVT_SCROLLWIN, self.OnScrollEvt)

    def readData(self,filePath):
        f = open(filePath,'r')
        lines = f.readlines()
        uplinkLines = []
        for line in lines:
            uplink = []
            if line.startswith("ENB:SCHED:DL:"):
                info = line[13:]
                res = re.compile(r"T\[(\d+\.\d+)\] ([0-9 ]*)").findall(info)

                if len(res)==0:
                    continue

                allocMap = res[0][1].split()
                lng = len(allocMap)

                for i in range(25):
                    if i<lng:
                        info_block = Struct(empty=False,id=int(allocMap[i]),direction="DL")
                        uplink.append(info_block)
                    else:
                        info_block = Struct(empty=True,id=0)
                        uplink.append(info_block)

                uplinkLines.append(uplink)
                #print("uplinknextline")

        self.info_array = np.array(uplinkLines)
        #print(info_array)
        #allocation(info_array)

    def init_data(self, dataFilePath):

        self.readData(filePath=dataFilePath)
        (rows,cols) = self.info_array.shape

        # Extents of data sequence: 
        self.i_min = 0
        self.i_max = cols

        # Size of plot window:       
        self.i_window = 100

        # Indices of data interval to be plotted:
        self.i_start = 0
        self.i_end = self.i_start + self.i_window

    def plot_next_part(self):
        del self.ax.patches[:]
        for (x,y),info in np.ndenumerate(self.info_array[ : , self.i_start:self.i_end]):
            if info.empty:
                color = "white"
            else:
                color = colors[info.id]

            size = 3
            rect = Rectangle([x-size/2,y-size/2],size,size,facecolor=color,edgecolor="black")
            self.ax.add_patch(rect)
        #????????
        self.ax.set_ylim(*self.ax.get_ylim()[::-1])


    def init_plot(self):
        self.ax = self.fig.add_subplot(111)
        self.ax.patch.set_facecolor('white')
        #ax.set_aspect('equal','box')
        self.ax.xaxis.set_major_locator(NullLocator())
        self.ax.yaxis.set_major_locator(NullLocator())

        #initial plot
        self.plot_next_part()

    def draw_plot(self):
        self.plot_next_part()

        # Redraw:                  
        self.canvas.draw()

    def OnScrollEvt(self, event):

        # Update the indices of the plot:
        self.i_start = self.i_min + event.GetPosition()
        self.i_end = self.i_min + self.i_window + event.GetPosition()
        self.draw_plot()

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame(parent=None,id=-1,fPath=inputFilePath)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

if __name__ == '__main__':
    inputFilePath = raw_input("Podaj sciezke do pliku: ")
    app = MyApp()
    app.MainLoop()
