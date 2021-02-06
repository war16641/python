from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.basegeometric import BaseGeometric
from code2021.MyGeometric.linesegment import LineSegment
from typing import List

class PolyLine:
    def __init__(self,segs):
        self.segs=[]#type:List[BaseGeometric]
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