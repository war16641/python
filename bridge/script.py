from GoodToolPython.excel.excel import FlatDataModel
from copy import deepcopy
from typing import List, Tuple
import math


def __计算钢束伸长量_子脚本(fdm: FlatDataModel, 张拉控制应力=1395, 弹模=1.95e5, 偏差系数=0.0015, 摩擦系数=0.25) -> List[FlatDataModel]:
    fdm = deepcopy(fdm)
    fdm.vn.append('θ/rad')
    fdm.vn.append('kx+μθ')
    fdm.vn.append('起点应力/MPa')
    fdm.vn.append('平均应力/Mpa')
    fdm.vn.append('终点应力/Mpa')
    fdm.vn.append('伸长量/mm')

    for i, u in enumerate(fdm.units):
        u.data['θ/rad'] = u.data['θ/°'] / 180 * 3.1415926
        u.data['kx+μθ'] = u.data['孔道长度x/m'] * 偏差系数 + 摩擦系数 * u.data['θ/rad']
        if i == 0:
            u.data['起点应力/MPa'] = 张拉控制应力
        else:
            u.data['起点应力/MPa'] = fdm.units[i - 1]['终点应力/Mpa']
        u.data['平均应力/Mpa'] = u.data['起点应力/MPa'] * (1 - math.exp(-1 * u.data['kx+μθ'])) / u.data['kx+μθ']
        u.data['终点应力/Mpa'] = u.data['起点应力/MPa'] * math.exp(-1 * u.data['kx+μθ'])
        u.data['伸长量/mm'] = u.data['平均应力/Mpa'] / 弹模 * u.data['孔道长度x/m'] * 1000
    # fdm.show_in_excel()
    fdm1 = deepcopy(fdm)
    fdm1 = fdm1.narrow(fdm1.vn[4:])
    t = fdm['伸长量/mm']
    l = sum(t)  # 累计伸长量
    return fdm, fdm1, l


