"""
里程
"""
import re
from typing import overload, Tuple

from excel.excel import FlatDataModel


class ErrorMileage(Exception):#mileage抛出的错误
    pass

class Mileage:

    @overload
    def __init__(self):
        pass

    @overload
    def __init__(self, string: str):
        pass

    def __init__(self, string: str = None):
        self.guanhao = ""
        self.number = 0.0
        self.duanlianbiao=None #type:FlatDataModel #断链表的每一行描述一个断链点 里程在两个断链点之间
        if string is None:
            return
        assert isinstance(string, str), "必须为str"
        self.guanhao, self.number = Mileage.get_guanhao_and_mileage(string)

    def __add__(self, other)->'Mileage':
        """
        移动里程
        @param other: 移动的长度
        @return:
        """
        assert isinstance(other,(int,float)),"必须为float"
        assert other>=0,"必须为正"
        if self.duanlianbiao is None:#如果self没有指定断链表 直接数值加减 并保留相同冠号
            rt=Mileage()
            rt.guanhao=self.guanhao
            rt.number=self.number+other
            return rt

        #如果指定了冠号
        # 首先查找当前里程位于两个断链点之间
        i=self.find_chain_in_duanlianbiao()

        if self.number + other <= self.duanlianbiao[i + 1].data["等号左里程数"]:
            #如果移动后还在这个区间内
            rt = Mileage()
            rt.guanhao = self.guanhao
            rt.number = self.number + other
            return rt
        else:#如果不在了
            # 加上的值 超过了当前这个区间 需要移动到下一个断链点
            # #先检查是否超出了断链表
            # if i==len(self.duanlianbiao)-1:
            #     raise ErrorMileage("相加后的里程超出了断链表：%s+%f"%(self,other))
            dist_to_self = 0.0  # qidian到self的距离 属于提前计算
            dist_to_self = self.duanlianbiao[i + 1].data["等号左里程数"] - self.number
            for j in range(i + 1, len(self.duanlianbiao) - 1):
                # 先计算这一段起点
                qidian = Mileage()
                qidian.guanhao = self.duanlianbiao[j].data["等号右里程冠号"]
                qidian.number = self.duanlianbiao[j].data["等号右里程数"]
                qidian.duanlianbiao = self.duanlianbiao
                # 计算这一段的长度
                lenth = self.duanlianbiao[j + 1].data["等号左里程数"] - self.duanlianbiao[j].data["等号右里程数"]
                chazi = other - dist_to_self  # 距离目标的距离
                if chazi <= lenth:  # 就是这一段
                    qidian.number += chazi
                    return qidian
                else:  # 这一段长度不满足 还得下移一段
                    # 计算qidian到self的距离 提前计算
                    dist_to_self += lenth
                pass
            raise ErrorMileage("相加后的里程超出了断链表：%s+%f" % (self, other))


    def __sub__(self, other)->float:
        """
        两个里程标相减
        @param other:
        @return:返回距离
        """
        assert isinstance(other,Mileage),"类型错误"
        if self.duanlianbiao is None and other.duanlianbiao is None:#均无断链表
            if self.guanhao!=other.guanhao:
                raise ErrorMileage("冠号不同不能相减")
            return self.number-other.number
        if self.duanlianbiao !=other.duanlianbiao:
            raise ErrorMileage("两者具有不同的断链表")
        #开始相减
        i=self.find_chain_in_duanlianbiao()
        j=other.find_chain_in_duanlianbiao()
        if i==j:
            return self.number-other.number
        #不同的冠号时
        #区分大小
        if i<j:
            xiao=self.copy()
            da=other.copy()
            sc=-1
        else:
            xiao=other.copy()
            da=self.copy()
            sc=1
            i,j=j,i#让i为小的
        #以xiao为基准 去慢慢靠近大
        i_cur=i
        dist=0.0
        while True:
            #计算i_cur到下一个断链点的距离
            t=xiao.duanlianbiao[i_cur+1].data['等号左里程数']-xiao.number
            dist+=t
            xiao.number=xiao.duanlianbiao[i_cur+1].data['等号右里程数']
            xiao.guanhao = xiao.duanlianbiao[i_cur + 1].data['等号右里程冠号']
            i_cur+=1
            if i_cur==j:
                break
        #计算da到自己左端点的距离
        dist1=da.number-da.duanlianbiao[j].data['等号右里程数']
        return sc*(dist1+dist)
    def copy(self)->'Mileage':
        """复制一个新的"""
        rt=Mileage()
        rt.guanhao=self.guanhao
        rt.number=self.number
        rt.duanlianbiao=self.duanlianbiao
        return rt

    def __str__(self):
        return "%s%f"%(self.guanhao,self.number)

    def find_chain_in_duanlianbiao(self)->int:
        """
        找到自己在断链中的位置
        @return: 返回i，表明自己属于断链表中的[i,i+1]的断链点之间
        """
        for i,u in enumerate(self.duanlianbiao):
            if u.data["等号右里程冠号"] != self.guanhao:
                continue
            if u.data["等号右里程数"]<=self.number<=self.duanlianbiao[i+1].data["等号左里程数"]:
                return i
        raise ErrorMileage("并未在断链表中找到这个里程：%s\n 断链表和里程不匹配"%self)
        pass

    @staticmethod
    def get_guanhao_and_mileage(string: str) -> Tuple[str, float]:
        """
        从文本中读取里程和冠号
        如：DZ1k100+123.1  DZ1k100
        @param string:
        @return:
        """
        p1 = re.compile(r'([\w]+[kK])(\d+)\+?(\d*\.?\d*)', re.S)
        rt = re.findall(p1, string)
        if len(rt) == 0:
            raise Exception("错误的里程格式:%s" % string)
        rt = rt[0]
        rt = list(rt)
        if len(rt[2]) == 0:  # 如果没有读到千米下的数值
            rt[2] = "0"
        return rt[0], float(rt[1]) * 1000 + float(rt[2]),

    def __gt__(self, other):
        assert isinstance(other,Mileage),"类型错误"
        if self.duanlianbiao is not None or other.duanlianbiao is not None :
            assert self.duanlianbiao==other.duanlianbiao,"断链表不一致"
        zid=self.find_chain_in_duanlianbiao()
        oid=other.find_chain_in_duanlianbiao()
        if zid>oid:
            return True
        elif zid<oid:
            return False
        else:#在同一个区间内
            return self.number>other.number

    def __lt__(self, other):
        assert isinstance(other,Mileage),"类型错误"
        if self.duanlianbiao is not None or other.duanlianbiao is not None :
            assert self.duanlianbiao==other.duanlianbiao,"断链表不一致"
        zid=self.find_chain_in_duanlianbiao()
        oid=other.find_chain_in_duanlianbiao()
        if zid>oid:
            return False
        elif zid<oid:
            return True
        else:#在同一个区间内
            return self.number<other.number

    def __eq__(self, other):
        assert isinstance(other,Mileage),"类型错误"
        if self.duanlianbiao is not None or other.duanlianbiao is not None :
            assert self.duanlianbiao==other.duanlianbiao,"断链表不一致"
        return self.guanhao==other.guanhao and self.number==other.number
        # zid=self.find_chain_in_duanlianbiao()
        # oid=other.find_chain_in_duanlianbiao()
        # return zid==oid and self.number==other.number

    def __ge__(self, other):
        if self==other:
            return True
        if self>other:
            return True
        return False

    def __le__(self, other):
        if self==other:
            return True
        if self<other:
            return True
        return False
if __name__ == '__main__':
    string="""ID	等号左里程冠号	等号左里程数	等号右里程冠号	等号右里程数	断链长度
0	DK	199500	DK	199500	0
1	DK	236600	D1K	236600	0
2	D1K	246000.3155	DK	248000	1999.6845
3	DK	286259.754	DK	286259.754	0
"""
    fdm=FlatDataModel.load_from_string(stringtxt=string,
                                       vn_syle='fromstring',
                                       separator=' ')
    fdm.show_in_excel()