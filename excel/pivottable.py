"""
数据透视表 模仿excel
重要提醒：bind事件使用控件.bind()，不要使用窗口.bind(,,控件)的做法
绑定listbox的鼠标事件后 无法选中item
"""
import wx
import wx.grid
from GoodToolPython.excel.excel import FlatDataModel
import os
from GoodToolPython.wx_examples.mylistbox import MyListbox
from matplotlib.backends import backend_wxagg
from matplotlib.figure import Figure
from statistics_nyh import absmax, absmin

statfuncs={'max':lambda x:max(x),
           'min':lambda x:min(x),
           'count':lambda x:len(x),
           'absmax':lambda x:absmax(x),
           'absmin':lambda x:absmin(x),
           'absmax1': lambda x: abs(absmax(x)),
           'absmin1': lambda x: abs(absmin(x)),#绝对值
           }
class StatFuncInfo:#统计的信息
    def __init__(self,field,func,statname=None):
        self.fieldname=field
        self.funcname=func
        if statname is None:
            statname=field
        self.statname=statname #统计后的字段名

class PivotTable(wx.Frame):
    def __init__(self):
        super(PivotTable, self).__init__(None, title="数据透视表", size=(1920, 900))

        #字段
        self.fdm=None #type:FlatDataModel
        # initial ui
        panel = wx.Panel(self, -1)
        sizer = wx.GridBagSizer()

        self.st_filein = wx.StaticText(panel, label="文件:")
        sizer.Add(self.st_filein, pos=(0, 0), flag=wx.ALL, border=5)
        self.tc_filein = wx.TextCtrl(panel,size=(300, 20))
        self.tc_filein.Value=r"E:\我的文档\python\GoodToolPython\excel\test1.xlsx"
        sizer.Add(self.tc_filein, pos=(0, 1), span=(1,5), flag= wx.EXPAND | wx.ALL, border=5)
        self.bt_filein=wx.Button(panel,label="打开")
        sizer.Add(self.bt_filein, pos=(0, 10), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)
        self.Bind(wx.EVT_BUTTON, self.OnFilein, self.bt_filein)

        self.st_fileinfo = wx.StaticText(panel, label="无")
        sizer.Add(self.st_fileinfo, pos=(1, 0), flag=wx.ALL, border=5)

        self.st_1 = wx.StaticText(panel, label="字段名")
        sizer.Add(self.st_1, pos=(2, 0), flag=wx.ALL, border=5)
        self.lb_vn=wx.ListBox(panel,size=(200,500))
        sizer.Add(self.lb_vn, pos=(2, 1),span=(5,2), flag=wx.ALL, border=5)
        self.lb_vn.Bind(wx.EVT_CHAR, self.OnlbvnChar)
        self.lb_vn.Bind(wx.EVT_KILL_FOCUS,self.OnLbKillFocus)

        self.st_2 = wx.StaticText(panel, label="分类字段名")
        sizer.Add(self.st_2, pos=(2, 3), flag=wx.ALL, border=5)
        self.lb_vnclass=wx.ListBox(panel,size=(200,200))
        sizer.Add(self.lb_vnclass, pos=(2, 4),span=(2,2), flag=wx.ALL, border=5)
        self.lb_vnclass.Bind(wx.EVT_CHAR, self.OnLbvnclassChar)
        self.lb_vnclass.Bind(wx.EVT_KILL_FOCUS, self.OnLbKillFocus)

        self.st_3 = wx.StaticText(panel, label="统计字段名")
        sizer.Add(self.st_3, pos=(5, 3), flag=wx.ALL, border=5)
        self.lb_vnstat=MyListbox(panel,size=(200,200))
        self.lb_vnstat.mymethod=lambda x:x.fieldname+":"+x.funcname
        sizer.Add(self.lb_vnstat, pos=(5, 4),span=(2,2), flag=wx.ALL, border=5)
        self.lb_vnstat.Bind(wx.EVT_CHAR, self.OnLbvnstatChar)
        # self.lb_vnstat.Bind(wx.EVT_KILL_FOCUS, self.OnLbKillFocus)
        self.lb_vnstat.Bind(wx.EVT_LISTBOX,self.OnLbstatSelectItem)

        self.st_4 = wx.StaticText(panel, label="统计函数设置：")
        sizer.Add(self.st_4, pos=(8, 0),flag=wx.ALL, border=5)
        self.st_statfield = wx.StaticText(panel, label="无", size=(60,20))
        sizer.Add(self.st_statfield, pos=(8, 1), flag=wx.ALL, border=5)
        self.cb_statfunc = wx.ComboBox(panel, value='max',choices=list(statfuncs.keys()),style=wx.CB_READONLY, size=(60,20))
        sizer.Add(self.cb_statfunc, pos=(8, 3), flag=wx.ALL, border=5)
        self.cb_statfunc.Bind(wx.EVT_COMBOBOX,self.OnCbstatfuncSelect)
        self.tc_statname=wx.TextCtrl(panel,size=(120,20))
        sizer.Add(self.tc_statname, pos=(8, 4),span=(1,2), flag=wx.ALL, border=5)
        self.bt_statinfo=wx.Button(panel,label='提交')
        sizer.Add(self.bt_statinfo, pos=(8, 6),span=(1,1), flag=wx.ALL, border=5)
        self.bt_statinfo.Bind(wx.EVT_BUTTON,self.OnBtstatinfo)

        self.bt_excute = wx.Button(panel, label='执行')
        sizer.Add(self.bt_excute, pos=(9, 0), span=(1, 1), flag=wx.ALL, border=5)
        self.bt_excute.Bind(wx.EVT_BUTTON, self.OnBtexcute)


        canvaspanel=wx.Panel(panel, size=(600, 600))
        sizer.Add(canvaspanel, pos=(0, 12), span=(8, 1), flag=wx.ALL, border=5)
        self.canvas=backend_wxagg.FigureCanvasWxAgg(canvaspanel, -1, Figure())
        panel.SetSizerAndFit(sizer)
    def OnFilein(self,event=None):
        self.fdm=FlatDataModel.load_from_excel_file(fullname=self.tc_filein.Value)
        pathname, tmpfilename = os.path.split(self.tc_filein.Value)
        self.st_fileinfo.SetLabel("%s,字段数：%d,个数：%d"%(tmpfilename,len(self.fdm.vn),len(self.fdm)))

        self.reset()
    def reset(self):
        self.lb_vn.Clear()
        for i in self.fdm.vn:
            self.lb_vn.Append(i)

    def OnlbvnChar(self, event=None):
        # print("OnlbvnChar")
        if -1 == self.lb_vn.Selection:
            return
        key = event.GetKeyCode()  # 获得键盘事件的键值

        if key == wx.WXK_F1:  # 移动到vnclass中
            # print('f1')
            t=self.lb_vn.StringSelection
            self.lb_vnclass.Append(t)
            self.lb_vn.Delete(self.lb_vn.Selection)
        elif key == wx.WXK_F2:  # 移动到vnstat中
            t=self.lb_vn.StringSelection
            self.lb_vnstat.Append(StatFuncInfo(t,'max')) #默认max作为统计函数
            # self.lb_vn.Delete(self.lb_vn.Selection)
    def OnLbvnclassChar(self, event=None):
        key = event.GetKeyCode()  # 获得键盘事件的键值

        if key == wx.WXK_F3:  # 移回到vnclass中
            if -1==self.lb_vnclass.Selection:
                return
            t=self.lb_vnclass.StringSelection
            self.lb_vn.Insert(t,0)
            self.lb_vnclass.Delete(self.lb_vnclass.Selection)

    def OnLbvnstatChar(self,event=None):
        key = event.GetKeyCode()  # 获得键盘事件的键值
        if key == wx.WXK_F3:  # 删除
            if -1 == self.lb_vnstat.Selection:
                return
            t=self.lb_vnstat.selected_data
            self.lb_vnstat.mydata.remove(t)
            self.lb_vnstat.MyRefresh()


    def OnPanelMouseEvent(self,evt=None):
        print("panel")

    def test1(self,evt=None):
        print('test1')

    def OnLbKillFocus(self,evt=None):
        # self.lb_vn.SetSelection()
        evt.EventObject.SetSelection(-1)


    def OnLbstatSelectItem(self,evt=None):
        fieldname=self.lb_vnstat.selected_data.fieldname
        funcname=self.lb_vnstat.selected_data.funcname
        self.st_statfield.SetLabel(fieldname)
        self.cb_statfunc.SetSelection(list(statfuncs.keys()).index(funcname))
        self.tc_statname.Value=self.lb_vnstat.selected_data.statname

    def OnCbstatfuncSelect(self,evt=None):
        pass
        # t=self.lb_vnstat.selected_data
        # if t is None:
        #     return
        # t.funcname=self.cb_statfunc.Value
        # self.lb_vnstat.MyRefresh()
    def OnBtstatinfo(self,evt=None):
        t = self.lb_vnstat.selected_data
        if t is None:
            return
        t.funcname=self.cb_statfunc.Value
        t.statname=self.tc_statname.Value
        self.lb_vnstat.MyRefresh()

    def OnBtexcute(self,evt=None):
        if self.fdm is None or len(self.lb_vnstat.mydata)==0:
            return
        #收集分类字段
        classify_names=[]
        for i in range(self.lb_vnclass.Count):
            classify_names.append(self.lb_vnclass.GetString(i))
        #收集statistics_func
        statistics_func=[]
        for i in self.lb_vnstat:
            t=[i.fieldname,statfuncs[i.funcname],i.statname]
            statistics_func.append(t)
        #执行
        o=self.fdm.flhz(classify_names=classify_names,statistics_func=statistics_func)
        # o.show_in_excel()
        axes=self.canvas.figure.gca()
        axes.cla()
        axes.plot(o[o.vn[0]],o[o.vn[1]])
        self.canvas.draw()
        pass


if __name__ == '__main__':
    app = wx.App()
    frame = PivotTable()
    frame.Show()
    app.MainLoop()