def 计算钢束伸长量(fdm: FlatDataModel, 张拉控制应力=1395, 弹模=1.95e5, 偏差系数=0.0015, 摩擦系数=0.25) -> Tuple[FlatDataModel, float]:
    """
    计算钢束生产量

    主要是计算不动点在哪儿
    算法类似于牛顿拉普森算法。先变化一点点，算出斜率。然后利用此斜率估计不动点，直到达到容许误差
    :param fdm: 钢束的平面数据模型 四个列
    :param 张拉控制应力:
    :param 弹模:
    :param 偏差系数:
    :param 摩擦系数:
    :return:
    """

    def calc_stree2(x):
        nonlocal fdm, 张拉控制应力, 偏差系数, 摩擦系数, n_expected, fdm1, fdm2, l1, l2, fdm1_, fdm2_
        fdm1 = deepcopy(fdm)
        fdm1.units = fdm1.units[0:n_expected]  # 删除后半
        # 修改最后一段数据
        fdm1.units[-1].data['孔道长度x/m'] = x
        if fdm1.units[-1].data['曲率半径/m'] != 0:
            fdm1.units[-1].data['θ/°'] = fdm1.units[-1].data['孔道长度x/m'] / fdm1.units[-1].data['曲率半径/m'] / 3.14159 * 180
        fdm1_, t, l1 = __计算钢束伸长量_子脚本(fdm1)
        stress1 = t.units[-1].data['终点应力/Mpa']

        fdm2 = deepcopy(fdm)
        fdm2.units = fdm2.units[n_expected - 1:]  # 删除前半
        # 修改第一段数据
        fdm2.units[0].data['孔道长度x/m'] = fdm.units[n_expected - 1].data['孔道长度x/m'] - x
        if fdm2.units[0].data['曲率半径/m'] != 0:
            fdm2.units[0].data['θ/°'] = fdm2.units[0].data['孔道长度x/m'] / fdm2.units[0].data['曲率半径/m'] / 3.14159 * 180

        fdm2.units.reverse()  # 颠倒顺序
        fdm2_, t, l2 = __计算钢束伸长量_子脚本(fdm2)
        stress2 = t.units[-1].data['终点应力/Mpa']
        return stress1 - stress2

    fdm = deepcopy(fdm)
    number = len(fdm)  # 分段的个数
    n_expected = round(number / 2.0 + 0.01)  # 预计的不动点所处的分段编号
    x = 0.5 * fdm.units[n_expected - 1].data['孔道长度x/m']  # 默认在中点

    iter_counter1 = 0
    fdm1 = None
    fdm2 = None
    fdm1_, fdm2_ = None, None
    l1, l2 = 0, 0
    while True:
        iter_counter1 += 1
        # 检查n_expected的合理性
        assert 0 <= n_expected <= len(fdm), '迭代失败。迭代算法预计不动点出现段超出了合理值'
        print(n_expected)
        assert iter_counter1 <= 20, '迭代失败。d1达到最大循环次数。'
        iter_counter2 = 0
        while True:
            iter_counter2 += 1
            delta = calc_stree2(x)
            if abs(delta) < 0.1:
                break
            step_size = fdm.units[n_expected - 1].data['孔道长度x/m'] * 0.01
            x2 = x + step_size
            delta2 = calc_stree2(x2)
            k = (delta2 - delta) / (x2 - x)  # 变化斜率
            x = x - delta / k  # 更新x
            if iter_counter2 > 20:
                raise Exception("最大迭代次数")

        # 检查x的合理性
        if x > fdm.units[n_expected - 1].data['孔道长度x/m']:
            n_expected += 1  # 不动点在下一段
            x = 0.5 * fdm.units[n_expected - 1].data['孔道长度x/m']  # 默认在中点
        elif x < 0:
            n_expected -= 1  # 不动点在上一段
            x = 0.5 * fdm.units[n_expected - 1].data['孔道长度x/m']  # 默认在中点
        else:  # 合理 退出循环
            break
    # 快要结束
    l = l1 + l2  # 合计伸长量
    # 将两个fdm合为一个
    fdm_last = deepcopy(fdm1_)
    t = deepcopy(fdm2_.units)
    t.reverse()
    fdm_last.units.extend(t)
    return fdm_last, l
    # print(x)
    # print(n_expected)
    # print(l1+l2)


def 计算长发体惯量(x, y, z, 密度):
    """

    :param x:
    :param y:
    :param z:
    :param 密度:
    :return: 质量,j1,j2,j3质量和3个方向的转动惯量
    """
    质量 = x * y * z * 密度
    j1 = 质量 / 12 * (y ** 2 + z ** 2)
    j2 = 质量 / 12 * (x ** 2 + z ** 2)
    j3 = 质量 / 12 * (y ** 2 + x ** 2)
    return 质量, j1, j2, j3


def test1():
    data = [[1, 7.832, 0, 0], [2, 0.786, 4.5, 10], [3, 15.264, 0, 0], [4, 0.786, 4.5, 10], [5, 7.832, 0, 10]]
    fdm = FlatDataModel.load_from_list(['编号', '孔道长度x/m', 'θ/°', '曲率半径/m'], data)
    print(计算钢束伸长量(fdm))


def test2():
    data = [[1, 8.778, 0, 0], [2, 1.495, 8.56, 10], [3, 0.863, 0, 0], [4, 1.858, 10.65, 10], [5, 4.746, 0, 0],
            [6, 1.858, 10.65, 10], [7, 0.736, 0, 0], [8, 1.748, 10.01, 10], [9, 6.965, 0, 0], [10, 1.351, 7.74, 10],
            [11, 1.55, 0, 0], ]
    fdm = FlatDataModel.load_from_list(['编号', '孔道长度x/m', 'θ/°', '曲率半径/m'], data)
    f, l = 计算钢束伸长量(fdm)
    print(f)
    # f.show_in_excel()
    print(l)


if __name__ == '__main__':
    test2()
