import math
from floatvarwithdimension import FloatVarWithDimension
import wx
import wx.grid
# from GoodToolPython.wx_examples.myvalidators import MyNumberValidator
from valuewithdimension import ValueWithDimension
# from GoodToolPython.wx_examples.mynumbertextctrl import MyNumberTextCtrl
from wx_examples.mynumbertextctrl import MyNumberTextCtrl

class PeriodCalculator(wx.Frame):
    """
    周期计算器
    """
    unit_dic={'stiff':["N/m","kN/m"],
              'mass':["kg","t"],
              'period':['s'],
              'frequency':['s^-1'],
              'circle_frequency':['s^-1']}
    def __init__(self):
        super(PeriodCalculator, self).__init__(None, title="周期计算器",size=(500,700))

        #initial ui
        panel = wx.Panel(self, -1)
        sizer = wx.GridBagSizer(2, 2)

        self.st_stiff=wx.StaticText(panel,label="刚度:")
        sizer.Add(self.st_stiff,pos=(0,0),flag=wx.ALL,border=5)
        self.tc_stiff = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_stiff, pos=(0, 1),span=(1,2) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.cho_stiff=wx.Choice(panel,choices=self.unit_dic['stiff'])
        self.cho_stiff.Select(0)
        self.Bind(wx.EVT_CHOICE,self.OnStiffUnitChange,self.cho_stiff)
        sizer.Add(self.cho_stiff, pos=(0, 3), span=(1, 1), flag= wx.ALIGN_LEFT, border=5)

        self.st_mass=wx.StaticText(panel,label="质量:")
        sizer.Add(self.st_mass,pos=(1,0),flag=wx.ALL,border=5)
        self.tc_mass = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_mass, pos=(1, 1),span=(1,2) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.cho_mass=wx.Choice(panel,choices=self.unit_dic['mass'])
        self.cho_mass.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnMassUnitChange, self.cho_mass)
        sizer.Add(self.cho_mass, pos=(1, 3), span=(1, 1), flag=wx.ALIGN_LEFT, border=5)

        self.st_period=wx.StaticText(panel,label="周期:")
        sizer.Add(self.st_period,pos=(2,0),flag=wx.ALL,border=5)
        self.tc_period = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_period, pos=(2, 1),span=(1,2) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.st2_period = wx.StaticText(panel,label="s")
        sizer.Add(self.st2_period, pos=(2, 3),span=(1,1) ,flag=wx.EXPAND | wx.ALL, border=5)

        self.st_frequency=wx.StaticText(panel,label="频率:")
        sizer.Add(self.st_frequency,pos=(3,0),flag=wx.ALL,border=5)
        self.tc_frequency = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_frequency, pos=(3, 1),span=(1,2) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.st2_frequency = wx.StaticText(panel,label="Hz")
        sizer.Add(self.st2_frequency, pos=(3,3),span=(1,1) ,flag=wx.EXPAND | wx.ALL, border=5)

        self.st_cfrequency=wx.StaticText(panel,label="圆频率:")
        sizer.Add(self.st_cfrequency,pos=(4,0),flag=wx.ALL,border=5)
        self.tc_cfrequency = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_cfrequency, pos=(4, 1),span=(1,2) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.st2_cfrequency = wx.StaticText(panel,label="rad/s")
        sizer.Add(self.st2_cfrequency, pos=(4,3),span=(1,1) ,flag=wx.EXPAND | wx.ALL, border=5)

        self.bt_tozero=wx.Button(panel,label="置零")
        self.Bind(wx.EVT_BUTTON, self.OnSetZero, self.bt_tozero)
        sizer.Add(self.bt_tozero,pos=(5,0),span=(1,1) ,flag=wx.EXPAND | wx.ALL, border=5)
        self.bt_calc = wx.Button(panel, label="计算")
        self.Bind(wx.EVT_BUTTON,self.OnCalc,self.bt_calc)
        sizer.Add(self.bt_calc, pos=(5, 2), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)

        self.st_hist=wx.StaticText(panel,label="历史:")
        sizer.Add(self.st_hist, pos=(6, 0), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)
        self.grid_his=wx.grid.Grid(panel)
        self.grid_his.CreateGrid(10,5)#行，列
        self.grid_his.SetColLabelValue(0,'刚度')
        self.grid_his.SetColLabelValue(1, '质量')
        self.grid_his.SetColLabelValue(2, '周期')
        self.grid_his.SetColLabelValue(3, '频率')
        self.grid_his.SetColLabelValue(4, '圆频率')
        self.grid_his.EnableDragGridSize(False)
        self.hist_ct=0
        sizer.Add(self.grid_his, pos=(7, 0), span=(3, 4), flag=wx.EXPAND | wx.ALL, border=5)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK,self.OnWhat,self.grid_his)




        self.OnSetZero()
        panel.SetSizerAndFit(sizer)

        self.stiff_unit="N/m"
        self.mass_unit="kg"#当前的单位

    def OnCalc(self,event=None):
        #从tc中获取变量
        stiff, mass, period, frequency, cfrequency=self.GetTcValue()

        stiff, mass, period, frequency, cfrequency=self.algorithm_calc_period(stiff=stiff,
                                                                              mass=mass,
                                                                              period=period,
                                                                              frequency=frequency,
                                                                              cfrequency=cfrequency)

        #更新到tc中
        self.SetTcValue([stiff, mass, period, frequency, cfrequency])

        #历史
        self.grid_his.SetCellValue(self.hist_ct,0,str(stiff))
        self.grid_his.SetCellValue(self.hist_ct, 1, str(mass))
        self.grid_his.SetCellValue(self.hist_ct, 2, str(period))
        self.grid_his.SetCellValue(self.hist_ct, 3, str(frequency))
        self.grid_his.SetCellValue(self.hist_ct, 4, str(cfrequency))
        self.hist_ct+=1
    def OnSetZero(self,event=None):
        """置零"""
        self.SetTcValue([0]*5)

    def SetTcValue(self,data):
        """设置5个数据"""
        self.tc_stiff.Value=str(data[0])
        self.tc_mass.Value = str(data[1])
        self.tc_period.Value = str(data[2])
        self.tc_frequency.Value = str(data[3])
        self.tc_cfrequency.Value = str(data[4])

    def GetTcValue(self):
        """获取5个数据"""
        stiff =self.tc_stiff.Value #文本为空时 设为0
        mass = self.tc_mass.Value
        period = self.tc_period.Value
        frequency = self.tc_frequency.Value
        cfrequency = self.tc_cfrequency.Value
        return stiff,mass,period,frequency,cfrequency

    def OnStiffUnitChange(self,evt=None):
        if self.stiff_unit!=evt.String:
            stiff, mass, period, frequency, cfrequency = self.GetTcValue()
            t=ValueWithDimension(stiff,self.stiff_unit)
            t.switch_dimension(evt.String)
            self.stiff_unit=evt.String
            self.tc_stiff.Value = str(t.value)
        pass

    def OnMassUnitChange(self,evt=None):
        if self.mass_unit!=evt.String:
            stiff, mass, period, frequency, cfrequency = self.GetTcValue()
            t=ValueWithDimension(mass,self.mass_unit)
            t.switch_dimension(evt.String)
            self.mass_unit=evt.String
            self.tc_mass.Value = str(t.value)

    def OnWhat(self,evt=None):
        if evt.Col==-1:#双击行标签
            if len(self.grid_his.GetCellValue(evt.Row,0))==0:
                return #不能为空
            t=[self.grid_his.GetCellValue(evt.Row,0),
               self.grid_his.GetCellValue(evt.Row,1),
               self.grid_his.GetCellValue(evt.Row,2),
               self.grid_his.GetCellValue(evt.Row,3),
               self.grid_his.GetCellValue(evt.Row,4)]
            self.SetTcValue(t)


    @staticmethod
    def algorithm_calc_period(stiff=0.,mass=0.,period=0.,frequency=0.,cfrequency=0.):
        """
        计算周期
        只需给定两个变量
        @param stiff:
        @param mass:
        @param period:
        @param frequency:
        @param cfrequency: 圆频率
        @return: stiff,mass,period,frequency,cfrequency
        """
        # 处理周期 频率 圆频率
        if period!=0:
            frequency=period**-1
            cfrequency=frequency * 2 * math.pi
        elif frequency!=0:
            period=frequency**-1
            cfrequency=frequency * 2 * math.pi
        elif cfrequency!=0:
            frequency=cfrequency/2/math.pi
            period=frequency ** -1



        if stiff==0:
            stiff=mass*cfrequency**2
        elif mass==0:
            mass=stiff/cfrequency**2
        elif frequency==0:
            cfrequency=(stiff/mass)**0.5
            frequency=cfrequency / 2 / math.pi
            period=frequency ** -1
        else:
            raise  Exception("错误")

        return stiff,mass,period,frequency,cfrequency



if __name__ == '__main__':
    app = wx.App()
    frame = PeriodCalculator()
    frame.Show()
    app.MainLoop()