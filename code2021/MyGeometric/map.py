import unittest
from math import ceil, floor, pi
from typing import List
import pickle
import matplotlib.pyplot as plt
import numpy as np
from mybaseclasses.emptyclass import EmptyClass
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D
from .rect import Rect


mylogger=MyLogger('mapmesh12873d')
mylogger.hide_level=True
mylogger.hide_name=True
mylogger.setLevel('debug')
class MeshedMap:
    def __init__(self, leftdown: Vector3D, rightup:Vector3D):
        self.leftdown,self.rightup=leftdown,rightup
        self.cells=[]#type:list[Rect]
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
        #         nc=Rect(Vector3D(x,y),celllength,celllength,0.0)
        #         nc.facecolor='g'#额外添加一个颜色变量
        #         self.cells.append(nc)
        ys=np.arange(self.leftdown.y, self.rightup.y, celllength)
        xs=np.arange(self.leftdown.x,self.rightup.x,celllength)
        for y in ys:
            for x in xs:
                nc=Rect(Vector3D(x,y),celllength,celllength,0.0)
                nc.facecolor='g'#额外添加一个颜色变量
                self.cells.append(nc)
        self.array=np.array(self.cells)
        self.array=self.array.reshape((len(ys),len(xs)))


    def change_color_in_rects(self,rects:List[Rect],color):
        #改变rects内的cell的颜色
        for r in rects:
            for c in self.get_cells_in_rect_fast(r):
                c.facecolor=color

    def get_cells_in_rect_fast(self,rect:Rect,precise=False)->List[Rect]:
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
        if hasattr(rect,'last_cells'):
            #检查是否是相同的调用
            if rect.last_cells.meshedmap==self:
                mylogger.debug('rect之前执行过此命令。')
                return rect.last_cells.cells
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

        #写入last_cells
        ec=EmptyClass()
        ec.meshedmap=self
        ec.cells=rv
        rect.last_cells=ec
        mylogger.debug('在rect中保留此命令结果。')
        # if not hasattr(rect,'cells_in_mm'):
        #     rect.cells_in_mm=rv#在rect中保留结果
        #     mylogger.debug('在rect中保留此命令结果。')
        return rv
    def show(self,additional_rect:Rect=None):
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
    def load_from_file(fullname=r'd:\last_mapmesh.npy')-> 'MeshedMap':
        #冲文件中载入
        f = open(fullname, "rb")
        t1 = pickle.load(f)
        t2 = pickle.load(f)
        t3 = pickle.load(f)
        mm=MeshedMap(t1, t2)
        mm.mesh(t3)
        f.close()
        return mm


