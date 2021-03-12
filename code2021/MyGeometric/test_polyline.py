from math import pi
from unittest import TestCase, main
import matplotlib.pyplot as plt
from code2021.MyGeometric.angletool import AngleTool
from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine, PointRegionRelation
from code2021.mydataexchange import make_data_from_paragraph
from sympy import symbols
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

    def test_line_integral_of_vector_function(self):
        pl = PolyLine.make1(
            [Vector3D(0, 0), Vector3D(1, 0), Vector3D(1, 1), Vector3D(0.5, 2), Vector3D(0, 1), Vector3D(0, 0)])
        # x, y = symbols('x y')
        # jg=pl.line_integral_of_vector_function(P=0, Q=x, pt0=pl.start_point, pt1=pl.end_point, i1=3)
        # self.assertAlmostEqual(1.5,jg,delta=0.00001)
        self.assertAlmostEqual(1.5, pl.get_area(), delta=0.00001)
        pl=pl.rotate(base_point=Vector3D(12.314,123.1),angle=1.82637)
        # jg = pl.line_integral_of_vector_function(P=0, Q=x, pt0=pl.start_point, pt1=pl.end_point, i1=3)
        # self.assertAlmostEqual(1.5, jg, delta=0.00001)
        self.assertAlmostEqual(1.5, pl.get_area(), delta=0.00001)

        elo0=LineSegment(Vector3D(-1, 1), Vector3D(-1, 0))
        elo1 = LineSegment(Vector3D(-1, 0), Vector3D(1, 0))
        elo2 = LineSegment(Vector3D(1, 0), Vector3D(1, 1))
        a = Arc(Vector3D(0, 1), 1, 0, pi)
        pl = PolyLine([elo0,elo1, elo2, a])
        # x, y = symbols('x y')
        # jg = pl.line_integral_of_vector_function(P=0, Q=x, pt0=pl.start_point, pt1=pl.end_point, i1=3)
        jg=pl.get_area()
        self.assertAlmostEqual(0.5*pi+2,jg,delta=0.0001)
        pl=pl.reverse()
        jg = pl.get_area()
        self.assertAlmostEqual(-0.5 * pi - 2, jg, delta=0.0001)


    def test_in_closed_area(self):
        paragraph = """

        pl polyline 10
        _ lineseg 17265.67576962,-2545.72547728,0.00000000,17307.53902349,-2514.31389450,0.00000000
        _ lineseg 17307.53902349,-2514.31389450,0.00000000,17301.16519211,-2562.49646488,0.00000000
        _ lineseg 17301.16519211,-2562.49646488,0.00000000,17334.14275302,-2604.03316163,0.00000000
        _ lineseg 17334.14275302,-2604.03316163,0.00000000,17297.00832927,-2605.69463450,0.00000000
        _ lineseg 17297.00832927,-2605.69463450,0.00000000,17278.44114415,-2638.37017831,0.00000000
        _ lineseg 17278.44114415,-2638.37017831,0.00000000,17236.31852781,-2631.72430469,0.00000000
        _ lineseg 17236.31852781,-2631.72430469,0.00000000,17230.22182418,-2603.75624949,0.00000000
        _ lineseg 17230.22182418,-2603.75624949,0.00000000,17252.94587214,-2586.58775006,0.00000000
        _ lineseg 17252.94587214,-2586.58775006,0.00000000,17223.29373729,-2554.18911839,0.00000000
        _ lineseg 17223.29373729,-2554.18911839,0.00000000,17265.67576962,-2545.72547728,0.00000000
        """
        d = make_data_from_paragraph(paragraph, ignore_lines=0)
        pl = d['pl']  # type:PolyLine

        pt=Vector3D(17265.67576962,-2545.72547728)
        self.assertTrue(PointRegionRelation.on_border==pl.in_closed_area(pt))
        pt = Vector3D(17259.3277,-2530.6722 )
        self.assertTrue(PointRegionRelation.out == pl.in_closed_area(pt))
        pt = Vector3D(17292.0785 , -2542.2558)
        self.assertTrue(PointRegionRelation.inside == pl.in_closed_area(pt))
        pt = Vector3D(17255.4423  , -2552.3508 )
        self.assertTrue(PointRegionRelation.inside == pl.in_closed_area(pt))
        pt = Vector3D(17253.3554 , -2586.6292 )
        self.assertTrue(PointRegionRelation.inside == pl.in_closed_area(pt))
        pt = Vector3D(17252.7412   , -2586.6081)
        self.assertTrue(PointRegionRelation.out == pl.in_closed_area(pt))

if __name__ == '__main__':
    main()