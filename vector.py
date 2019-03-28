import  math
import random
import copy
class Vector:
    """向量类"""

    relative_tol=0.0001 # 向量相等时的相对误差最大值
    def __init__(self,x=0,y=0):
        self.x,self.y=x,y

    def __str__(self):
        return "%f,%f" %(self.x,self.y)

    def __eq__(self, other):
        assert isinstance(other,Vector)
        maxv=max(abs(self.x),abs(self.y),abs(other.x),abs(other.y))
        if maxv==0:
            return True

        if (self.x-other.x)/maxv<self.relative_tol and (self.y-other.y)/maxv<self.relative_tol:
            return True
        else:
            return  False

    def __mul__(self, other):
        c=copy.deepcopy(self)

        if isinstance(other,(float,int)):
            c.x*=other
            c.y*=other
            return c # 向量乘以数 返回向量
        elif isinstance(other,Vector):
            return self.x*other.x+self.y*other.y # 向量相乘 返回数
        else:
            raise Exception("未知类型")

    def __iadd__(self, other):
        if isinstance(other,Vector):
            self.x+=other.x
            self.y+=other.y
            return self
        else:
            raise Exception("未知类型")

    def __sub__(self, other):
        if isinstance(other, Vector):
            c = copy.deepcopy(self)
            c.x = self.x - other.x
            c.y = self.y - other.y
            return c
        else:
            raise Exception("未知类型")

    def __add__(self, other):
        if isinstance(other,Vector):
            c=copy.deepcopy(self)
            c.x=self.x+other.x
            c.y=self.y+other.y
            return c
        else:
            raise Exception("未知类型")


    def reflect(self,wall_norm_vector):
        """撞到墙上的反射
        wall_norm_vector是墙的正向法向量
        要求与墙的法向量夹角在90到270度之间"""
        assert isinstance(wall_norm_vector,Vector)
        diff_angle=self.angle-wall_norm_vector.angle
        diff_angle=self.format_angle(diff_angle)
        if not (math.pi/2-0.0001 <=diff_angle<=math.pi*1.5+0.0001):
            print('sd')
        assert math.pi/2-0.0001 <=diff_angle<=math.pi*1.5+0.0001
        c=self*-1
        new_angle=2*wall_norm_vector.angle-c.angle
        mo=c.modulus
        return Vector(mo*math.cos(new_angle),mo*math.sin(new_angle))

    @property
    def modulus(self):
        return (self.x**2+self.y**2)**0.5

    @modulus.setter
    def modulus(self,v): # 设定模
        assert not (self.x == 0 and self.y == 0) #零向量不能设定模
        assert v>=0 # 模不能为负
        t=self.modulus
        self.x*=v/t
        self.y*=v/t


    @property
    def angle(self):
        """返回向量与x轴的角度 弧度值 逆时针旋转为正
        返回值是-pi ，pi"""
        if self.x==0:
            if self.y==0:
                return 0.0 # 0向量与x轴夹角为0
            elif self.y>0:
                return math.pi/2
            else:
                return -math.pi/2

        t=math.atan(self.y/self.x)

        if self.x<0:
            if self.y>0:
                return t + math.pi
            else:
                return t-math.pi

        return t

    @staticmethod
    def is_same_angle(x,y,tol=0.0001):
        """判断两个角度值是否相同,tol是误差"""
        if abs(x-y)<tol:
            return True
        if x>y: # 取大值给y
            t=y
            y=x
            x=t

        diff=y-x
        tmp=round(diff/math.pi/2)
        x+=tmp*2*math.pi

        if abs(y-x)<tol:
            return True
        else:
            return False

    @staticmethod
    def format_angle(angle):
        """将angle转换到0到2pi中"""
        assert isinstance(angle,(float,int))
        diff=angle
        tmp=math.floor(diff/2/math.pi)
        angle-=tmp*2*math.pi
        assert angle>=0 and angle<=2*math.pi
        return angle




if __name__=="__main__":
    # 测试开始
    assert Vector.is_same_angle(2.422+10*math.pi+0.000001,2.422)
    assert Vector.is_same_angle(2.422-10*math.pi+0.000001,2.422)
    assert Vector.is_same_angle(2.422-0*math.pi+0.000001,2.422)

    num=1
    while num<200:
        angle=random.uniform(-6,6)
        v=Vector(math.cos(angle),math.sin(angle))
        t=Vector.is_same_angle(v.angle,angle)
        # print(v.angle)
        #print(t)
        assert t
        num+=1

    wall_vector=Vector(0,1)
    light=Vector(-1,-1)
    re=Vector(-1,1)
    assert re==light.reflect(wall_vector)

    wall_vector = Vector(1, -1)
    light = Vector(-1, 0)
    re = Vector(0, -1)
    assert re == light.reflect(wall_vector)

    assert Vector(0,0)==Vector(0,1e-6)

    a=Vector(1,2.3)
    a.modulus=2
    assert a.modulus==2

    a = Vector(1, 2.3)
    b = Vector(10, 20)
    a+=b
    print(a)





    #测试结束



