import math
import random
import copy
from typing import TypeVar, Generic
import numpy
from enum import Enum, unique
import nose.tools

T_Vector = TypeVar('T_Vector')
T_Plane = TypeVar('T_Plane')
T_Line = TypeVar('T_Line')


class Vector3D(Generic[T_Vector]):
    tol_for_eq = 1e-6  # 判断相等时的误差

    def __init__(self, x=0., y=0., z=0.):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other: T_Vector) -> T_Vector:
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x += other.x
        c.y += other.y
        c.z += other.z
        return c

    def __iadd__(self, other: T_Vector) -> T_Vector:
        assert isinstance(other, Vector3D)
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other: T_Vector) -> T_Vector:
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x -= other.x
        c.y -= other.y
        c.z -= other.z
        return c

    def __isub__(self, other: T_Vector) -> T_Vector:
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

    def __rmul__(self, other: float) -> T_Vector:
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
            return math.pi - Vector3D.angle(self.normal, other.normal)
        elif isinstance(other, Line3D):
            # 要求直线与平面的关系必须为斜交或者垂直
            assert self.judge_position_relation(other) in (self.PositionRelationForLine.skew, \
                                                           self.PositionRelationForLine.perpendicular)
            alpha = Vector3D.angle(self.normal, other.direction)
            if alpha < math.pi / 2:
                return math.pi / 2 - alpha
            else:
                return alpha - math.pi / 2
        else:
            raise Exception("type error")

    def projection(self, item: (T_Line, T_Vector)) -> T_Line:
        """
        直线elo在此平面内的投影所得的直线
        elo不能垂直于平面
        :param elo:
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
        return Line3D.make_line_by_2_points(pt1_pro, pt2_pro)


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
        self.direction, self.point = direction, point

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
                return False
            else:
                return True

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
            if Vector3D.is_parallel(tmp1, self.direction):  # 共线
                return self.PositionRelation.collinear
            return self.PositionRelation.intersect
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
        return Vector3D.angle(self.direction, other.direction)

    @staticmethod
    def make_line_by_2_points(point1: Vector3D, point2: Vector3D) -> T_Line:
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


if __name__ == '__main__':
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
    # 测试结束
