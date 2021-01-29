from unittest import TestCase,main

from vector3d import Vector3D

from .rect import  Rect


class TestRect(TestCase):

    def test1(self):
        rect=Rect(Vector3D(0,0),1,1)
        self.assertTrue(Vector3D(0,0) in rect)
        self.assertTrue(Vector3D(1, 1) in rect)
        self.assertFalse(Vector3D(0, 1.1) in rect)
        self.assertTrue(rect.__contains__(Vector3D(0,1.1),tol=0.11))

        rect1=Rect(Vector3D(1,1),1,1)
        a,b=rect.get_dist_from_rect(rect1)
        self.assertEqual([0,0],[a,b])

        rect1 = Rect(Vector3D(-1, 0), 1, 1)
        a, b = rect.get_dist_from_rect(rect1)
        self.assertEqual([0, 0], [a, b])

        rect1 = Rect(Vector3D(-1, 0), 2, 2)
        a, b = rect.get_dist_from_rect(rect1)
        self.assertEqual([0, 0], [a, b])

        rect1 = Rect(Vector3D(-1, 0), 0.5, 0.5)
        a, b = rect.get_dist_from_rect(rect1)
        self.assertEqual([0.5, 0], [a, b])

    def test2(self):
        rect = Rect(Vector3D(0, 0), 1, 1,3.14/6)
        self.assertFalse(Vector3D(1, 1) in rect)
        self.assertTrue(Vector3D(0.366, 1.3) in rect)

if __name__ == '__main__':
    main()
