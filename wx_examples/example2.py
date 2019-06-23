"""
自定义事件 多线程
开启线程后 标题每一秒都会变化
按下暂停 继续 会中断 恢复线程的执行
"""
import wx,time
import threading

def ticking(mf):
    ct=1
    while True:
        time.sleep(1)
        while not mf.flag:
            time.sleep(1)
        ct+=1
        evt = MyTestEvent(myEVT_MY_TEST, mf.button2.GetId())  # 5 创建自定义事件对象
        evt.SetEventArgs("test event"+str(ct))  # 6添加数据到事件
        mf.GetEventHandler().ProcessEvent(evt)  # 7 处理事件

class MyTestEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.eventArgs = ""

    def GetEventArgs(self):
        return self.eventArgs

    def SetEventArgs(self, args):
        self.eventArgs = args


myEVT_MY_TEST = wx.NewEventType()  # 2 创建一个事件类型
EVT_MY_TEST = wx.PyEventBinder(myEVT_MY_TEST)  # 3 创建一个绑定器对象


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300), pos=(300, 300))
        panel = wx.Panel(self, -1)
        self.Bind(EVT_MY_TEST, self.HandleEvt)  # 4绑定事件处理函数

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
        self.SetLabel(evt.GetEventArgs())


def run():
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    run()

