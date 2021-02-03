from unittest import TestCase,main

from code2021.MyGeometric.entitytool import Entitytool
from code2021.MyGeometric.linesegment import LineSegment
from vector3d import Vector3D
class TestEntitytool(TestCase):
    def test__intersection_point_line_line(self):
        a=LineSegment(Vector3D(-1,0),Vector3D(1,0))
        b=LineSegment(Vector3D(0,-1),Vector3D(0,1))
        t=Vector3D(0,0)
        self.assertTrue(t==Entitytool.intersection_point(a,b))

        b = LineSegment(Vector3D(0, -1), Vector3D(0, -0.5))
        self.assertTrue(None==Entitytool.intersection_point(a,b))

if __name__ == '__main__':
    main()