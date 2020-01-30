"""
自定义事件 多线程
开启线程后 标题每一秒都会变化
按下暂停 继续 会中断 恢复线程的执行
"""
import wx,time
import threading


class MyTestEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id=-1):
        wx.PyCommandEvent.__init__(self, evtType, id=id)
        self.eventArgs = ""  # 需要传递的参数给这个变量

    @staticmethod
    def make_new_event_type():
        """
        定义一个新的事件类型及他的绑定器
        @return: 事件类型，事件绑定
        """
        evt = wx.NewEventType()
        evt_binder = wx.PyEventBinder(evt)
        return evt, evt_binder


evt,evt_binder=MyTestEvent.make_new_event_type() # 2 创建新的事件类型及他的绑定器


def ticking(mf):
    ct=1
    while True:
        time.sleep(1)
        while not mf.flag:
            time.sleep(1)
        ct+=1
        t = MyTestEvent(evt,-1)  # 4 创建自定义事件对象
        t.eventArgs=str(ct)  # 5 设定参数
        mf.GetEventHandler().ProcessEvent(t)  # 6 处理事件



class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300), pos=(300, 300))
        panel = wx.Panel(self, -1)
        self.Bind(evt_binder, self.HandleEvt)  # 3 在Frame中绑定事件处理函数

        self.button2 = wx.Button(panel, id=-1, pos=(40, 80), label="开启线程")
        self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)

        self.button1 = wx.Button(panel, id=-1, pos=(40, 40), label="暂停")
        self.Bind(wx.EVT_BUTTON, self.OnButton1Click, self.button1)
        self.flag = True

    def OnButton1Click(self,evt):
        if self.flag is False:
            self.flag=True
            self.button1.SetLabel("暂停")
        else:
            self.flag=False
            self.button1.SetLabel("继续")

    def OnButton2Click(self, event):
        self.SetLabel('2')
        self.t=threading.Thread(target=ticking,args=(self,))
        self.t.start()





    def HandleEvt(self,evt):
        self.SetLabel(evt.eventArgs)


def run():
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    run()

