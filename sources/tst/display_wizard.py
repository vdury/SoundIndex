#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx


class DisplaySlider(wx.Frame):

    def __init__(self, length):
        super(DisplaySlider, self).__init__(None)
        self.InitUI(length)

    def InitUI(self, length):

        pnl = wx.Panel(self)


        sld = wx.Slider(pnl, value=length, minValue=3, maxValue=length, pos=(20, 50),
            size=(250, -1), style=wx.SL_HORIZONTAL)
        self.btn = wx.Button(self, label='Submit', pos=(200,130))
        self.btn.SetFocus()
        sld.Bind(wx.EVT_SCROLL, self.OnSliderScroll)
        self.exp = wx.StaticText(pnl, label='Select how many seconds you \nwant to display at once:', pos=(20,10))
        self.txt = wx.StaticText(pnl, label=str(length), pos=(20, 90))
        #self.btn.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSize((320, 200))
        self.SetTitle('Zooming Selection')
        self.Centre()
        self.Show(True)

    def OnClose(self, e):
        self.Close(True)

    def OnSliderScroll(self, e):

        obj = e.GetEventObject()
        val = obj.GetValue()

        self.txt.SetLabel(str(val))


def main():

    ex = wx.App()
    DisplaySlider(100)
    ex.MainLoop()

if __name__ == '__main__':
    main()
