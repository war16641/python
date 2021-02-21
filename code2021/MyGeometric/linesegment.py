from code2021.MyGeometric.basegeometric import BaseGeometric
from vector3d import Vector3D, Line3D, get_trans_func
import matplotlib.pyplot as plt
import numpy as np


class LineSegment(BaseGeometric):
    def __init__(self,p1:Vector3D=None,p2:Vector3D=None):
        self._p1=None #type:Vector3D
        self._p2=None#type:Vector3D
        self._tf=None#两个坐标变换函数
        self._tfi=None
        self._line=None#type:Line3D#线段代表的线
        self.p1,self.p2=p1,p2


    @property
    def p1(self):
        if self._p1 is None:
            raise Exception("p1尚未赋值")
        return self._p1
    @p1.setter
    def p1(self,v):
        if v is not None:
            assert isinstance(v,Vector3D),"类型错误"
            v=v.copy()
        self._p1=v
        self._tf=None
        self._tfi=None
        self._line=None

    @property
    def p2(self):
        if self._p2 is None:
            raise Exception("p2尚未赋值")
        return self._p2
    @p2.setter
    def p2(self,v):
        if v is not None:
            assert isinstance(v,Vector3D),"类型错误"
            v = v.copy()
        self._p2=v
        self._tf=None
        self._tfi=None
        self._line = None

    @property
    def line(self):
        if self._line is None:
            self._line=Line3D.make_line_by_2_points(self.p1,self.p2)
        return self._line

    @property
    def tfi(self):
        if self._tfi is None:
            self._tf,self._tfi=get_trans_func(self.p1,self.line.dangle)
        return self._tfi

    @property
    def tf(self):
        if self._tfi is None:
            self._tf,self._tfi=get_trans_func(self.p1,self.line.dangle)
        return self._tf

    @property
    def length(self):
        return abs(self.p1-self.p2)

    @property
    def dangle(self):
        """
        方向角
        @return:
        """
        return self.line.dangle

    def __contains__(self, item:Vector3D,tol=1e-5):
        """
        判断点是否在线段上
        @param item:
        @param tol:
        @return:
        """
        assert isinstance(item,Vector3D),"类型错误"
        p=self.tf(item)
        if abs(p.y)>Vector3D.tol_for_eq:
            return False
        if -tol<=p.x<=self.length+tol:
            return True
        else:
            return False

    def calc_nearest_point(self, target:Vector3D, tol=1e-5):
        """
        计算点在线段上最近的点
        @param target:
        @param tol:
        @return: 最近点，该点的长度坐标(可以为负 也可以超过长度),target是否在直线上
        长度坐标：=0 起点，=长度 终点
        """
        assert isinstance(target,Vector3D),"类型错误"
        p=target.get_nearest_point_to_line(self.line)
        p1=self.tf(p)
        return p,p1.x,abs(target-p)<tol
        pass

    def draw_in_axes(self,axes=None):
        if axes is None:
            fig1, axes = plt.subplots()

        line=axes.plot([self.p1.x,self.p2.x],[self.p1.y,self.p2.y],'k-')
        return line,axes


    @property
    def start_point(self):
        return self.p1
    @property
    def end_point(self):
        return self.p2

    def __eq__(self, other):
        assert isinstance(other,LineSegment),"类型错误"
        if self.p1==other.p1 and self.p2 ==other.p2:
            return True
        else:
            return False

    def mirror(self,elo:Line3D)->'LineSegment':
        """镜像"""
        assert isinstance(elo,Line3D),"类型错误"
        p1=self.p1.mirror(elo)
        p2 = self.p2.mirror(elo)
        return LineSegment(p1,p2)

    @property
    def mid_point(self):
        return (self.p1+self.p2)*0.5

    def reverse(self)->'LineSegment':
        """逆向 返回一个新的
        """
        return LineSegment(self.p2,self.p1)

    def copy(self):
        """复制一个新的"""
        return LineSegment(self.p1,self.p2)

    def move(self,base_point:Vector3D,target_point:Vector3D)->'LineSegment':
        assert isinstance(base_point,Vector3D) and isinstance(target_point,Vector3D),\
        "类型错误"
        vec=target_point-base_point
        return LineSegment(self.p1+vec,self.p2+vec)

    def rotate(self,base_point:Vector3D,angle:float)->'LineSegment':
        """旋转 得到一个新的"""
        return LineSegment(self.p1.rotate(base_point,angle),self.p2.rotate(base_point,angle))