import wx
from myfile import is_number
from wx_examples.myvalidators import MyNumberValidator


class MyNumberTextCtrl(wx.TextCtrl):
    """
    数字文本框
    有validator的输入限制
    重载的value属性 可通过他读取设置值：
    """

    def __init__(self, parent, value_on_invalid=0,text_on_invalid=0, *args, **kwargs):
        super().__init__(parent, validator=MyNumberValidator(), *args, **kwargs)
        self.value_on_invalid = value_on_invalid  # 当读取的不为数时 返回的值，通常为0或者none
        self.text_on_invalid=text_on_invalid#当读取的不为数时，文本框内设置的值

    @property
    def Value(self) -> float:  # 获取数字
        t = super().Value
        f, v = is_number(t)
        if f is False:  # 非法数
            super().ChangeValue(str(self.text_on_invalid))
            return self.value_on_invalid
        else:
            return v

    @Value.setter  # 设置数
    def Value(self, v):
        """

        @param v: 可以是float 或者数字的字符串
        @return:
        """
        v = float(v)
        super().ChangeValue(str(v))


class Frame(wx.Frame):
    def __init__(self):
        super(Frame, self).__init__(None)
        panel = wx.Panel(self)
        self.tc1 = wx.TextCtrl(panel)
        # print(self.tc1.__base__)
        self.Bind(wx.EVT_TEXT, self.OnWhat, self.tc1)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnWhat, self.tc1)
        self.tc2 = MyNumberTextCtrl(panel, pos=(100, 100))
        self.bt = wx.Button(panel, pos=(0, 100))
        self.Bind(wx.EVT_BUTTON, self.sw, self.bt)
        self.bt2 = wx.Button(panel, pos=(0, 50))
        self.Bind(wx.EVT_BUTTON, self.st, self.bt2)

    def OnWhat(self, evt=None):
        print("what")
        pass

    def sw(self, evt):
        print(self.tc2.Value)

    def st(self, evt):
        self.tc2.Value = self.tc1.Value

if __name__ == '__main__':

    app = wx.App()
    fr = Frame()
    fr.Show()
    app.MainLoop()