import tkinter as tk
from tkinter import ttk
class Tet: # 测试用的类 没什么实际的用处
    def __init__(self,x=0.0):
        self.x=x

class FloatVarWithDimension(tk.DoubleVar):
    """继承doublevar  主要为了实现绑定功能 重载它的set方法
     另外据观察：变量从控件中的更新 在 执行DoubleVar.get()以后"""

    def __init__(self, master=None, value=None, name=None,order=1,unit='m'):
        super().__init__(master,value,name)
        self.__number_with_dimension=NumberWithDimension(value=value,affect_var=None,order=order,unit=unit)

    def set(self,v):

        super().set(v)
        # 改变number_with_dimension
        self.__number_with_dimension.change_value(v)

    def get(self):
        v=super().get()
        self.set(v)
        return v

    def update_value(self):
        '''从__number_with_dimension更新值'''
        self.set(self.__number_with_dimension.value)

    @property
    def unit(self):
        return self.__number_with_dimension.unit
    @unit.setter
    def unit(self,x):
        self.__number_with_dimension.unit=x
        self.update_value() # 改变单位可能会引起值的改变所以结束时调用更新

class NumberWithDimension:
    """带量刚的数
        affect_var是受影响的变量 当number改变时 会去触发affect_var改变"""

    unit_scale_dict={"mm":1.,
                "cm":10.,
                "m":1000.}

    def __init__(self,value=0.,affect_var=None,order=1,unit="m"):
        if value is None:
            value=0
        self._value=value
        self.affect_var=affect_var
        self.order=order
        if unit not in self.unit_scale_dict.keys():
            raise Exception("此单位不存在")
        self._unit=unit

    def change_value(self,x):
        """只是改变_value的值,不动affect_var
           当这个调用来源于affect_var自身时 为避免死循环，为调用这个函数"""
        self._value=x

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self,x):
        self.change_value(x)
        # 改变affect_var的值
        if self.affect_var is None:
            return
        # 根据affect_var的类型来写
        if isinstance(self.affect_var,Tet):
            self.affect_var.x=x
        elif isinstance(self.affect_var,tk.DoubleVar):
            self.affect_var.set(x)
        else:
            raise Exception("未支持的类型")



    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self,newunit):
        if newunit not in self.unit_scale_dict.keys():
            raise Exception("此单位不存在")
        before_unit=self._unit  # 保存之前的单位
        self._unit=newunit  # 改变单位
        # 根据前后的单位调整value的值
        if newunit==before_unit:
            return
        # 改变value的值
        self.value=self.value*(self.unit_scale_dict[before_unit]/self.unit_scale_dict[newunit])**self.order

    @property
    def dimension(self):
        if self.order==1:
            return self.unit
        return "%s**%d"%(self.unit,self.order)






if __name__=="__main__":
    av=Tet(2.0)
    x=NumberWithDimension(2,av,2,'m')
    print("量纲值：%f  量纲:%s  受影响值:%f"%(x.value,x.dimension, av.x))
    x.value=4
    print("量纲值：%f  量纲:%s  受影响值:%f"%(x.value,x.dimension, av.x))
    x.unit="mm"
    print("量纲值：%f  量纲:%s  受影响值:%f"%(x.value,x.dimension, av.x))