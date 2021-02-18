from math import pi
from unittest import TestCase, main
import matplotlib.pyplot as plt
from code2021.MyGeometric.angletool import AngleTool
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from vector3d import Vector3D


class TestPolyLine(TestCase):
    def test_1(self):
        elo1=LineSegment(Vector3D(0,0),Vector3D(1,0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a=Arc(Vector3D(0,1),1,0,pi)
        pl=PolyLine([elo1,elo2,a])
        # _,ax=pl.draw_in_axes()
        # plt.show()

    def test_2(self):
        elo1=LineSegment(Vector3D(0,0),Vector3D(1,0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a=Arc(Vector3D(0,1),1,0,pi)
        pl=PolyLine([elo1,elo2,a])
        self.assertTrue(Vector3D(0,0) in pl)
        self.assertTrue(Vector3D(1, 0) in pl)
        self.assertTrue(Vector3D(1, 1) in pl)
        self.assertTrue(Vector3D(0, 2) in pl)
        self.assertTrue(Vector3D(-1, 1) in pl)
        self.assertFalse(Vector3D(0, 2.1) in pl)
        self.assertFalse(Vector3D(1, 1.1) in pl)
        self.assertAlmostEqual(1+1+pi,pl.length,delta=0.0004)

    def test_calc_nearest_point(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        # _, ax = pl.draw_in_axes()
        # plt.show()
        target=Vector3D(0,0)
        goal,le,on=pl.calc_nearest_point(target)
        self.assertTrue(goal==Vector3D(0,0))
        self.assertAlmostEqual(0,le,delta=0.0001)
        self.assertTrue(on)

        target=Vector3D(0.5,0)
        goal,le,on=pl.calc_nearest_point(target)
        self.assertTrue(goal==Vector3D(0.5,0))
        self.assertAlmostEqual(0.5,le,delta=0.0001)
        self.assertTrue(on)

        target=Vector3D(0.5,0.1)
        goal,le,on=pl.calc_nearest_point(target)
        self.assertTrue(goal==Vector3D(0.5,0))
        self.assertAlmostEqual(0.5,le,delta=0.0001)
        self.assertTrue(on==False)

        target=Vector3D(0.0,2.1)
        goal,le,on=pl.calc_nearest_point(target)
        self.assertTrue(goal==Vector3D(0,2))
        self.assertAlmostEqual(1+1+1*pi/2,le,delta=0.0001)
        self.assertTrue(on==False)

if __name__ == '__main__':
    main()