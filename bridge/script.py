from GoodToolPython.excel.excel import FlatDataModel
from copy import deepcopy
from typing import List
import math
def asdg(fdm):
    r= 计算钢束伸长量(fdm)
    return r[1]

def 计算钢束伸长量(fdm:FlatDataModel,张拉控制应力=1395,弹模=1.95e5,偏差系数=0.0015,摩擦系数=0.25)->List[FlatDataModel]:
    fdm=deepcopy(fdm)
    fdm.vn.append('θ/rad')
    fdm.vn.append('kx+μθ')
    fdm.vn.append('起点应力/MPa')
    fdm.vn.append('平均应力/Mpa')
    fdm.vn.append('终点应力/Mpa')
    fdm.vn.append('伸长量/mm')

    for i,u in enumerate(fdm.units):
        u.data['θ/rad']=u.data['θ/°']/180*3.1415926
        u.data['kx+μθ']=u.data['孔道长度x/m']*偏差系数+摩擦系数*u.data['θ/rad']
        if i==0:
            u.data['起点应力/MPa'] =张拉控制应力
        else:
            u.data['起点应力/MPa'] =fdm.units[i-1]['终点应力/Mpa']
        u.data['平均应力/Mpa']=u.data['起点应力/MPa']*(1-math.exp(-1*u.data['kx+μθ']))/u.data['kx+μθ']
        u.data['终点应力/Mpa']=u.data['起点应力/MPa']*math.exp(-1*u.data['kx+μθ'])
        u.data['伸长量/mm']=u.data['平均应力/Mpa']/弹模*u.data['孔道长度x/m']*1000
    # fdm.show_in_excel()
    fdm1=deepcopy(fdm)
    fdm1=fdm1.narrow(fdm1.vn[3:])
    return fdm,fdm1

