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
        # plt.autoscale(enable=True, axis='both', tight=True)
        #  plt.show()

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

    def test_move(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        vec=Vector3D(0,1)
        pl1=pl.move(Vector3D(0,0),vec)
        self.assertTrue(pl.start_point+vec==pl1.start_point)
        self.assertTrue(pl.end_point + vec == pl1.end_point)
        self.assertAlmostEqual(pl.length,pl1.length,delta=0.0001)

    def test_rotate(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        _,ax=pl.draw_in_axes()
        pl1=pl.rotate(Vector3D(0,0),pi/2)
        _,ax=pl1.draw_in_axes(ax)
        self.assertTrue(pl1.end_point==Vector3D(-1,-1))
        # plt.autoscale(enable=True, axis='both', tight=True)
        # plt.show()

    def test_init(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        elo=LineSegment(Vector3D(-1, 1), Vector3D(0, 0))
        pl1=PolyLine([pl,elo])

    def test_offset(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        pl1 = pl.offset(1, 'r')
        self.assertTrue(Vector3D(0.000000,-1.000000)==pl1.start_point)
        self.assertTrue(Vector3D(-2.000000,1.000000) == pl1.end_point)

    def test_point_by_length_coord(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        t,beta=pl.point_by_length_coord(1.5)
        goal=Vector3D(1,0.5)
        self.assertTrue(goal==t)
        self.assertAlmostEqual(pi/2,beta,delta=0.0001)
        t,beta=pl.point_by_length_coord(2+pi/2)
        goal=Vector3D(0,2)
        self.assertTrue(goal==t)
        self.assertAlmostEqual(pi , beta, delta=0.0001)

    def test_trim(self):
        elo1 = LineSegment(Vector3D(0, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo1, elo2, a])
        pl1=pl.trim(Vector3D(0.5,0),pl.start_point)
        self.assertAlmostEqual(pl.length-0.5,pl1.length,delta=0.001)
        pl1=pl.trim(Vector3D(0.5,0),pl.end_point)
        self.assertAlmostEqual(0.5,pl1.length,delta=0.001)
if __name__ == '__main__':
    main()