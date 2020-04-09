import wx
from matplotlib.backends import backend_wxagg
from matplotlib.figure import Figure


class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None,size=(800,800))
        rp=wx.Panel(self,size=(600,600))
        self.panel = backend_wxagg.FigureCanvasWxAgg(rp, -1, Figure())
        axes = self.panel.figure.gca()
        axes.cla()
        axes.plot([1, 2, 3], [1, 2, 3])

        self.panel.draw()

        self.bt1=wx.Button(self,label='清除',pos=(500,600))
        self.bt1.Bind(wx.EVT_BUTTON,self.onbt1)
        self.bt2=wx.Button(self,label='画一画',pos=(500,630))
        self.bt2.Bind(wx.EVT_BUTTON,self.onbt2)
    def onbt1(self,evt):
        self.panel.figure.clear()
        self.panel.draw()

    def onbt2(self, evt):
        axes = self.panel.figure.gca()
        axes.cla()
        axes.plot([1, 2, 3], [1, 2, 3])
        self.panel.draw()
app = wx.App()
f = TestFrame()
f.Show(True)
app.MainLoop()
