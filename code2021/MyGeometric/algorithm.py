from typing import List, Tuple
import matplotlib.pyplot as plt
from code2021.MyGeometric.map import MeshedMap
from code2021.MyGeometric.rect import Rect
from code2021.mydataexchange import make_data_from_file
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D
import numpy as np
import time
import code2021.MyGeometric.map as mymap

mylogger = MyLogger('ALGO14881')
mylogger.hide_level = True
mylogger.hide_name = True
mylogger.setLevel('debug')


class Algo1:
    def __init__(self, target: Rect, bk: List[Rect], coeff_for_mesh=1 / 8.0):
        self.target = target
        self.bk = bk

        # 建立map

        bigsize = min(target.width, target.height)  # 目标的大尺寸
        self.sense_size = bigsize / 8.0  # 感觉尺寸 用于判定距离的大小

        t = [x for x in bk]
        t.append(target)
        maprect = Algo1.determine_map_size(t, self.sense_size)
        self.mm = MeshedMap(maprect.bound_corners[0], maprect.bound_corners[1])

        self.coeff_for_mesh = coeff_for_mesh
        self.mm.mesh(coeff_for_mesh * bigsize)

    def show(self):
        # 显示边框线
        fig = plt.figure()  # 创建图
        ax = fig.add_subplot(aspect='equal')  # 创建子图
        ax.set_xbound(self.mm.leftdown.x, self.mm.rightup.x)
        ax.set_ybound(self.mm.leftdown.y, self.mm.rightup.y)
        # 绘图
        for i in self.bk:
            self.add_rect_to_axes(i, ax, 'r')
        i = self.target
        self.add_rect_to_axes(i, ax, 'g')
        # plt.show()
        return ax

    @staticmethod
    def determine_map_size(rects: List[Rect], margin: float) -> Rect:
        lst = []
        for i in rects:
            lst.extend(i.bound_corners)
        ld, ru = Vector3D.get_bound_corner(lst)  # 获取背景的范围
        return Rect.make_by_two_corners(ld - Vector3D(margin * 2, margin * 2), ru + Vector3D(margin * 2, margin * 2))

    @staticmethod
    def default_dist_func(rect1, rect2):
        dist1, dist2 = rect1.get_dist_from_rect(rect2)
        return (dist1 ** 2 + dist2 ** 2) ** 0.5

    @staticmethod
    def default_dist_func1(rect1, rect2):
        return abs(rect1.xy - rect2.xy)

    @staticmethod
    def default_valve_func(percent, dist):
        return percent * dist + dist

    @staticmethod
    def default_valve_func1(percent, dist):
        if percent < 0.15:
            return percent * dist + dist + percent
        else:
            return percent * dist * 10 + dist + percent + 15

    def set_bk(self):
        # 把rects占据的cell填红
        self.mm.change_color_in_rects(self.bk, 'r')
        # for r in self.bk:
        #     for c in self.mm.get_cells_in_rect_fast(r):
        #         c.facecolor = 'r'
        # pass
        # pass

    def solve(self, valve_func=None,
              additional_valve=None,
              coeffs=(1, 1),
              dist_func=None) -> Rect:
        """
        在mapmesh中寻找一片指定大小的空白区域rect（非红色区域）
    算法介绍：
    遍历每一个区域 ，计算这个区域的红色覆盖率，距离 通过价值函数（二元函数）与附加价值函数的和，排序得出最佳区域（越低越好）
    其中：距离可以通过dist_func指定，默认为当前的rect与target_rect的距离，
        @param valve_func: 价值函数 一个二元函数 即当前rect的（红色覆盖率，移动距离） 如果不指定会使用本文件中的价值函数
        @param additional_valve: 附加价值函数（一元函数，以当前rect作为函数输入）
        @param coeffs: 长度为2的序列，依次为价值函数和附加价值函数的系数，
        @param dist_func: 距离函数（二元函数，依次以target_rect和当前rect作为函数输入）
        @return:
        """
        # 处理输入参数
        if valve_func is None:
            valve_func = Algo1.default_valve_func1
        if additional_valve is None:
            additional_valve = lambda x: 0
        if dist_func is None:
            dist_func = Algo1.default_dist_func1

        # # 先把rects占据的cell填红
        # for r in self.bk:
        #     for c in self.mm.get_cells_in_rect_fast(r):
        #         c.facecolor = 'r'
        # pass

        # 开始计算
        outr = []  # 存储每一步的结果
        target_rect = self.target
        mm = self.mm
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
                t1 = 0 if t1 < 0 else t1  # 由于numofcells_in_target只是近似 可能会导致这个值为负 这时需要改为0
                t2 = dist / self.sense_size
                outr.append(
                    [thisrect, t1, dist, valve_func(t1, t2) * coeffs[0] + additional_valve(thisrect) * coeffs[1]])

        # 排序取最小
        outr.sort(key=lambda x: x[3])

        # 测试代码
        # axes=self.show()
        # self.add_rect_to_axes(outr[0][0],axes,color='b')
        # for i in outr[0:10]:
        #     print(i)
        # plt.show()

        return outr[0][0]

    @staticmethod
    def load_from_datafile(filepath, ignore_lines=0) -> 'Algo1':
        d = make_data_from_file(filepath, ignore_lines)
        target = None
        bk = []
        coeff = None
        for k, v in d.items():
            if k == "target":
                target = v
            elif k[0:2] == "bk":
                bk.append(v)
            elif k[0:5] == "coeff":
                coeff = v
            else:
                pass
        if coeff is None:
            return Algo1(target, bk)
        else:
            return Algo1(target, bk, coeff_for_mesh=coeff)

    def save(self, filename):
        def rect_line(rect: Rect):
            return "%f,%f,%f,%f,%f,%f" % (rect.xy.x, rect.xy.y, rect.xy.z, rect.width, rect.height, rect.rotation)

        with open(filename, 'w') as f:
            f.write("target rect %s\n" % rect_line(self.target))
            f.write("coeff float %f\n" % self.coeff_for_mesh)
            for i, r in enumerate(self.bk):
                f.write("bk%d rect %s\n" % (i, rect_line(r)))

    def add_rect_to_axes(self, rect, axes, color):
        axes.add_patch(plt.Rectangle((rect.xy.x, rect.xy.y), rect.width, rect.height,
                                     facecolor='w',
                                     edgecolor=color,
                                     linewidth=1))

    @staticmethod
    def solve_batch(targets: List[Rect],
                    bks: List[Rect],
                    margin,
                    valve_func=None,
                    additional_valve=None,
                    coeffs=(1, 1),
                    dist_func=None,
                    coeff_for_mesh=1 / 8.0,
                    delete_used_bk=False) -> List[Rect]:
        """
        多个target在bk中的求解
        一个一个解
        @param targets:
        @param bks:
        @param margin:
        @param valve_func:
        @param additional_valve:
        @param coeffs:
        @param dist_func:
        @param coeff_for_mesh:
        @param delete_used_bk: true时 计算完一个 删除这个target用到的bk 
        @return:
        """
        rt = []
        for cur_job, target in enumerate(targets):
            mylogger.debug("计算第%d个。。。"%cur_job)
            mylogger.debug("当前bks数量：%d"%len(bks))
            start_time = time.time()

            # 计算当前target的map范围
            thissize = min(target.height, target.width)
            # margin = 20*thissize
            thismaprect = Rect.make_by_two_corners(target.center - Vector3D(margin, margin),
                                                   target.center + Vector3D(margin, margin))
            # 搜集在这个map范围内的bk
            thisbk = []
            for bk in bks:
                if bk.center in thismaprect:
                    thisbk.append(bk)
            a = Algo1(target, thisbk, coeff_for_mesh=0.2)
            a.set_bk()
            rt1 = a.solve(dist_func=dist_func,
                          valve_func=valve_func)
            # #下面三行为测试
            # ax=a.show()
            # a.add_rect_to_axes(rt1,ax,'b')
            # plt.show()
            mylogger.debug(rt1.__str__())
            mylogger.debug("%d/%d完成，耗时%fs" % (cur_job, len(targets), time.time() - start_time))
            rt.append(rt1)
            # 删除用过的bk
            if delete_used_bk:
                [bks.remove(x) for x in thisbk]
        return rt

    @staticmethod
    def solve_batch_from_batch(filepath, ignore_lines=0, delete_used_bk=False) -> Tuple[List[Rect], List[Rect]]:
        d = make_data_from_file(filepath, ignore_lines)
        target = []
        bk = []
        margin = None
        for k, v in d.items():
            if k[0:6] == "target":
                target.append(v)
            elif k[0:2] == "bk":
                bk.append(v)
            elif k[0:6] == 'margin':
                margin = v
            else:
                pass
        return Algo1.solve_batch(targets=target,
                                 bks=bk,
                                 margin=margin,
                                 coeff_for_mesh=0.2,
                                 delete_used_bk=delete_used_bk), target


if __name__ == '__main__':
    a = Algo1.load_from_datafile(r"D:\dataexchange.txt")
    r = a.solve(dist_func=Algo1.default_dist_func1,
                valve_func=Algo1.default_valve_func1)
    print(r)
