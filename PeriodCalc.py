from tkinter import *
from tkinter import ttk
from floatvarwithdimension import FloatVarWithDimension
import math

class PeriodCalc:
    unit_dic={'stiff':["N*m^-1","kN*m^-1"],
              'mass':["kg","t"],
              'period':['s'],
              'frequency':['s^-1'],
              'circle_frequency':['s^-1']}
    def __init__(self):
        self.tk = Tk()
        self.tk.title("周期计算器")


        self.stiff=FloatVarWithDimension(self.tk,dimension_text='N*m^-2')
        self.mass=FloatVarWithDimension(self.tk,dimension_text='kg')
        self.period=FloatVarWithDimension(self.tk,dimension_text='s')
        self.frequency=FloatVarWithDimension(self.tk,dimension_text='s^-1')
        self.circle_frequency=FloatVarWithDimension(self.tk,dimension_text='s^-1')



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

        numberChosen = ttk.Combobox(self.tk, width=12, textvariable=self.unit_dic['stiff'], state='readonly')
        numberChosen['values'] = ("mm","cm","m")  # 设置下拉列表的值
        numberChosen.grid(row=1, column=2,sticky=E)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        numberChosen.bind("<<ComboboxSelected>>",self.unit_change)


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
        pass

    def clear(self):
        pass





if __name__=="__main__":
    PeriodCalc()