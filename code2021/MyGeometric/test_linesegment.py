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

    def test_move(self):
        elo = LineSegment(Vector3D(0, 0), Vector3D(10, 0))
        elo1=elo.move(Vector3D(0,0),Vector3D(0,1))
        goal=LineSegment(Vector3D(0,1),Vector3D(10,1))
        self.assertTrue(goal==elo1)

    def test_rotate(self):
        elo = LineSegment(Vector3D(1, 0), Vector3D(10, 0))
        elo1=elo.rotate(Vector3D(0,0),pi/2)
        goal=LineSegment(Vector3D(0, 1), Vector3D(0, 10))
        self.assertTrue(goal==elo1)

    def test_offset(self):
        elo=LineSegment(Vector3D(1664.60224689 , 681.10226583 ),Vector3D(3029.44978319,1183.63587211 ))
        elo1=elo.offset(10,'L')
        elog=LineSegment(Vector3D(1661.14703955 , 690.48637699 ),Vector3D(3025.99457585  , 1193.01998327))
        self.assertTrue(elog==elo1)
        elo1=elo.offset(10,'r')
        elog=LineSegment(Vector3D(1668.05745422    ,671.71815467 ),Vector3D( 3032.90499053 ,1174.25176095))
        self.assertTrue(elog==elo1)

        elo=LineSegment(Vector3D(1794.06164258  , 274.18655991 ),Vector3D(2357.52943508 ,-272.51042640 ))
        elo1=elo.offset(20,'L')
        elog=LineSegment(Vector3D( 1807.98854970 ,288.54069722    ),Vector3D(2371.45634220 , -258.15628909))
        self.assertTrue(elog==elo1)
        elo1=elo.offset(20,'r')
        elog=LineSegment(Vector3D( 1780.13473546 , 259.83242259  ),Vector3D( 2343.60252796 ,-286.86456372 ))
        self.assertTrue(elog==elo1)

    def test_point_by_length_coord(self):
        g3=3**0.5
        elo=LineSegment(Vector3D(0,0),Vector3D(g3,1))
        goal=Vector3D(g3/2,0.5)
        t,_=elo.point_by_length_coord(1)
        self.assertTrue(t==goal)
    def test_trim(self):
        g3 = 3 ** 0.5
        elo = LineSegment(Vector3D(0, 0), Vector3D(g3, 1))
        elo1=elo.trim(Vector3D(g3/2,1/2),elo.start_point)
        goal=LineSegment(Vector3D(g3/2,1/2), Vector3D(g3, 1))
        self.assertTrue(elo1==goal)
        elo1=elo.trim(Vector3D(g3/2,1/2),elo.end_point)
        goal=LineSegment(Vector3D(0, 0),Vector3D(g3/2,1/2))
        self.assertTrue(elo1==goal)
if __name__ == '__main__':
        main()