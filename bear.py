import numpy as np
import matplotlib.pyplot as plt
from copy import deepcopy
class Circle:
    def __init__(self,f0,f1,extent,x0):
        assert x0>=extent[0] and x0<=extent[1]
        self.f0,self.f1,self.extent,self._x=f0,f1,extent,x0
        self.f=f0#当前反力
    @property
    def x(self):
        return self._x
    @x.setter
    def x(self,v):
        assert v>=self.extent[0] and v<=self.extent[1]
        self._x=v
    def move(self,dx):
        #dx分为正负
        if dx>0:
            if self.x + dx <= self.extent[1]:
                self.x += dx
                self.f=self.f0
                return self.f0
            else:
                self.x = self.extent[1]
                self.f=self.f1
                return self.f1
        elif dx<0:
            if self.x + dx >= self.extent[0]:
                self.x += dx
                self.f=-self.f0
                return -self.f0
            else:
                self.x = self.extent[0]
                self.f=-self.f1
                return -self.f1
        else:
            pass

    def moves(self,x0,dx_seq):
        self.x=x0
        print('%f,%f'%(dx_seq[0],self.f))
        for i in range(1,len(dx_seq)):
            dx=dx_seq[i]-dx_seq[i-1]
            self.move(dx)
            print('%f,%f' % (dx_seq[i], self.f))

class Circles:
    def __init__(self,c_lst):
        self.c_lst=c_lst#type:list[Circle]
        self.f=0
        for c in self.c_lst:
            self.f+=c.f
    def move(self,dx):
        self.f=0
        for c in self.c_lst:
            c.move(dx)
            self.f+=c.f

    def moves(self,x_seq):
        length=len(x_seq)
        # x=np.zeros((length,))
        y=np.zeros((length,))
        # x[0]=x_seq[0]
        y[0]=self.f
        for i in range(1,length):
            dx=x_seq[i]-x_seq[i-1]
            self.move(dx)
            y[i]=self.f
            # x[i]=x_seq[0]
        return x_seq,y


def test1():
    s0=10#设计位移
    s=9.#位移荷载的峰值
    num_loop=5#周期荷载的圈数
    c1=Circle(f0=0,f1=1,extent=[0,s0],x0=0)
    c2 = Circle(f0=0, f1=1, extent=[0, s0], x0=s0)
    cs=Circles([c1,c2])
    oa=np.arange(0.,s,0.1)
    ac=np.arange(s,-s,-0.1)
    ca=np.arange(-s,0.0,0.1)
    lu=np.hstack((oa,ac,ca,))
    num=len(lu)
    lu=np.tile(lu,num_loop)
    x,y=cs.moves(lu)
    for i in range(5):
        start=i*num
        end=(i+1)*num
        plt.plot(x[start:end],y[start:end],label='cricle'+str(i+1))
        # plt.show()
    plt.legend()
    plt.show()
if __name__ == '__main__':
    c=Circle(f0=0,f1=1,extent=[0,5],x0=0)
    lucus=np.arange(0,10,0.1)
    lucus1 = np.arange(10, 0, -0.1)
    lu=np.hstack((lucus,lucus1))
    # c.moves(0,lu)
    test1()