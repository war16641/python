from math import pi
from unittest import TestCase, main

from code2021.MyGeometric.rect import Rect
from vector3d import Vector3D

from .map import  MeshedMap

class TestMeshedMap(TestCase):
    def test1(self):
        mm = MeshedMap(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = Rect.make_by_two_corners(Vector3D(18.7, 18.7), Vector3D(41.1, 41.1))
        jg = mm.get_cells_in_rect_fast(r)
        for i in jg:
            i.facecolor = 'r'
        # ax,_ = mm.show()
        # r.draw_in_axes(ax)
        # plt.show()
        self.assertEqual(12 * 12, len(jg))

    def test_2(self):
        mm = MeshedMap(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = Rect(xy=Vector3D(10,20),width=20,height=10,rotation=pi/6)
        jg=mm.get_cells_in_rect_fast(r)
        for i in jg:
            i.facecolor = 'r'
        # ax,fig = mm.show()
        # r.draw_in_axes(ax)
        # print(len(jg))
        # plt.show()
        a=1
        self.assertEqual(99,len(jg))

    def test_3(self):
        mm = MeshedMap(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = Rect(xy=Vector3D(10,20),width=20,height=10,rotation=pi/6)
        jg=mm.get_cells_in_rect_fast(r,precise=True)
        for i in jg:
            i.facecolor = 'r'
        # ax,fig = mm.show()
        # r.draw_in_axes(ax)
        # plt.show()
        # print(len(jg))
        self.assertEqual(49,len(jg))
        jg1 = mm.get_cells_in_rect_fast(r, precise=True)
        self.assertEqual(jg,jg1)#看是否调用之前的结果
if __name__ == '__main__':
    main()