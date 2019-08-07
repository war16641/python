from xydata import XYData
from myfile import read_file
from statistics_nyh import absmax
import numpy as np
class EarthquakeWave(XYData):
    """地震波"""

    #合法单位
    unit_dict={'m/s^2':1,
               'm*s^-2': 1,
               'g':9.816,
               'gal':0.01}

    def __init__(self,name='',xy=None,x=None,y=None,unit='m/s^2'):
        assert unit in self.unit_dict.keys(),'无效单位'
        self.unit=unit # type:str
        super().__init__(name=name,xy=xy,x=x,y=y)#初始化父类

    def __str__(self):
        return "%s,共%d个数据点,单位%s,峰值%f"%(self.name,len(self),self.unit,absmax(self.y))

    def switch_unit(self,new_unit:str):
        """转换单位"""
        assert new_unit in self.unit_dict.keys(),'无效单位'
        old_unit=self.unit
        scale=self.unit_dict[old_unit]/self.unit_dict[new_unit]
        self.y=self.y*scale
        self.unit=new_unit

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

def test2():
    ew=生成反应谱(A=0.3,C=1.7,episilon=0.03,Tg=0.6)
    ew.plot()

if __name__ == '__main__':
    test2()


