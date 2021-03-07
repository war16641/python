from unittest import TestCase,main

from code2021.MyGeometric.ray import Ray
from vector3d import Vector3D, Line3D, get_trans_func, ParametricEquationOfLine

class TestRay(TestCase):
    def test_1(self):
        ray=Ray(base_pt=Vector3D(0,0),direct=Vector3D(1,0))
        pt=Vector3D(0,0)
        self.assertTrue(pt in ray)
        pt = Vector3D(2, 0)
        self.assertTrue(pt in ray)
        pt = Vector3D(-0.01, 0)
        self.assertTrue(pt not in ray)

        ray=Ray(base_pt=Vector3D(0,0),direct=Vector3D(-1,0))
        pt=Vector3D(0,0)
        self.assertTrue(pt in ray)
        pt = Vector3D(2, 0)
        self.assertTrue(pt not in ray)
        pt = Vector3D(-0.01, 0)
        self.assertTrue(pt  in ray)


if __name__ == '__main__':
    main()
