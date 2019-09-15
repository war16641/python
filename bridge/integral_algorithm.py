from math import *
import cmath
from statistics_nyh import is_approximately_equal
# from bridge.seismic import EarthquakeWave
import bridge.seismic
import numpy as np
from myfile import read_file
from xydata import XYData

def SegmentalPrecision(m, k, c=0, xi=0, ew:'EarthquakeWave'=None, v0=0, dv0=0):
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
    assert isinstance(ew, bridge.seismic.EarthquakeWave), '地震波对象错误'

    if xi!=0:
        assert c!=0,'c xi不能同时指定'
        c=xi*sqrt(2*m*k)

    length=len(ew)
    v=np.zeros((length,))
    dv = np.zeros((length,))
    ddv = np.zeros((length,))#代表位移 速度 加速度
    v[0]=v0
    dv[0]=dv0
    t_span= ew.x[1] - ew.x[0]#认为是等时间间隔的

    #处理荷载项
    ew.switch_unit('m/s^2')
    f= -1 * m * ew.y
    for i in range(1,length):#i是当前要计算的
        f0=f[i-1]
        n=(f[i]-f0)/t_span
        v1, dv1, ddv1=二阶偏微分方程(m=m,c=c,k=k,f0=f0,n=n,t_span=t_span,v0=v[i-1],dv0=dv[i-1])
        v[i]=v1
        dv[i]=dv1
        ddv[i]=ddv1
    return v,dv,ddv

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
    assert c**2<4*m*k,'必须是小阻尼问题'

    #计算常数
    r=(-c+cmath.sqrt(c**2-4*m*k))/2/m
    alpha = r.real
    beta = r.imag
    c1 = (v0 * k ** 2 - f0 * k + c * n) / k ** 2
    c2 = -(k * n - dv0 * k ** 2 + alpha * k ** 2 * v0 + alpha * c * n - alpha * k * f0) / (beta * k ** 2)
    #计算
    v = exp(alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span)) + (k * f0 - c * n) / k ** 2 + n / k * t_span
    dv = n / k + exp(alpha * t_span) * (beta * c2 * cos(beta * t_span) - beta * c1 * sin(beta * t_span)) + alpha * exp(
        alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span))
    ddv = 2 * alpha * exp(alpha * t_span) * (beta * c2 * cos(beta * t_span) - beta * c1 * sin(beta * t_span)) - exp(
        alpha * t_span) * (beta ** 2 * c1 * cos(beta * t_span) + beta ** 2 * c2 * sin(beta * t_span)) + alpha ** 2 * exp(
        alpha * t_span) * (c1 * cos(beta * t_span) + c2 * sin(beta * t_span))
    return v,dv,ddv




def test_二阶偏微分方程():
    t=二阶偏微分方程(m=1,
            c=0.1,
            k=3,
            f0=4,
            t_span=0.1,
            n=2,
            v0=5,
            dv0=-0.5)
    print("%f,%f,%f"%t)
    assert is_approximately_equal(t,[4.896,-1.566,-10.331],tol=1e-2)

def test_分段精确法():
    ew=bridge.seismic.EarthquakeWave(xy=read_file(r"E:\市政院\施工招标上部出图-王博-20190706\22号\BC社区双层拱桥抗震\地震波-用\E2-(4).Txt"))
    v,dv,ddv=SegmentalPrecision(m=1, k=3, c=0.1, ew= ew, v0 = 0, dv0 = 0)
    t=XYData('v',x=ew.x,y=dv)
    t.plot()
if __name__ == '__main__':
    test_二阶偏微分方程()
    test_分段精确法()