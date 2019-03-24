import math

class Line:
    """代表平面中的直线"""

    def __init__(self,A=0,B=0,C=0,name=''):
        """直线解析式 Ax+By+C=0"""
        assert  not (A==0 and B==0)
        self.A,self.B,self.C=A,B,C
        self.name=name

    def __str__(self):
        return "名称：%s   %fx+%fy+%f=0"%(self.name,self.A,self.B,self.C)

    def distance_to_point(self,x,y):
        """到点的距离 x y是点坐标"""
        return abs(self.A*x+self.B*y+self.C)/(self.A**2+self.B**2)**0.5


if __name__=="__main__":
    a=Line(A=0,B=1,C=0)
    print(a.distance_to_point(10,3.3))
    a=[1,2,-4,2]
    print(a.index(min(a)))
    print(a[3])
