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

        super().set(v)
        # 改变number_with_dimension
        self.__number_with_dimension.value=v

    def get(self):
        v=super().get()
        self.set(v)
        return v

    def update_value(self):
        '''从__number_with_dimension更新值'''
        self.set(self.__number_with_dimension.value)

    @property
    def unit(self):
        return self.__number_with_dimension.dimension_text
    @unit.setter
    def unit(self,x):
        self.__number_with_dimension.switch_dimension(x)
        self.update_value() # 改变单位可能会引起值的改变所以结束时调用更新






