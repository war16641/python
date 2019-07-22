"""
计算土弹簧刚度
已知土层分层信息 计算一个桩在土体内的土弹簧 水平刚度
"""
import numpy as np
from GoodToolPython.mybaseclasses.tools import is_vector_like,format_vector
from GoodToolPython.excel.excel import DataUnit,FlatDataModel
class Level:
    """一层土"""
    def __init__(self,thickness,scale_factor,friction_angle=0):
        self.thickness=float(thickness)#type:float#土层厚度
        self.scale_factor=float(scale_factor)#type:float#土体的比例系数 可根据土体类别 液性指数查表得
        self.friction_angle=float(friction_angle)#type:float#土层摩擦角 默认为0 角度
class SoilInfo:
    """土体分层信息
    坐标系以土顶层标高为起点 向下为正"""
    def __init__(self):
        self.levels=[]#type:list[Level]

    @property
    def num(self):
        return len(self.levels)

    def judge_scale_factor(self,z):
        """
        通过深度判断土层 返回该图层的scale_factor
        :param z:
        :return:
        """
        s=0
        for i in range(self.num):
            s=s+self.levels[i].thickness
            if z<=s:
                return self.levels[i].scale_factor
        raise Exception("超过土层最大深度")

    def calc_springs(self,b1,pts)->FlatDataModel:
        """
        计算土弹簧
        :param b1: 桩的计算宽度 规范中有
        :param pts: 土弹簧点深度列表
        :return:
        """
        def script(dz):
            nonlocal last_stiff,last_z,b1,pts,fm,z
            scale_factor = self.judge_scale_factor(z)
            this_stiff = last_stiff + scale_factor * b1 * dz * (z - last_z)
            last_z = z
            last_stiff = this_stiff
            u=DataUnit(fm)
            u.data['深度']=z
            u.data['土弹簧刚度'] = this_stiff
            u.data['该点土层比例系数'] = scale_factor
            fm.units.append(u)
            # stiffs.append(this_stiff)
            pass
        assert is_vector_like(pts),'pts必须是向量'
        pts=format_vector(pts)
        assert isinstance(b1,(int,float))
        last_stiff=0.
        last_z=0.
        fm=FlatDataModel()
        fm.vn=['深度','土弹簧刚度','该点土层比例系数']
        for i,z in enumerate(pts):
            if i==0:#第一个点
                dz=(pts[1]-z)*0.5#认为第一个单元的长度是第1节点到第1节点与第2节点的中点的距离
                script(dz)
                continue
            if i==len(pts)-1:#最后一个点
                dz=(pts[i]-pts[i-1])*0.5#最后一个单元的长度是最后一个节点到最后一个中点的距离
                script(dz)
                continue

            dz=(pts[i+1]+pts[i])/2.0-(pts[i-1]+pts[i])/2.0#中间单元的长度认为是最近的两个中点的差值
            script(dz)

        return fm
if __name__ == '__main__':
    si=SoilInfo()
    si.levels.append(Level(thickness=29.15,scale_factor=5000))
    si.levels.append(Level(thickness=40,scale_factor=1e4))
    pts=np.linspace(2.3,42.3,41)
    # print(pts)
    t=si.calc_springs(b1=1.98,pts=pts)
    t.show_in_excel()
