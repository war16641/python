"""
数据透视表 模仿excel
重要提醒：bind事件使用控件.bind()，不要使用窗口.bind(,,控件)的做法
绑定listbox的鼠标事件后 无法选中item
"""
from typing import List

import matplotlib
import wx
import wx.grid
from GoodToolPython.excel.excel import FlatDataModel, myunique
import os
from GoodToolPython.wx_examples.mylistbox import MyListbox
# from matplotlib.backends import backend_wxagg
from matplotlib.figure import Figure
from statistics_nyh import absmax, absmin
import matplotlib as mpl
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np



# 解决中文乱码问题
#sans-serif就是无衬线字体，是一种通用字体族。
#常见的无衬线字体有 Trebuchet MS, Tahoma, Verdana, Arial, Helvetica, 中文的幼圆、隶书等等。
mpl.rcParams['font.sans-serif']=['SimHei'] #指定默认字体 SimHei为黑体
mpl.rcParams['axes.unicode_minus']=False #用来正常显示负号



#这个变量保存字符与函数对应关系
statfuncs={'max':lambda x:max(x),
           'min':lambda x:min(x),
           'sum':lambda x:sum(x),
           'count':lambda x:len(x),
           'absmax':lambda x:absmax(x),
           'absmin':lambda x:absmin(x),
           'absmax1': lambda x: abs(absmax(x)),
           'absmin1': lambda x: abs(absmin(x)),#绝对值
           }
class StatFuncInfo:#统计的信息
    y=None#做图的y变量
    y2=None#做图 右边轴的变量
    def __init__(self,field,func,statname=None,yfield="no"):
        self.fieldname=field
        self.funcname=func
        if statname is None:
            statname=field
        self.statname=statname #统计后的字段名
        if yfield=="y":
            StatFuncInfo.y=self
        elif yfield=="y2":
            StatFuncInfo.y2=self
        elif yfield=="no":
            pass
        else:
            raise TypeError

    @property
    def yfield(self):
        if StatFuncInfo.y is self:
            return 'y'
        if StatFuncInfo.y2 is self:
            return 'y2'
        return 'no'

class ClassifyFieldInfo:
    """
    在fdm的flhz函数中只有分类变量
    但是在本程序中分类变量分为：自变量和图例变量 自变量只能有一个 其他都是图例变量 如果要做图的话
    """
    def __init__(self,fieldname,islegend=False):
        self.fieldname=fieldname
        self.islegend=islegend#是否是图例变量

    @staticmethod
    def dispinlistbox(x):
        #在mylistbox中显示方法
        st=x.fieldname
        if x.islegend:
            st+= ",图例变量"

        return st

    @staticmethod
    def dispinlistbox1(x):
        st = x.fieldname
        st+=":"+x.funcname
        if x.yfield!="no":
            st+=","+x.yfield
        return st

