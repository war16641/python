"""
给一个倒计时，然后执行关闭或者休眠电脑
要求两个启动参数
动作,计时时间
"""
import wx
from mybaseclasses.emptyclass import EmptyClass
from wx_examples.sandclock import SandClock
import os,sys
if __name__ == '__main__':
    assert len(sys.argv)==3,"启动参数错误"
    if sys.argv[1]=="sleep":
        rt = EmptyClass()
        app=wx.App()
        fr=SandClock(rt,int(sys.argv[2]),"即将睡眠电脑...")
        fr.Show()
        app.MainLoop()
        if rt.answer=='doit':
            os.system("shutdown /h")
    elif sys.argv[1]=="shutdown":
        rt = EmptyClass()
        app=wx.App()
        fr=SandClock(rt,int(sys.argv[2]),"即将关闭电脑...")
        fr.Show()
        app.MainLoop()
        if rt.answer=='doit':
            os.system("shutdown /s")
