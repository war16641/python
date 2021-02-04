from math import pi
import matplotlib.patches as mpatches

from code2021.MyGeometric.basegeometric import BaseGeometric
from vector3d import Vector3D,get_trans_func_polar
import matplotlib.pyplot as plt
from code2021.MyGeometric.angletool import AngleTool
class Arc(BaseGeometric):

    def __init__(self,center:Vector3D,radius,angle1:float,da):
        """

        @param center:
        @param radius:
        @param angle1:
        @param da: 为正时 逆时针转 不能大于2pi
        """
        assert isinstance(center,Vector3D),"类型错误"
        assert abs(da)<=1e-6+2*pi,"da绝对值必须在2pi内"
        self._center=center #type:Vector3D
        self._angle1=angle1
        self._da=da
        self._angle2=self._angle1+self._da
        self._radius=radius
        self._tf,self._tfi=None,None


    @property
    def radius(self):
        return self._radius

    @property
    def center(self):
        return self._center

    @property
    def da(self):
        return self._da

    @property
    def length(self):
        return self._radius*abs(self._da)
    @property
    def tf(self):
        if self._tf is None:
            self._tf,self._tfi=get_trans_func_polar(self._center)
        return self._tf
    @property
    def tfi(self):
        if self._tf is None:
            self._tf, self._tfi = get_trans_func_polar(self._center)
        return self._tfi

    def draw_in_axes(self,axes=None):
        # ax.relim()
        # ax.autoscale_view()
        if axes is None:
            _, axes = plt.subplots()
        if self._da>0:
            arc = mpatches.Arc((self.center.x, self.center.y), self.radius*2, self.radius*2, 0,
                            AngleTool.toD(self._angle1), AngleTool.toD(self._angle2),
                               color='k')
        else:
            arc = mpatches.Arc((self.center.x, self.center.y), self.radius*2, self.radius*2, 0,
                            AngleTool.toD(self._angle2), AngleTool.toD(self._angle1),
                               color='k')
        axes.add_patch(arc)
        return arc,axes

    @property
    def start_point(self):
        return self.tfi(Vector3D(self._angle1,self.radius))
    @property
    def end_point(self):
        return self.tfi(Vector3D(self._angle2,self.radius))

    def __contains__(self, item):
        """
        没有完善
        尤其是涉及arc跨越2pi时
        @param item:
        @return:
        """
        assert isinstance(item,Vector3D),"类型错误"
        t=self.tf(item)
        #计算小的端点
        if self._da>0:
            mp=self._angle1
        else:
            mp=self._angle2
        #计算t点到mp点转过的角度 并放入0到2pi
        need=AngleTool.format(t.x-mp)
        #need与da比较
        if abs(self._da)<need+Vector3D.tol_for_eq:
            return False
        if abs(t.y-self.radius)<Vector3D.tol_for_eq:
            return True
        else:
            return False
        # if self._angle1-Vector3D.tol_for_eq<=t.x<=self._angle2+Vector3D.tol_for_eq \
        #     and abs(t.y-self.radius)<Vector3D.tol_for_eq:
        #     return True
        # return False