import  math
import random
import copy
class Vector3D:
    def __init__(self,x=0.,y=0.,z=0.):
        self.x,self.y,self.z=x,y,z
    def __add__(self,other):
        assert isinstance(other,Vector3D)
        c=copy.deepcopy(self)
        c.x += other.x
        c.y += other.y
        c.z += other.z
        return c
    def __sub__(self,other):
        assert isinstance(other,Vector3D)
        c=copy.deepcopy(self)
        c.x -= other.x
        c.y -= other.y
        c.z -= other.z
        return c
    def __mul__(self, other):
        print(type(other))
        if isinstance(other,(float,int)):
            c = copy.deepcopy(self)
            c.x *= other
            c.y *= other
            c.z *= other
            return c
        elif isinstance(other,Vector3D):
            return self.x*other.x+self.y*other.y+self.z*other.z
        else:
            raise Exception("type error")
    @property
    def modulus(self):
        """模"""
        return (self.x**2+self.y**2+self.z**2)**0.5
    @modulus.setter
    def modulus(self,v):
        assert not (self.x == 0 and self.y == 0 and self.z == 0)  # 零向量不能设定模
        assert v >= 0  # 模不能为负
        t = self.modulus
        self.x *= v / t
        self.y *= v / t
        self.z *=v/t
    @staticmethod
    def cross_product(v1,v2):
        """向量叉乘"""
        assert isinstance(v1,Vector3D)
        assert isinstance(v2,Vector3D)
        return Vector3D(v1.y*v2.z-v1.z*v2.y,v1.z*v2.x-v1.x*v2.z,v1.x*v2.y-v1.y*v2.x)
    @staticmethod
    def angle(v1,v2):
        """返回两个向量的夹角 返回范围：0，pi"""
        assert isinstance(v1, Vector3D)
        assert isinstance(v2, Vector3D)
        t=v1*v2/(v1.modulus*v2.modulus)
        return math.acos(t)
