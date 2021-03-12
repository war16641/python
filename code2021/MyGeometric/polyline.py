from enum import unique, Enum

from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.basegeometric import BaseGeometric
import code2021.MyGeometric.entitytool as ET
from code2021.MyGeometric.linesegment import LineSegment
from typing import List, Tuple

from code2021.MyGeometric.ray import Ray
from mybaseclasses.mylogger import MyLogger
from sympy import symbols
from vector3d import Vector3D, Line3D

logger=MyLogger('polyline1231')
logger.setLevel('debug')
logger.hide_level=True
logger.hide_name=True


@unique
class PointRegionRelation(Enum):  # 点与面域关系
    inside = 1 #内部
    out = 2 #外部
    on_border = 3 #边境

class PolyLine:
    def __init__(self,segs):
        self.segs=[]#type:List[BaseGeometric]
        self._length=None #type:float
        for i,seg in enumerate(segs):
            assert isinstance(seg,BaseGeometric) or isinstance(seg,PolyLine),"类型错误"
            if i!=0:#检查首尾
                assert self.segs[-1].end_point == seg.start_point,"首尾不能连接\n%s\n\%s"\
                                    %(self.segs[i-1].__str__(),seg.__str__())
            #添加到自身
            if isinstance(seg,PolyLine):
                for i1 in seg:
                    self.segs.append(i1.copy())
            else:
                self.segs.append(seg.copy())


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

    def mirror(self, elo: Line3D) -> 'PolyLine':
        """镜像"""
        assert isinstance(elo, Line3D), "类型错误"
        lst=[x.mirror(elo) for x in self]
        return PolyLine(lst)

    def reverse(self)->'PolyLine':
        lst=[x.reverse() for x in self]
        lst.reverse()
        return PolyLine(lst)

    def move(self,base_point:Vector3D,target_point:Vector3D)->'PolyLine':
        """平移 得到新的"""
        lst=[x.copy().move(base_point,target_point) for x in self]
        return PolyLine(lst)

    def rotate(self,base_point:Vector3D,angle:float)->'PolyLine':
        lst = [x.copy().rotate(base_point, angle) for x in self]
        return PolyLine(lst)

    @property
    def start_point(self):
        return self.segs[0].start_point

    @property
    def end_point(self):
        return self.segs[-1].end_point

    def offset(self,distance:float,direction='L')->'PolyLine':
        """
        偏移
        返回新的
        @param distance:
        @param direction:  L R
        @return:
        """
        lst=[]
        for seg in self:
            lst.append(seg.offset(distance,direction))
        #处理相邻两个seg的交点
        for i in range(len(lst)-1):
            seg1,seg2=lst[i],lst[i+1]
            if isinstance(seg1,LineSegment) and isinstance(seg2,LineSegment):
                pt=ET.Entitytool.intersection_point(seg1.line,seg2.line)
                #调整点
                if pt is None:#没有交点 即seg1 seg2共线 直接改变seg2起点=seg1终点
                    seg2.start_point=seg1.end_point.copy()
                else:
                    seg1.end_point=pt.copy()
                    seg2.start_point=pt.copy()
            elif isinstance(seg1,LineSegment) and isinstance(seg2,Arc):
                t=seg2.intersec_point_with_line_as_circle(seg1.line)
                if t is None:
                    raise Exception("直线与圆无交点")
                if len(t)==1:
                    pt=Vector3D(t[0][0],t[0][1])
                else:#有两个交点 近的那个点才是真的交点
                    pt1=Vector3D(t[0][0],t[0][1])
                    pt2 = Vector3D(t[1][0], t[1][1])
                    pt0=seg1.end_point#这里可能出差 这里以offset后的seg1的终点作为判断“近”的标准
                    dist1=abs(pt1-pt0)
                    dist2=abs(pt2-pt0)
                    if dist1<=dist2:
                        pt=pt1
                    else:
                        pt=pt2
                # 调整点
                seg1.end_point = pt.copy()
                seg2.start_point = pt.copy()
            elif isinstance(seg2,LineSegment) and isinstance(seg1,Arc):
                t=seg1.intersec_point_with_line_as_circle(seg2.line)
                if t is None:
                    raise Exception("直线与圆无交点")
                if len(t)==1:
                    pt=Vector3D(t[0][0],t[0][1])
                else:#有两个交点 近的那个点才是真的交点
                    pt1=Vector3D(t[0][0],t[0][1])
                    pt2 = Vector3D(t[1][0], t[1][1])
                    pt0=seg1.end_point#这里可能出差 这里以offset后的seg1的终点作为判断“近”的标准
                    dist1=abs(pt1-pt0)
                    dist2=abs(pt2-pt0)
                    if dist1<=dist2:
                        pt=pt1
                    else:
                        pt=pt2
                # 调整点
                seg1.end_point = pt.copy()
                seg2.start_point = pt.copy()
            else:
                raise Exception("未知的seg1 seg2 类型组合")
        return PolyLine(lst)


    def point_by_length_coord(self, length: float) -> Tuple['Vector3D',float]:
        """
        通过长度坐标获取线上的点
        @param length:长度坐标 只能在0到长度之间
        @return:点,该点处曲线的切向角
        """
        assert isinstance(length,(int,float)),"类型错误"
        assert 0<=length<=self.length,"参数值不在合理范围类%s"%length.__str__()
        #需要确定是在哪一个seg内
        dist=0.0
        for i,seg in enumerate(self):
            if length<=dist+seg.length:
                break
            else:
                dist+=seg.length
        return seg.point_by_length_coord(length-dist)

    def trim(self,pt:Vector3D,pt_direction:Vector3D)->'PolyLine':
        """
        裁切 类似于cad中trim
        @param pt: 裁断点
        @param pt_direction:指定要裁切部分 内部通过长度坐标计算 建议使用start 和end point指定 其他的可能引发意外
        @return:
        """
        assert isinstance(pt,Vector3D) and isinstance(pt_direction,Vector3D),"类型错误"
        #确定pt出现的seg
        target_id=-1
        target=None#包含pt的seg
        for i,seg in enumerate(self):
            if pt in seg:
                target=seg
                target_id=i
        assert target is not None,"pt不在线上"
        #确定trim的方向
        _, coord0, _ = self.calc_nearest_point(pt)#这一行与上段代码有重复计算 暂时没时间优化
        _,coord1,_=self.calc_nearest_point(pt_direction)
        if coord1<=coord0:#裁切小坐标侧
            lst=[x.copy() for x in self.segs[target_id:]]
             #修剪target
            lst[0]=lst[0].trim(pt,lst[0].start_point)
        else:
            lst=[x.copy() for x in self.segs[0:target_id+1]]
             #修剪target
            lst[-1]=lst[-1].trim(pt,lst[-1].end_point)
        return PolyLine(lst)



    def copy(self)->'PolyLine':
        return PolyLine([x.copy() for x in self])

    def line_integral_of_vector_function(self,P,Q,pt0,pt1,i1:int=None)->float:
        """
        计算第二类曲线积分
        @param P:
        @param Q:
        @param pt0:
        @param pt1:
        @param i1: 强制指定pt1所在seg的id 基于0
        @return:
        """
        flag0,i0=self.find_seg_index(pt0)

        if isinstance(i1,int):#强制指定i1
            i1=len(self.segs)-1
            flag1=True
        else:
            flag1, i1 = self.find_seg_index(pt1)
        assert flag0 and flag1,"pt0 pt1要求在线上"
        sp=pt0#每次积分的起点
        jf=0
        for i in range(i0,i1):
            seg=self.segs[i]
            this_jfz=seg.line_integral_of_vector_function(P,Q,sp,seg.end_point)
            logger.debug("第%d段积分=%f"%(i,this_jfz))
            jf+=this_jfz
            sp=seg.end_point.copy()
        seg=self.segs[i1]
        this_jfz=seg.line_integral_of_vector_function(P,Q,sp,pt1)
        jf+=this_jfz
        logger.debug("第%d段积分=%f" % (i1, this_jfz))
        return jf

    def find_seg_index(self,pt:Vector3D)->Tuple[bool,int]:
        """
        contain的加强版
        除了返回是否在线上，还回返回pt所在seg的编号
        @param pt:
        @return:
        """
        assert isinstance(pt,Vector3D),"类型错误"
        for i,seg in enumerate(self.segs):
            t= pt in seg
            if t is True:
                return True,i
        return False,-1

    def get_area(self):
        """
        求取面积
        运用第二类曲线积分算 使P=0,Q=x 格林公式
        @return:
        """
        #检查是否闭合
        # assert self.start_point==self.end_point,"多段线不闭合，无法计算面积"
        return self.line_integral_of_vector_function(P=-0.5*symbols('y'),Q=0.5*symbols('x'),
                                                     pt0=self.start_point,
                                                     pt1=self.end_point,
                                                     i1=len(self.segs)-1)


    def check_continuity(self):
        """检查连续性"""
        for i in range(len(self.segs)-1):
            if self.segs[i].end_point!=self.segs[i+1].start_point:
                return False
        return True

    def in_closed_area(self,pt:Vector3D)->PointRegionRelation:
        """
        判断点是否在多段线围城的内部
        通过射线法判断
        @param pt:
        @return:
        """
        def quchong(lst):#去重
            t=[]
            for i in lst:
                if i not in t:
                    t.append(i)
            return t
        assert isinstance(pt,Vector3D)
        assert self.start_point==self.end_point,'必须要求闭合多段线'
        if pt in self:#在线上
            return PointRegionRelation.on_border
        #从pt到startpoint的射线判断
        r1=Ray(base_pt=pt,direct=self.start_point-pt)
        lst=[]#存储交点
        for seg in self.segs:
            t=ET.Entitytool.intersection_point(seg,r1)
            if isinstance(t,Vector3D):
                lst.append(t)
            elif isinstance(t,list):
                lst.extend(t)
        #去重
        lst=quchong(lst)
        if len(lst) % 2==0:
            rt1=PointRegionRelation.out
        else:
            rt1 = PointRegionRelation.inside

        #从pt到0.9长度坐标的射线判断
        t, _ = self.point_by_length_coord(self.length *0.9)
        r1=Ray(base_pt=pt,direct=t-pt)
        lst=[]#存储交点
        for seg in self.segs:
            t=ET.Entitytool.intersection_point(seg,r1)
            if isinstance(t,Vector3D):
                lst.append(t)
            elif isinstance(t,list):
                lst.extend(t)
        # 去重
        lst = quchong(lst)
        if len(lst) % 2==0:
            rt2=PointRegionRelation.out
        else:
            rt2 = PointRegionRelation.inside

        #若rt1 和rt2一致 返回 否则引入第三个点
        if rt1==rt2:
            return rt1

        #从pt到
        t,_=self.point_by_length_coord(self.length/2.0)
        r1=Ray(base_pt=pt,direct=t-pt)
        lst=[]#存储交点
        for seg in self.segs:
            t=ET.Entitytool.intersection_point(seg,r1)
            if isinstance(t,Vector3D):
                lst.append(t)
            elif isinstance(t,list):
                lst.extend(t)
        # 去重
        lst = quchong(lst)
        if len(lst) % 2==0:
            rt3=PointRegionRelation.out
        else:
            rt3 = PointRegionRelation.inside
        rt=[rt1,rt2,rt3]
        #返回大多数结果
        if rt.count(PointRegionRelation.inside)==2:
            return PointRegionRelation.inside
        else:
            return PointRegionRelation.out