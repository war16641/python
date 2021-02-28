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
        self.assertAlmostEqual(pi/2,arc1.length,delta=0.0001)
        # _,ax=arc.draw_in_axes()
        # arc1.draw_in_axes(ax)
        # plt.autoscale(enable=True, axis='both', tight=True)
        # plt.show()

    def test_offset(self):
        arc = Arc(Vector3D(4313.55631273, -689.66607504), radius=782.54781885,
                  angle1=AngleTool.toR(3.554659), da=AngleTool.toR(141.118385))
        arc1=arc.offset(100,'r')
        arc2 = Arc(Vector3D(4313.55631273, -689.66607504), radius=882.54781885,
                  angle1=AngleTool.toR(3.554659), da=AngleTool.toR(141.118385))
        self.assertTrue(arc2==arc1)

        arc = Arc(Vector3D(4313.55631273, -689.66607504), radius=782.54781885,
                  angle1=AngleTool.toR(3.554659), da=AngleTool.toR(-141.118385))
        arc1=arc.offset(100,'r')
        arc2 = Arc(Vector3D(4313.55631273, -689.66607504), radius=682.54781885,
                  angle1=AngleTool.toR(3.554659), da=AngleTool.toR(-141.118385))
        self.assertTrue(arc2==arc1)

    def test_pt_change(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        arc.start_point=Vector3D(0,0)
        self.assertAlmostEqual(1,arc.radius,delta=0.001)
        self.assertTrue(Vector3D(0,0)==arc.start_point)
        self.assertTrue(Vector3D(0, 2) == arc.end_point)
        self.assertAlmostEqual(pi,arc.da,delta=0.0001)
        self.assertAlmostEqual(pi,arc.length,delta=0.001)
        self.assertTrue(Vector3D(0,0) in arc)

        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(-90))
        arc.start_point=Vector3D(0,2)
        self.assertAlmostEqual(1,arc.radius,delta=0.001)
        self.assertTrue(Vector3D(0,2)==arc.start_point)
        self.assertTrue(Vector3D(0, 0) == arc.end_point)
        self.assertAlmostEqual(-pi,arc.da,delta=0.0001)
        self.assertAlmostEqual(pi,arc.length,delta=0.001)
        self.assertTrue(Vector3D(0,0) in arc)

        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        arc.end_point=Vector3D(-1,1)
        self.assertAlmostEqual(1,arc.radius,delta=0.001)
        self.assertTrue(Vector3D(1,1)==arc.start_point)
        self.assertTrue(Vector3D(-1, 1) == arc.end_point)
        self.assertAlmostEqual(pi,arc.da,delta=0.0001)
        self.assertAlmostEqual(pi,arc.length,delta=0.001)
        self.assertTrue(Vector3D(-1,1) in arc)

        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(-90))
        arc.end_point=Vector3D(-1,1)
        self.assertAlmostEqual(1,arc.radius,delta=0.001)
        self.assertTrue(Vector3D(1,1)==arc.start_point)
        self.assertTrue(Vector3D(-1, 1) == arc.end_point)
        self.assertAlmostEqual(-pi,arc.da,delta=0.0001)
        self.assertAlmostEqual(pi,arc.length,delta=0.001)
        self.assertTrue(Vector3D(-1,1) in arc)

    def test_point_by_length_coord(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        g2=2**0.5
        goal=Vector3D(g2/2,1+g2/2)
        t,beta=arc.point_by_length_coord(pi/4)
        self.assertTrue(goal==t)
        self.assertAlmostEqual(pi*3/4,beta,delta=0.0001)

        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(-90))
        g2=2**0.5
        goal=Vector3D(g2/2,1-g2/2)
        t,beta=arc.point_by_length_coord(pi/4)
        self.assertTrue(goal==t)
        self.assertAlmostEqual(AngleTool.format1(pi * -3 / 4), AngleTool.format1(beta), delta=0.0001)

    def test_trim(self):
        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(90))
        g2 = 2 ** 0.5
        pt=Vector3D(g2 / 2, 1 + g2 / 2)
        arc1=arc.trim(pt,arc.start_point)
        goal=Arc(Vector3D(0, 1), radius=1., angle1=AngleTool.toR(45), da=AngleTool.toR(45))
        self.assertTrue(goal==arc1)
        pt=Vector3D(g2 / 2, 1 + g2 / 2)
        arc1=arc.trim(pt,arc.end_point)
        goal=Arc(Vector3D(0, 1), radius=1., angle1=AngleTool.toR(0), da=AngleTool.toR(45))
        self.assertTrue(goal==arc1)

        arc = Arc(Vector3D(0, 1), radius=1., angle1=0, da=AngleTool.toR(-90))
        g2 = 2 ** 0.5
        pt=Vector3D(g2 / 2, 1- g2 / 2)
        arc1=arc.trim(pt,arc.start_point)
        goal=Arc(Vector3D(0, 1), radius=1., angle1=AngleTool.toR(-45), da=AngleTool.toR(-45))
        self.assertTrue(goal==arc1)
        pt=Vector3D(g2 / 2, 1 - g2 / 2)
        arc1=arc.trim(pt,arc.end_point)
        goal=Arc(Vector3D(0, 1), radius=1., angle1=AngleTool.toR(0), da=AngleTool.toR(-45))
        self.assertTrue(goal==arc1)
if __name__ == '__main__':
    main()