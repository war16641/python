import wx
import wx.xrc
import wx.grid
import math
from GoodToolPython.wx_examples.mynumbertextctrl import MyNumberTextCtrl
from GoodToolPython.mybaseclasses.emptyclass import EmptyClass
from valuewithdimension import ValueWithDimension


class CircleCalculator(wx.Frame):

    def __init__(self, parent=None):
        wx.Frame.__init__(self, parent, id=wx.ID_ANY, title=wx.EmptyString, pos=wx.DefaultPosition,
                          size=wx.Size(452, 500), style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)

        panel=wx.Panel(self)
        sizer = wx.GridBagSizer(0,0)


        choices=["mm","cm","m"]
        choices2 = ["mm^2", "cm^2", "m^2"]
        rowct=0

        self.st_radius=wx.StaticText(panel,label="半径")
        sizer.Add(self.st_radius, pos=(rowct, 0), flag=wx.ALL, border=5)
        self.tc_radius = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_radius, pos=(rowct, 1), span=(1, 1), flag=wx.ALL, border=5)
        self.cho_radius = wx.Choice(panel, choices=choices)
        self.cho_radius.Select(0)
        sizer.Add(self.cho_radius, pos=(rowct, 2), span=(1, 1), flag=wx.ALL, border=5)
        self.cho_all = wx.Choice(panel, choices=choices)
        self.cho_all.Select(0)
        self.cho_all.oldunit="mm"
        self.Bind(wx.EVT_CHOICE,self.OnAllUnitChange,self.cho_all)
        self.Bind(wx.EVT_CHOICE, self.OnUnitChange, self.cho_radius)
        self.cho_radius.oldunit = "mm"
        self.cho_radius.varindex=0 #代表gettcvalue返回值的序号
        self.cho_radius.infect_tc=self.tc_radius #这三个参数方便响应单位改变事件
        sizer.Add(self.cho_all, pos=(rowct, 3), span=(1, 1), flag=wx.ALL, border=5)
        rowct+=1


        self.st_diameter=wx.StaticText(panel,label="直径")
        sizer.Add(self.st_diameter, pos=(rowct, 0), flag=wx.ALL, border=5)
        self.tc_diameter = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_diameter, pos=(rowct, 1), span=(1, 1), flag=wx.ALL, border=5)
        self.cho_diameter = wx.Choice(panel, choices=choices)
        self.cho_diameter.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnUnitChange, self.cho_diameter)
        self.cho_diameter.oldunit = "mm"
        self.cho_diameter.varindex=1
        self.cho_diameter.infect_tc=self.tc_diameter #这三个参数方便响应单位改变事件
        sizer.Add(self.cho_diameter, pos=(rowct, 2), span=(1, 1), flag=wx.ALL, border=5)
        rowct+=1

        self.st_perimeter=wx.StaticText(panel,label="周长")
        sizer.Add(self.st_perimeter, pos=(rowct, 0), flag=wx.ALL, border=5)
        self.tc_perimeter = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_perimeter, pos=(rowct, 1), span=(1, 1), flag=wx.ALL, border=5)
        self.cho_perimeter = wx.Choice(panel, choices=choices)
        self.cho_perimeter.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnUnitChange, self.cho_perimeter)
        self.cho_perimeter.oldunit = "mm"
        self.cho_perimeter.varindex=2
        self.cho_perimeter.infect_tc=self.tc_perimeter #这三个参数方便响应单位改变事件
        sizer.Add(self.cho_perimeter, pos=(rowct, 2), span=(1, 1), flag=wx.ALL, border=5)
        rowct+=1

        self.st_area=wx.StaticText(panel,label="面积")
        sizer.Add(self.st_area, pos=(rowct, 0), flag=wx.ALL, border=5)
        self.tc_area = MyNumberTextCtrl(panel)
        sizer.Add(self.tc_area, pos=(rowct, 1), span=(1, 1), flag=wx.ALL, border=5)
        self.cho_area = wx.Choice(panel, choices=choices2)
        self.cho_area.Select(0)
        self.Bind(wx.EVT_CHOICE, self.OnUnitChange, self.cho_area)
        self.cho_area.oldunit = "mm^2"
        self.cho_area.varindex=3
        self.cho_area.infect_tc=self.tc_area #这三个参数方便响应单位改变事件
        sizer.Add(self.cho_area, pos=(rowct, 2), span=(1, 1), flag=wx.ALL, border=5)
        rowct+=1


        self.bt_tozero=wx.Button(panel,label="置零")
        self.Bind(wx.EVT_BUTTON,self.OnSetZero,self.bt_tozero)
        sizer.Add(self.bt_tozero, pos=(rowct, 0), span=(1, 1), flag=wx.ALL, border=5)
        self.bt_calc = wx.Button(panel, label="计算")
        self.Bind(wx.EVT_BUTTON, self.OnCalc, self.bt_calc)
        sizer.Add(self.bt_calc, pos=(rowct, 1), span=(1, 1), flag=wx.ALL, border=5)
        rowct += 1

        self.st_hist=wx.StaticText(panel,label="历史:")
        sizer.Add(self.st_hist, pos=(rowct, 0), span=(1, 1), flag=wx.EXPAND | wx.ALL, border=5)
        rowct += 1

        self.grid_his=wx.grid.Grid(panel)
        self.grid_his.CreateGrid(10,4)#行，列
        self.grid_his.SetColLabelValue(0,'半径')
        self.grid_his.SetColLabelValue(1, '直径')
        self.grid_his.SetColLabelValue(2, '周长')
        self.grid_his.SetColLabelValue(3, '面积')
        self.grid_his.EnableDragGridSize(False)
        self.hist_ct=0
        sizer.Add(self.grid_his, pos=(rowct, 0), span=(3, 4), flag=wx.EXPAND | wx.ALL, border=5)
        # Columns
        self.grid_his.EnableDragColMove(False)
        self.grid_his.EnableDragColSize(False)
        self.grid_his.SetColLabelSize(30)
        self.grid_his.SetColLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        # Rows
        self.grid_his.EnableDragRowSize(False)
        self.grid_his.SetRowLabelSize(30)
        self.grid_his.SetRowLabelAlignment(wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.OnWhat, self.grid_his)





        self.OnSetZero()
        panel.SetSizerAndFit(sizer)



    def SetTcValue(self,data):
        self.tc_radius.Value=data[0]
        self.tc_diameter.Value = data[1]
        self.tc_perimeter.Value = data[2]
        self.tc_area.Value = data[3]

    def GetTcValue(self):
        return self.tc_radius.Value,self.tc_diameter.Value,self.tc_perimeter.Value,self.tc_area.Value

    def OnSetZero(self,evt=None):
        self.SetTcValue([0]*4)

    def OnCalc(self,evt=None):
        radius, diameter, perimeter, area=self.algorithm_calc_circle(*self.GetTcValue())
        self.SetTcValue([radius, diameter, perimeter, area])
        #添加历史
        self.grid_his.SetCellValue(self.hist_ct,0,str(radius))
        self.grid_his.SetCellValue(self.hist_ct, 1, str(diameter))
        self.grid_his.SetCellValue(self.hist_ct, 2, str(perimeter))
        self.grid_his.SetCellValue(self.hist_ct, 3, str(area))
        self.hist_ct+=1

    def OnUnitChange(self, evt):
        if evt.EventObject.oldunit!=evt.String:
            t = self.GetTcValue()
            t = ValueWithDimension(t[evt.EventObject.varindex], evt.EventObject.oldunit)
            t.switch_dimension(evt.String)
            evt.EventObject.oldunit = evt.String
            evt.EventObject.infect_tc.Value=t.value

    def OnAllUnitChange(self,evt):
        if evt.EventObject.oldunit!=evt.String:
            t=["mm","cm","m"]

            for i in [self.cho_radius,self.cho_diameter,self.cho_perimeter,self.cho_area]:
                i.SetSelection(t.index(evt.String))
                myevt=EmptyClass()
                myevt.String=i.GetItems()[t.index(evt.String)]
                myevt.EventObject=i
                self.OnUnitChange(myevt)

            evt.EventObject.oldunit=evt.String

    def OnWhat(self,evt=None):
        if evt.Col==-1:#双击行标签
            if len(self.grid_his.GetCellValue(evt.Row,0))==0:
                return #不能为空
            t=[self.grid_his.GetCellValue(evt.Row,0),
               self.grid_his.GetCellValue(evt.Row,1),
               self.grid_his.GetCellValue(evt.Row,2),
               self.grid_his.GetCellValue(evt.Row,3),]
            self.SetTcValue(t)


    @staticmethod
    def algorithm_calc_circle(radius=0.,diameter=0.,perimeter=0.,area=0.):
        """
        计算圆参数的算法
        只需要给定一个参数
        @param radius:
        @param diameter:
        @param perimeter:
        @param area:
        @return: radius,diameter,perimeter,area
        """
        def script():
            #通过半径算出其他参数
            nonlocal radius,diameter,perimeter,area
            diameter=2*radius
            perimeter=diameter*math.pi
            area=math.pi*radius**2
        t=[radius,diameter,perimeter,area]
        assert t.count(0.0)==3,"只需一个参数"

        #计算半径
        if radius!=0.0:
            pass
        elif diameter!=0.0:
            radius=diameter/2
        elif perimeter!=0.0:
            radius=perimeter/2/math.pi
        else:
            radius=(area/math.pi)**0.5

        # 通过半径算出其他参数
        diameter = round(2 * radius,7)
        perimeter = round(diameter * math.pi,7)
        area = round(math.pi * radius ** 2,7)

        return radius,diameter,perimeter,area

if __name__ == '__main__':
    app = wx.App()
    frame = CircleCalculator()
    frame.Show()
    app.MainLoop()