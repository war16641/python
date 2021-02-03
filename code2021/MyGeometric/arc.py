from math import pi

from vector3d import Vector3D


class Arc:

    def __init__(self,center:Vector3D,radius,angle1:float,da):
        assert isinstance(center,Vector3D),"类型错误"
        assert 0<=da<=2*pi,"da必须在0到2pi内"
        self._center=center #type:Vector3D
        self._angle1=angle1
        self._da=da
        self._angle2=self._angle1+self._da
        self._radius=radius

    @property
    def radius(self):
        return self._radius

    @property
    def center(self):
        return self._center

    @property
    def da(self):
        return self._da

    @property
    def length(self):
        return self._radius*self._da
