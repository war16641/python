import math
import random
import copy
from typing import TypeVar, Generic

T = TypeVar('T')


class Vector3D(Generic[T]):
    tol_for_eq=1e-6 # 判断相等时的误差
    def __init__(self, x=0., y=0., z=0.):
        self.x, self.y, self.z = x, y, z

    def __add__(self, other: T) -> T:
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x += other.x
        c.y += other.y
        c.z += other.z
        return c

    def __iadd__(self, other:T)->T:
        assert isinstance(other,Vector3D)
        self.x+=other.x
        self.y += other.y
        self.z += other.z
        return self

    def __sub__(self, other: T) -> T:
        assert isinstance(other, Vector3D)
        c = copy.deepcopy(self)
        c.x -= other.x
        c.y -= other.y
        c.z -= other.z
        return c

    def __isub__(self, other:T)->T:
        assert isinstance(other, Vector3D)
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __mul__(self, other:T) -> (float,T):
        if isinstance(other, (float, int)):
            c = copy.deepcopy(self)
            c.x *= other
            c.y *= other
            c.z *= other
            return c
        elif isinstance(other, Vector3D):
            return self.x * other.x + self.y * other.y + self.z * other.z
        else:
            raise Exception("type error")

    def __eq__(self, other:(T,int))->bool:
        if isinstance(other,Vector3D):
            c = self - other
            if c.modulus < self.tol_for_eq:
                return True
            else:
                return False
        elif isinstance(other,int):
            assert other==0 # 当和数比较时，只能和0比较
            if self.modulus<=self.tol_for_eq:
                return True
            else:
                return False
        else:
            raise Exception("type error")


    def __str__(self)->str:
        return "%f,%f,%f" % (self.x, self.y, self.z)



    @property
    def modulus(self)->float:
        """模"""
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5

    @modulus.setter
    def modulus(self, v: float)->None:
        assert not (self.x == 0 and self.y == 0 and self.z == 0)  # 零向量不能设定模
        assert v >= 0  # 模不能为负
        t = self.modulus
        self.x *= v / t
        self.y *= v / t
        self.z *= v / t

    @staticmethod
    def cross_product(v1, v2) -> T:
        """向量叉乘"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        return Vector3D(v1.y * v2.z - v1.z * v2.y, v1.z * v2.x - v1.x * v2.z, v1.x * v2.y - v1.y * v2.x)

    @staticmethod
    def angle(v1: T, v2: T)->float:
        """返回两个向量的夹角 返回范围：0，pi"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        t = v1 * v2 / (v1.modulus * v2.modulus)
        return math.acos(t)


if __name__ == '__main__':
    a = Vector3D(1, 1, 1)
    b=Vector3D(2, 2, 2)
    c=Vector3D(1, 1, 1)
    assert a*b==6
    assert a!=b
    assert a==c
    a+=c
    assert a==b

    a=Vector3D(0,0,0)
    b=Vector3D(1e-7,0,-1e-8)
    assert a==0
    assert b==0
