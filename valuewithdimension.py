from copy import deepcopy
from unittest import TestCase as tc
import re

from myfile import is_number


class SmallDimension:
    """描述某一类量纲的单位和阶数"""
    def __init__(self,dim,unit):
        self.dim=dim
        self.order=unit
    def __eq__(self, other):
        """判断阶数是否相同"""
        if self.order==other.order:
            return True
        return False
        # if self.order==0 and other.order==0:
        #     return True
        # if self.dim==other.dim and self.order == other.order:
        #     return True
        # return False

    def __ne__(self, other):
        return not self.__eq__(other)

def save_dimension_wrapper(func):
    """在对ValueWithDimension进行运算前 保存单位系统 在结束后复原单位系统"""
    def wrapper(*args):
        assert len(args)==2
        one=args[0]
        save_dimension1=one.dimension_text_exclude_order
        second=args[1]
        if isinstance(second,ValueWithDimension):
            save_dimension2=second.dimension_text_exclude_order # 存储单位
        v=func(*args)
        if isinstance(second,ValueWithDimension):
            second.switch_dimension(save_dimension2)
        one.switch_dimension(save_dimension1)
        return v
    return wrapper



class ValueWithDimension:
    length_dimension={'mm':1,
                      'cm':10,
                      'm':1000}
    mass_dimension={'kg':1,
                    't':1000}
    time_dimesion={'ms':1e-3,
                   's':1,
                   'min':60,
                   'h':3600}
    force_dimesion={'N':1,
                    'kN':1000}
    valid_dimension={'length':length_dimension,
                     'mass':mass_dimension,
                     'time':time_dimesion,
                     'force':force_dimesion}

    dimensionless={'length':1,
                     'mass':1,
                     'time':-2,
                     'force':-1} # 这个字典代表1=m*kg*s^-2*N^-1

    def __init__(self,value=0,*args):
        """构造用法案例"""
        """g=9.8 m*s^-2可用"""
        """g=ValueWithDimension(9.8,"m*s^-2")"""
        """g=ValueWithDimension(9.8,'m',1,'s',-2)"""

        self.value=value
        self.dimension={'length':SmallDimension('m',0),
                        'mass':SmallDimension('kg',0),
                        'time':SmallDimension('s',0),
                        'force':SmallDimension('N',0)}
        if 0!=len(args) % 2:
            if 1==len(args) and isinstance(args[0],str):
                dtext=args[0]
                dimension_setup=self.dimension_text_interpreter(dtext)
            elif 1==len(args) and isinstance(args[0],ValueWithDimension):
                self.value=args[0].value
                self.dimension=deepcopy(args[0].dimension)
                return
            else:
                raise Exception("必须两个一组")
        else:
            dimension_setup=list(args)

        for i in range(0,len(dimension_setup)-1,2):
            dim=dimension_setup[i]
            od=dimension_setup[i+1]
            self.dimension[self.dimension_interpreter(dim)].dim=dim
            if self.dimension[self.dimension_interpreter(dim)].order != 0:
                raise Exception("重复指定同一个量纲")
            self.dimension[self.dimension_interpreter(dim)].order = od

    def switch_dimension1(self,x):
        """处理给定具体单位时的字符串如 x='kg/s*m^2'"""
        lst=re.split('[*/^]',x)
        tmp=[x for x in lst if not x.isdigit()]
        self.switch_dimension(",".join(tmp))
    def switch_dimension(self,line,flag_auto=True):
        """改变单位体系"""
        """
        line是字符串可以是：
        kg,s,t
        kg/s*t^2

        flag_auto代表是否进行智能判断 开启智能判断可能会导致死循环
        """

        assert isinstance(line,str)
        if '*' in line or '/' in line or '^' in line:
            lst = re.split('[*/^]', line)
            args = [x for x in lst if not is_number(x)[0]]
        else:
            args = line.split(",")

        # 如果有力的单位将质量设为0 如果有质量的的单位将力设为0
        if True==flag_auto:
            for ut in args:
                if self.dimension_interpreter(ut) == 'force':
                    self.format(erase_dim='mass')
                    break
                if self.dimension_interpreter(ut) == 'mass':
                    self.format(erase_dim='force')
                    break



        for ut in args:
            tp=self.dimension_interpreter(ut)
            old_un=self.dimension[tp].dim
            if old_un != ut:
                self.value=self.value*(self.valid_dimension[tp][old_un]/self.valid_dimension[tp][ut])**self.dimension[tp].order
                self.dimension[tp].dim=ut

    def is_same_dimension(self,x):
        """判断两个数是否有相同的量纲"""
        self.format()
        x.format()
        for k in self.dimension.keys():
            if self.dimension[k]!=x.dimension[k]:
                return False
        return True



    def format(self,erase_dim='force'):
        """由于时间 质量 长度 和力 是重复的，在一些情况下会造成麻烦 这里默认去掉力"""
        assert erase_dim in self.dimension.keys()
        self.switch_dimension("kg,m,s,N",False) # 先转化为默认单位
        if self.dimension[erase_dim].order==0:
            return
        tmp=deepcopy(self.dimensionless)
        scale=-1.0/tmp[erase_dim]
        for k in tmp.keys():
            tmp[k]=tmp[k]*scale
        x=self.dimension[erase_dim].order
        for k,v in self.dimension.items():
            if k==erase_dim:
                v.order=0
                continue
            v.order+=tmp[k]*x
        #
        #
        #
        #
        #
        #
        # if self.dimension['force'].order!=0:
        #     if 'N'==self.dimension['force'].dim:
        #         self.switch_dimension("kg,m,s")
        #         self.dimension['length'].order+=self.dimension['force'].order
        #         self.dimension['mass'].order += self.dimension['force'].order
        #         self.dimension['time'].order -= self.dimension['force'].order*2
        #         self.dimension['force'].order=0
        #     elif 'kN'==self.dimension['force'].dim:
        #         self.switch_dimension("t,m,s")
        #         self.dimension['length'].order+=self.dimension['force'].order
        #         self.dimension['mass'].order += self.dimension['force'].order
        #         self.dimension['time'].order -= self.dimension['force'].order*2
        #         self.dimension['force'].order=0
        #     else:
        #         raise Exception("不应该执行到这里")

    @save_dimension_wrapper
    def __add__(self, other):
        assert self.is_same_dimension(other)
        # 单位会向第一个看齐
        save_dimension=other.dimension_text_exclude_order
        other.switch_dimension(self.dimension_text_exclude_order)
        c=deepcopy(self)
        c.value+=other.value
        other.switch_dimension(save_dimension)
        return c

    @save_dimension_wrapper
    def __sub__(self, other):
        assert self.is_same_dimension(other)
        # 单位会向第一个看齐
        other.switch_dimension(self.dimension_text_exclude_order)
        c = deepcopy(self)
        c.value -= other.value
        return c

    @save_dimension_wrapper
    def __truediv__(self, other):
        c = deepcopy(self)
        if isinstance(other, (float, int)):
            c.value = c.value / other
            return c
        if isinstance(other, ValueWithDimension):
            # save_dimension = other.dimension_text_exclude_order
            other.switch_dimension(self.dimension_text_exclude_order)  # 统一单位
            c.value = self.value / other.value
            for k in c.dimension.keys():
                c.dimension[k].order -= other.dimension[k].order
            # other.switch_dimension(save_dimension)
            return c
        raise Exception("类型错误")

    @save_dimension_wrapper
    def __mul__(self, other):
        c=deepcopy(self)
        if isinstance(other,(float,int)):
            c.value=c.value*other
            return c
        if isinstance(other,ValueWithDimension):
            other.switch_dimension(self.dimension_text_exclude_order) # 统一单位
            c.value=self.value*other.value
            for k in c.dimension.keys():
                c.dimension[k].order+=other.dimension[k].order
            return c
        raise Exception("类型错误")

    def __pow__(self, power, modulo=None):
        c=deepcopy(self)
        c.value=c.value**power
        for v in c.dimension.values():
            v.order=v.order*power
        return c

    @save_dimension_wrapper
    def __eq__(self, other):
        if isinstance(other,(float,int)):# 与数比较
            if other==0 and self.value==0:
                return True
            tmp=[x.order for x in self.dimension.values()]
            tmp=[x for x in tmp if x!=0]
            if len(tmp)==0:
                if other==self.value:
                    return True
                else:
                    return False
            else:
                return False



        self.format()
        other.format()
        other.switch_dimension(self.dimension_text_exclude_order)  # 统一单位
        if self.value!=other.value:
            return False
        for k in self.dimension.keys():
            if self.dimension[k].order != other.dimension[k].order:
                return False
        return True





    @property
    def dimension_text(self):
        """返回单位字符串"""
        line = [v.dim + "^%f" % v.order for v in self.dimension.values()]
        line = "*".join(line)
        return line

    @property
    def dimension_text_exclude_order(self):
        """返回字符串 不含阶数 用，连接"""
        line=[v.dim for v in self.dimension.values()]
        return ",".join(line)


    def __str__(self):
        return "%f %s"%(self.value,self.dimension_text)

    @staticmethod
    def dimension_interpreter(dim):
        """根据具体的单位返回单位的类别"""
        # if dim in ValueWithDimension.length_dimension.keys():
        #     return "length"
        # if dim in ValueWithDimension.mass_dimension.keys():
        #     return "mass"
        for k,v in ValueWithDimension.valid_dimension.items():
            if dim in v.keys():
                return k

        raise Exception("无效单位")

    @staticmethod
    def dimension_text_interpreter(text):
        """将单位字符串转化为可以识别的列表
        a="mm*t^2"
        b="m^3*kg^1"
        print(ValueWithDimension.dimension_text_interpreter(a))
        print(ValueWithDimension.dimension_text_interpreter(b))"""
        id1=text.split("*")
        lst=[]
        for v in id1:
            if '^' in v:
                idline = v.split('^')
                assert len(idline) == 2
                idline[1] = float(idline[1])
                lst = lst + idline
            else:
                idline = [v]
                idline.append(1.0)
                lst = lst + idline
        return lst



