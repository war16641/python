from typing import Tuple
from math import cos, sin, pi
from vector3d import Vector3D, get_trans_func

def get_basic_vectors(theta):
    """
    经常要用到旋转theta（逆时针）后的坐标系基向量
    @param theta:
    @return:
    """
    return (Vector3D(cos(theta),sin(theta),0),
            Vector3D(-sin(theta),cos(theta),0),
            Vector3D(0,0,1))


class Rect:
    """
    仿照matplotlib patch 中rectangle的定义
    """
    def __init__(self,xy:Vector3D,
                 width,
                 height,
                 rotation=0.):
        """
        使用方法：输入的四个变量 是不能在初始化后更改的，经过在语法上可以更改。更改后导致许多衍生量计算不正确。
        @param xy: 左下角的点或者插入点
        @param width:
        @param height:
        @param rotation: 旋转角 逆时针为正
        """
        self.xy=xy
        self.width=width
        self.height=height
        self.rotation=rotation
        #只能读取的
        self._tf,self._tfi=get_trans_func(self.xy,self.rotation)#坐标系变换函数
        self._center=self._tfi(Vector3D(self.width/2.0,self.height/2.0))#中心坐标 在原坐标系中
        self._corners=(self._tfi(Vector3D(0,0)),
                       self._tfi(Vector3D(self.width,0)),
                       self._tfi(Vector3D(self.width,self.height)),
                       self._tfi(Vector3D(0,self.height)))#四个角点 原坐标系
        self._bound_corners=tuple(Vector3D.get_bound_corner(self._corners))#范围角点

    def __str__(self):
        return "插入点%f,%f 宽%f 高%f 旋转%f"%(self.xy.x,self.xy.y,self.width,self.height,self.rotation)

    @property
    def center(self):
        return self._center
    @property
    def corners(self):
        return self._corners
    @property
    def bound_corners(self)->Tuple[Vector3D,Vector3D]:
        return self._bound_corners


    def __contains__(self, item,tol=0.0):
        """
        点在矩形内
        @param item:
        @param tol:误差
        @return:
        """
        assert isinstance(item,Vector3D)
        newp=self._tf(item)
        if -tol<=newp.x<=self.width+tol and -tol<=newp.y<=self.height+tol:
            return True
        else:
            return False

    def draw_in_axes(self,ax,color='b'):
        """
        在ax中汇出自己的矩形
        @param ax:
        @return:
        """
        t=list(self.corners)
        t.append(t[0])
        xs=[x.x for x in t]
        ys=[x.y for x in t]
        ax.plot(xs,ys,color+'-')

    @staticmethod
    def make_by_two_corners(v1:Vector3D,v2:Vector3D)->'Rect':
        """

        @param v1:
        @param v2:
        @return:
        """
        return Rect(xy=v1,
                      width=v2.x-v1.x,
                      height=v2.y-v1.y)

    def get_dist_from_rect(self,other:'Rect'):
        assert isinstance(other,Rect)
        #先处理x
        if self.bound_corners[0].x<other.bound_corners[0].x:#谁的起点在前面
            before=self
            after=other
        else:
            before=other
            after=self
        t=before.bound_corners[1].x-before.bound_corners[0].x-(after.bound_corners[0].x-before.bound_corners[0].x)
        if t<0:
            x_dist=-t
        else:
            x_dist=0#两者接壤或者相交
        #先处理y
        if self.bound_corners[0].y<other.bound_corners[0].y:#谁的起点在前面
            before=self
            after=other
        else:
            before=other
            after=self
        t=before.bound_corners[1].y-before.bound_corners[0].y-(after.bound_corners[0].y-before.bound_corners[0].y)
        if t<0:
            y_dist=-t
        else:
            y_dist=0#两者接壤或者相交

        return x_dist,y_dist