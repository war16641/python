import unittest
from math import ceil, floor, pi
from typing import List
import pickle
import matplotlib.pyplot as plt
import numpy as np
from autocad.toapoint import MyRect
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D


mylogger=MyLogger('mapmesh123d')
mylogger.hide_level=True
mylogger.hide_name=True
mylogger.setLevel('debug')
class MapMesh:
    def __init__(self, leftdown: Vector3D, rightup:Vector3D):
        self.leftdown,self.rightup=leftdown,rightup
        self.cells=[]#type:list[MyRect]
        self.array=None
        self.cell_length=0.

    @property
    def width(self):
        return self.rightup.x-self.leftdown.x
    @property
    def height(self):
        return self.rightup.y - self.leftdown.y
    def mesh(self,celllength):
        self.cell_length=celllength
        t1=ceil(self.width/float(celllength))
        #稍微加宽以保证为整数
        self.rightup.x=self.leftdown.x+t1*celllength
        t2=ceil(self.height/float(celllength))
        #稍微加宽以保证为整数
        self.rightup.y=self.leftdown.y+t2*celllength
        #开始mesh
        self.cells=[]
        # for x in np.arange(self.leftdown.x,self.rightup.x,celllength):
        #     for y in np.arange(self.leftdown.y,self.rightup.y,celllength):
        #         nc=MyRect(Vector3D(x,y),celllength,celllength,0.0)
        #         nc.facecolor='g'#额外添加一个颜色变量
        #         self.cells.append(nc)
        for y in np.arange(self.leftdown.y, self.rightup.y, celllength):
            for x in np.arange(self.leftdown.x,self.rightup.x,celllength):
                nc=MyRect(Vector3D(x,y),celllength,celllength,0.0)
                nc.facecolor='g'#额外添加一个颜色变量
                self.cells.append(nc)
        self.array=np.array(self.cells)
        self.array=self.array.reshape((t2,t1))

    def get_cells_in_rect_fast(self,rect:MyRect,precise=False)->List[MyRect]:
        """
        快速得到在rect中所有的cells
        要求rect旋转角度=0 以后可以改进不为零的情况
        @param rect:
        @return:
        """
        def script(x):#防止越界
            if x<0:
                x=0
            return x
        #为了提高速度 一旦执行了这个命令 rect中会保留生成的cell列表
        if hasattr(rect,'cells_in_mm'):
            mylogger.debug('rect之前执行过此命令。')
            return rect.cells_in_mm
        ld,ru=rect.bound_corners#使用
        t1=int(round((ld.x-self.leftdown.x)/self.cell_length))
        t2=int(round((ru.x-self.leftdown.x)/self.cell_length))
        r1=int(round((ld.y-self.leftdown.y)/self.cell_length))
        r2 = int(round((ru.y- self.leftdown.y) / self.cell_length))
        # t=self.array[script(r1):r2+1,script(t1):t2+1]
        t = self.array[script(r1):r2 + 0, script(t1):t2 + 0]
        if precise is False or abs(rect.rotation)<1e-5:
            rv= t.reshape((t.size,)).tolist()
        else:#要求准确 且 呆选择角度
            #一个个去验证
            lst=[]
            for i in t.reshape((t.size,)).tolist():
                if i.center in rect:
                    lst.append(i)
            rv= lst
        if not hasattr(rect,'cells_in_mm'):
            rect.cells_in_mm=rv#在rect中保留结果
            mylogger.debug('在rect中保留此命令结果。')
        return rv
    def show(self,additional_rect:MyRect=None):
        fig = plt.figure()  # 创建图
        ax = fig.add_subplot(aspect='equal')  # 创建子图
        ax.set_xbound(self.leftdown.x,self.rightup.x)
        ax.set_ybound(self.leftdown.y, self.rightup.y)
        if additional_rect is not None:
            additional_cells=self.get_cells_in_rect_fast(additional_rect)
        else:
            additional_cells=[]
        for i in self.cells:
            if i in additional_cells:
                cl='b'#蓝色显示额外
            else:
                cl=i.facecolor
            ax.add_patch(plt.Rectangle((i.xy.x,i.xy.y), i.width, i.height,
                                       facecolor=cl,
                                       edgecolor='w',
                                       linewidth=1))
        # for x in np.arange(self.leftdown.x,self.rightup.x-0.1*self.cell_length,self.cell_length):
        #     for y in np.arange(self.leftdown.y,self.rightup.y-0.1*self.cell_length,self.cell_length):
        #         ax.add_patch(plt.Rectangle((x, y), self.cell_length, self.cell_length,
        #                                           facecolor='r',
        #                                           edgecolor='g',
        #                                           linewidth=1))
        return ax,fig
        # plt.show()

    def save_to_file(self,fullname=r'd:\last_mapmesh.npy'):
        #写入文件保存
        #仅保留以下三个变量
        t1=pickle.dumps(self.leftdown)
        t2=pickle.dumps(self.rightup)
        t3=pickle.dumps(self.cell_length)
        with open(fullname,'wb') as f:
            f.write(t1)
            f.write(t2)
            f.write(t3)

    @staticmethod
    def load_from_file(fullname=r'd:\last_mapmesh.npy')->'MapMesh':
        #冲文件中载入
        f = open(fullname, "rb")
        t1 = pickle.load(f)
        t2 = pickle.load(f)
        t3 = pickle.load(f)
        mm=MapMesh(t1,t2)
        mm.mesh(t3)
        f.close()
        return mm

