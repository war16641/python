"""
存放一些解决几何元素关系的函数
因为可能会涉及到不同的图素 为了不破坏类之间的耦合性 单独开一个文件
"""
from code2021.MyGeometric.arc import Arc, CircleLineIntersecionProblem
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
    def _intersection_point_line_arc(a,b)->Vector3D:
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
        else:
            raise Exception("未知类型")