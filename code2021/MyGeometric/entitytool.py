"""
存放一些解决几何元素关系的函数
因为可能会涉及到不同的图素 为了不破坏类之间的耦合性 单独开一个文件
"""
from code2021.MyGeometric.linesegment import LineSegment
from vector3d import Vector3D


# class NoIntersectionPoint(Exception):#无交点时抛出这个错误
#     pass

class Entitytool:

    @staticmethod
    def _intersection_point_line_line(a:LineSegment,b:LineSegment)->Vector3D:
        t=a.line.get_intersect_point(b.line)
        if t is None:
            return None
        if t in a and t in b:
            return t
        else:
            return None
        pass

    @staticmethod
    def intersection_point(a,b)->Vector3D:
        """
        求两个图素交点
        没有交点时返回None
        @param a:
        @param b:
        @return:
        """
        if isinstance(a,LineSegment) and isinstance(b,LineSegment):
            return Entitytool._intersection_point_line_line(a,b)
        else:
            raise Exception("未知类型")