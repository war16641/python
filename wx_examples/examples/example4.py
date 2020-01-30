"""
多窗口实例
打开子窗口时 父窗口disable
关闭子窗口时 父窗口enable
"""

import wx

class MyFramech(wx.Frame):
    def __init__(self,prt):
        super(MyFramech, self).__init__(prt)
        self.panel = wx.Panel(self, -1)
        self.button = wx.Button(self.panel, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onClick, self.button)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def onClick(self,evt):
        self.SetLabel("2")

    def OnCloseWindow(self,evt):
        self.GetParent().Enable()
        self.Destroy()
class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.panel = wx.Panel(self, -1)
        self.button = wx.Button(self.panel, wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.onClick, self.button)

    def onClick(self,evt):
        self.SetLabel("1")
        dl=MyFramech(prt=self)
        dl.Show()
        self.Disable()


if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    frame.Show()
    app.MainLoop()