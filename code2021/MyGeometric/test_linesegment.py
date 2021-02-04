from unittest import TestCase,main
from math import pi, sin, cos
from code2021.MyGeometric.linesegment import LineSegment
from vector3d import Vector3D


class TestLineSegment(TestCase):
    def test_1(self):
        elo=LineSegment(Vector3D(0,0),Vector3D(10,0))
        self.assertEqual(10.0,elo.length)

        elo=LineSegment()
        elo.p1=Vector3D(0,0)
        elo.p2=Vector3D(10,0)
        self.assertEqual(10.0, elo.length)

        g3=3**0.5
        elo = LineSegment(Vector3D(0, 0), Vector3D(g3, 1))
        self.assertAlmostEqual(30/180.0*pi,elo.dangle,delta=1e-5)

    def test_2(self):
        elo = LineSegment(Vector3D(0, 0), Vector3D(10, 0))
        self.assertEqual(False, Vector3D(-1, 0) in elo)
        self.assertEqual(True,Vector3D(0,0) in elo)
        self.assertEqual(True, Vector3D(5, 0) in elo)
        self.assertEqual(True, Vector3D(10, 0) in elo)
        self.assertEqual(False, Vector3D(10.01, 0) in elo)
        self.assertEqual(True, elo.__contains__(Vector3D(10.01, 0),tol=0.1))

        g3 = 3 ** 0.5
        elo = LineSegment(Vector3D(0, 0), Vector3D(g3, 1))
        self.assertEqual(True, Vector3D(g3/2, 0.5) in elo)

    def test_3(self):
        g3 = 3 ** 0.5
        elo = LineSegment(Vector3D(0, 0), Vector3D(g3, 1))
        self.assertEqual(True, Vector3D(g3/2, 0.5) in elo)
        goal=Vector3D(g3/2,0.5)
        d30=30/180.0*pi
        te=Vector3D(g3/2-sin(d30),0.5+cos(d30))
        r1,r2,r3=elo.calc_nearest_point(te)
        self.assertEqual(goal,r1)
        self.assertAlmostEqual(1,r2,delta=1e-5)
        self.assertFalse(r3)

if __name__ == '__main__':
        main()