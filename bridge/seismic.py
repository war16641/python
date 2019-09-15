from xydata import XYData
from myfile import read_file
from statistics_nyh import absmax
import numpy as np
import math
import cmath
from copy import deepcopy
from math import *
from typing import Union, Sequence, overload, List,Generic,TypeVar,Optional

class 动力积分算法:
    @staticmethod
    def 二阶偏微分方程(m, c, k, f0, n, t_span, v0, dv0):
        """
        二阶偏微分方程求解
        从matlab搬过来的
        解决 m*ddv+c*dv+k*v=f0+n*t 的问题
        :param m:
        :param c:
        :param k: 质量 阻尼刚度
        :param f0:
        :param n:
        :param t_span: 时长
        :param v0: 初始位移
        :param dv0: 初始速度
        :return:v,dv,ddv
        """
        assert c ** 2 < 4 * m * k, '必须是小阻尼问题'

        # 计算常数
        r = (-c + cmath.sqrt(c ** 2 - 4 * m * k)) / 2 / m
        alpha = r.real
        beta = r.imag
        c1 = (v0 * k ** 2 - f0 * k + c * n) / k ** 2
        c2 = -(k * n - dv0 * k ** 2 + alpha * k ** 2 * v0 + alpha * c * n - alpha * k * f0) / (beta * k ** 2)
        # 计算
        v = exp(alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span)) + (
                    k * f0 - c * n) / k ** 2 + n / k * t_span
        dv = n / k + exp(alpha * t_span) * (
                    beta * c2 * cos(beta * t_span) - beta * c1 * sin(beta * t_span)) + alpha * exp(
            alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span))
        ddv = 2 * alpha * exp(alpha * t_span) * (beta * c2 * cos(beta * t_span) - beta * c1 * sin(beta * t_span)) - exp(
            alpha * t_span) * (
                          beta ** 2 * c1 * cos(beta * t_span) + beta ** 2 * c2 * sin(beta * t_span)) + alpha ** 2 * exp(
            alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span))
        return v, dv, ddv

    @staticmethod
    def SegmentalPrecision(m, k, c=0, xi=0, ew: 'EarthquakeWave' = None, v0=0, dv0=0):
        """
        用分段精确法 求解动力响应
        :param m:
        :param k:
        :param c:
        :param xi: 阻尼比 c和xi 不能同时指定
        :param ew:
        :param v0:
        :param dv0: 起点的位移和速度
        :return: v,dv,ddv
        """
        assert isinstance(ew, EarthquakeWave), '地震波对象错误'

        if xi != 0:
            assert abs(c) <1e-5, 'c xi不能同时指定'
            c = xi * sqrt(2 * m * k)

        length = len(ew)
        v = np.zeros((length,))
        dv = np.zeros((length,))
        ddv = np.zeros((length,))  # 代表位移 速度 加速度
        v[0] = v0
        dv[0] = dv0
        t_span = ew.x[1] - ew.x[0]  # 认为是等时间间隔的

        # 处理荷载项
        ew.switch_unit('m/s^2')
        f = -1 * m * ew.y
        for i in range(1, length):  # i是当前要计算的
            f0 = f[i - 1]
            n = (f[i] - f0) / t_span
            v1, dv1, ddv1 = 动力积分算法.二阶偏微分方程(m=m, c=c, k=k, f0=f0, n=n, t_span=t_span, v0=v[i - 1], dv0=dv[i - 1])
            v[i] = v1
            dv[i] = dv1
            ddv[i] = ddv1
        return v, dv, ddv


