#!/usr/bin/python
# -*- coding: utf-8 -*-

import wx


class Example(wx.Frame):

    def __init__(self, *args, **kw):
        super(Example, self).__init__(*args, **kw)

        pub.subscribe(self.InitUI(), "widgetPanel")

    def InitUI(self):

        pnl = wx.Panel(self)


        wx.StaticText(self, label='Select how many seconds you \nwant to display at once:',
            pos=(20,20))
        #wx.StaticText(self, label='Fahrenheit: ', pos=(20, 80))
        #wx.StaticText(self, label='Celsius: ', pos=(20, 150))
        #sld = wx.Slider(pnl, value=100, minValue=3, maxValue=100, pos=(20, 80),
        #        size=(250, -1), style=wx.SL_HORIZONTAL)

        #self.celsius = wx.StaticText(self, label='hlhkj', pos=(150, 150))
        self.sc = wx.SpinCtrl(self, value='0', pos=(150, 75), size=(60, -1))
        self.sc.SetRange(0, 1000)

        #btn = wx.Button(self, label='Compute', pos=(70, 230))
        #btn.SetFocus()
        cbtn = wx.Button(self, label='Submit', pos=(185, 230))

        #btn.Bind(wx.EVT_BUTTON, self.OnCompute)
        #cbtn.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSize((350, 310))
        self.SetTitle('wx.SpinCtrl')
        self.Centre()
        self.Show(True)

    def OnClose(self, e):

        self.Close(True)

    def OnCompute(self, e):

        fahr = self.sc.GetValue()
        cels = round((fahr - 32) * 5 / 9.0, 2)
        self.celsius.SetLabel(str(cels))
