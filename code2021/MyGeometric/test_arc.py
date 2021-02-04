from unittest import TestCase,main
from code2021.MyGeometric.angletool import *
from code2021.MyGeometric.arc import Arc
from vector3d import Vector3D


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

if __name__ == '__main__':
    main()