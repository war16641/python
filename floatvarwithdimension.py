import tkinter as tk
from tkinter import ttk
from valuewithdimension import  ValueWithDimension
class Tet: # 测试用的类 没什么实际的用处
    def __init__(self,x=0.0):
        self.x=x

class FloatVarWithDimension(tk.DoubleVar):
    """继承doublevar  主要为了实现绑定功能(将控件的floatvar与ValueWithDimension绑定) 重载它的set方法
     另外据观察：变量从控件中的更新 在 执行DoubleVar.get()以后"""

    def __init__(self, master=None, value=None, name=None,dimension_text=''):
        super().__init__(master,value,name)
        if value is None:
            value=0
        self.__number_with_dimension=ValueWithDimension(value,dimension_text)


    def set(self,v):
        if isinstance(v,(float,int)):
            super().set(v)
            # 改变number_with_dimension
            self.__number_with_dimension.value = v
        elif isinstance(v,ValueWithDimension):
            self.__number_with_dimension=v
            super().set(v.value)
        else:
            raise Exception("未知类型")


    def get(self):
        v=super().get()
        self.set(v)
        return v

    def update_value(self):
        '''从__number_with_dimension更新值'''
        self.set(self.__number_with_dimension.value)

    @property
    def value(self):
        return self.__number_with_dimension.value

    @property
    def dimension(self):
        return self.__number_with_dimension.dimension_text
    @property
    def value_and_dimension(self):
        return "%f %s"%(self.value,self.dimension)


    def switch_dimension(self,*args):
        self.__number_with_dimension.switch_dimension(*args)
        self.update_value()

    def format(self,erase_dim='force'):
        self.__number_with_dimension.format(erase_dim=erase_dim)
        self.update_value()

    def __add__(self, other):
        return self.__number_with_dimension.__add__(other.__number_with_dimension)

    def __sub__(self, other):
        return self.__number_with_dimension.__sub__(other.__number_with_dimension)

    def __mul__(self, other):
        if isinstance(other,(float,int,ValueWithDimension)):
            return self.__number_with_dimension.__mul__(other)
        elif isinstance(other,FloatVarWithDimension):
            return self.__number_with_dimension.__mul__(other.__number_with_dimension)

        return Exception("未知类型")

    def __truediv__(self, other):
        if isinstance(other,(float,int,ValueWithDimension)):
            return self.__number_with_dimension.__truediv__(other)
        elif isinstance(other,FloatVarWithDimension):
            return self.__number_with_dimension.__truediv__(other.__number_with_dimension)

        return Exception("未知类型")

    def __pow__(self, power, modulo=None):
        return self.__number_with_dimension.__pow__(power,modulo)

    def __eq__(self, other):
        if isinstance(other,(int,float)):
            return self.__number_with_dimension==other
        if isinstance(other,FloatVarWithDimension):
            return self.__number_with_dimension==other.__number_with_dimension
        if isinstance(other,ValueWithDimension):
            return self.__number_with_dimension==other
        raise Exception("未知类型")










