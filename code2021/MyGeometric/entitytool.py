"""
存放一些解决几何元素关系的函数
因为可能会涉及到不同的图素 为了不破坏类之间的耦合性 单独开一个文件
"""
from code2021.MyGeometric.arc import Arc, CircleLineIntersecionProblem
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from vector3d import Vector3D


# class NoIntersectionPoint(Exception):#无交点时抛出这个错误
#     pass

class Entitytool:

    @staticmethod
    def _intersection_point_line_line(a:LineSegment,b:LineSegment)->Vector3D:
        """
        返回交点 没有就返回none
        @param a:
        @param b:
        @return:
        """
        t=a.line.get_intersect_point(b.line)
        if t is None:
            return None
        if t in a and t in b:
            return t
        else:
            return None
        pass

    @staticmethod
    def _intersection_point_line_arc(a,b)->Vector3D:
        """
        直线与圆弧
        返回none
        或者vector
        或者[vector,vector]
        @param a:
        @param b:
        @return:
        """
        if isinstance(a,LineSegment):
            elo=a
            arc=b
        else:
            elo = b
            arc = a
        p = CircleLineIntersecionProblem()
        p.a = arc.center.x
        p.b=arc.center.y
        p.r = arc.radius
        #将line转换为直线一般表达式
        if abs(elo.line.direction.x)<1e-9:
            p.A=1
            p.B=0
            p.C=-elo.line.point.x
        else:
            k=elo.line.direction.y/elo.line.direction.x
            b=elo.line.point.y-k*elo.line.point.x
            p.A=k
            p.B=-1
            p.C=b
        ia=p.solve()
        if ia is None:
            return None
        else:
            ia=[Vector3D(x[0],x[1]) for x in ia]
        fa=[]
        for i in ia:
            if i in elo and i in arc:
                fa.append(i)
        if len(fa)==1:
            return fa[0]
        elif len(fa)==2:
            return fa
        else:
            return None

    @staticmethod
    def _intersection_point_line_polyline(a,b):
        if isinstance(a,LineSegment):
            elo=a
            pl=b
        else:
            elo=b
            pl=a
        for seg in pl:
            t=Entitytool.intersection_point(elo,seg)
            if isinstance(t,Vector3D):
                return t
            elif isinstance(t,list) and isinstance(t[0],Vector3D):#如果遇到返回两个交点 那就返回第一个
                return t[0]
        return None

    @staticmethod
    def _intersection_point_polyline_polyline(a,b):
        for seg1 in a:
            t=Entitytool.intersection_point(seg1,b)
            if t is not None:
                return t
        return None

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
        if isinstance(a, LineSegment) and isinstance(b, Arc) or \
                isinstance(b, LineSegment) and isinstance(a, Arc):
            return Entitytool._intersection_point_line_arc(a,b)
        if isinstance(a, LineSegment) and isinstance(b, PolyLine) or \
                isinstance(b, LineSegment) and isinstance(a, PolyLine):
            return Entitytool._intersection_point_line_polyline(a,b)
        if isinstance(a,PolyLine) and isinstance(b,PolyLine):
            return Entitytool._intersection_point_polyline_polyline(a,b)
        else:
            raise Exception("未知类型")

