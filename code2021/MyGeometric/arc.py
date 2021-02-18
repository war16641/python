from math import pi, sqrt
import matplotlib.patches as mpatches

from code2021.MyGeometric.basegeometric import BaseGeometric
from vector3d import Vector3D,get_trans_func_polar
import matplotlib.pyplot as plt
from code2021.MyGeometric.angletool import AngleTool

class CircleLineIntersecionProblem:
    """
    圆和直线交点问题
    (x-a)**2+(y-b)**2+r**2=0
    A*x+B*y+C=0
    """
    def __init__(self):
        self.a=self.b=0
        self.r=0
        self.A=self.B=self.C=0

    def solve(self):
        """
        相离时 返回none
        相切时 返回[(交点坐标)] 当圆心到直线距离与r相对误差补不足1e-6时 认为相切
        相交时 返回 [(交点1坐标),(交点2坐标)]
        @return:
        """
        a,b,r=self.a,self.b,self.r
        A,B,C=self.A,self.B,self.C
        #检查根的个数
        dist=abs((A*a+B*b+C)/sqrt(A**2+B**2))
        if dist>r:
            return None
        else:
            t= [(-(B*(-A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2)) + C)/A,
                     -A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2),),
                    (-(B*(A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2)) + C)/A,
                     A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2),)]
            if abs(dist-r)/r<1e-5:#相切
                return [t[0]]
            else:#相交
                return t


class Arc(BaseGeometric):

    def __init__(self,center:Vector3D,radius,angle1:float,da):
        """

        @param center:
        @param radius:
        @param angle1:
        @param da: 为正时 逆时针转 不能大于2pi
        """
        assert isinstance(center,Vector3D),"类型错误"
        assert abs(da)<=1e-6+2*pi,"da绝对值必须在2pi内"
        self._center=center #type:Vector3D
        self._angle1=angle1
        self._da=da
        self._angle2=self._angle1+self._da
        self._radius=radius
        self._tf,self._tfi=None,None


    @property
    def radius(self):
        return self._radius

    @property
    def center(self):
        return self._center

    @property
    def da(self):
        return self._da

    @property
    def length(self):
        return self._radius*abs(self._da)
    @property
    def tf(self):
        if self._tf is None:
            self._tf,self._tfi=get_trans_func_polar(self._center)
        return self._tf
    @property
    def tfi(self):
        if self._tf is None:
            self._tf, self._tfi = get_trans_func_polar(self._center)
        return self._tfi

    def draw_in_axes(self,axes=None):
        # ax.relim()
        # ax.autoscale_view()
        if axes is None:
            _, axes = plt.subplots()
        if self._da>0:
            arc = mpatches.Arc((self.center.x, self.center.y), self.radius*2, self.radius*2, 0,
                            AngleTool.toD(self._angle1), AngleTool.toD(self._angle2),
                               color='k')
        else:
            arc = mpatches.Arc((self.center.x, self.center.y), self.radius*2, self.radius*2, 0,
                            AngleTool.toD(self._angle2), AngleTool.toD(self._angle1),
                               color='k')
        axes.add_patch(arc)
        return arc,axes

    @property
    def start_point(self):
        return self.tfi(Vector3D(self._angle1,self.radius))
    @property
    def end_point(self):
        return self.tfi(Vector3D(self._angle2,self.radius))

    def __contains__(self, item):
        """
        没有完善
        尤其是涉及arc跨越2pi时
        @param item:
        @return:
        """
        assert isinstance(item,Vector3D),"类型错误"
        t=self.tf(item)
        #计算小的端点
        if self._da>0:
            mp=self._angle1
        else:
            mp=self._angle2
        #计算t点到mp点转过的角度 并放入0到2pi
        need=AngleTool.format(t.x-mp)
        #need与da比较
        if abs(self._da)<need-Vector3D.tol_for_eq:
            return False
        if abs(t.y-self.radius)<Vector3D.tol_for_eq:
            return True
        else:
            return False
        # if self._angle1-Vector3D.tol_for_eq<=t.x<=self._angle2+Vector3D.tol_for_eq \
        #     and abs(t.y-self.radius)<Vector3D.tol_for_eq:
        #     return True
        # return False

    def __eq__(self, other):
        assert isinstance(other,Arc),"类型错误"
        if self.center!=other.center:
            return False
        if abs(self.radius-other.radius)>Vector3D.tol_for_eq:
            return False
        if abs(self._angle1-other._angle1)>Vector3D.tol_for_eq:
            return  False
        if abs(self.da-other.da)>Vector3D.tol_for_eq:
            return False
        return True

    def calc_nearest_point(self, target: Vector3D, tol=1e-5):
        """
        计算点在线段上最近的点
        @param target:
        @param tol:
        @return: 最近点，该点的长度坐标(可以为负 也可以超过长度),target是否在直线上
        长度坐标：=0 起点，=长度 终点
        """
        assert isinstance(target,Vector3D),"类型错误"
        p=self.tf(target)
        p1=Vector3D(p.x,self.radius)#计算最近点
        rt=self.tfi(p1)
        #计算长度坐标
        le=abs(p.x-self._angle1)*self.radius
        #判断是否在arc上
        on=False
        #计算小的端点
        if self._da>0:
            mp=self._angle1
        else:
            mp=self._angle2
        #计算t点到mp点转过的角度 并放入0到2pi
        need=AngleTool.format(p.x-mp)
        #need与da比较
        if abs(self._da)<need-tol:
            on= False
        else:
            if abs(p.y-self.radius)<tol:
                on= True
            else:
                on= False

        return rt,le,on