from typing import List, Any
from nose.tools import assert_raises

from GoodToolPython.vector3d import Vector3D,Line3D
class Polylines2D:
    points_list: List[Vector3D]
    tol=1e-15#判断相等的误差
    def __init__(self,name:str=''):
        self.name=name#名称
        self.points_list=[]

    def append(self,pt:Vector3D)->None:
        assert isinstance(pt,Vector3D)
        if self.num_of_points>0:
            assert pt.x>self.points_list[-1].x,'要求x坐标严格递增'
        self.points_list.append(pt)

    @property
    def num_of_points(self):#点的个数
        return len(self.points_list)
    @property
    def num_of_lines(self):#线的个数
        return len(self.points_list)-1

    def get_slope(self,id_line=0)->(float,float):
        """
        返回斜率
        :param id_line:线编号
        :return: 斜率 正无穷时返回'inf'
        """
        assert self.num_of_lines>=id_line,'线的编号越界'
        p1=self.points_list[id_line]
        p2=self.points_list[id_line+1]
        if abs(p1.y-p2.y)<self.tol:
            slope='inf'#此时斜率为正无穷
        else:
            slope=(p1.y-p2.y)/(p1.x-p2.x)
        return slope

    def __getitem__(self, x:float)->float:
        """
        获取横坐标为x时，y的值
        :param x:
        :return:
        """
        assert isinstance(x,(int,float))
        if x<self.points_list[0].x:
            raise Exception("x小于最小x值，不在多段线段上")
        for id,pt in enumerate(self.points_list):
            if pt.x>=x:#找到了
                elo=Line3D.make_line_by_2_points(self.points_list[id-1],pt)
                return elo.get_point('x',x).y
        raise Exception("x大于最大x值，不在多段线上")

if __name__ == '__main__':
    pl=Polylines2D()
    pl.append(Vector3D())
    pl.append(Vector3D(1,1))
    assert_raises(Exception,pl.append,Vector3D(1,1))
    assert_raises(Exception, pl.append, Vector3D(0.5,0 ))
    assert 1.==pl[1]
    assert 0.5 == pl[0.5]
    assert_raises(Exception, pl.__getitem__, 1.1)
    assert_raises(Exception, pl.__getitem__, -1.1)

