from math import sqrt, cos, sin, pi
from typing import Tuple
from unittest import TestCase,main

from vector3d import Vector3D, Line3D
import numpy as np
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.polyline import PolyLine
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.angletool import AngleTool
from code2021.mydataexchange import make_data_from_paragraph,toline,read_single_line
import matplotlib.pyplot as plt
class Huanhe:
    """
    代表铁路线路中的 从HZ到ZH点的曲线 包括缓和+圆弧+缓和
    这里的缓和：使用的螺旋线 参考网址：https://wenku.baidu.com/view/c879363c33b765ce0508763231126edb6f1a76ff.html
    边界条件 也即HZ前的条件：
    1.HZ点为0,0
    2.HZ点的斜率为0

    注意：cos(fai)使用3项=1-fai**2/2+fai**4/24
         sin(fai)使用2项=fai-fai**3/6
    """
    def __init__(self):
        self.r1=0
        self.elo1=0
        self.length=0
        self._rotate_direction='L'#默认左转


        self._mirror_axes=None#type:LineSegment#对称轴 无边界条件下

    @property
    def rotate_direction(self):
        return self._rotate_direction
    @rotate_direction.setter
    def rotate_direction(self,v):
        assert isinstance(v,str),"类型错误"
        if v.upper()=='L':
            self._rotate_direction='L'
        elif v.upper()=='R':
            self._rotate_direction = 'R'
        else:
            raise Exception("参数错误")

    def get_coordiantes(self, elo):
        C=1/(2.0*self.r1*self.elo1)
        return Vector3D(elo - elo ** 5 *C**2/ 10+elo**9*C**4/216,
                        C/3*elo**3-elo**7*C**3/42)

    @property
    def HY_point(self):#HY点
        return self.get_coordiantes(self.elo1)

    @property
    def arc_angle(self):#圆弧段的角度
        return (self.length-self.elo1*2)/self.r1


    def get_polyline(self,num_of_huanhexian=50)->PolyLine:
        """
        生成缓和线+圆弧+缓和线 对应的polyline
        @param num_of_huanhexian: 缓和线的线段数
        @return:
        """
        points=[]
        for elo in np.linspace(0,self.elo1,num_of_huanhexian):
            points.append(self.get_coordiantes(elo))
        hh1=PolyLine.make1(points)
        # 计算圆心
        fai = self.elo1 ** 2 / (2 * self.r1 * self.elo1)
        ep = self.HY_point
        center = Vector3D(ep.x - self.r1 * sin(fai), ep.y + self.r1 * cos(fai))
        #生成圆弧
        vec1 = ep - center
        arc = Arc(center, self.r1, AngleTool.format(vec1.own_angle), self.arc_angle)
        #对称 得到另一边的缓和线
        mirror_axes = Line3D.make_line_by_2_points(arc.center, arc.mid_point)
        hh2=hh1.mirror(mirror_axes)
        hh2=hh2.reverse()
        lst=[x for x in hh1]
        lst.append(arc)
        lst.extend(hh2.segs)
        #保存对称轴的方向角
        self._mirror_axes=LineSegment(mirror_axes.point,mirror_axes.point+mirror_axes.direction)
        return PolyLine(lst)

    def get_polyline_jiexu(self, num_of_huanhexian=50, ZH:Vector3D=None, angle0:float=0.0)->Tuple[PolyLine, Vector3D, float, Vector3D, float]:
        """
        设定边界条件
        @param num_of_huanhexian:
        @param ZH: ZH
        @param angle0: 前置的直线的方向角
        @return:
        """
        if ZH is None:
            ZH=Vector3D(0, 0)
        assert isinstance(ZH, Vector3D), "类型错误"
        assert isinstance(angle0,(float,int)),"类型错误"
        pl=self.get_polyline(num_of_huanhexian)
        ma=self._mirror_axes
        #处理左转右转
        if 'R'==self.rotate_direction:
            ma=ma.mirror(Line3D.make_line_by_2_points(Vector3D(0,0),Vector3D(1,0)))
            pl=pl.mirror(Line3D.make_line_by_2_points(Vector3D(0,0),Vector3D(1,0)))
        #把pl变换到HZ上
        if Vector3D(0,0)!=ZH:
            ma=ma.move(Vector3D(0,0), ZH)
            pl1=pl.move(Vector3D(0,0), ZH)
        else:
            pl1=pl
        if 0.0!=angle0:
            ma=ma.rotate(base_point=ZH, angle=angle0)
            pl2=pl1.rotate(base_point=ZH, angle=angle0)
        else:
            pl2=pl1
        #计算其他信息
        HZ=pl2.end_point.copy()#HZ点 也是本曲线结束的点
        angle_1=-angle0-pi+2*ma.dangle#HZ点出对应的方向角
        return pl2, ZH, angle0, HZ, angle_1

class TestLineSegment(TestCase):
    def test_1(self):
        hhx = Huanhe()
        hhx.elo1 = 590
        hhx.r1 = 8000
        hhx.length = 2126.127582
        hhx.rotate_direction = 'R'
        pl,_,_,_,_ = hhx.get_polyline_jiexu()
        self.assertTrue(pl.end_point==Vector3D(2111.603260,-203.355948))

        pl, _, _, _, angle1 = hhx.get_polyline_jiexu(ZH=Vector3D(1000, 2000), angle0=AngleTool.toR(30))
        self.assertTrue(pl.end_point == Vector3D(2930.380040,2879.690213,0.000000))
        self.assertAlmostEqual(18.99829659472041,AngleTool.toD(angle1),delta=0.0001)


if __name__ == '__main__':
    main()
    # hhx=Huanhe()
    # hhx.elo1=590
    # hhx.r1=8000
    # hhx.length=2126.127582
    # hhx.rotate_direction='R'
    # pl=hhx.get_polyline_jiexu()
    # pl1=hhx.get_polyline()
    # print(toline(pl,'pl1'))
    # _,ax=pl.draw_in_axes()
    # pl1.draw_in_axes(ax)
    # plt.autoscale(enable=True, axis='both', tight=True)
    # plt.show()
