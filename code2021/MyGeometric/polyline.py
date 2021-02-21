from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.basegeometric import BaseGeometric
from code2021.MyGeometric.linesegment import LineSegment
from typing import List

from vector3d import Vector3D


class PolyLine:
    def __init__(self,segs):
        self.segs=[]#type:List[BaseGeometric]
        self._length=None #type:float
        for i,seg in enumerate(segs):
            assert isinstance(seg,BaseGeometric),"类型错误"
            if i==0:
                self.segs.append(seg)
            else:
                if self.segs[i-1].end_point != seg.start_point:
                    raise Exception("首尾不能连接\n%s\n\%s"
                                    %(self.segs[i-1].__str__(),seg.__str__()))
                self.segs.append(seg)

    def draw_in_axes(self,axes=None):
        lst=[]
        for seg in self.segs:
            t,axes=seg.draw_in_axes(axes)
            lst.append(t)
        return lst,axes

    def __iter__(self):
        return self.segs.__iter__()

    @property
    def length(self):
        if self._length is None:#没有计算就计算
            t=0.0
            for seg in self:
                t+=seg.length
            self._length=t
        return  self._length

    def __contains__(self, item):
        assert isinstance(item,Vector3D),"类型错误"
        for i,seg in enumerate(self.segs):
            t= item in seg
            if t is True:
                return True
        return False

    def calc_nearest_point(self, target: Vector3D, tol=1e-5):
        """
        算法：
        如果发现target在某个seg上 好办
        如果不在，将最近点到target的距离排序 取最低值
        @param target:
        @param tol:
        @return: 最近点，该点的长度坐标,target是否在直线上
        """
        def script1(i):#计算第1到第i个的长度和
            t=0.0
            for id in range(i):
                t+=self.segs[id].length
            return t
        assert isinstance(target, Vector3D), "类型错误"
        hangs=[]#存储 每个seg的最近点,编号i,到target距离,le
        target_id=None
        potential=None
        flag=False
        for i,seg in enumerate(self.segs):
            t,le,on=seg.calc_nearest_point(target,tol)
            if on is True:#如果在改个seg上 直接结束了
                target_id=i
                potential=t
                final_on=True
                flag=True
                break
            else:
                #加入hangs 最后进行比较
                hangs.append((t,i,abs(target-t),le))
        if target_id is None:#没有发现在seg上
            #对hangs排序 取最近的
            hangs.sort(key=lambda x:x[2])
            target_id=hangs[0][1]
            potential=hangs[0][0]
            final_on=False
        #计算长度坐标
        t=script1(target_id)
        if flag:
            t=t+le#没有加入到hangs 直接使用le
        else:
            t=t+hangs[0][3]
        return potential,t,final_on


    def __eq__(self, other):
        if id(self)==id(other):
            return True
        if not isinstance(other,PolyLine):
            return False
        if len(self.segs)!=len(other.segs):
            return False
        for seg1,seg2 in zip(self,other):
            if seg1!=seg2:
                return False
        return True

    @staticmethod
    def make1(points)->'PolyLine':
        """从一堆点中生成多段线"""
        lst=[]
        for i in range(len(points)-1):
            p1,p2=points[i],points[i+1]
            lst.append(LineSegment(p1,p2))
        pl=PolyLine(lst)
        return pl