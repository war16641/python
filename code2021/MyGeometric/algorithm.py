from typing import List
import matplotlib.pyplot as plt
from code2021.MyGeometric.map import MeshedMap
from code2021.MyGeometric.rect import Rect
from code2021.mydataexchange import make_data_from_file
from vector3d import Vector3D
import numpy as np

class Algo1:
    def __init__(self,target:Rect,bk:List[Rect]):
        self.target=target
        self.bk=bk

        #建立map

        bigsize=max(target.width,target.height) #目标的大尺寸
        self.sense_size=bigsize #感觉尺寸 用于判定距离的大小
        lst=[]
        for i in bk:
            lst.extend(i.corners)
        lst.extend(target.corners)
        ld,ru=Vector3D.get_bound_corner(lst)#获取背景的范围
        #map的尺寸为背景范围+2倍目标尺寸
        maprect=Rect.make_by_two_corners(ld-Vector3D(bigsize*2,bigsize*2),ru+Vector3D(bigsize*2,bigsize*2))

        self.mm=MeshedMap(maprect.bound_corners[0],maprect.bound_corners[1])
        self.mm.mesh(1/8.0*bigsize)
    def show(self):
        fig = plt.figure()  # 创建图
        ax = fig.add_subplot(aspect='equal')  # 创建子图
        ax.set_xbound(self.mm.leftdown.x, self.mm.rightup.x)
        ax.set_ybound(self.mm.leftdown.y, self.mm.rightup.y)
        #绘图
        for i in self.bk:
            self.add_rect_to_axes(i,ax,'r')
        i=self.target
        self.add_rect_to_axes(i, ax, 'g')
        # plt.show()
        return ax



    @staticmethod
    def default_dist_func(rect1,rect2):
        dist1, dist2 = rect1.get_dist_from_rect(rect2)
        return (dist1 ** 2 + dist2 ** 2) ** 0.5

    @staticmethod
    def default_dist_func1(rect1,rect2):
        return abs(rect1.xy-rect2.xy)


    @staticmethod
    def default_valve_func(percent,dist):
        return percent*dist+dist

    @staticmethod
    def default_valve_func1(percent,dist):
        if percent<0.15:
            return percent*dist+dist
        else:
            return percent*dist*10+dist


    def solve(self,valve_func=None,
                   additional_valve=None,
                   coeffs=(1,1),
                   dist_func=None)->Rect:
        #处理输入参数
        if valve_func is None:
            valve_func = Algo1.default_valve_func
        if additional_valve is None:
            additional_valve = lambda x: 0
        if dist_func is None:
            dist_func = Algo1.default_dist_func

        # 先把rects占据的cell填红
        for r in self.bk:
            for c in self.mm.get_cells_in_rect_fast(r):
                c.facecolor = 'r'
        pass

        #开始计算
        outr = []#存储每一步的结果
        target_rect=self.target
        mm=self.mm
        numofcells_in_target = target_rect.height * target_rect.width / mm.cell_length ** 2  # target rect中cell个数 不取整
        for x in np.arange(mm.leftdown.x, mm.rightup.x - target_rect.width, mm.cell_length):
            for y in np.arange(mm.leftdown.y, mm.rightup.y - target_rect.height, mm.cell_length):
                thisrect = Rect(Vector3D(x, y), target_rect.width, target_rect.height, 0.0)  # 新位置
                number_goodcells = 0
                # dist = abs(target_rect.center - thisrect.center)  # 中心点距离
                dist = dist_func(target_rect, thisrect)  # 使用距离函数
                for c in mm.get_cells_in_rect_fast(thisrect):
                    if c.facecolor == 'g':
                        number_goodcells += 1
                # 红色cell占比 移动距离
                t1 = (numofcells_in_target - number_goodcells) / numofcells_in_target
                t1=0 if t1<0 else t1 #由于numofcells_in_target只是近似 可能会导致这个值为负 这时需要改为0
                t2 = dist/self.sense_size
                outr.append([thisrect, t1, t2, valve_func(t1, t2) * coeffs[0] + additional_valve(thisrect) * coeffs[1]])

        #排序取最小
        outr.sort(key=lambda x: x[3])
        return outr[0][0]

        #测试代码
        axes=self.show()
        self.add_rect_to_axes(outr[0][0],axes,color='b')
        for i in outr[0:10]:
            print(i)
        plt.show()


    @staticmethod
    def load_from_datafile(filepath,ignore_lines=0)->'Algo1':
        d=make_data_from_file(filepath,ignore_lines)
        target=None
        bk=[]
        for k,v in d.items():
            if k=="target":
                target=v
            elif k[0:2]=="bk":
                bk.append(v)
            else:
                pass
        return Algo1(target,bk)

    def add_rect_to_axes(self,rect,axes,color):
        axes.add_patch(plt.Rectangle((rect.xy.x, rect.xy.y), rect.width, rect.height,
                                   facecolor='w',
                                   edgecolor=color,
                                   linewidth=1))
if __name__ == '__main__':
    a=Algo1.load_from_datafile(r"D:\dataexchange.txt")
    r=a.solve(dist_func=Algo1.default_dist_func1,
            valve_func=Algo1.default_valve_func1)
    print(r)