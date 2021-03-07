from copy import deepcopy
from math import pi, sqrt
from typing import Tuple

import matplotlib.patches as mpatches
import sympy

from code2021.MyGeometric.basegeometric import BaseGeometric
from sympy import symbols
from vector3d import Vector3D, get_trans_func_polar, Line3D
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
            #若A不等于0
            if abs(A)>1e-7:
                y1=(A**2*b - A*B*a - A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2) - B*C)/(A**2 + B**2)
                y2= (A**2*b - A*B*a + A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2) - B*C)/(A**2 + B**2)
                x1=-(B*y1 + C)/A
                x2 = -(B * y2 + C) / A
            elif abs(B)>1e-7:#若B不等于0
                x1=(-A*B*b - A*C + B**2*a - B*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2))/(A**2 + B**2)
                x2= (-A*B*b - A*C + B**2*a + B*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2))/(A**2 + B**2)
                y1=-(A*x1 + C)/B
                y2 = -(A * x2 + C) / B
            else:
                raise Exception("A B近似为0 放弃计算")
            # t= [(-(B*(-A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2)) + C)/A,
            #          -A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2),),
            #         (-(B*(A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2)) + C)/A,
            #          A*sqrt(-A**2*a**2 + A**2*r**2 - 2*A*B*a*b - 2*A*C*a - B**2*b**2 + B**2*r**2 - 2*B*C*b - C**2)/(A**2 + B**2) - (-A**2*b + A*B*a + B*C)/(A**2 + B**2),)]
            if abs(dist-r)/r<1e-5:#相切
                return [(x1,y1,)]
            else:#相交
                return [(x1,y1,),(x2,y2,)]