class EarthquakeWave(XYData):
    """地震波  有时也能代表反应谱"""

    #合法单位
    unit_dict={'m/s^2':1,
               'm*s^-2': 1,
               'g':9.816,
               'gal':0.01}

    @overload
    def __init__(self,name='',xy=None,unit='m/s^2'):
        self.unit = unit  # type:str
        self.谱 = {}  # 存储反应谱
        pass
    @overload
    def __init__(self,name='',x=None,y=None,unit='m/s^2'):
        pass

    def __init__(self,name='',xy=None,x=None,y=None,unit='m/s^2'):
        assert unit in self.unit_dict.keys(),'无效单位'
        self.unit=unit # type:str
        super().__init__(name=name,xy=xy,x=x,y=y)#初始化父类
        self.谱={}#存储反应谱



    def __str__(self):
        return "%s,共%d个数据点,单位%s,峰值%f"%(self.name,len(self),self.unit,absmax(self.y))

    def switch_unit(self,new_unit:str):
        """转换单位"""
        assert new_unit in self.unit_dict.keys(),'无效单位'
        old_unit=self.unit
        scale=self.unit_dict[old_unit]/self.unit_dict[new_unit]
        self.y=self.y*scale
        self.unit=new_unit

    def 计算谱(self,T_int=0.01,T_end=6,阻尼比=0.05):
        T=np.arange(0,T_end,T_int)
        T[0]=0.02#周期不能为0，手动修改第一个周期

        #初始化谱
        length_谱=len(T)

        sd=np.zeros((length_谱,))
        psv=np.zeros((length_谱,))
        psa=np.zeros((length_谱,))

        #开始计算
        k=1
        wave=deepcopy(self)
        for i,t in enumerate(T):
            m=k*(t/2/math.pi)**2
            v,dv,ddv=动力积分算法.SegmentalPrecision(m=m, k=k, xi=阻尼比, ew=wave)
            #计算谱值
            sd[i]=abs(absmax(v))
            psv[i] = abs(absmax(dv))
            psa[i] = abs(absmax(ddv+self.y))

        sd=XYData('sd',x=T,y=sd)
        psv = XYData('psv', x=T, y=psv)
        psa = EarthquakeWave('psa', x=T, y=psa)#使用earthquakewave 描述psa谱
        self.谱['sd'] = sd
        self.谱['psv'] = psv
        self.谱['psa'] = psa

    def 显示谱(self,tp='psa'):
        assert tp in self.谱.keys(),'不存在%s谱'%tp
        self.谱[tp].plot()


def 生成反应谱(A,C,episilon,Tg,T_int=0.01,T_end=6,name='',unit='g')->EarthquakeWave:
    """
    ccj 城市桥梁反应谱

    :param A: 地震峰值加速度
    :param C: 调整系数
    :param episilon: 阻尼比
    :param Tg: 特征周期
    :param T_int: 生成的周期间隔
    :param T_end: 结束周期
    :param name:
    :param unit: 单位
    :return:
    """
    jieta1=0.02+(0.05-episilon)/8
    jieta2=1+(0.05-episilon)/(0.06+1.7*episilon)
    gama=0.9+(0.05-episilon)/(0.5+5*episilon)
    Smax=2.25*C*A
    T=np.arange(0,T_end,T_int)#生成周期数组
    S=[]
    for t in T:
        if t<0.1:
            k=(jieta2*Smax-0.45*Smax)/0.1
            S.append(0.45*Smax+k*t)
        elif t<Tg:
            S.append(jieta2*Smax)
        elif t<5*Tg:
            S.append(jieta2*Smax*(Tg/t)**gama)
        else:
            S.append((jieta2*0.2**gama-jieta1*(t-5*Tg))*Smax)
    return EarthquakeWave(name=name,x=T,y=S,unit=unit)
def test1():
    ori = read_file(r"E:\市政院\施工招标上部出图-王博-20190706\22号\BC社区双层拱桥抗震\地震波-用\E2-(4).Txt")
    xy = EarthquakeWave(name='kobe', xy=ori)
    # xy.plot()
    print(xy)
    xy.switch_unit('g')
    print(xy)
    xy.计算谱()
    xy.显示谱('psa')

def test2():
    ew=生成反应谱(A=0.3,C=1.7,episilon=0.03,Tg=0.6)
    ew.plot()

def test3():
    pass

if __name__ == '__main__':
    test1()


