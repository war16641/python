from xydata import XYData
from myfile import read_file
from statistics import absmax
class EarthquakeWave(XYData):
    """地震波"""

    #合法单位
    unit_dict={'m/s^2':1,
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

def test1():
    ori = read_file(r"E:\市政院\施工招标上部出图-王博-20190706\22号\BC社区双层拱桥抗震\地震波-用\E2-(4).Txt")
    xy = EarthquakeWave(name='kobe', xy=ori)
    # xy.plot()
    print(xy)
    xy.switch_unit('g')
    print(xy)

if __name__ == '__main__':
    test1()


