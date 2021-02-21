from unittest import TestCase,main
from code2021.MyGeometric.angletool import *
from code2021.MyGeometric.arc import Arc, CircleLineIntersecionProblem
from vector3d import Vector3D, Line3D
import matplotlib.pyplot as plt

class TestArc(TestCase):
    def test1(self):
        arc=Arc(Vector3D(1,0),radius=1.1,angle1=0,da=AngleTool.toR(90))
        self.assertAlmostEqual(1.1*pi/2,arc.length,delta=0.001)

        arc=Arc(Vector3D(0,1),radius=1.,angle1=0,da=AngleTool.toR(180))
        self.assertEqual(Vector3D(1,1),arc.start_point)
        self.assertEqual(Vector3D(-1,1),arc.end_point)
        self.assertTrue(Vector3D(0,2) in arc)

    def test2(self):
        arc=Arc(Vector3D(0,1),radius=1.,angle1=0,da=AngleTool.toR(-180))
        self.assertEqual(Vector3D(1,1),arc.start_point)
        self.assertEqual(Vector3D(-1,1),arc.end_point)
        self.assertTrue(Vector3D(0,0) in arc)

    def test_CircleLineIntersecionProblem(self):
        p = CircleLineIntersecionProblem()
        p.a = p.b = 1
        p.r = 1
        g3 = 3 ** 0.5
        p.A = p.B = 1
        p.C = -(1 + 2.414213562)
        r=p.solve()
        self.assertEqual(1,len(r))
        self.assertAlmostEqual(1.707123023470,r[0][0])


        p.C = -(1 + 1.414213562)
        r = p.solve()
        self.assertEqual(2,len(r))

        p.C = -(1 + 3.414213562)
        r = p.solve()
        self.assertEqual(None, r)

    def test_calc_nearest_point(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        arc.draw_in_axes()
        # plt.autoscale(enable=True, axis='both', tight=True)
        # plt.show()
        ta=Vector3D(1,1)
        goal,le,on=arc.calc_nearest_point(ta)
        self.assertTrue(ta==goal)
        self.assertAlmostEqual(0,le,delta=1e-5)
        self.assertTrue(on)

        ta=Vector3D(1.1,1)
        goal,le,on=arc.calc_nearest_point(ta)
        self.assertTrue(Vector3D(1,1)==goal)
        self.assertAlmostEqual(0,le,delta=1e-5)
        self.assertFalse(on)

        ta=Vector3D(0,2.1)
        goal,le,on=arc.calc_nearest_point(ta)
        self.assertTrue(Vector3D(0,2)==goal)
        self.assertAlmostEqual(pi*0.5,le,delta=1e-5)
        self.assertFalse(on)

    def test_make_by_3_points(self):
        arc=Arc.make_by_3_points(Vector3D(0,0),Vector3D(0,1),Vector3D(-0.1,0))
        self.assertTrue(Vector3D(0,1)==arc.start_point)
        self.assertTrue(Vector3D(-1,0) == arc.end_point)
        self.assertAlmostEqual(pi/2,arc.length,delta=0.0001)

        arc = Arc.make_by_3_points(Vector3D(0, 0), Vector3D(0, 1), Vector3D(-0.1, 0),direction=-1.0)
        self.assertTrue(Vector3D(0, 1) == arc.start_point)
        self.assertTrue(Vector3D(-1, 0) == arc.end_point)
        self.assertAlmostEqual(3*pi / 2, arc.length, delta=0.0001)

        arc=Arc.make_by_3_points(Vector3D(0,0),Vector3D(-1,0),Vector3D(0,0.1))
        self.assertTrue(Vector3D(-1,0)==arc.start_point)
        self.assertTrue(Vector3D(0,1) == arc.end_point)
        self.assertAlmostEqual(3*pi/2,arc.length,delta=0.0001)

        arc=Arc.make_by_3_points(Vector3D(0,0),Vector3D(-1,0),Vector3D(0,0.1),direction=-1.0)
        self.assertTrue(Vector3D(-1,0)==arc.start_point)
        self.assertTrue(Vector3D(0,1) == arc.end_point)
        self.assertAlmostEqual(1*pi/2,arc.length,delta=0.0001)

    def test_move(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        vec=Vector3D(1,0)
        arc1=arc.move(Vector3D(0,0),vec)
        self.assertTrue(arc.start_point+vec==arc1.start_point)
        self.assertTrue(arc.end_point+vec==arc1.end_point)

    def test_rotate(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        arc1=arc.rotate(Vector3D(0,1),pi/2)
        goal = Arc(Vector3D(0, 1), radius=1., angle1=pi/2, da=AngleTool.toR(90))
        self.assertTrue(goal==arc1)

    def test_mirror(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        arc1=arc.mirror(Line3D.make_line_by_2_points(Vector3D(0,0),Vector3D(1,0)))
        self.assertTrue(Vector3D(1,-1)==arc1.start_point)
        self.assertTrue(Vector3D(0,-2)==arc1.end_point)
        # _,ax=arc.draw_in_axes()
        # arc1.draw_in_axes(ax)
        # plt.autoscale(enable=True, axis='both', tight=True)
        # plt.show()
if __name__ == '__main__':
    main()