class PivotTable(wx.Frame):
    def __init__(self):
        super(PivotTable, self).__init__(None, title="数据透视表", size=(850, 800))

        #字段
        self.fdm=None #type:FlatDataModel
        self.rfdm=None#type:FlatDataModel
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
        self.lb_vnclass=MyListbox(panel,size=(200,200))
        self.lb_vnclass.mymethod=ClassifyFieldInfo.dispinlistbox#指定显示方法
        sizer.Add(self.lb_vnclass, pos=(2, 4),span=(2,2), flag=wx.ALL, border=5)
        self.lb_vnclass.Bind(wx.EVT_CHAR, self.OnLbvnclassChar)
        self.lb_vnclass.Bind(wx.EVT_KILL_FOCUS, self.OnLbKillFocus)

        self.st_3 = wx.StaticText(panel, label="统计字段名")
        sizer.Add(self.st_3, pos=(5, 3), flag=wx.ALL, border=5)
        self.lb_vnstat=MyListbox(panel,size=(200,200))
        self.lb_vnstat.mymethod=ClassifyFieldInfo.dispinlistbox1#指定显示方法
        sizer.Add(self.lb_vnstat, pos=(5, 4),span=(2,2), flag=wx.ALL, border=5)
        self.lb_vnstat.Bind(wx.EVT_CHAR, self.OnLbvnstatChar)
        # self.lb_vnstat.Bind(wx.EVT_KILL_FOCUS, self.OnLbKillFocus)
        self.lb_vnstat.Bind(wx.EVT_LISTBOX,self.OnLbstatSelectItem)

        self.st_4 = wx.StaticText(panel, label="统计函数设置：")
        sizer.Add(self.st_4, pos=(8, 0),flag=wx.ALL, border=5)
        self.st_statfield = wx.StaticText(panel, label="无", size=(60,20))
        sizer.Add(self.st_statfield, pos=(8, 1), flag=wx.ALL, border=5)
        self.cb_statfunc = wx.ComboBox(panel, value='max',choices=list(statfuncs.keys()),style=wx.CB_READONLY, size=(60,20))
        sizer.Add(self.cb_statfunc, pos=(8, 2), flag=wx.ALL, border=5)
        self.cb_statfunc.Bind(wx.EVT_COMBOBOX,self.OnCbstatfuncSelect)
        self.tc_statname=wx.TextCtrl(panel,size=(120,20))
        sizer.Add(self.tc_statname, pos=(8, 3),span=(1,2), flag=wx.ALL, border=5)
        self.cb_yfield = wx.ComboBox(panel, value='no',choices=["no",'y','y2'],style=wx.CB_READONLY, size=(60,30))
        sizer.Add(self.cb_yfield, pos=(8, 5), flag=wx.ALL, border=5)
        self.bt_statinfo=wx.Button(panel,label='提交')
        sizer.Add(self.bt_statinfo, pos=(8, 6),span=(1,1), flag=wx.ALL, border=5)
        self.bt_statinfo.Bind(wx.EVT_BUTTON,self.OnBtstatinfo)

        self.bt_excute = wx.Button(panel, label='执行')
        sizer.Add(self.bt_excute, pos=(9, 0), span=(1, 1), flag=wx.ALL, border=5)
        self.bt_excute.Bind(wx.EVT_BUTTON, self.OnBtexcute)
        self.bt_plot = wx.Button(panel, label='做图')
        sizer.Add(self.bt_plot, pos=(9, 1), span=(1, 1), flag=wx.ALL, border=5)
        self.bt_plot.Bind(wx.EVT_BUTTON, self.OnPlot)
        self.bt_save = wx.Button(panel, label='保存')
        sizer.Add(self.bt_save, pos=(9, 2), span=(1, 1), flag=wx.ALL, border=5)
        self.bt_save.Bind(wx.EVT_BUTTON, self.OnSave)

        # canvaspanel=wx.Panel(panel, size=(600, 600))
        # sizer.Add(canvaspanel, pos=(0, 12), span=(8, 1), flag=wx.ALL, border=5)
        # self.canvas=backend_wxagg.FigureCanvasWxAgg(canvaspanel, -1, Figure())
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
            tt=ClassifyFieldInfo(t)
            self.lb_vnclass.Append(tt)
            self.lb_vn.Delete(self.lb_vn.Selection)
            self.lb_vnclass.MyRefresh()
        elif key == wx.WXK_F2:  # 移动到vnstat中
            t=self.lb_vn.StringSelection
            self.lb_vnstat.Append(StatFuncInfo(t,'max')) #默认max作为统计函数
            # self.lb_vn.Delete(self.lb_vn.Selection)
    def OnLbvnclassChar(self, event=None):
        key = event.GetKeyCode()  # 获得键盘事件的键值

        if key == wx.WXK_F3:  # 移回到vnclass中
            if -1==self.lb_vnclass.Selection:
                return
            t=self.lb_vnclass.selected_data
            self.lb_vn.Insert(t.fieldname,0)
            self.lb_vnclass.mydeleteitem(t)
            # self.lb_vnclass.MyRefresh()
        elif key == wx.WXK_F4:  # 更改图例变量
            t=self.lb_vnclass.selected_data
            if t.islegend is True:
                t.islegend=False
            else:
                t.islegend=True
            self.lb_vnclass.MyRefresh()


    def OnLbvnstatChar(self,event=None):
        key = event.GetKeyCode()  # 获得键盘事件的键值
        if key == wx.WXK_F3:  # 删除
            if -1 == self.lb_vnstat.Selection:
                return
            t=self.lb_vnstat.selected_data
            self.lb_vnstat.mydeleteitem(t)



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
        yfield=self.lb_vnstat.selected_data.yfield
        self.st_statfield.SetLabel(fieldname)
        self.cb_statfunc.SetSelection(list(statfuncs.keys()).index(funcname))
        self.tc_statname.Value=self.lb_vnstat.selected_data.statname
        self.cb_yfield.SetSelection(['no','y','y2'].index(yfield))

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
        StatFuncInfo.y=None if StatFuncInfo.y is t else StatFuncInfo.y
        StatFuncInfo.y2 = None if StatFuncInfo.y2 is t else StatFuncInfo.y2#先清除与当前项相关的y变量信息
        if self.cb_yfield.Value == 'y':
            StatFuncInfo.y=t
        elif self.cb_yfield.Value == 'y2':
            StatFuncInfo.y2 = t
        self.lb_vnstat.MyRefresh()

    def OnBtexcute(self,evt=None):
        if self.fdm is None or len(self.lb_vnstat.mydata)==0:
            return
        #收集分类字段
        classify_names_noleg=[]
        classify_names_leg=[]#自变量和图例变量
        for i in self.lb_vnclass:
            if i.islegend:
                classify_names_leg.append(i.fieldname)
            else:
                classify_names_noleg.append(i.fieldname)
        #收集statistics_func
        statistics_func=[]
        for i in self.lb_vnstat:
            t=[i.fieldname,statfuncs[i.funcname],i.statname]
            statistics_func.append(t)
        #执行
        classify_names=[x for x in classify_names_leg]
        classify_names.extend(classify_names_noleg)
        self.rfdm=self.fdm.flhz(classify_names=classify_names,statistics_func=statistics_func)

        #提示消息框
        dlg = wx.MessageDialog(None, u"数据透视完成", u"标题信息", wx.OK)
        if dlg.ShowModal() == wx.ID_OK:
            pass
            # self.Close(True)
        dlg.Destroy()
        # #后处理
        # #排序
        # bunches=rfdm.make_bunches(classify_names=classify_names_leg)
        # xname=classify_names_noleg[0]#自变量名
        # yname=StatFuncInfo.y.fieldname
        # # yname=statistics_func[0][2]
        # #外部打开figure 显示结果
        # fig, ax = plt.subplots()
        # # axes = self.canvas.figure.gca()
        # # axes.cla()
        # myfont = FontProperties(fname='C:\Windows\Fonts\STXINGKA.TTF',size=10) # 前提是对应路径下有你想要使用的字体文件
        #
        # for k,bunch in bunches.items():
        #     ax.plot(bunch[xname], bunch[yname],label=k)
        # fig.legend(prop=myfont,loc="upper left")#
        # # self.canvas.draw()
        # plt.show()
        pass

    @staticmethod
    def makenames(classify_names_leg,ulegtypes)->List[str]:
        """
        图例名称
        @param classify_names_leg: 图例变量的list
        @param ulegtypes: 独特值
        @return:
        """
        r=[]
        for i in ulegtypes:
            t=[]
            for name,value in zip(classify_names_leg,i):
                t.append("%s:%f"%(name,value))
            r.append(",".join(t))#添加图例名称 逗号分隔
        return r

    def OnPlot(self,evt):
        #收集分类字段
        classify_names_noleg=[]
        classify_names_leg=[]#自变量和图例变量
        for i in self.lb_vnclass:
            if i.islegend:
                classify_names_leg.append(i.fieldname)
            else:
                classify_names_noleg.append(i.fieldname)
        #收集statistics_func
        statistics_func=[]
        for i in self.lb_vnstat:
            t=[i.fieldname,statfuncs[i.funcname],i.statname]
            statistics_func.append(t)

        #开始做图
        if StatFuncInfo.y is None:
            # 提示消息框
            dlg = wx.MessageDialog(None, u"未指定y变量", u"标题信息", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        bunches=self.rfdm.make_bunches(classify_names=classify_names_leg)
        xname=classify_names_noleg[0]#自变量名
        yname=StatFuncInfo.y.fieldname
        #外部打开figure 显示结果
        fig, ax = plt.subplots()
        myfont = FontProperties(fname='C:\Windows\Fonts\STXINGKA.TTF',size=10) # 前提是对应路径下有你想要使用的字体文件
        for k,bunch in bunches.items():
            ax.plot(bunch[xname], bunch[yname],label=k)
        plt.xlabel(xname)
        plt.ylabel(yname)


        #y2变量
        if StatFuncInfo.y2 is  None:
            fig.legend(prop=myfont, loc="upper left")  #
            plt.show()
            return #结束
        print("y2")
        ax2=ax.twinx()
        yname = StatFuncInfo.y2.fieldname
        plt.ylabel(yname)
        for k,bunch in bunches.items():
            ax2.plot(bunch[xname], bunch[yname],label=k)
        fig.legend(prop=myfont, loc="upper left")  #
        plt.show()

    def OnSave(self,evt):
        #保存文件
        """
        Create and show the Save FileDialog
        """
        with wx.FileDialog(self, "Save xlsx file", wildcard="excel files (*.xlsx)|*.xlsx",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return  # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            self.rfdm.save(pathname)



if __name__ == '__main__':
    app = wx.App()
    frame = PivotTable()
    frame.Show()
    app.MainLoop()
