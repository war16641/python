from tkinter import *
from tkinter import ttk
import math

class CircleCalc:
    """圆的计算器"""

    unit_scale={"mm":1.,
                "cm":10.,
                "m":1000.}

    def __init__(self):
        self.tk = Tk()
        self.tk.title("圆计算器")
        self.radius=DoubleVar(self.tk)
        self.diameter=DoubleVar(self.tk)
        self.perimeter=DoubleVar(self.tk)
        self.area=DoubleVar(self.tk)
        self.lst = [self.radius, self.diameter, self.perimeter, self.area]

        self.unit=StringVar(self.tk)
        self.unit_before = "mm"
        #self.unit_change_enable_flag=BooleanVar(self.tk)


        Label(self.tk, text="半径").grid(row=0, sticky=E)  # 靠右
        Label(self.tk, text="直径").grid(row=1, sticky=E)  # 第二行，靠左
        Label(self.tk, text="周长").grid(row=2, sticky=E)  # 靠右
        Label(self.tk, text="面积").grid(row=3, sticky=E)  # 第二行，靠左
        Label(self.tk, text="单位").grid(row=0, column=2,sticky=E)  # 第二行，靠左

        Entry(self.tk, textvariable=self.radius).grid(row=0, column=1)
        Entry(self.tk, textvariable=self.diameter).grid(row=1, column=1)
        Entry(self.tk, textvariable=self.perimeter).grid(row=2, column=1)
        Entry(self.tk, textvariable=self.area).grid(row=3, column=1)

        Button(self.tk, text="计算", command=self.calc).grid(row=4, column=1)
        Button(self.tk, text="清除", command=self.clear).grid(row=4, column=0)

        numberChosen = ttk.Combobox(self.tk, width=12, textvariable=self.unit, state='readonly')
        numberChosen['values'] = ("mm","cm","m")  # 设置下拉列表的值
        numberChosen.grid(row=1, column=2)  # 设置其在界面中出现的位置  column代表列   row 代表行
        numberChosen.current(0)  # 设置下拉列表默认显示的值，0为 numberChosen['values'] 的下标值
        numberChosen.bind("<<ComboboxSelected>>",self.unit_change)

        #Checkbutton(self.tk, text="单位有效", variable=self.unit_change_enable_flag).grid(row=2, column=2,sticky=E)


        self.tk.mainloop()

    def calc(self):


        lst = [x.get() for x in self.lst]  # 转变为float
        if lst.count(0) != 3:
            raise Exception("只能有一个变量不为0")
        # 根据给出的是哪一个变量计算其余三个变量
        if lst[0] != 0:
            pass
        elif lst[1] != 0:
            lst[0] = lst[1] / 2
        elif lst[2] != 0:
            lst[0] = lst[2] / 2 / math.pi
        elif lst[3] != 0:
            lst[0] = (lst[3] / math.pi) ** 0.5

        lst[1] = lst[0] * 2
        lst[2] = lst[1] * math.pi
        lst[3] = lst[0] ** 2 * math.pi

        self.radius.set(lst[0])
        self.diameter.set(lst[1])
        self.perimeter.set(lst[2])
        self.area.set(lst[3])

    def clear(self):
        for x in self.lst:
            x.set(0)

    def unit_change(self,evt):
        #print(self.unit.get())
        if self.unit.get() != self.unit_before:
            #print("单位改变:%s->%s"%(self.unit_before,self.unit.get()))

            # 改变4个值
            scale=CircleCalc.unit_scale[self.unit_before]/CircleCalc.unit_scale[self.unit.get()]
            self.radius.set(self.radius.get()*scale)
            self.diameter.set(self.diameter.get() * scale)
            self.perimeter.set(self.perimeter.get() * scale)
            self.area.set(self.area.get() * scale**2)

            self.unit_before = self.unit.get()



if __name__=="__main__":
    t=CircleCalc()