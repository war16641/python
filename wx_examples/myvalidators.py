"""
一些validators 用于检测用户输入

"""

import wx


# import wx.lib.imagebrowser


class MyNumberValidator(wx.Validator):  # 创建验证器子类
    """
    只能输入数字
    """
    def __init__(self):
        wx.Validator.__init__(self)
        self.ValidInput = ['.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'e','E']
        self.StringLength = 0
        self.Bind(wx.EVT_CHAR, self.OnCharChanged)  # 绑定字符输入事件

    def OnCharChanged(self, event):
        # 得到输入字符的 ASCII 码
        keycode = event.GetKeyCode()
        # 退格（ASCII 码 为8），删除一个字符。
        if keycode == 8:
            self.StringLength -= 1
            # 事件继续传递
            event.Skip()
            return

        # 把 ASII 码 转成字符
        InputChar = chr(keycode)

        if InputChar in self.ValidInput:
            # 第一个字符为 .,非法，拦截该事件，不会成功输入
            if InputChar == '.' and self.StringLength == 0:
                return False
            # 在允许输入的范围，继续传递该事件。
            else:
                event.Skip()
                self.StringLength += 1
                return True
        return False

    def Clone(self):
        return MyNumberValidator()

    def Validate(self, win):  # 1 使用验证器方法
        print(111)
        textCtrl = self.GetWindow()
        text = textCtrl.GetValue()
        valid_text = ''
        for i in text:
            if i in self.ValidInput:
                valid_text += i
        textCtrl.SetValue(valid_text)
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
