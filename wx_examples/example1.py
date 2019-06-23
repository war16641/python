"""
静态文本  计时器的使用
实现了以1s为间隔现实系统的时间
"""
import wx,time

class StaticTextExampleFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, \
         "Static text example", size =(800, 600))
        panel = wx.Panel(self, -1)

        #基本静态的文本
        self.te1=wx.StaticText(panel, wx.ID_ANY, "这是个基本的静态文本。", (100, 10))

        #为文本指定前景色和背景色
        self.te2 = wx.StaticText(panel, wx.ID_ANY, "指定文本前景和背景色", (100, 30))
        self.te2.SetForegroundColour("Green")
        self.te2.SetBackgroundColour("Black")

        #指定居中对齐
        text = wx.StaticText(panel, wx.ID_ANY, "居中对齐", (100,50), (160, -1),\
                                wx.ALIGN_CENTER)
        text.SetForegroundColour("White")
        text.SetBackgroundColour("Black")

        #指定右对齐
        text =wx.StaticText(panel, wx.ID_ANY, "居右对齐", (100,70),(160, -1),\
                                wx.ALIGN_RIGHT)

        #指定字体的静态文本的font
        text = wx.StaticText(panel, wx.ID_ANY,"设置文本font", (20,100))
        font=wx.Font(18,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        # font = wx.Font(18,wx.NORMAL)
        text.SetFont(font)

        #设置多行文本
        multiStr ="现在你看到\n的是多行\n文本"
        wx.StaticText(panel, wx.ID_ANY, multiStr, (20, 150))

        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.OnTimer,self.timer)
        self.timer.Start(1000)

    def OnTimer(self,evt):
        t=time.localtime(time.time())
        str1=time.strftime("%Y-%M-%D",t)
        str2=time.strftime("%H:%M:%S",t)
        self.te1.SetLabel(str1)
        self.te2.SetLabel(str2)



def main():
    app = wx.App()
    frame = StaticTextExampleFrame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    main()