from typing import List

from code2021.MyGeometric.map import MeshedMap
from code2021.MyGeometric.rect import Rect
from vector3d import Vector3D


class Algo1:
    def __init__(self,target:Rect,bk:List[Rect]):
        self.target=target
        self.bk=bk

        #建立map

        bigsize=max(target.width,target.height) #目标的大尺寸
        lst=[]
        for i in bk:
            lst.extend(i.corners)
        ld,ru=Vector3D.get_bound_corner(lst)#获取背景的范围
        #map的尺寸为背景范围+2倍目标尺寸
        maprect=Rect.make_by_two_corners(ld-Vector3D(bigsize*2,bigsize*2),ru+Vector3D(bigsize*2,bigsize*2))

        self.mm=MeshedMap(maprect.corners[0],maprect.corners[1])
        self.mm.mesh(1/8.0*bigsize)
    def show(self):
        self.mm.show()