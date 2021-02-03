from unittest import TestCase,main
from code2021.MyGeometric.angletool import *
from code2021.MyGeometric.arc import Arc
from vector3d import Vector3D


class TestArc(TestCase):
    def test1(self):
        arc=Arc(Vector3D(1,0),radius=1.1,angle1=0,da=AngleTool.toR(90))
        self.assertAlmostEqual(1.1*pi/2,arc.length,delta=0.001)


if __name__ == '__main__':
    main()