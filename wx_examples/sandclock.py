import wx

import time
from mybaseclasses.emptyclass import EmptyClass

class SandClock(wx.Frame):
    """
    这是可视化的倒数时间的app
    rtc用来存储结果   rtc.answer：'stop' 用户终止
                                 'doit' 计时完成
    """

    def __init__(self, rtc:EmptyClass,timelength=3,hint="这是提示"):
        wx.Frame.__init__(self, None, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(460, 620), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        self.Center()
        self.SetTitle("倒计时")

        assert timelength<999,"计时时间小于999s"
        self.timelength=int(timelength)
        self.rtc=rtc

        panel=wx.Panel(self)
        sizer = wx.GridBagSizer()

        self.st_hint = wx.StaticText(panel, label=hint)
        sizer.Add(self.st_hint, pos=(0, 0), flag=wx.ALL | wx.ALIGN_CENTER)
        font=wx.Font(30,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        self.st_hint.SetFont(font)
        self.st_hint.SetForegroundColour("green")



        self.st=wx.StaticText(panel,label=str(self.timelength))
        self.st.SetForegroundColour("red")
        sizer.Add(self.st,pos=(1,0),flag=wx.ALL|wx.ALIGN_CENTER)
        font=wx.Font(200,wx.DECORATIVE,wx.ITALIC,wx.NORMAL)
        self.st.SetFont(font)

        self.bt_stop=wx.Button(panel,size=(400,300),label="停止")
        font = wx.Font(120, wx.DECORATIVE, wx.ITALIC, wx.NORMAL)
        self.bt_stop.SetFont(font)
        self.Bind(wx.EVT_BUTTON,self.OnStop,self.bt_stop)
        sizer.Add(self.bt_stop, pos=(2, 0), flag=wx.ALL | wx.ALIGN_CENTER)




        self.timer=wx.Timer(self)
        self.Bind(wx.EVT_TIMER,self.OnTimer,self.timer)
        self.timer.Start(900)
        self.start_time=time.time()#起始时间














        panel.SetSizerAndFit(sizer)
        self.Bind(wx.EVT_CLOSE,self.OnClose,self)


    def OnTimer(self,evt=None):
        # print(1)
        t=time.time()
        elapse_time=round(t-self.start_time)
        self.st.SetLabel(str(self.timelength-elapse_time))
        if elapse_time==self.timelength:#计时完成
            self.Destroy()
            self.rtc.answer='doit'

    def OnStop(self,evt):#用户终止计时
        self.Destroy()
        self.rtc.answer = 'stop'

    def OnClose(self,evt):
        self.Destroy()
        self.rtc.answer = 'stop' #关闭按钮也视为用户停止



if __name__ == '__main__':
    rt=EmptyClass()
    app = wx.App()
    frame = SandClock(rt,3)
    frame.Show()

    app.MainLoop()
    print(rt.answer)