def 计算钢束伸长量1(fdm:FlatDataModel,张拉控制应力=1395,弹模=1.95e5,偏差系数=0.0015,摩擦系数=0.25)->List[FlatDataModel]:
    def calc_delta(x):
        nonlocal fdm,张拉控制应力,偏差系数,摩擦系数,n_expected
        for i in range(n_expected-1):
            u=fdm.units[i]
            u.data['θ/rad'] = u.data['θ/°'] / 180 * 3.1415926
            u.data['kx+μθ'] = u.data['孔道长度x/m'] * 偏差系数 + 摩擦系数 * u.data['θ/rad']
            if i == 0:
                u.data['起点应力/MPa'] = 张拉控制应力
            else:
                u.data['起点应力/MPa'] = fdm.units[i - 1]['终点应力/Mpa']
            u.data['平均应力/Mpa'] = u.data['起点应力/MPa'] * (1 - math.exp(-1 * u.data['kx+μθ'])) / u.data['kx+μθ']
            u.data['终点应力/Mpa'] = u.data['起点应力/MPa'] * math.exp(-1 * u.data['kx+μθ'])
            u.data['伸长量/mm'] = u.data['平均应力/Mpa'] / 弹模 * u.data['孔道长度x/m'] * 1000
        #最后一段单独计算
        i=n_expected-1
        u = fdm.units[i]
        u.data['θ/rad'] = u.data['θ/°'] / 180 * 3.1415926
        u.data['kx+μθ'] = x * 偏差系数 + 摩擦系数 * u.data['θ/rad']
        if i == 0:
            u.data['起点应力/MPa'] = 张拉控制应力
        else:
            u.data['起点应力/MPa'] = fdm.units[i - 1]['终点应力/Mpa']
        u.data['平均应力/Mpa'] = u.data['起点应力/MPa'] * (1 - math.exp(-1 * u.data['kx+μθ'])) / u.data['kx+μθ']
        u.data['终点应力/Mpa'] = u.data['起点应力/MPa'] * math.exp(-1 * u.data['kx+μθ'])
        u.data['伸长量/mm'] = u.data['平均应力/Mpa'] / 弹模 * x * 1000

        saved_stress=u.data['终点应力/Mpa'] #保存最终终点应力

        #另外一边
        for i in range(len(fdm)-1,n_expected-1,-1):
            u = fdm.units[i]
            u.data['θ/rad'] = u.data['θ/°'] / 180 * 3.1415926
            u.data['kx+μθ'] = u.data['孔道长度x/m'] * 偏差系数 + 摩擦系数 * u.data['θ/rad']
            if i == len(fdm)-1:
                u.data['起点应力/MPa'] = 张拉控制应力
            else:
                u.data['起点应力/MPa'] = fdm.units[i + 1]['终点应力/Mpa']
            u.data['平均应力/Mpa'] = u.data['起点应力/MPa'] * (1 - math.exp(-1 * u.data['kx+μθ'])) / u.data['kx+μθ']
            u.data['终点应力/Mpa'] = u.data['起点应力/MPa'] * math.exp(-1 * u.data['kx+μθ'])
            u.data['伸长量/mm'] = u.data['平均应力/Mpa'] / 弹模 * u.data['孔道长度x/m'] * 1000

        # 最后一段单独计算
        i = n_expected - 1
        u = fdm.units[i]
        u.data['θ/rad'] = u.data['θ/°'] / 180 * 3.1415926
        u.data['kx+μθ'] = (x) * 偏差系数 + 摩擦系数 * u.data['θ/rad']
        u.data['起点应力/MPa'] = fdm.units[i + 1]['终点应力/Mpa']
        u.data['平均应力/Mpa'] = u.data['起点应力/MPa'] * (1 - math.exp(-1 * u.data['kx+μθ'])) / u.data['kx+μθ']
        u.data['终点应力/Mpa'] = u.data['起点应力/MPa'] * math.exp(-1 * u.data['kx+μθ'])
        u.data['伸长量/mm'] = u.data['平均应力/Mpa'] / 弹模 * (x) * 1000

        return saved_stress-u.data['终点应力/Mpa'] #返回差值

    def calc_stree2(x):
        nonlocal fdm, 张拉控制应力, 偏差系数, 摩擦系数, n_expected
        fdm1=deepcopy(fdm)
        fdm1.units=fdm1.units[0:n_expected]#删除后半
        fdm1.units[-1].data['孔道长度x/m']=x
        t=计算钢束伸长量(fdm1)[1]
        stress1=t.units[-1].data['终点应力/Mpa']

        fdm2 = deepcopy(fdm)
        fdm2.units = fdm2.units[n_expected - 1:]  # 删除前半
        fdm2.units[0].data['孔道长度x/m'] = fdm.units[n_expected-1].data['孔道长度x/m']-x
        fdm2.units.reverse()#颠倒顺序
        t = 计算钢束伸长量(fdm2)[1]
        stress2 = t.units[-1].data['终点应力/Mpa']
        return stress1-stress2

    fdm=deepcopy(fdm)
    fdm.vn.append('θ/rad')
    fdm.vn.append('kx+μθ')
    fdm.vn.append('起点应力/MPa')
    fdm.vn.append('平均应力/Mpa')
    fdm.vn.append('终点应力/Mpa')
    fdm.vn.append('伸长量/mm')
    number=len(fdm)#分段的个数
    n_expected=round(number/2.0+0.01)#预计的不动点所处的分段编号
    x=0.5*fdm.units[n_expected-1].data['孔道长度x/m']#默认在中点

    iter_counter1=0
    while True:
        iter_counter1+=1
        #检查n_expected的合理性
        assert 0<=n_expected<=len(fdm),'迭代失败。迭代算法预计不动点出现段超出了合理值'
        print(n_expected)
        assert iter_counter1<=20,'迭代失败。d达到最大循环次数。'
        iter_counter2=0
        while True:
            iter_counter2+=1
            delta=calc_stree2(x)
            if abs(delta)<0.1:
                break
            step_size=fdm.units[n_expected-1].data['孔道长度x/m']*0.01
            x2=x+step_size
            delta2=calc_stree2(x2)
            k=(delta2-delta)/(x2-x)#变化斜率
            x=x-delta/k#更新x
            if iter_counter2>20:
                raise Exception("最大迭代次数")

        #检查x的合理性
        if x>fdm.units[n_expected-1].data['孔道长度x/m']:
            n_expected+=1#不动点在下一段
            x=0.5*fdm.units[n_expected-1].data['孔道长度x/m']#默认在中点
        elif x<0:
            n_expected-=1#不动点在上一段
            x = 0.5 * fdm.units[n_expected - 1].data['孔道长度x/m']  # 默认在中点
        else:#合理 退出循环
            break
    print(x)
    print(n_expected)


def test1():
    data = [[1, 7.832, 0], [2, 0.786, 4.5], [3, 15.264, 0], [4, 0.786, 4.5], [5, 7.832, 0]]
    fdm = FlatDataModel.load_from_list(['编号', '孔道长度x/m', 'θ/°'], data)
    print(计算钢束伸长量1(fdm))

if __name__ == '__main__':
    data = [[1, 8.778, 0], [2, 1.495, 8.56],[3, 0.863, 0],[4, 1.858, 10.65],[5, 4.746, 0],[6, 1.858, 10.65],[7, 0.736, 0],[8, 1.748, 10.01],[9, 6.965, 0],[10, 1.351, 7.74],[11, 1.55, 0],]
    fdm = FlatDataModel.load_from_list(['编号', '孔道长度x/m', 'θ/°'], data)
    print(计算钢束伸长量1(fdm))
