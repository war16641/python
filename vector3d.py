import math
from math import cos, sin, pi
import random
import copy
import unittest
from typing import TypeVar, Generic, List, Tuple, overload
import numpy
from GoodToolPython.linearalgebra import MyLinearAlgebraEquations
from enum import Enum, unique
import nose.tools
from collections.abc import Iterable
import  sympy as sp
from sympy import symbols, integrate

T_Vector = TypeVar('T_Vector')
T_Plane = TypeVar('T_Plane')
T_Line = TypeVar('T_Line')

class Line3D:
    pass

class Vector3D(Generic[T_Vector]):
    tol_for_eq = 1e-6  # 判断相等时的误差

    def __init__(self, x=0., y=0., z=0.):
        if isinstance(x,Iterable):
            if len(x)==2:
                self.x,self.y=x[0],x[1]
                self.z=0.
            elif len(x)==3:
                self.x, self.y,self.z = x[0], x[1],x[2]
            else:
                raise Exception("参数错误")
            return
        self.x, self.y, self.z = x, y, z

    def __abs__(self):
        return self.modulus
    def __add__(self, other: T_Vector) -> 'Vector3D':
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x += other.x
        c.y += other.y
        c.z += other.z
        return c

    def __iadd__(self, other: T_Vector) -> 'Vector3D':
        assert isinstance(other, Vector3D)
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other: T_Vector) -> 'Vector3D':
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x -= other.x
        c.y -= other.y
        c.z -= other.z
        return c

    def __isub__(self, other: T_Vector) -> 'Vector3D':
        assert isinstance(other, Vector3D)
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other: T_Vector) -> (float, T_Vector):
        if isinstance(other, (float, int)):
            c = copy.deepcopy(self)
            c.x *= other
            c.y *= other
            c.z *= other
            return c
        elif isinstance(other, Vector3D):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            raise Exception("type error")

    def __rmul__(self, other: float) -> 'Vector3D':
        assert isinstance(other, (float, int))
        return self.__mul__(other)

    def __pow__(self, power, modulo=None):
        """

        :param power:
        :param modulo:
        :return:
        """
        assert power == 2.0
        return self * self

    def __truediv__(self, other):
        assert isinstance(other,(int,float))
        return Vector3D(self.x/other,self.y/other,self.z/other,)
        pass

    def __eq__(self, other: (T_Vector, int)) -> bool:
        if isinstance(other, Vector3D):
            c = self - other
            if c.modulus < self.tol_for_eq:
                return True
            else:
                return False
        elif isinstance(other, int):
            assert other == 0  # 当和数比较时，只能和0比较
            if self.modulus <= self.tol_for_eq:
                return True
            else:
                return False
        else:
            raise Exception("type error")

    def __str__(self) -> str:
        return "%f,%f,%f" % (self.x, self.y, self.z)

    def get_standard_copy(self, scale=1.) -> T_Vector:
        """
        返回一个标准大小的复制向量
        :param scale:复制向量的模
        :return:
        """
        r = copy.deepcopy(self)
        r.modulus = 1
        return r

    def copy(self)->'Vector3D':
        """复制一个新的"""
        return Vector3D(self.x,self.y,self.z)

    def distance_to_plane(self, p: T_Plane) -> float:
        """
        点到平面的距离
        :param p: 平面
        :return:
        """
        assert isinstance(p, Plane3D)
        n_st = p.normal.get_standard_copy()
        return abs((self - p.point) * n_st)

    def distance_to_line(self, elo: T_Line) -> float:
        """点到直线的距离"""
        assert isinstance(elo, Line3D)
        d_st = elo.direction.get_standard_copy()
        y = self - elo.point
        lt = y * d_st
        z = d_st * lt
        return (y - z).modulus

    def get_nearest_point_to_line(self,elo:'Line3D')->"Vector3D":
        """点到直线最近的点"""
        assert isinstance(elo,Line3D)
        n=elo.direction.get_standard_copy()
        p=elo.point
        pm=self-p
        pn=(pm*n)*n
        return p+pn

    @staticmethod
    def is_parallel(v1: T_Vector, v2: T_Vector):
        """判断两个向量是否平行"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        v1_st = copy.deepcopy(v1)
        v1_st.modulus = 1
        v2_st = copy.deepcopy(v2)
        v2_st.modulus = 1
        return 1 - abs(v1_st * v2_st) < Vector3D.tol_for_eq

    def is_perpendicular(self, other: T_Vector) -> bool:
        """
        判断是否垂直
        :param other:
        :return:
        """
        assert isinstance(other, Vector3D)
        return self * other == 0

    def mixed_product(self, b: T_Vector, c: T_Vector) -> float:
        """
        混合积 [self,b,c]
        :param b:
        :param c:
        :return:
        """
        assert isinstance(b, Vector3D)
        assert isinstance(c, Vector3D)
        return self * Vector3D.cross_product(b, c)

    def decompose(self, v1: T_Vector, v2: T_Vector, v3: T_Vector) -> list:
        """
        将向量分解到3个方向上去 3个方向不能同平面
        :param v1: 只表示方向
        :param v2:
        :param v3:
        :return: 3个向量组成的list
        """
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        assert isinstance(v3, Vector3D)
        assert abs(v1.mixed_product(v2, v3)) > self.tol_for_eq  # "3个向量不能是同平面"
        # 利用线性方程组求解
        A = numpy.hstack((v1.get_matrix(), v2.get_matrix(), v3.get_matrix()))
        b = self.get_matrix()
        eq = MyLinearAlgebraEquations(A=A, b=b)
        assert eq.num_of_solutions is MyLinearAlgebraEquations.NumOfSolution.one  # 这种分解一定是唯一的
        a1 = v1 * eq.x[0, 0]
        b1 = v2 * eq.x[1, 0]
        c1 = v3 * eq.x[2, 0]
        return [a1, b1, c1]

    def get_coordinates_under_cartesian_coordinates_system(self,basic_vectors:tuple)->'Vector3D':
        """
        将本向量在新的笛卡尔坐标系中分解 返回新坐标
        :param basic_vectors: 新的笛卡尔坐标的基向量 这些基向量既不一定正交 也不一定是单位向量 但是要求不能共面
        :return: 新笛卡尔坐标系的坐标 组成的向量
        """
        assert isinstance(basic_vectors,tuple)
        assert len(basic_vectors)==3#要求其为包含3个向量的元组
        v1,v2,v3=basic_vectors
        assert abs(v1.mixed_product(v2, v3)) > self.tol_for_eq  , "3个向量不能是同平面"
        # 利用线性方程组求解
        A = numpy.hstack((v1.get_matrix(), v2.get_matrix(), v3.get_matrix()))
        b = self.get_matrix()
        eq = MyLinearAlgebraEquations(A=A, b=b)
        assert eq.num_of_solutions is MyLinearAlgebraEquations.NumOfSolution.one  # 这种分解一定是唯一的
        return Vector3D(eq.x[0, 0],eq.x[1, 0],eq.x[2, 0])#这个向量仅代表在basic_vectors下的坐标

    def get_matrix(self) -> numpy.matrix:
        """
        将坐标以列矩阵的形式返回
        :return:
        """
        t = numpy.matrix([self.x, self.y, self.z])
        return t.T

    @property
    def modulus(self) -> float:
        """模"""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    @modulus.setter
    def modulus(self, v: float) -> None:
        assert not (self.x == 0 and self.y == 0 and self.z == 0)  # 零向量不能设定模
        # assert v >= 0  # 模不能为负
        t = self.modulus
        sign = 1
        if v < 0:
            sign = -1  # 当v模为负时，向量反向
            v *= -1
        self.x *= v / t * sign
        self.y *= v / t * sign
        self.z *= v / t * sign

    def get_spheroidal_coordinates(self):
        """
        返回该点在球坐标系下的坐标
        球坐标系定义见《微积分 下册》P146 图7-25
        :return: phi,theta,r
                phi -pi,pi
                theta 0,pi
                r >=0
        """
        phi=self.calculate_angle_in_xoy(self.x,self.y)
        r=self.modulus
        tmp1=(self.x**2+self.y**2)**0.5
        theta=math.asin(tmp1/r)
        return phi,theta,r
        pass


    @staticmethod
    def calculate_angle_in_xoy(x:float=0.,y:float=0.)->float:
        """
        计算平面内的点(x,y)与原点连线 和 x轴形成的夹角 以x轴正向转向y轴正向为正
        :param x:
        :param y:
        :return:-pi,pi
        """
        if x==0:
            if y==0:
                return 0.0 # 0向量与x轴夹角为0
            elif y>0:
                return math.pi/2
            else:
                return -math.pi/2

        t=math.atan(y/x)

        if x<0:
            if y>0:
                return t + math.pi
            else:
                return t-math.pi

        return t

    @staticmethod
    def cross_product(v1, v2) -> T_Vector:
        """向量叉乘"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        return Vector3D(v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x)

    @staticmethod
    def angle(v1: T_Vector, v2: T_Vector) -> float:
        """返回两个向量的夹角 返回范围：0，pi"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        t = v1 * v2 / (v1.modulus * v2.modulus)
        return math.acos(t)

    def angle(self,other)->float:
        assert isinstance(other,Vector3D)
        t = self * other / (self.modulus * other.modulus)
        #有时候t会在±1处波动 把他设置为±1
        if t>1 and t-1<self.tol_for_eq:
            t=1
        elif t<-1 and -1-t<self.tol_for_eq:
            t=-1

        return math.acos(t)

    @staticmethod
    def make_random_vector()->T_Line:
        """
        随机产生一直线
        :return:
        """
        return Vector3D(x=random.random(),
                        y=random.random(),
                        z=random.random())

    @staticmethod
    def make_from_array(arr)->T_Vector:
        """
        从array中生成向量
        要求arr的长度为3
        :param arr:
        :return:
        """
        assert isinstance(arr,numpy.ndarray)
        assert len(arr)==3
        return Vector3D(arr[0],arr[1],arr[2])

    @staticmethod
    def make_from_list(arr)->T_Vector:
        """
        从FLOAT的llist中生成向量
        要求arr的长度为3
        :param arr:
        :return:
        """
        assert isinstance(arr,(tuple,list))
        if len(arr)==0:
            return Vector3D(0,0,0)
        elif len(arr)==1:
            return Vector3D(arr[0])
        elif len(arr)==2:
            return Vector3D(arr[0],arr[1])
        else:
            return Vector3D(arr[0],arr[1],arr[2])

    def __getitem__(self, item):
        """
        使用索引访问xyz
        @param item: 0 1 2
        @return:
        """
        if item==0:
            return self.x
        elif item==1:
            return self.y
        elif item==2:
            return self.z
        else:
            raise Exception("参数错误")

    @staticmethod
    def get_bound_corner(lst:List['Vector3D'])-> Tuple['Vector3D', 'Vector3D']:
        """
        获取这些点的xyz范围 即范围角点
        @param lst:
        @return:
        """
        assert isinstance(lst,(tuple,list))
        t1=[x.x for x in lst]
        t2 = [x.y for x in lst]
        t3 = [x.z for x in lst]
        t1a=min(t1)
        t1b=max(t1)
        t2a=min(t2)
        t2b=max(t2)
        t3a=min(t3)
        t3b=max(t3)
        return Vector3D(t1a,t2a,t3a),Vector3D(t1b,t2b,t3b)

    @property
    def own_angle(self):
        """自己在xoy平面内的向量
        计算平面内的点(x,y)与原点连线 和 x轴形成的夹角 以x轴正向转向y轴正向为正
        :return:-pi,pi
        """
        x=self.x
        y=self.y
        if x == 0:
            if y == 0:
                return 0.0  # 0向量与x轴夹角为0
            elif y > 0:
                return math.pi / 2
            else:
                return -math.pi / 2

        t = math.atan(y / x)

        if x < 0:
            if y > 0:
                return t + math.pi
            else:
                return t - math.pi

        return t

    def mirror(self,elo:Line3D)->'Vector3D':
        assert isinstance(elo,Line3D),"类型错误"
        A,B,C=elo.expression()
        x0,y0=self.x,self.y
        return Vector3D(-(A*(A*x0 + B*y0 + 2*C) + B*(A*y0 - B*x0))/(A**2 + B**2),
                        (A*(A*y0 - B*x0) - B*(A*x0 + B*y0 + 2*C))/(A**2 + B**2))

    def rotate(self,base_point:'Vector3D',angle:float)->'Vector3D':
        """
        绕base point逆时针旋转angle
        @param base_point:
        @param angle:
        @return:
        """
        assert isinstance(base_point,Vector3D) and isinstance(angle,(float,int))\
        ,"类型错误"
        tf,tfi=get_trans_func_polar(base_point,(self-base_point).own_angle)
        rou=abs(base_point-self)
        p2_new=Vector3D(angle,rou)#待求点在新坐标系下的坐标
        return tfi(p2_new)

class Plane3D(Generic[T_Plane]):
    """平面"""

    @unique
    class PositionRelationForPlane(Enum):  # 面与面的位置关系 同样一下定义是严格互斥 不同于数学上的定义
        coplane = 1
        parallel = 2
        perpendicular = 3
        skew = 4

    @unique
    class PositionRelationForLine(Enum):
        include = 1
        parallel = 2
        perpendicular = 3
        skew = 4

    def __init__(self, normal: Vector3D, point: Vector3D):
        """
        采用平面上一点和法向量来表示平面
        :param normal: 法向量
        :param point: 平面上的一个点
        """
        assert isinstance(normal, Vector3D)
        assert isinstance(point, Vector3D)
        self.normal = normal
        self.point = point

    def __str__(self) -> str:
        return "normal:%s point:%s" % (self.normal, self.point)

    def __contains__(self, item: (T_Vector, T_Line)) -> bool:
        """
        判断点、线是否在平面上
        :param item:
        :return:
        """
        if isinstance(item, Vector3D):
            if item.distance_to_plane(self) < Vector3D.tol_for_eq:
                return True
            else:
                return False
        elif isinstance(item, Line3D):
            if item.point.distance_to_plane(self) < Vector3D.tol_for_eq \
                    and item.direction.is_perpendicular(self.normal):
                return True
            else:
                return False

        else:
            raise Exception("type error")

    def __judge_pr_plane(self, pl: T_Plane) -> PositionRelationForPlane:
        """
        判断面与面的位置关系 只能内部调用
        :param pl:
        :return:
        """
        if Vector3D.is_parallel(self.normal, pl.normal):  # 至少平行
            tmp1 = self.point - pl.point
            if tmp1.is_perpendicular(self.normal):
                return self.PositionRelationForPlane.coplane
            else:
                return self.PositionRelationForPlane.parallel
        else:  # 相交了
            if self.normal.is_perpendicular(pl.normal):
                return self.PositionRelationForPlane.perpendicular
            else:
                return self.PositionRelationForPlane.skew

    def __judge_pr_line(self, elo: T_Line) -> PositionRelationForLine:
        if self.normal.is_perpendicular(elo.direction):  # 至少平行
            if elo.point in self:
                return self.PositionRelationForLine.include
            else:
                return self.PositionRelationForLine.parallel
        else:  # 非平行
            if Vector3D.is_parallel(self.normal, elo.direction):
                return self.PositionRelationForLine.perpendicular
            else:
                return self.PositionRelationForLine.skew

    def judge_position_relation(self, item: (T_Line, T_Plane)) -> Enum:
        if isinstance(item, Plane3D):
            return self.__judge_pr_plane(item)
        elif isinstance(item, Line3D):
            return self.__judge_pr_line(item)
        else:
            raise Exception("type error")

    def angle(self, other: (T_Plane, T_Line)) -> float:
        """
        计算两个平面夹角
        :param other:
        :return: 范围：0,pi 与平面  0,pi/2 与直线
        """
        if isinstance(other, Plane3D):
            return math.pi-self.normal.angle(other.normal)
            # return math.pi - Vector3D.angle(self.normal, other.normal)
        elif isinstance(other, Line3D):
            # 要求直线与平面的关系必须为斜交或者垂直
            assert self.judge_position_relation(other) in (self.PositionRelationForLine.skew, \
                                                           self.PositionRelationForLine.perpendicular)
            alpha=self.normal.angle(other.direction)
            # alpha = Vector3D.angle(self.normal, other.direction)
            if alpha < math.pi / 2:
                return math.pi / 2 - alpha
            else:
                return alpha - math.pi / 2
        else:
            raise Exception("type error")

    def projection(self, item: (T_Line, T_Vector)) -> (T_Line,T_Vector):
        """
        直线elo在此平面内的投影所得的直线 或是
        点在此平面的投影所得点
        elo不能垂直于平面
        :param item:
        :return:
        """
        if isinstance(item, Vector3D):
            return self.__projection_point(item)
        elif isinstance(item, Line3D):
            return self.__projection_line(item)
        else:
            raise Exception("type error")

    def __projection_point(self, pt: T_Vector) -> T_Vector:
        """
        空间点在平面上的投影
        :param pt:
        :return:
        """
        assert isinstance(pt, Vector3D)
        n = self.normal.get_standard_copy()
        a = pt - self.point
        m = a * n
        n.modulus = m
        b = a - n
        return self.point + b

    def __projection_line(self, elo: T_Line) -> T_Line:
        """
        直线在此平面内的投影
        要求直线不能垂直于平面
        :param elo:
        :return:
        """
        assert isinstance(elo, Line3D)
        assert self.judge_position_relation(
            elo) is not self.PositionRelationForLine.perpendicular  # 直线不能垂直于此平面 否则不会产生投影直线
        # 利用直线上任意两点在平面的投影计算投影直线
        pt1 = elo.point
        pt2 = elo.point + elo.direction
        pt1_pro = self.projection(pt1)
        pt2_pro = self.projection(pt2)
        tmp=Line3D.make_line_by_2_points(pt1_pro, pt2_pro)
        assert abs(elo.direction.mixed_product(tmp.direction,self.normal))<Vector3D.tol_for_eq
        return tmp

    def get_intersect_line(self,other:T_Plane)->T_Line:
        """
        计算此平面与另一平面的交线
        要求此两平面的关系为斜交 垂直 否则返回None
        :param other:
        :return:
        """
        assert isinstance(other,Plane3D)
        if self.judge_position_relation(other) not in (self.PositionRelationForPlane.skew,\
                                                       self.PositionRelationForPlane.perpendicular):
            return None
        else:
            d=Vector3D.cross_product(self.normal,other.normal)
            tmp=Line3D.make_line_by_2_points(self.get_random_point(),other.get_random_point())#随机穿过两平面的一直线
            # tmp=Line3D.make_line_by_2_points(Vector3D(10,0,0),Vector3D(0,1,10))
            tmp1=self.projection(tmp)#该直线在此平面的投影
            p=other.get_intersect_point(tmp1)#投影直线与另一平面的交点
            return Line3D(direction=d,point=p)

    def get_intersect_point(self,elo:T_Line)->T_Vector:
        """
        获取直线与此平面的交点
        要求直线与平面： 斜交或者垂直 否则返回None
        :param elo:
        :return:
        """
        assert isinstance(elo,Line3D)
        if self.judge_position_relation(elo) not in (self.PositionRelationForLine.skew,\
                                                     self.PositionRelationForLine.perpendicular):
            return None
        else:
            m=self.point-elo.point
            t=(m*self.normal)/(elo.direction*self.normal)
            return elo.point+t*elo.direction

    def get_random_line(self)->T_Line:
        """
        随机获取平面上一直线
        :return:
        """
        tmp=Line3D(direction=Vector3D.make_random_vector(),
                   point=Vector3D.make_random_vector())#产生随机直线
        return self.projection(tmp)#返回随机直线在平面上的投影

    def get_random_point(self)->T_Vector:
        """随机获得平面上一点"""
        return self.get_random_line().get_random_point()



class ParametricEquationOfLine:
    """
    直线的参数方程
    x=x1*t + x2
    y=y1*t + y2
    """
    zeros_tol=1e-9#等于0的误差
    @overload
    def __init__(self,A:float,B:float,C:float):
        pass
    @overload
    def __init__(self,elo:Line3D):
        pass

    def __init__(self,A:float=None,B:float=None,C:float=None,
                 elo:Line3D=None):
        """
        可以通过直线一般方程的三个系数实例化
        或者 通过line3d对象实例化
        @param A:
        @param B:
        @param C:
        @param elo:
        """
        self.x1,self.x2=0,0
        self.y1,self.y2=0,0
        if A is not None and B is not None and C is not None:
            assert isinstance(A,(int,float)) and isinstance(B,(int,float)) and \
                   isinstance(C, (int, float)),"类型错误"
            if abs(A)>ParametricEquationOfLine.zeros_tol:
                self.x1=-B
                self.x2=-C/A
                self.y1=A
                self.y2=0
            elif abs(B)>ParametricEquationOfLine.zeros_tol:
                self.x1=B
                self.x2=0
                self.y1=-A
                self.y2=-C/B
            else:
                raise Exception("A B都等于0")
        elif isinstance(elo,Line3D):
            A,B,C=elo.expression()
            if abs(A)>ParametricEquationOfLine.zeros_tol:
                self.x1=-B
                self.x2=-C/A
                self.y1=A
                self.y2=0
            elif abs(B)>ParametricEquationOfLine.zeros_tol:
                self.x1=B
                self.x2=0
                self.y1=-A
                self.y2=-C/B
            else:
                raise Exception("A B都等于0")
        else:
            raise Exception("参数错误")


    def calc_t(self,pt:Vector3D)->float:
        """
        求解点pt的参数
        @param pt:
        @return:
        """
        assert isinstance(pt,Vector3D)
        x=pt.x
        y=pt.y

        # 判断哪一个的一阶系数不为0
        if abs(self.x1) > ParametricEquationOfLine.zeros_tol:
            rt= (x - self.x2) / self.x1
        else:
            rt= (y - self.y2) / self.y1

        #反向验证是否得到这个点
        if self.get_point(rt)==pt:
            return rt
        else:
            raise Exception("求解t失败，点%s不在此参数方程上"%pt.__str__())


    def get_point(self,t:float)->Vector3D:
        """通过参数t得到点"""
        assert isinstance(t,(int,float))
        return Vector3D(self.x1*t+self.x2,self.y1*t+self.y2)

    def line_integral_of_vector_function(self,P,Q,pt0,pt1)->float:
        """
        第二类曲线积分
        即：int(Pdx+Qdy)
        算法：微积分下册 P182
        注意：本函数不会检查参数的类型
        @param P: x,y的函数 由含有x y的表达式构成
        @param Q:x,y的函数 由含有x y的表达式构成
        @param pt0:起点
        @param pt1:终点
        @return:积分值
        """
        t,x,y=symbols('t,x,y')
        dx=self.x1#dx/dt
        dy=self.y1#dy/dt
        tihuan={x:self.x1*t+self.x2,
                y:self.y1*t+self.y2}#使用t替换x y
        if isinstance(P,(int,float)):
            P1=P
        else:
            P1=P.subs(tihuan)
        if isinstance(Q,(int,float)):
            Q1=Q
        else:
            Q1=Q.subs(tihuan)
        jfs=P1*dx+Q1*dy#积分式 Pdx+Qdy 使用t替换后 需加上xy对t的导数
        t0=self.calc_t(pt0)
        t1=self.calc_t(pt1)#计算积分起止点
        jg=integrate(jfs,(t,t0,t1))
        return float(jg)




class Line3D(Generic[T_Line]):
    """线"""

    @unique
    class PositionRelation(Enum):  # 线与线位置关系枚举类 以下的定义不是严格意义上的数学定义 它们之间是互斥的 比如intersect就只指不会平行也不会垂直也不会共线的相交
        parallel = 1
        perpendicular = 2
        intersect = 3
        non_intersect = 4
        collinear = 5

    def __init__(self,
                 direction: T_Vector,
                 point: T_Vector = Vector3D(0, 0, 0)
                 ):
        """
        采用线上一点和线的方向表示直线
        :param direction:
        :param point:
        """
        assert isinstance(direction, Vector3D)
        assert isinstance(point, Vector3D)
        assert not direction == 0  # 方向不能为0
        self.direction, self.point = copy.deepcopy(direction), copy.deepcopy(point)

    def __str__(self):
        return "direction:%s point:%s" % (self.direction, self.point)

    def __contains__(self, item):
        """判断点是否在线上"""
        assert isinstance(item, Vector3D)
        return Vector3D.is_parallel(item - self.point, self.direction)

    def __eq__(self, other: T_Line) -> bool:
        assert isinstance(other, Line3D)
        if not Vector3D.is_parallel(self.direction, other.direction):  # 方向要相同
            return False
        if self.point == other.point:  # 点相同
            return True
        else:
            if Vector3D.is_parallel(self.direction, self.point - other.point):  # 两线任一点构成的向量与方向相同
                return True
            else:
                return False

    @staticmethod
    def distance_between_two_lines(elo1: T_Line, elo2: T_Line) -> float:
        """
        两个线之间的距离
        警告：当两个线平行的时候 返回的距离为0
        :param elo1:
        :param elo2:
        :return:
        """
        assert isinstance(elo1, Line3D)
        assert isinstance(elo2, Line3D)

        # A=numpy.matrix([[2*elo1.direction**2,-2*elo1.direction*elo2.direction],
        #                 [-2*elo1.direction*elo2.direction,2*elo2.direction**2]])
        # b=numpy.matrix([[2*elo1.direction*elo2.point-2*elo1.direction*elo1.point],
        #                 [2*elo2.direction*elo1.point-2*elo2.direction*elo2.point]])
        # xishu=A.I*b
        # t1=xishu[0,0]
        # t2=xishu[1,0]
        # return (elo1.point+t1*elo1.direction-elo2.point-t2*elo2.direction).modulus

        t1 = Vector3D.cross_product(elo1.direction, elo2.direction)  # 先得到最短垂线的方向
        t2 = elo1.point - elo2.point  # 取连接两条线的任一向量
        return abs(t1 * t2)

    def judge_position_relation(self, other: T_Line) -> PositionRelation:
        """
        判断两直线的最准确的位置关系
        不相交时也不会平行
        :param other:
        :return: 平行 垂直 相交 不相交
        """
        assert isinstance(other, Line3D)
        if Vector3D.is_parallel(self.direction, other.direction):  # 同向
            tmp1 = self.point - other.point
            if tmp1==0:
                tmp1+=self.direction#处理当两个直线的点重合时的意外情况
            if Vector3D.is_parallel(tmp1, self.direction):  # 共线
                return self.PositionRelation.collinear
            return self.PositionRelation.parallel
        if self.distance_between_two_lines(self, other) < Vector3D.tol_for_eq:  # 共面
            if self.direction.is_perpendicular(other.direction):
                return self.PositionRelation.perpendicular
            else:
                return self.PositionRelation.intersect
        else:  # 不相交
            return self.PositionRelation.non_intersect

    def angle(self, other: T_Line) -> float:
        """
        与另一直线的夹角 调用Vector.angle实现
        当两线不在统一平面内时 将两线投影到平面（以公垂线为法线的平面）形成的角度
        :param other:
        :return: 位于0到pi之间
        """
        assert isinstance(other, Line3D)
        return self.direction.angle(other.direction)
        # return Vector3D.angle(self.direction, other.direction)
    def get_intersect_point(self,other:T_Line)->T_Vector:
        """
        计算与另一直线的交点
        要求此两直线位置关系为 相交 垂直 否则返回None
        :param other:
        :return:
        """
        assert isinstance(other,Line3D)
        if self.judge_position_relation(other) not in (self.PositionRelation.perpendicular,\
                                                       self.PositionRelation.intersect):
            return None
        else:
            tmp=other.point-self.point
            li=tmp.decompose(self.direction,other.direction,Vector3D.cross_product(self.direction,other.direction))
            return self.point+li[0]

    def get_random_point(self)->T_Vector:
        """
        随机获得直线上一点
        :return:
        """
        return self.point+self.direction*random.uniform(0.1,100)

    @staticmethod
    def make_line_by_2_points(point1: Vector3D, point2: Vector3D) -> 'Line3D':
        """
        通过直线上两点生成直线
        :param point1:
        :param point2:
        :return:
        """
        assert isinstance(point1, Vector3D)
        assert isinstance(point2, Vector3D)
        assert point1 != point2
        return Line3D(direction=point2 - point1, point=point1)

    def get_point(self,axis:str='x',v:float=0.)->'Vector3D':
        """
        通过指定直线上一点某一个分量的值 返回此点坐标
        :param axis:
        :param v:
        :return:
        """
        assert isinstance(axis,str)
        assert isinstance(v,(int,float))
        axis=axis.lower()
        if axis == 'x':
            assert self.direction.x>1e-15,'此直线不存在x=0的点'
            t=(v-self.point.x)/self.direction.x
            return self.point+t*self.direction
        else:
            raise Exception("参数错误")

    def get_parameter(self,p:Vector3D)->float:
        """
        得到点在直线上的参数
        具体：直线为参数式方程形式 每一个点都会对应一个参数值
        使用了广义逆矩阵求解
        警告：不检查点是否真的在直线上
        @param p:
        @return:
        """
        A = numpy.array([[self.direction.x], [self.direction.y], [self.direction.z]])
        b = numpy.array([[p.x-self.point.x], [p.y-self.point.y], [p.z-self.point.z]])
        return MyLinearAlgebraEquations.least_squares_solution(A,b)

    def calc_line_integral_of_vector_function(self,m:Vector3D,n:Vector3D,P,Q):
        """
        求曲线（直线）的第二类积分
        来自于《微积分下层》 P181 ，使用参数方程法计算第二类积分
        @param m: 积分起点 不会检查这个点是否真的在直线上 下同
        @param n:  积分终点
        @param P:
        @param Q:
        @return:
        """
        # assert isinstance(P,sp.core.symbol.Symbol)
        # assert isinstance(Q, sp.core.symbol.Symbol)
        x=sp.symbols('x')
        y = sp.symbols('y')
        z = sp.symbols('z')
        alpha=sp.symbols('alpha')
        P=P.subs([[x,self.direction.x*alpha+self.point.x],
                  [y,self.direction.y*alpha+self.point.y],
                  [z,self.direction.z*alpha+self.point.z]])#使用参数计算第二类积分
        Q=Q.subs([[x,self.direction.x*alpha+self.point.x],
                  [y,self.direction.y*alpha+self.point.y],
                  [z,self.direction.z*alpha+self.point.z]])#使用参数计算第二类积分
        alpha1=self.get_parameter(m)
        alpha2=self.get_parameter(n)#积分上下限
        return sp.integrate(P*self.direction.x+Q*self.direction.y,(alpha,alpha1,alpha2))

    @property
    def dangle(self):
        """
        直线的方向角
        @return:
        """
        return Vector3D.calculate_angle_in_xoy(self.direction.x,self.direction.y)

    def expression(self):
        """一般表达式
        Ax+By+C=0
        返回 A,B,C
        """
        if abs(self.direction.x)>1e-6:
            k=self.direction.y/self.direction.x
            b=self.point.y-k*self.point.x
            return k,-1,b
        else:#k为无穷大 竖直线
            return 1,0,-self.point.x

def get_trans_func_polar(p:Vector3D=None,theta=0.0):
    """
    极坐标转换函数
    先平移 后旋转
    仅支持平面内的变化 z恒=0
    @param p: 在原坐标系下的从原坐标系原点指向新坐标系原点的向量
    @param theta: 旋转角度 逆时针为正
    @return: 函数和逆函数
    """
    class transfuncpolar:
        def __init__(self, p: Vector3D = None, theta=0.):
            if p is None:
                p = Vector3D(0, 0, 0)
            self.p = p
            self.theta = theta

        def calc(self, v: Vector3D):
            sl = v - self.p
            # 计算半径 rou
            rou = abs(sl)

            # 计算角度
            theta = (sl.own_angle - self.theta)

            return Vector3D(theta, rou)

        def calci(self, v: Vector3D):
            theta1 = v.x + self.theta
            x = v.y * cos(theta1)
            y = v.y * sin(theta1)
            return Vector3D(x + self.p.x, y + self.p.y)

    tfp=transfuncpolar(p=p,theta=theta)
    return tfp.calc,tfp.calci


def get_trans_func(p:Vector3D=None,theta=0.0):
    """
    得到坐标系平移旋转后的坐标变化函数
    坐标变化
    仅支持平面内的变化 z恒=0
    @param p: 在原坐标系下的从原坐标系原点指向新坐标系原点的向量
    @param theta: 旋转角度 逆时针为正
    @return: 函数和逆函数
    """
    class transfunc:
        def __init__(self,p:Vector3D=None,theta=0.):
            if p is None:
                p=Vector3D(0,0,0)
            self.p=p
            self.theta=theta

        def calc(self,v):
            """

            @param v: 在原始坐标系下的坐标
            @return: 在新坐标系下坐标
            """

            return Vector3D(x=cos(self.theta)*v.x+sin(self.theta)*v.y-self.p.x*cos(self.theta)-self.p.y*sin(self.theta),
                            y=-sin(self.theta) * v.x + cos(self.theta) * v.y + self.p.x * sin(self.theta) - self.p.y * cos(self.theta))

        def calci(self,v):
            """
            逆变换
            @param v:
            @return:
            """
            return Vector3D(
                x=cos(self.theta) * v.x - sin(self.theta) * v.y + self.p.x ,
                y=sin(self.theta) * v.x + cos(self.theta) * v.y + self.p.y )

    t=transfunc(p=p,theta=theta)
    return t.calc,t.calci



class TestCase(unittest.TestCase):
    def test1(self):
        # 测试开始
        a = Vector3D(1, 1, 1)
        b = Vector3D(2, 2, 2)
        c = Vector3D(1, 1, 1)
        assert a * b == 6
        assert a != b
        assert a == c
        a += c
        assert a == b

        a = Vector3D(0, 0, 0)
        b = Vector3D(1e-7, 0, -1e-8)
        assert a == 0
        assert b == 0

        a = Vector3D(1, 1, 1)
        b = Vector3D(2, 2, 2)
        assert b == 2 * a

        v = Vector3D(1, 1, 1)
        a = Vector3D(1, 0, 0)
        b = Vector3D(0, 1, 0)
        b1 = Vector3D(1, 1, 0)
        c = Vector3D(0, 0, 1)
        nose.tools.assert_raises(AssertionError, v.decompose, a, b, b1)
        li = v.decompose(a, b, c)
        assert li[0] == a and li[1] == b and li[2] == c

        elo1 = Line3D(direction=Vector3D(1, 0, 0), point=Vector3D())
        elo2 = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(2, 0, 0))
        assert Vector3D(2, 0, 0) == elo1.get_intersect_point(elo2) and Vector3D(2, 0, 0) == elo2.get_intersect_point(
            elo1)
        elo2 = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(2, 0, 1))
        # nose.tools.assert_raises(AssertionError,elo1.get_intersect_point,elo2)
        assert elo1.get_intersect_point(elo2) is None
        elo2 = Line3D(direction=Vector3D(1, -1, 0), point=Vector3D(0, 1, 0))
        assert Vector3D(1, 0, 0) == elo1.get_intersect_point(elo2)

        v = Vector3D(1, 1, 1)
        phi, _, _ = v.get_spheroidal_coordinates()
        assert phi == math.pi / 4
        v = Vector3D(-1, -1, 1)
        phi, _, _ = v.get_spheroidal_coordinates()
        assert phi == -3 * math.pi / 4
        v = Vector3D(1, -1, 1)
        phi, _, _ = v.get_spheroidal_coordinates()
        assert phi == -math.pi / 4
        v = Vector3D(-1, 1, 1)
        phi, _, _ = v.get_spheroidal_coordinates()
        assert phi == 3 * math.pi / 4
        v = Vector3D(-1, 3 ** 0.5, 1)
        phi, _, _ = v.get_spheroidal_coordinates()
        assert abs(phi - 2 * math.pi / 3) < 1e-15
        # 测试结束

        # 测试开始平面
        a = Vector3D(0, 0, 1)
        b = Vector3D(2, 2, 2)
        p1 = Plane3D(a, b)
        assert b in p1
        c = Vector3D(1, 1.1, 2)
        assert c in p1
        assert a not in p1
        elo = Line3D(Vector3D(0, 1, 0), Vector3D(2, -.2, 2))
        assert elo in p1

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        b = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(10, 10, 10))
        assert a.judge_position_relation(b) == a.PositionRelationForPlane.parallel
        b = Plane3D(normal=Vector3D(0, 1, 0), point=Vector3D(10, 10, 10))
        assert a.judge_position_relation(b) == a.PositionRelationForPlane.perpendicular
        b = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(10, 10, 0))
        assert a.judge_position_relation(b) == a.PositionRelationForPlane.coplane
        b = Plane3D(normal=Vector3D(1, 0, 1), point=Vector3D(10, 10, 0))
        assert a.judge_position_relation(b) == a.PositionRelationForPlane.skew

        elo = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(0, 0, 0))
        assert a.judge_position_relation(elo) is a.PositionRelationForLine.include
        elo = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(0, 0, 10))
        assert a.judge_position_relation(elo) is a.PositionRelationForLine.parallel
        elo = Line3D(direction=Vector3D(0, 0, 1), point=Vector3D(0, 0, 10))
        assert a.judge_position_relation(elo) is a.PositionRelationForLine.perpendicular
        elo = Line3D(direction=Vector3D(1, 1, 1), point=Vector3D(0, 0, 10))
        assert a.judge_position_relation(elo) is a.PositionRelationForLine.skew

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        b = Plane3D(normal=Vector3D(0, 1, 0), point=Vector3D(10, 10, 10))
        assert a.angle(b) == math.pi / 2

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        elo = Line3D(direction=Vector3D(0, 0, -1), point=Vector3D())
        assert a.angle(elo) == math.pi / 2
        elo = Line3D(direction=Vector3D(0, 1, 1), point=Vector3D())
        assert abs(a.angle(elo) - math.pi / 4) < Vector3D.tol_for_eq
        elo = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D())
        nose.tools.assert_raises(AssertionError, a.angle, elo)

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        pt = Vector3D(10, 10, 0)
        assert a.projection(pt) == pt
        b = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 2))
        assert b.projection(pt) == Vector3D(10, 10, 2)

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        line = Line3D(direction=Vector3D(0, 0, 1), point=Vector3D())
        nose.tools.assert_raises(AssertionError, a.projection, line)
        line = Line3D(direction=Vector3D(1, 1, 0), point=Vector3D(0, 0, 10))
        line1 = Line3D(direction=Vector3D(1, 1, 0), point=Vector3D())
        t = a.projection(line)
        assert t == line1
        line = Line3D(direction=Vector3D(0, 1, 1), point=Vector3D(0, 0, 0))
        line1 = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D())
        assert a.projection(line) == line1

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        assert a.get_random_line() in a
        assert a.get_random_point() in a

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        b = Plane3D(normal=Vector3D(1, 0, 0), point=Vector3D(0, 0, 0))
        elo = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D())
        assert a.get_intersect_line(b) == elo

        a = Plane3D(normal=Vector3D(0, 0, 1), point=Vector3D(0, 0, 0))
        elo = Line3D(direction=Vector3D(0, 0, 1), point=Vector3D(10, 20, 0))
        assert a.get_intersect_point(elo) == Vector3D(10, 20, 0)
        elo = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(10, 20, 0))
        assert a.get_intersect_point(elo) is None
        # 测试结束

        # 测试开始 直线
        a = Line3D(Vector3D(1, 0, 0))
        b = Vector3D(1.1, 0, 0)
        c = Vector3D(1, 4, 3)
        assert b in a
        assert c not in a
        assert b.distance_to_line(a) == 0
        assert c.distance_to_line(a) == 5.

        a = Line3D(Vector3D(1, 0, 0))
        b = Line3D(Vector3D(0, 1, 0), Vector3D(0, 0, 4))
        assert 4 == Line3D.distance_between_two_lines(a, b)
        assert a.judge_position_relation(b) == a.PositionRelation.non_intersect
        c = Line3D(Vector3D(-1.3, 0, 0), Vector3D(111, 0, 0))
        assert a.judge_position_relation(c) == a.PositionRelation.collinear

        a = Line3D(Vector3D(1, 0, 0))
        b = Line3D(Vector3D(0, 1, 0), Vector3D(0, 0, 4))
        assert a.angle(b) == math.pi / 2

        a = Line3D(Vector3D(1, 0, 0))
        assert a.get_random_point() in a

        elo = Line3D(point=Vector3D(1, 1, 0),
                     direction=Vector3D(1, 2, 0))
        assert elo.get_point('x', 6) == Vector3D(6, 11)

        # 测试结束

        # 测试x载入
        v = Vector3D([1, 2])
        assert 1 == v.x and 2 == v.y and 0 == v.z
        v = Vector3D([1, 2, 3])
        assert 1 == v.x and 2 == v.y and 3 == v.z
        # 测试结束

        # 测试除法
        v = Vector3D(2, 4, 5)
        r = v / 2.0
        assert r.z == 2.5
        # 测试结束

        # 测试点到直线最近点
        elo = Line3D(point=Vector3D(0, 0), direction=Vector3D(1, 1))
        m = Vector3D(2, 0)
        n = m.get_nearest_point_to_line(elo)
        assert n == Vector3D(1, 1)
        elo = Line3D(point=Vector3D(0, 0), direction=Vector3D(1, 1))
        m = Vector3D(1, 1)
        n = m.get_nearest_point_to_line(elo)
        assert n == Vector3D(1, 1)
        elo = Line3D(point=Vector3D(0, 0, 1), direction=0.3 * Vector3D(0, 3 / 2, 0.8660254))
        m = Vector3D(0, 2, 1)
        n = m.get_nearest_point_to_line(elo)
        assert n == Vector3D(0, 3 / 2, 1 + 0.8660254)
        # 测试结束

    def test2(self):
        elo=Line3D(point=Vector3D(0,0),direction=Vector3D(1,0))
        x=sp.symbols('x')
        y = sp.symbols('y')
        P=x**2
        Q=x+y
        t=elo.calc_line_integral_of_vector_function(m=Vector3D(0,0),
                                                        n=Vector3D(1,0),
                                                        P=P,
                                                        Q=Q)
        self.assertAlmostEqual(t,1/3,delta=1e-5)

        elo=Line3D(point=Vector3D(0,1),direction=Vector3D(2,1))
        x=sp.symbols('x')
        y = sp.symbols('y')
        P=x**2
        Q=x+y
        t=elo.calc_line_integral_of_vector_function(m=Vector3D(2,2),
                                                        n=Vector3D(4,3),
                                                        P=P,
                                                        Q=Q)
        self.assertAlmostEqual(t,24.1666666666667, delta=1e-5)

        elo = Line3D(point=Vector3D(0, 0), direction=Vector3D(1, 0))
        self.assertAlmostEqual((0,-1,0),elo.expression())
        elo = Line3D(point=Vector3D(0, 0), direction=Vector3D(0, 1))
        self.assertAlmostEqual((1, 0, 0), elo.expression())


    def test3(self):
        tran,trani=get_trans_func_polar(Vector3D(2, 1), 0)
        p1 = Vector3D(2 + 1.73205080756888, 1 + 1)
        Vector3D.tol_for_eq = 0.0001
        v1 = Vector3D(30.0 / 180.0 * pi, 2)
        v2 = tran(p1)
        self.assertTrue(v1 == v2)
        self.assertTrue(p1 == trani(tran(p1)))

    def test_vector_mirror(self):
        p0=Vector3D(0,0)
        elo=Line3D(Vector3D(0,1),Vector3D(0.5,0))
        goal=Vector3D(1,0)
        t=p0.mirror(elo)
        self.assertTrue(goal==t)

        p0=Vector3D(1,2)
        elo=Line3D(Vector3D(1,1),Vector3D(0,0))
        goal=Vector3D(2,1)
        t=p0.mirror(elo)
        self.assertTrue(goal==t)

    def test_rotate(self):
        p1=Vector3D(1,0)
        p2=p1.rotate(base_point=Vector3D(0,0),angle=pi/2)
        goal=Vector3D(0,1)
        self.assertTrue(goal==p2)
        p2=p1.rotate(base_point=Vector3D(0,0),angle=-pi/2)
        goal=Vector3D(0,-1)
        self.assertTrue(goal==p2)

        p1=Vector3D(2,0)
        p2=p1.rotate(base_point=Vector3D(1,0),angle=pi/2)
        goal=Vector3D(1,1)
        self.assertTrue(goal==p2)


    def test_ParametricEquationOfLine(self):
        elo=Line3D.make_line_by_2_points(Vector3D(1,0),Vector3D(1,1))
        p=ParametricEquationOfLine(elo=elo)
        for i in range(10):
            t=random.random()
            pt=p.get_point(t)
            self.assertAlmostEqual(t,p.calc_t(pt),delta=1e-9)
            self.assertAlmostEqual(t, p.calc_t(pt), delta=1e-9)

    def test_ParametricEquationOfLine2(self):

        elo = Line3D.make_line_by_2_points(Vector3D(0, 0), Vector3D(1, 1))
        x, y = symbols('x y')
        pl = ParametricEquationOfLine(elo=elo)
        jg = pl.line_integral_of_vector_function(P=x + y,
                                                 Q=x * y,
                                                 pt0=Vector3D(0, 0),
                                                 pt1=Vector3D(1, 1))
        self.assertAlmostEqual(4/3,jg,delta=0.00001)

if __name__ == '__main__':
    unittest.main()