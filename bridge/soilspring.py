"""
计算土弹簧刚度
已知土层分层信息 计算一个桩在土体内的土弹簧 水平刚度
"""
import numpy as np

from GoodToolPython.excel.excel import DataUnit, FlatDataModel


class Level:
    """一层土"""

    def __init__(self, thickness, scale_factor, friction_angle=0):
        self.thickness = float(thickness)  # type:float#土层厚度
        self.scale_factor = float(scale_factor)  # type:float#土体的比例系数 可根据土体类别 液性指数查表得
        self.friction_angle = float(friction_angle)  # type:float#土层摩擦角 默认为0 角度


class Pile:
    """
    一根桩
    """

    def __init__(self, calc_width, start_z, end_z, num_of_segments, x=0., y=0., sap_section_name=''):
        self.calc_width = float(calc_width)  # 桩的计算宽度
        self.start_z = float(start_z)  # 桩顶标高
        self.end_z = float(end_z)  # 桩底标高
        self.x, self.y = float(x), float(y)  # 桩的平面坐标
        self.num_of_segments = int(num_of_segments)  # 划分单元个数
        self.sap_section_name = sap_section_name  # sap2000的截面名

        self.__z_pts = None

    def __iter__(self):  # 迭代z坐标
        self.__z_pts = np.linspace(self.start_z, self.end_z, self.num_of_segments + 1)
        return self.__z_pts.__iter__()


class SoilInfo:
    """土体分层信息
    坐标系以土顶层标高为起点 向上为正"""

    def __init__(self, ground_level=0.):
        self.levels = []  # type:list[Level]
        self.ground_level = float(ground_level)  # 地面标高

    @property
    def num(self):
        return len(self.levels)

    def judge_scale_factor(self, z):
        """
        通过深度判断土层 返回该图层的scale_factor
        :param z:
        :return:
        """
        s = self.ground_level
        if z >= s:  # 在地面以上
            return 0.
        for i in range(self.num):
            s = s - self.levels[i].thickness
            if z >= s:
                return self.levels[i].scale_factor
        raise Exception("超过土层最大深度")

    def calc_springs(self, pile) -> FlatDataModel:
        """
        计算土弹簧水平刚度
        :param pile: PIle对象
        :return:
        """

        def script(dz):
            nonlocal last_stiff, last_z, b1, pts, fm, z
            scale_factor = self.judge_scale_factor(z)
            this_stiff = last_stiff + scale_factor * b1 * dz * (last_z - z)
            last_z = z
            last_stiff = this_stiff
            u = DataUnit(fm)
            u.data['z坐标'] = z
            u.data['土弹簧刚度'] = this_stiff
            u.data['该点土层比例系数'] = scale_factor
            fm.units.append(u)
            # stiffs.append(this_stiff)
            pass

        assert isinstance(pile, Pile), 'pile必须是Pile对象'
        b1 = pile.calc_width
        assert isinstance(b1, (int, float))
        last_stiff = 0.
        last_z = 0.
        fm = FlatDataModel()
        fm.vn = ['z坐标', '土弹簧刚度', '该点土层比例系数']
        pts = list(pile)
        for i, z in enumerate(pts):
            if i == 0:  # 第一个点
                dz = (pts[1] - z) * -1 * 0.5  # 认为第一个单元的长度是第1节点到第1节点与第2节点的中点的距离
                script(dz)
                continue
            if i == len(pts) - 1:  # 最后一个点
                dz = (pts[i] - pts[i - 1]) * -1 * 0.5  # 最后一个单元的长度是最后一个节点到最后一个中点的距离
                script(dz)
                continue

            dz = (pts[i - 1] + pts[i]) / 2.0 - (pts[i + 1] + pts[i]) / 2.0  # 中间单元的长度认为是最近的两个中点的差值
            script(dz)

        return fm


def test2():
    si = SoilInfo()
    si.levels.append(Level(thickness=29.15, scale_factor=5000))
    si.levels.append(Level(thickness=40, scale_factor=1e4))
    pts = np.linspace(0, 40, 41)
    pile = Pile(calc_width=1.98, start_z=0, end_z=40, num_of_segments=40)
    pts = -1 * pts
    t = si.calc_springs(pile=pile)
    stiffs1 = t['土弹簧刚度']
    # t.show_in_excel()

    si = SoilInfo()
    si.levels.append(Level(thickness=29.15, scale_factor=5000))
    si.levels.append(Level(thickness=40, scale_factor=1e4))
    pts = np.linspace(-2, 40, 43)
    pile1 = Pile(calc_width=1.98, start_z=-2, end_z=40, num_of_segments=42)
    t = si.calc_springs(pile=pile1)
    stiffs2 = t['土弹簧刚度']
    assert stiffs1[-1] == stiffs2[-1]
    # t.show_in_excel()
    # assert stiffs[0]==11385
    # assert stiffs[1] == 21285
    # assert abs(stiffs[-1]-536085) <0.1
    # print(stiffs)


def test1():
    si = SoilInfo()
    si.levels.append(Level(thickness=29.15, scale_factor=5000))
    si.levels.append(Level(thickness=40, scale_factor=1e4))
    pts = np.linspace(2.3, 42.3, 41)
    pile = Pile(calc_width=1.98, start_z=-2.3, end_z=-42.3, num_of_segments=40)
    t = si.calc_springs(pile=pile)
    stiffs = t['土弹簧刚度']
    # t.show_in_excel()
    assert stiffs[0] == 11385
    assert stiffs[1] == 21285
    assert abs(stiffs[-1] - 536085) < 0.1
    # print(stiffs)


if __name__ == '__main__':
    test2()
    test1()
    # si = SoilInfo()
    # si.levels.append(Level(thickness=29.15, scale_factor=5000))
    # si.levels.append(Level(thickness=40, scale_factor=1e4))
    # pts = np.linspace(2.3, 42.3, 41)
    # # print(pts)
    # t = si.calc_springs(b1=1.98, pts=pts)
    # t.show_in_excel()