class Arc(BaseGeometric):

    def __init__(self,center:Vector3D,radius,angle1:float,da):
        """

        @param center:
        @param radius:
        @param angle1:
        @param da: 为正时 逆时针转 绝对值不能大于2pi
        """
        assert isinstance(center,Vector3D),"类型错误"
        assert abs(da)<=1e-6+2*pi,"da绝对值必须在2pi内"
        self._center=center.copy() #type:Vector3D
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
    @start_point.setter
    def start_point(self,v):
        assert isinstance(v,Vector3D),"类型错误"
        if abs(abs(v-self.center)-self.radius)>Vector3D.tol_for_eq:
            raise Exception("点%s不在圆上"%v.__str__())
        vec=v-self.center
        self._angle1=AngleTool.format(vec.own_angle)
        #修改弧度角 逻辑比较混乱 分为正负两种
        if self._da>=0:
            self._da=AngleTool.format(self._angle2-self._angle1)
        else:
            self._da=-AngleTool.format(self._angle1-self._angle2)



    @property
    def end_point(self):
        return self.tfi(Vector3D(self._angle2,self.radius))
    @end_point.setter
    def end_point(self,v):
        assert isinstance(v,Vector3D),"类型错误"
        if abs(abs(v-self.center)-self.radius)>Vector3D.tol_for_eq:
            raise Exception("点%s不在圆上"%v.__str__())
        vec = v - self.center
        self._angle2 = AngleTool.format(vec.own_angle)
        # 修改弧度角 逻辑比较混乱 分为正负两种
        if self._da >= 0:
            self._da = AngleTool.format(self._angle2 - self._angle1)
        else:
            self._da = -AngleTool.format(self._angle1 - self._angle2)

    @property

    def mid_point(self):
        return self.tfi(Vector3D(0.5*(self._angle2+self._angle1),self.radius))

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
        if abs(AngleTool.format(self._angle1-other._angle1))>Vector3D.tol_for_eq:
            return  False
        if abs(AngleTool.format(self.da-other.da))>Vector3D.tol_for_eq:
            return False
        return True

    def calc_nearest_point(self, target: Vector3D, tol=1e-5):
        """
        计算点在线段上最近的点
        如果最近点不在圆弧两个端点内部 最近点取两个端点的一个 长度坐标会加上本身长度
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
        # 根据转向来
        if self.da>=0:
            le=AngleTool.format(p.x-self._angle1)*self.radius
        else:
            le = AngleTool.format(self._angle1-p.x) * self.radius
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
        inner=False#判断这个rt点是否在圆弧内部
        if abs(self._da)<need-tol:
            on= False
        else:
            inner=True
            if abs(p.y-self.radius)<tol:
                on= True
            else:
                on= False


        if inner is False:#如果不在arc上 长度坐标失去意义 这里加上自身长度
            le+=self.length
            t1=AngleTool.format(p.x-self._angle1)
            t2=AngleTool.format(p.x-self._angle2)
            if t1<t2:#此时最近点也失去意义 只能是两个端点
                rt=deepcopy(self.start_point)
            else:
                rt=deepcopy(self.end_point)


        return rt,le,on

    @staticmethod
    def make_by_3_points(p0:Vector3D,p1:Vector3D,p2:Vector3D,direction=1.0)->'Arc':
        """
        从三个点中生成arc
        只能生成逆时针的弧线
        @param p0:圆心
        @param p1: 圆弧起点
        @param p2: 圆弧终点到圆心 上的任何一点
        @param direction: 1.0为逆时针 -1.0为顺时针
        @return:
        """

        direction=1.0 if direction>=0 else -1.0
        if not (isinstance(p0,Vector3D),isinstance(p1,Vector3D),isinstance(p2,Vector3D)):
            raise Exception("参数类型错误")
        vec1=p1-p0#圆心到圆弧起点
        vec2=p2-p0
        radius=abs(vec1)

        angle1=AngleTool.format(vec1.own_angle)
        angle2=AngleTool.format(vec2.own_angle)
        delta_angle=AngleTool.format((angle2-angle1)*direction)
        return Arc(p0,radius,angle1,delta_angle*direction)

    def mirror(self, elo: Line3D) -> 'Arc':
        """镜像"""
        assert isinstance(elo, Line3D), "类型错误"
        center=self.center.mirror(elo)
        sp=self.start_point.mirror(elo)
        ep=self.end_point.mirror(elo)
        return Arc.make_by_3_points(center,sp,ep,-1*self.da)


    def reverse(self)->'Arc':
        """
        逆向 返回一个新的
        @return:
        """
        return Arc.make_by_3_points(self.center,self.end_point,self.start_point,-1*self.da)

    def copy(self)->'Arc':
        """复制一个新的"""
        return Arc(self.center.copy(),self.radius,self._angle1,self.da)

    def move(self,base_point:Vector3D,target_point:Vector3D)->'Arc':
        """移动 得到一个新的"""
        vec=target_point-base_point
        return Arc(self.center+vec,
                   self.radius,
                   self._angle1,
                   self.da)

    def rotate(self,base_point:Vector3D,angle:float)->'Arc':
        """旋转 得到一个新的"""
        center=self.center.rotate(base_point,angle)
        angle1=self._angle1+angle
        return Arc(center,self.radius,angle1,self.da)
        # return Arc.make_by_3_points(p0=self.center.rotate(base_point,angle),
        #                             p1=self.start_point.rotate(base_point,angle),
        #                             p2=self.end_point.rotate(base_point,angle))

    def offset(self,distance:float,direction='L')->'Arc':
        """
        偏移
        返回新的
        @param distance:
        @param direction:  L R
        @return:
        """
        direction=direction.upper()
        if self._da>0:
            if direction=='R':
                r=abs(distance)+self.radius
            elif direction=='L':
                r = self.radius - abs(distance)
            else:
                raise Exception("参数错误")
        else:
            if direction=='R':
                r=self.radius-abs(distance)
            elif direction=='L':
                r = abs(distance) + self.radius
            else:

                raise Exception("参数错误")

        return Arc(self.center,r,self._angle1,self.da)

    def intersec_point_with_line_as_circle(self,elo:Line3D):
        """
        计算圆与直线elo的交点
        本身为弧 但此时作为圆
        @param elo:
        @return:
        """
        assert isinstance(elo,Line3D),"类型错误"
        clp=CircleLineIntersecionProblem()
        clp.A,clp.B,clp.C=elo.expression()
        clp.a,clp.b=self.center.x,self.center.y
        clp.r=self.radius
        return clp.solve()

    def point_by_length_coord(self, length: float) -> Tuple['Vector3D',float]:
        """
        通过长度坐标获取线上的点
        @param length:长度坐标 只能在0到长度之间
        @return:点,该点处曲线的切向角
        """
        assert isinstance(length,(int,float)),"类型错误"
        assert 0<=length<=self.length,"参数值不在合理范围类%s"%length.__str__()
        theta=length/self.radius
        if self.da>=0:
            pass
        else:
            theta=-theta
        alpha=self._angle1+theta
        # 计算切向角
        if self.da>=0:
            beta=alpha+pi/2
        else:
            beta=3*pi/2+alpha
        t=Vector3D(alpha,self.radius)
        return self.tfi(t),beta


    def trim(self,pt:Vector3D,pt_direction:Vector3D)->'Arc':
        """
        裁切 类似于cad中trim
        @param pt: 裁断点
        @param pt_direction:指定要裁切部分 内部通过长度坐标计算 建议使用start 和end point指定 其他的可能引发意外
        @return:
        """
        assert isinstance(pt,Vector3D) and isinstance(pt_direction,Vector3D),"类型错误"
        assert pt in self,"pt不在线上"
        #确定trim的方向
        _, coord0, _ = self.calc_nearest_point(pt)
        _,coord1,_=self.calc_nearest_point(pt_direction)
        if coord1<=coord0:#裁切小坐标一侧
            return Arc.make_by_3_points(p0=self.center,
                                        p1=pt,
                                        p2=self.end_point,
                                        direction=self.da)
        else:
            return Arc.make_by_3_points(p0=self.center,
                                        p1=self.start_point,
                                        p2=pt,
                                        direction=self.da)

    def line_integral_of_vector_function(self, P, Q, pt0:Vector3D, pt1:Vector3D) -> float:
        """
        第二类线积分
        参数方程：
        x=x0+r*cos(theta)
        y=y0+r*siun(theta)
        x0,y0为圆心

        @param P: x,y的函数 由含有x y的表达式构成
        @param Q: x,y的函数 由含有x y的表达式构成
        @param pt0:
        @param pt1:
        @return: 积分值
        """
        t, x, y = symbols('t,x,y')#t代表theta
        dx = -self.radius*sympy.sin(t)  # dx/dt
        dy = self.radius*sympy.cos(t)  # dy/dt
        tihuan={x:self.center.x+self.radius*sympy.cos(t),
                y:self.center.y+self.radius*sympy.sin(t)}#使用t替换x y
        if isinstance(P,(int,float)):
            P1=P
        else:
            P1=P.subs(tihuan)
        if isinstance(Q,(int,float)):
            Q1=Q
        else:
            Q1=Q.subs(tihuan)
        jfs = P1 * dx + Q1 * dy  # 积分式 Pdx+Qdy 使用t替换后 需加上xy对t的导数
        _,cd0,_=self.calc_nearest_point(pt0)
        _,cd1,_ = self.calc_nearest_point(pt1)#计算积分起止点的长度坐标
        tt=self.tf(pt0)
        t0=tt.x#积分起点的角度
        if self.da>=0:
            t1=t0+(cd1-cd0)/self.radius
        else:
            t1=t0-(cd1-cd0)/self.radius
        jg = sympy.integrate(jfs, (t, t0, t1))
        return float(jg)