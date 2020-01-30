"""
自定义事件
用法步骤：
1.实例化新的类型和绑定器   evt, evt_binder=make_new_event_type()
2.在frame中绑定类型和处理的函数 Frame实例.Bind(evt_binder,Frame实例.处理的函数名)
3.实例化一个新类型事件   e=MyEvent(evt)
                        e.eventArgs=123 #设定参数
4.调用Frame对象处理这个事件 Frame实例.GetEventHandler().ProcessEvent(e)
"""
import wx


class MyEvent(wx.PyCommandEvent):  # 1 定义事件
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