def print_outr(outr,n=5):
    print('打印计算结果:')
    for i,o in enumerate(outr):
        print('%d: %f,%f,%f'%(i,o[1],o[2],o[3]))
        if i==n:
            break
def typical_valve_func(x):
    #一个典型的价值函数 红色占比和距离直接相乘 加上距离
    return x[1]*x[2]+x[2]
def find_whiterect(mm:MapMesh,rects:List[MyRect],target_rect:MyRect,valve_func=None)->MyRect:
    """
    在mapmesh中寻找一片指定大小的空白区域rect（非红色区域）
    算法介绍：遍历每一个区域 ，计算这个区域的红色覆盖率，移动距离 通过价值函数，排序得出最佳区域
    @param mm:
    @param rects:
    @param target_rect:
    @param valve_func:价值函数 一个二元函数 即当前rect的（红色覆盖率，移动距离） 如果不指定会使用本文件中的价值函数
    @return:
    """

    if valve_func is None:
        valve_func=typical_valve_func
    #先把rects占据的cell填红
    for r in rects:
        for c in mm.get_cells_in_rect_fast(r):
            c.facecolor='r'
    # mm.show(additional_rect=target_rect)
    ax,_=mm.show()
    target_rect.draw_in_axes(ax)
    plt.show()
    # 开始计算最佳位置
    outr = []
    numofcells_in_target = target_rect.height * target_rect.width / mm.cell_length ** 2#target rect中cell个数 不取整
    for x in np.arange(mm.leftdown.x, mm.rightup.x - target_rect.width, mm.cell_length):
        for y in np.arange(mm.leftdown.y, mm.rightup.y - target_rect.height, mm.cell_length):
            thisrect = MyRect(Vector3D(x, y), target_rect.width, target_rect.height, 0.0)  # 新位置
            number_goodcells = 0
            dist = abs(target_rect.center - thisrect.center)  # 距离
            for c in mm.get_cells_in_rect_fast(thisrect):
                if c.facecolor == 'g':
                    number_goodcells += 1
            #红色cell占比 移动距离
            t1=(numofcells_in_target-number_goodcells)/numofcells_in_target
            t2=dist
            outr.append([thisrect,t1 ,t2 ,valve_func(t1,t2) ])
    # 根据计算结果排序得出最优
    outr.sort(key=lambda x:x[3])
    print_outr(outr)
    ax,_=mm.show()
    outr[0][0].draw_in_axes(ax)
    plt.show()
    return outr[0][0]#返回计算得出的 最佳的rect

    pass

class TestCase(unittest.TestCase):
    def test1(self):
        mm = MapMesh(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = MyRect.make_by_two_corners(Vector3D(18.7, 18.7), Vector3D(41.1, 41.1))
        jg=mm.get_cells_in_rect_fast(r)
        for i in jg:
            i.facecolor = 'r'
        # ax,_ = mm.show()
        # r.draw_in_axes(ax)
        # plt.show()
        self.assertEqual(12*12,len(jg))
    def test_2(self):
        mm = MapMesh(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = MyRect(xy=Vector3D(10,20),width=20,height=10,rotation=pi/6)
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
        mm = MapMesh(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        r = MyRect(xy=Vector3D(10,20),width=20,height=10,rotation=pi/6)
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
    def test_4(self):#测试保存
        mm = MapMesh(Vector3D(0, 0), Vector3D(80., 90))
        mm.mesh(2.)
        mm.save_to_file()
        mm1=MapMesh.load_from_file()

        r = MyRect(xy=Vector3D(10,20),width=20,height=10,rotation=pi/6)
        jg=mm1.get_cells_in_rect_fast(r,precise=True)
        for i in jg:
            i.facecolor = 'r'
        self.assertEqual(49,len(jg))
        self.assertEqual(Vector3D(80,90),mm1.rightup)
        self.assertEqual(2, mm1.cell_length)
        # ax,fig = mm.show()
        # r.draw_in_axes(ax)
        # plt.show()
if __name__ == '__main__':

    unittest.main()
    # a=1
    # mm=MapMesh(Vector3D(0,0),Vector3D(80.,90))
    # mm.mesh(2.)
    # # r=MyRect(xy=Vector3D(19.1,19.1),width=40.5,height=40.5)
    # r=MyRect.make_by_two_corners(Vector3D(18.7,18.7),Vector3D(41.1,41.1))
    # for i in mm.get_cells_in_rect_fast(r):
    #     i.facecolor='r'
    # ax=mm.show()
    # # ax.plot([0,100],[0,150],'-')
    # r.draw_in_axes(ax)
    # plt.show()