if __name__=="__main__":
    # 以下为测试所用 不能抛出异常
    # 测试开始
    a=ValueWithDimension(1,"mm*kg^-1")
    b=ValueWithDimension(0.5,"m*t^-1")
    c=ValueWithDimension(1.5,"m*t^-1")
    d=ValueWithDimension(0.5,"m^2*t^-2")
    e=2
    e1=ValueWithDimension(2)
    f=ValueWithDimension(0.25,"mm^2*kg^-2")

    assert a+b==c
    assert a*b==d
    assert a/b==e
    assert a/b==e1
    assert a-b ==b
    tc.assertRaises(None,Exception,a.__add__,d)
    assert b**2==f

    a=ValueWithDimension(60,'s')
    b=ValueWithDimension(1,"min")
    assert a==b


    a=ValueWithDimension(1.1,"kN")
    print(a)
    b=ValueWithDimension(1100,"kg*m*s^-2")
    assert a==b
    print(a)

    a=ValueWithDimension(1.1,'N')
    b=ValueWithDimension(2.2,"kg*m")
    c=ValueWithDimension(0.5,"s^-2")
    assert b*c==a
    d=ValueWithDimension(2,"N")
    e=a+d

    a = ValueWithDimension(1.1, 'N')
    a.switch_dimension('kg')
    b= ValueWithDimension(1.1, 'kg*m*s^-2')
    b.switch_dimension('N')

    assert a.dimension['mass'].order==1
    assert b.dimension['force'].order==1

    print(a)
    print(b)
    a = ValueWithDimension(1001, 'N*m^-1')
    a.switch_dimension('kN')
    assert abs(a.value-1.001)<1e-5
    print(a.value)

    a = ValueWithDimension(1001, 'N*m^-1')
    a.switch_dimension('kN*m^-1')
    assert abs(a.value - 1.001) < 1e-5
    print(a.value)

    # 测试结束













    pass
