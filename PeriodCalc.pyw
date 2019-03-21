from tkinter import *
from tkinter import ttk
from floatvarwithdimension import FloatVarWithDimension
import math

class PeriodCalc:
    unit_dic={'stiff':["N/m","kN/m"],
              'mass':["kg","t"],
              'period':['s'],
              'frequency':['s^-1'],
              'circle_frequency':['s^-1']}
    def __init__(self):
        self.tk = Tk()
        self.tk.title("周期计算器")


        self.stiff=FloatVarWithDimension(self.tk,dimension_text='N*m^-1')
        self.mass=FloatVarWithDimension(self.tk,dimension_text='kg')
        self.period=FloatVarWithDimension(self.tk,dimension_text='s')
        self.frequency=FloatVarWithDimension(self.tk,dimension_text='s^-1')
        self.circle_frequency=FloatVarWithDimension(self.tk,dimension_text='s^-1')

        self.varlist=[self.stiff,self.mass,self.period,self.frequency,self.circle_frequency]

        self.stiff_unit=StringVar(self.tk)
        self.mass_unit = StringVar(self.tk)




        Label(self.tk, text="刚度").grid(row=0, sticky=W)  # 靠右
        Label(self.tk, text="质量").grid(row=1, sticky=W)  # 第二行，靠左
        Label(self.tk, text="周期").grid(row=2, sticky=W)  # 靠右
        Label(self.tk, text="频率").grid(row=3, sticky=W)  # 第二行，靠左
        Label(self.tk, text="圆频率").grid(row=4,sticky=W)  # 第二行，靠左

        Entry(self.tk, textvariable=self.stiff).grid(row=0, column=1, sticky=W)
        Entry(self.tk, textvariable=self.mass).grid(row=1, column=1, sticky=W)
        Entry(self.tk, textvariable=self.period).grid(row=2, column=1, sticky=W)
        Entry(self.tk, textvariable=self.frequency).grid(row=3, column=1, sticky=W)
        Entry(self.tk, textvariable=self.circle_frequency).grid(row=4, column=1, sticky=W)

        numberChosen = ttk.Combobox(self.tk, width=12, textvariable=self.stiff_unit, state='readonly')
        numberChosen['values'] = self.unit_dic['stiff'] # 设置下拉列表的值
        numberChosen.grid(row=0, column=2,sticky=W)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        numberChosen.bind("<<ComboboxSelected>>",self.stiff_unit_change)

        numberChosen1 = ttk.Combobox(self.tk, width=12, textvariable=self.mass_unit, state='readonly')
        numberChosen1['values'] = self.unit_dic['mass']  # 设置下拉列表的值
        numberChosen1.grid(row=1, column=2, sticky=W)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen1.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        numberChosen1.bind("<<ComboboxSelected>>", self.mass_unit_change)

        numberChosen2 = ttk.Combobox(self.tk, width=12, state='readonly')
        numberChosen2['values'] = self.unit_dic['period']  # 设置下拉列表的值
        numberChosen2.grid(row=2, column=2, sticky=W)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen2.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值

        numberChosen2 = ttk.Combobox(self.tk, width=12, state='readonly')
        numberChosen2['values'] = self.unit_dic['frequency']  # 设置下拉列表的值
        numberChosen2.grid(row=3, column=2, sticky=W)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen2.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值

        numberChosen3 = ttk.Combobox(self.tk, width=12, state='readonly')
        numberChosen3['values'] = self.unit_dic['circle_frequency']  # 设置下拉列表的值
        numberChosen3.grid(row=4, column=2, sticky=W)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen3.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值



        Button(self.tk, text="计算", command=self.calc).grid(row=5, column=1)
        Button(self.tk, text="清除", command=self.clear).grid(row=5, column=0)



        namelst=['刚度', '质量', '周期', '频率','圆频率']
        self.tree = ttk.Treeview(self.tk, columns=namelst, show='headings')
        for x in namelst:
            self.tree.column(x, width=90, anchor='center')
            self.tree.heading(x,text=x)
        self.tree.grid(row=6, column=0,columnspan=3)




        self.tk.mainloop()

    def calc(self):
        print("开始："+self.mass.value_and_dimension)
        self.update_all_var()
        print("结束：" + self.mass.value_and_dimension)
        tmp=[x.value for x in self.varlist if x.value != 0]
        assert len(tmp)==2
        tmp=[self.frequency ,self.period,self.circle_frequency]
        tmp=[x.value for x in tmp if x.value!=0]
        assert len(tmp)==1 or len(tmp)==0
        # 处理周期 频率 圆频率
        if self.period.value!=0:
            self.frequency.set(self.period**-1)
            self.circle_frequency.set(self.frequency * 2 * math.pi)
        elif self.frequency.value!=0:
            self.period.set(self.frequency**-1)
            self.circle_frequency.set(self.frequency * 2 * math.pi)
        elif self.circle_frequency.value!=0:
            self.frequency.set(self.circle_frequency/2/math.pi)
            self.period.set(self.frequency ** -1)


        if self.stiff==0:
            self.stiff.set(self.mass*self.circle_frequency**2)
            self.stiff.switch_dimension(self.stiff_unit.get())
        elif self.mass==0:
            tmp=self.stiff/self.circle_frequency**2
            self.mass.set(tmp)
            self.mass.switch_dimension(self.mass_unit.get())
        elif self.frequency==0:
            print(self.stiff.value_and_dimension)
            print(self.mass.value_and_dimension)
            self.circle_frequency.set((self.stiff/self.mass)**0.5)
            self.circle_frequency.format(erase_dim='force') #单位格式化
            self.frequency.set(self.circle_frequency / 2 / math.pi)
            self.period.set(self.frequency ** -1)
        else:
            raise  Exception("错误")

        # 更新treeview
        lst=[x.value for x in self.varlist]
        self.tree.insert('', 'end', values=lst)

    def clear(self):
        for x in self.varlist:
            x.set(0)

    def stiff_unit_change(self,*args):
        self.update_all_var()
        if self.stiff_unit.get()=='N/m':
            self.stiff.switch_dimension('N,m')
        elif self.stiff_unit.get()=='kN/m':
            self.stiff.switch_dimension('kN,m')


    def mass_unit_change(self,*args):
        self.update_all_var()
        self.mass.switch_dimension(self.mass_unit.get())
        print(self.mass.value_and_dimension)

    def update_all_var(self):
        """更新所有的变量"""
        for x in self.varlist:
            x.get()





if __name__=="__main__":
    PeriodCalc()