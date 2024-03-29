from math import pi
from unittest import TestCase,main

from code2021.MyGeometric.angletool import AngleTool
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.entitytool import Entitytool
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from code2021.MyGeometric.ray import Ray
from vector3d import Vector3D
class TestEntitytool(TestCase):
    def test__intersection_point_line_line(self):
        a=LineSegment(Vector3D(-1,0),Vector3D(1,0))
        b=LineSegment(Vector3D(0,-1),Vector3D(0,1))
        t=Vector3D(0,0)
        self.assertTrue(t==Entitytool.intersection_point(a,b))

        b = LineSegment(Vector3D(0, -1), Vector3D(0, -0.5))
        self.assertTrue(None==Entitytool.intersection_point(a,b))


    def test__intersection_point_line_arc(self):
        g=1+2.414213562
        elo=LineSegment(Vector3D(g,0),Vector3D(0,g))
        arc=Arc(Vector3D(1,1),radius=1,angle1=AngleTool.toR(-90),da=AngleTool.toR(270))
        goal=Vector3D(1.707123023470,1.707123023470)
        Vector3D.tol_for_eq=0.01
        t=Entitytool.intersection_point(elo,arc)
        self.assertTrue(goal==t)

        arc=Arc(Vector3D(1,1),radius=1,angle1=AngleTool.toR(-90),da=AngleTool.toR(30))
        t = Entitytool.intersection_point(elo, arc)
        self.assertTrue(t ==None)

        arc = Arc(Vector3D(1,1), radius=1, angle1=AngleTool.toR(-90), da=AngleTool.toR(90))
        self.assertTrue(Entitytool.intersection_point(elo, arc) == None)
        arc = Arc(Vector3D(1,1), radius=1, angle1=AngleTool.toR(-90), da=AngleTool.toR(180))
        self.assertTrue(Entitytool.intersection_point(elo, arc) == goal)
        Vector3D.tol_for_eq = 1e-5

    def test__intersection_point_line_polyline(self):
        elo1=LineSegment(Vector3D(0,0),Vector3D(1,0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a=Arc(Vector3D(0,1),1,0,pi)
        pl=PolyLine([elo1,elo2,a])
        elo=LineSegment(Vector3D(0,0.5),Vector3D(10,0.5))
        goal=Vector3D(1,0.5)
        self.assertTrue(goal==Entitytool.intersection_point(pl,elo))

        elo = LineSegment(Vector3D(0, -0.5), Vector3D(10, -0.5))
        self.assertTrue(None == Entitytool.intersection_point(pl, elo))

        elo1=LineSegment(Vector3D(0.1,0),Vector3D(1,0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a=Arc(Vector3D(0,1),1,0,pi)
        pl=PolyLine([elo1,elo2,a])
        elo=LineSegment(Vector3D(0,0),Vector3D(0,10))
        goal=Vector3D(0,2)
        self.assertTrue(goal==Entitytool.intersection_point(pl,elo))

    def test__intersection_point_polyline_polyline(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        elo1 = LineSegment(Vector3D(0, -0.10), Vector3D(1, -0.1))
        a = Arc(Vector3D(0.5, -0.1), 0.5, 0, pi / 2)
        pl2 = PolyLine([elo1, a])
        t=Entitytool.intersection_point(pl,pl2)
        self.assertTrue(t==Vector3D(0.989898,0.000000))


    def test__intersection_point_ray_line3d(self):
        ray = Ray(base_pt=Vector3D(0, 0), direct=Vector3D(1, 0))
        elo=LineSegment(Vector3D(0.5,-1),Vector3D(0.5,1))
        goal=Vector3D(0.5,0)
        jg=Entitytool.intersection_point(ray,elo)
        self.assertTrue(jg==goal)

        ray = Ray(base_pt=Vector3D(0, 0), direct=Vector3D(0, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        goal=Vector3D(0,2)
        jg=Entitytool.intersection_point(ray,a)
        self.assertTrue(goal==jg)

        ray = Ray(base_pt=Vector3D(0, 0), direct=Vector3D(0, -1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        goal = Vector3D(0, 2)
        jg = Entitytool.intersection_point(ray, a)
        self.assertTrue(jg is None)

        ray = Ray(base_pt=Vector3D(-10, 0), direct=Vector3D(1,0))
        a = Arc(Vector3D(0, 0), 1, 0, pi+1)
        goal = Vector3D(1, 0)
        goal1 = Vector3D(-1,0)
        jg = Entitytool.intersection_point(ray, a)
        self.assertTrue(goal in jg and goal1 in jg)
if __name__ == '__main__':
    main()