"""
按钮 打开文件
"""


import wx,time
import threading



class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(300, 300), pos=(300, 300))
        panel = wx.Panel(self, -1)


        self.button2 = wx.Button(panel, id=-1, pos=(40, 80), label="打开")
        self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)



    def OnButton2Click(self, event):
        # self.SetLabel('2')
        file_wildcard = "Paint files(*.paint)|*.paint|All files(*.*)|*.*"
        dlg = wx.FileDialog(self, "Open XYZ file", wildcard="XYZ files (*.*)|*.*",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            print(dlg.GetPath())
        dlg.Destroy()








def run():
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    run()

