from collections.abc import Iterable

from code2021.finiterangefunction import FiniteRangeFunction
from unittest import TestCase,main

class Soil:
    """
    描述土体信息的
    """
    def __init__(self,gamma=0,sigma0=0,fi=0,m=0):
        self.gamma=gamma
        self.sigma0=sigma0
        self.fi=fi
        self.m=m

    def __eq__(self, other):
        assert isinstance(other,Soil),"类型错误"
        if id(self)==id(other):
            return True
        return False

class SoilLayer:
    """
    土层信息：
    FiniteRangeFunction 描述土层厚度和土层信息 它的结构是[[高度，soil]，...] 从高程低的向高程高的排列
    dm_height 地面高度 也就是地面高程
    土层最上层到最下层高度是下降的 默认地面高度为0
    """
    def __init__(self,soillayers,dm_height=0):
        """

        @param soillayers: [[土层厚，soil]，...]  注意：这里是从上往下排列的
        @param dm_height: 地面高程
        """
        assert isinstance(soillayers,Iterable)
        pts=[]
        sumh=0#累计厚度
        totalh=0#总厚度
        for i,v in enumerate(soillayers):
            h=v[0]
            soil=v[1]
            assert isinstance(h,(int,float)) and isinstance(soil,Soil)\
            ,"类型错误"
            totalh+=h
        for i in range(len(soillayers)-1,-1,-1):
            h=soillayers[i][0]
            soil = soillayers[i][1]
            if i==len(soillayers)-1:#最低层
                pts.append([-totalh, soil])
                pts.append([-totalh+h, soil])
                sumh+=h
            else:
                sumh+=h
                pts.append([-totalh+sumh,soil])
        #生成
        self.ff=FiniteRangeFunction(pts)
        assert isinstance(dm_height,(int,float))
        self.dm_height=dm_height

        pass

    def soil_at_height(self, height:float)->Soil:
        """获取高程处的土体信息"""
        assert isinstance(height,(int,float))
        height1=height-self.dm_height#折算为dm=0时的相等高度
        try:
            return self.ff.get_value(height1)
        except Exception as e:
            print(e.__str__())
            raise Exception("高度%f=相对高度%f，超出界限"%(height,height1))





class TestC(TestCase):
    def test1(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayer(layers)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(-5.5))
        self.assertEqual(s0, sl.soil_at_height(-0.1))
    def test2(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayer(layers,dm_height=100)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(94.5))
        self.assertEqual(s0, sl.soil_at_height(100))
        self.assertRaises(Exception,sl.soil_at_height,100.1)
        self.assertRaises(Exception, sl.soil_at_height, 93.9)
if __name__ == '__main__':
    main()
