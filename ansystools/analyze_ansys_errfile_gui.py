import os
import re

import wx, time
import threading
from ansystools.analze_ansys_errfile import AnsysErrorMessageManager, InfoType, Message, get_re_expression
from mybaseclasses.emptyclass import EmptyClass
from wx_examples.mylistbox import MyListbox


class MyEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id=-1):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.eventArgs = ""


def make_new_event():
    """
    生成新的事件以及他的绑定器
    @return:
    """
    evt = wx.NewEventType()  # 2 创建一个事件类型
    evt_binder = wx.PyEventBinder(evt)  # 3 创建一个绑定器对象
    return evt, evt_binder


EVT_Add, EVT_Add_Binder = make_new_event()
EVT_Modify, EVT_Modify_Binder = make_new_event()
EVT_MakeInfoType, EVT_MakeInfoType_Binder = make_new_event()


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(800, 800))
        panel = wx.Panel(self, -1)

        # 基本静态的文本
        self.te1 = wx.StaticText(panel, wx.ID_ANY, "这是个基本的静态文本。", pos=(30, 0), size=(200, 30))

        self.button2 = wx.Button(panel, id=-1, size=(30, 30), pos=(0, 0), label="打开")
        self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)

        # 列表
        self.lb = MyListbox(panel, -1, size=(600, 200), pos=(0, 160), style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.lb)
        self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnListBoxDClick, self.lb)
        self.lb.mymethod = lambda i: "%d.%s-->%s" % (i.sequence, i.header, i.description)
        # AnsysErrorMessageManager
        self.msgmgr = None  # type:AnsysErrorMessageManager
        self.msgmgr_bk = None  # type:AnsysErrorMessageManager
        self.msgmgr_diff = None  # type:AnsysErrorMessageManager
        self.msgmgr_minusdiff = None  # type:AnsysErrorMessageManager
        self.msgmgr_cur = None  # type:AnsysErrorMessageManager

        # 消息详细信息
        self.detailedbox = wx.TextCtrl(panel, wx.ID_ANY, "#单击以显示详细信息。", pos=(0, 420), size=(600, 80),
                                       style=wx.TE_READONLY | wx.TE_MULTILINE)
        self.infotypebox = wx.TextCtrl(panel, wx.ID_ANY, "#单击以显示详细信息。", pos=(0, 500), size=(600, 80),
                                       style=wx.TE_READONLY | wx.TE_MULTILINE)

        # 按钮 设为备份
        self.button_backup = wx.Button(panel, id=-1, size=(50, 30), pos=(520, 0), label="设为备份")
        self.Bind(wx.EVT_BUTTON, self.OnButtonBackupClick, self.button_backup)

        # 状态栏
        self.stautsbar = self.CreateStatusBar()

        # 单选框
        # self.ck1=wx.RadioButton(panel,-1,"主变量",size=(70,30),pos=(0,50),style=wx.RB_GROUP)
        # self.ck1=wx.RadioButton(panel,-1,"备份变量",size=(70,30),pos=(0,70))
        # self.Bind(wx.EVT_RADIOBUTTON,self.OnRidioButton,self.ck1)
        t = ['主变量      ', '备份变量    ', '差量     ', '负差量    ']
        self.radiobox2 = wx.RadioBox(panel, -1, "射频设备选择", pos=(150, 00), size=(300, 20), choices=t,
                                     style=wx.RA_SPECIFY_ROWS)
        self.Bind(wx.EVT_RADIOBOX, self.OnRidioButton, self.radiobox2)

        # 打开文件的路径
        self.filepath = ""

        # checkbox
        self.cb = wx.CheckBox(panel, -1, pos=(300, 140), size=(200, 20), label="只显示未知类型消息")
        self.Bind(wx.EVT_CHECKBOX, self.OnShowUnkownOnly, self.cb)

        # 子窗口 按钮
        self.child = MyFrameChild(prt=self)
        self.bt_child = wx.Button(panel, id=-1, pos=(520, 100), size=(80, 30), label="已知类型管理")
        self.Bind(wx.EVT_BUTTON, self.OnOpenChild, self.bt_child)

        # 制作消息类型
        self.bt_newinfotype = wx.Button(panel, id=-1, pos=(520, 130), size=(80, 30), label="制作消息类型")
        self.Bind(wx.EVT_BUTTON, self.OnBt_makeinfotype, self.bt_newinfotype)

    def OnButton2Click(self, event):
        dlg = wx.FileDialog(self, "Open err file", wildcard="err files (*.err)|*.err",
                            style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.filepath = dlg.GetPath()
            self.te1.SetLabel(dlg.GetPath())
            self.msgmgr = AnsysErrorMessageManager.load_from_file(dlg.GetPath())
            pathname, tmpfilename = os.path.split(dlg.GetPath())
            self.radiobox2.SetItemLabel(0, "主变量%s" % tmpfilename[0:-4])
            # 在列表框中显示信息 发送复选框消息
            self.radiobox2.SetSelection(0)
            evt = EmptyClass()
            evt.Selection = 0
            self.OnRidioButton(evt)

            self.stautsbar.SetStatusText("载入文件至主变量")
            # t=wx.CommandEvent(wx.EVT_RADIOBOX.typeId,self.radiobox2.GetId())
            # t.Selection=1
            # wx.PostEvent(self.GetEventHandler(),t)

            # self.lb.Clear()
            # for i in self.msgmgr.msg_array:
            #     self.lb.Append("%s-->%s"%(i.header ,i.description))
        dlg.Destroy()

    def OnListBox(self, evt):
        if self.msgmgr_cur is None:  # msgmgr_cur 还没读入数据
            self.stautsbar.SetStatusText("暂无数据")
            return

        msg = self.lb.selected_data
        # 显示消息
        self.detailedbox.SetValue(
            "%s\n%s" % (msg.header, msg.description))
        # 显示消息类型
        t = msg.infotype_id
        t = InfoType.known_infotype[t]
        self.infotypebox.SetValue(
            "%s\n%s" % (t.name, t.description))
        # #获取消息id
        # if self.cb.GetValue()==0:#未开启过滤
        #     r=evt.Selection
        # else:#开启过滤
        #     p=re.compile(r"\d+\.")
        #     r=p.search(evt.String)
        #     r=int(r.group(0)[0:-1])
        # #显示消息
        # self.detailedbox.SetValue("%s\n%s"%(self.msgmgr_cur.msg_array[r].header,self.msgmgr_cur.msg_array[r].description))
        # #显示消息类型
        # t=self.msgmgr_cur.msg_array[r].infotype_id
        # t=InfoType.known_infotype[t]
        # self.infotypebox.SetValue(
        #     "%s\n%s" % (t.name, t.description))

        # #显示消息
        # self.detailedbox.SetValue("%s\n%s"%(self.msgmgr_cur.msg_array[evt.Selection].header,self.msgmgr_cur.msg_array[evt.Selection].description))
        # #显示消息类型
        # t=self.msgmgr_cur.msg_array[evt.Selection].infotype_id
        # t=InfoType.known_infotype[t]
        # self.infotypebox.SetValue(
        #     "%s\n%s" % (t.name, t.description))

    def OnListBoxDClick(self, evt):  # 双击diff变量显示主变量位置
        if self.msgmgr_cur != self.msgmgr_diff and self.msgmgr_cur != self.msgmgr_minusdiff:
            if self.cb.GetValue() == 0:
                self.stautsbar.SetStatusText("无法响应双击事件")
                return
            else:  # 只显示 打开 ， 双击关闭只显示
                s = self.lb.selected_data.sequence
                self.cb.SetValue(0)  # 关闭只显示
                evt = EmptyClass()
                evt.Selection = self.radiobox2.GetSelection()
                self.OnRidioButton(evt)  # 刷新显示
                self.lb.SetSelection(s)
                return

        if self.msgmgr is None:
            self.stautsbar.SetStatusText("主变量暂无数据")
            return
        if self.msgmgr_cur is self.msgmgr_diff:
            t = self.msgmgr_diff.msg_array[evt.Selection]
            self.radiobox2.SetSelection(0)
            evt = EmptyClass()
            evt.Selection = 0
            self.OnRidioButton(evt)
            self.lb.SetSelection(t.sequence)
        elif self.msgmgr_cur is self.msgmgr_minusdiff:
            t = self.msgmgr_minusdiff.msg_array[evt.Selection]
            self.radiobox2.SetSelection(1)
            evt = EmptyClass()
            evt.Selection = 1
            self.OnRidioButton(evt)
            self.lb.SetSelection(t.sequence)
        pass

    def OnButtonBackupClick(self, evt):
        self.msgmgr_bk = self.msgmgr
        self.stautsbar.SetStatusText("已设为备份")
        # self.stautsbar.Show(True)
        pathname, tmpfilename = os.path.split(self.filepath)
        self.radiobox2.SetItemLabel(1, "备份变量%s" % tmpfilename[0:-4])

    def OnRidioButton(self, evt):

        def script(x):  # lb更新显示
            self.msgmgr_cur = x  # 设置msgmgr_cur
            self.lb.Clear()
            if x is None:
                self.lb.Append("无数据")
                return
            for i in x.msg_array:
                # self.lb.Append("%d.%s-->%s"%(i.sequence,i.header ,i.description))
                self.lb.Append(i)

        # 无论怎么样 都要设 不 只显示未知变量
        self.cb.SetValue(0)

        if evt.Selection == 1:
            script(self.msgmgr_bk)
        elif evt.Selection == 0:
            script(self.msgmgr)
        elif evt.Selection == 2:
            if self.msgmgr is not None and self.msgmgr_bk is not None:
                self.msgmgr_diff = self.msgmgr - self.msgmgr_bk  # 相减
                script(self.msgmgr_diff)
            else:
                self.stautsbar.SetStatusText("主变量或备份变量未准备，跳转到主变量显示")
                self.radiobox2.SetSelection(0)
                evt = EmptyClass()
                evt.Selection = 0
                self.OnRidioButton(evt)
        elif evt.Selection == 3:
            if self.msgmgr is not None and self.msgmgr_bk is not None:
                self.msgmgr_minusdiff = self.msgmgr_bk - self.msgmgr  # 相减
                script(self.msgmgr_minusdiff)
            else:
                self.stautsbar.SetStatusText("主变量或备份变量未准备，跳转到主变量显示")
                self.radiobox2.SetSelection(0)
                evt = EmptyClass()
                evt.Selection = 0
                self.OnRidioButton(evt)

    def OnShowUnkownOnly(self, evt):
        # 事件 只显示未知类型消息
        if self.msgmgr_cur is None:
            self.stautsbar.SetStatusText("无法执行 只显示未知消息 命令")
            self.cb.SetValue(0)
            return

        if evt.Int == 1:
            t = []
            for i in self.msgmgr_cur.msg_array:
                if i.infotype_id == len(InfoType.known_infotype) - 1:
                    t.append(i)
            self.lb.Clear()
            for i in t:
                self.lb.Append(i)
            self.stautsbar.SetStatusText("共有%d个未知类型消息" % len(t))
        elif evt.Int == 0:
            t = EmptyClass()
            t.Selection = self.radiobox2.GetSelection()
            self.OnRidioButton(t)
        else:
            raise Exception("未知错误")
        pass

    def OnOpenChild(self, evt=None):
        self.Disable()
        self.child.Show()

    def ReclassifyMsg(self):
        # 重新对所有AnsysErrorMessageManager进行重新分类
        # 在修改 已知消息类型 后 要执行
        t = [self.msgmgr, self.msgmgr_bk]
        for i in t:
            if i is not None:
                i.refresh()
        self.lb.MyRefresh()
        # 重新设置
        t = EmptyClass()
        t.Selection = 0
        self.OnRidioButton(t)
        self.cb.SetValue(0)

    def OnBt_makeinfotype(self, evt):
        if self.lb.selected_data is None:
            return
        if self.lb.selected_data.infotype_id != len(InfoType.known_infotype) - 1:
            return  # 没有选中数据 或者 数据不是未知类型 就
        # 打开类型管你
        self.OnOpenChild()
        # 投递制作消息
        evt = MyEvent(EVT_MakeInfoType)
        evt.eventArgs = self.lb.selected_data
        self.child.GetEventHandler().ProcessEvent(evt)


class MyFrameChild(wx.Frame):
    def __init__(self, prt):
        super(MyFrameChild, self).__init__(parent=prt, id=-1, size=(600, 600))
        self.prt = self.GetParent()  # type:MyFrame
        self.SetLabel("消息类型管理")
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.Bind(EVT_MakeInfoType_Binder, self.OnEVT_make_info_type)

        panel = wx.Panel(self, -1)

        # 列表
        self.lb = MyListbox(panel, -1, pos=(0, 30), size=(500, 500))
        self.lb.mymethod = lambda x: "%s-->%s" % (x.name, x.description)
        self.Refresh_lb()

        # 添加按钮
        self.bt_add = wx.Button(panel, -1, pos=(500, 30), size=(30, 30), label='添加')
        self.Bind(wx.EVT_BUTTON, self.OnShowChild_Add, self.bt_add)

        # 添加的 frame
        self.child_add = MyFrameAdd(self)

        self.Bind(EVT_Add_Binder, self.OnEVT_Add)  # 4绑定事件处理函数

        # 修改按钮
        self.bt_modify = wx.Button(panel, -1, pos=(500, 80), size=(30, 30), label='修改')
        self.Bind(wx.EVT_BUTTON, self.OnShowChild_Modify, self.bt_modify)
        self.Bind(EVT_Modify_Binder, self.OnEVT_Modify)

        # 重分类
        self.bt_reclassify = wx.Button(panel, -1, pos=(500, 130), size=(60, 30), label='重分类')
        self.Bind(wx.EVT_BUTTON, self.OnEVT_reclassify, self.bt_reclassify)

        # 保存已知类型
        self.bt_save = wx.Button(panel, -1, pos=(500, 160), size=(80, 30), label='保存已知类型')
        self.Bind(wx.EVT_BUTTON, self.OnBt_save, self.bt_save)

    def OnCloseWindow(self, evt):
        self.GetParent().Enable()
        self.Show(False)  # 关闭时 隐藏

    def OnShowChild_Add(self, evt):
        self.Disable()
        self.child_add.SetInitialText()
        self.child_add.mode = "add"
        self.child_add.Show()

    def OnShowChild_Modify(self, evt):
        if self.lb.selected_data is None:
            return
        self.Disable()
        self.child_add.SetInitialText(self.lb.selected_data)
        self.child_add.mode = "modify"
        self.child_add.Show()

    def OnEVT_Add(self, evt):
        InfoType.append_infotype(evt.eventArgs)
        # InfoType.known_infotype.insert(-1,evt.eventArgs)
        self.Refresh_lb()
        self.lb.SetSelection(len(InfoType.known_infotype) - 2)
        # print(evt.eventArgs.name)

    def OnEVT_Modify(self, evt):
        t = self.lb.Selection
        self.Refresh_lb()
        self.lb.SetSelection(t)

    def Refresh_lb(self):  # 刷新lb
        self.lb.Clear()
        for i in InfoType.known_infotype:
            self.lb.Append(i)

    def OnEVT_reclassify(self, evt):
        self.prt.ReclassifyMsg()

    def OnEVT_make_info_type(self, evt):
        # 制作
        self.Disable()
        self.child_add.SetInitialText()
        self.child_add.mode = "make"
        self.child_add.unknownmsg = evt.eventArgs
        self.child_add.detailed_ctrl.SetValue("%s\n%s" % (evt.eventArgs.header, evt.eventArgs.description))
        self.child_add.pattern_ctrl.SetValue(get_re_expression(evt.eventArgs.description))
        self.child_add.Show()

    def OnBt_save(self, evt):
        InfoType.save(r"E:\我的文档\python\GoodToolPython\ansystools\消息类型库.xlsx")


class MyFrameAdd(wx.Frame):
    def __init__(self, prt):
        super(MyFrameAdd, self).__init__(prt, -1, size=(500, 400))
        self.prt = self.GetParent()  # type:MyFrameChild
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

        panel = wx.Panel(self, -1)

        self.mode = "unset"  # "add" "modify" "make"
        self.target = None  # type:InfoType #当mode=“modify"时 这个变量标识修改的目标
        self.unknownmsg = None  # type:Message #当mode=“make"时 这个变量标识制作的目标
        # name
        self.name_ctrl = wx.TextCtrl(panel, -1, pos=(80, 0), size=(400, 25))
        wx.StaticText(panel, -1, pos=(0, 0), size=(70, 25), label='name:')
        # pattern
        self.pattern_ctrl = wx.TextCtrl(panel, -1, pos=(80, 25), size=(400, 75))
        wx.StaticText(panel, -1, pos=(0, 25), size=(70, 25), label='pattern:')
        # description
        self.description_ctrl = wx.TextCtrl(panel, -1, pos=(80, 100), size=(400, 75))
        wx.StaticText(panel, -1, pos=(0, 100), size=(70, 25), label='description:')

        # 确认
        self.apply_bt = wx.Button(panel, -1, pos=(80, 180), size=(60, 25), label="确认")
        self.Bind(wx.EVT_BUTTON, self.OnApply, self.apply_bt)

        # 取消
        self.cancel_bt = wx.Button(panel, -1, pos=(180, 180), size=(60, 25), label="取消")
        self.Bind(wx.EVT_BUTTON, self.OnCloseWindow, self.cancel_bt)

        # 消息显示
        self.detailed_ctrl = wx.TextCtrl(panel, -1, pos=(0, 205), size=(500, 100),
                                         style=wx.TE_READONLY | wx.TE_MULTILINE)

    def OnCloseWindow(self, evt=None):
        self.prt.Enable()
        self.Show(False)  # 关闭时 隐藏

    def OnApply(self, evt):

        if self.mode == "add":
            # 投递事件
            t = InfoType(name=self.name_ctrl.GetValue(),
                         pattern=self.pattern_ctrl.GetValue(),
                         description=self.description_ctrl.GetValue())
            evt = MyEvent(EVT_Add)
            evt.eventArgs = t
            self.prt.GetEventHandler().ProcessEvent(evt)
            self.OnCloseWindow()
        elif self.mode == "modify":
            self.target.name = self.name_ctrl.GetValue()
            self.target.pattern = self.pattern_ctrl.GetValue()
            self.target.description = self.description_ctrl.GetValue()

            evt = MyEvent(EVT_Modify)
            self.prt.GetEventHandler().ProcessEvent(evt)
            self.OnCloseWindow()
        elif self.mode == "make":
            p = re.compile(self.pattern_ctrl.GetValue())
            r = p.search(self.unknownmsg.description)
            if r is not None:  # 可以识别
                if len(self.name_ctrl.GetValue()) != 0:
                    t = InfoType(name=self.name_ctrl.GetValue(),
                                 pattern=self.pattern_ctrl.GetValue(),
                                 description=self.description_ctrl.GetValue())
                    evt = MyEvent(EVT_Add)
                    evt.eventArgs = t
                    self.prt.GetEventHandler().ProcessEvent(evt)
                    self.OnCloseWindow()
                else:
                    dlg = wx.MessageDialog(self, u"没有name", u"标题信息", wx.OK)
                    dlg.ShowModal()
                    dlg.Destroy()
            else:  # 不可以识别
                dlg = wx.MessageDialog(self, u"pattern不正确", u"标题信息", wx.OK)
                dlg.ShowModal()
                dlg.Destroy()
        else:
            raise Exception("未知错误")

    def SetInitialText(self, x=None):  # 设置textctrl的初始内容
        if x is None:
            self.description_ctrl.Clear()
            self.name_ctrl.Clear()
            self.pattern_ctrl.Clear()
            self.target = None
        elif isinstance(x, InfoType):
            self.name_ctrl.SetLabel(x.name)
            self.pattern_ctrl.SetLabel(x.pattern)
            self.description_ctrl.SetLabel(x.description)
            self.target = x
        else:
            raise Exception("未知参数。")


def run():
    app = wx.App()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()


if __name__ == '__main__':
    run()
