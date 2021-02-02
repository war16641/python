import re
from typing import Tuple
from unittest import TestCase,main

from excel.excel import FlatDataModel


def get_number_of_span(txt:str)->int:
    """
    返回孔跨数量
    1×24+（6×32.7）连续梁+10×32+2×24+1×32+2×24+1×31+21×32
    @param txt:
    @return:
    """
    l = re.findall("\d*×?\d+\.?\d*", txt)
    rt=0
    if len(l)==0:
        raise Exception("没有发现孔跨 %s"%txt)
    for i in l:
        t=i.find('×')
        if t==-1:
            rt+=1
        else:
            rt+=int(i[0:t])
    return rt

def collect_girder_type(txt:str)->Tuple[dict,int]:
    pt0 = "[^\(（](\d+)×(\d+\.?\d*)" #简支梁
    pt1 = "[\(（](\d+\+\d*×?\d+\+\d+)[\)）]"#三孔连续梁
    pt2 = "[\(（](\d+×\d+\.?\d*)[\)）]"#几×几的连续梁
    pt3="(\d+)m?系杆拱"#系杆拱
    ct0=ct1=ct2=ct3=0

    kongkua="废"+txt

    jianzhi = re.findall(pt0, kongkua)
    lianxu = re.findall(pt1, kongkua)
    lianxu2 = re.findall(pt2, kongkua)
    xgg = re.findall(pt3, kongkua)
    if len(jianzhi)+len(lianxu)+len(lianxu2)+len(xgg)==0:
        raise Exception("什么跨也没有%s"%txt)

    dic={}
    #开始按类型识别
    for nb,lx in jianzhi:
        lx="简支"+lx
        if lx not in dic.keys():
            #没有这个跨度的
            dic[lx]=float(nb)
            ct0+=float(nb)
        else:#已经有这个类型了
            dic[lx] = float(nb)+dic[lx]
            ct0+=float(nb)

    for lx in lianxu:
        lx="连续"+lx
        t = re.findall("(\d+)×", lx)
        for t1 in t:
            ct1+=int(t1)-1
        if lx not in dic.keys():
            #没有这个跨度的
            dic[lx]=1
            ct1+=3
        else:#已经有这个类型了
            dic[lx] = 1+dic[lx]
            ct1+=3

    for lx in lianxu2:
        lx="连续"+lx
        #计算孔跨数
        t = re.findall("(\d+)×", lx)
        if len(t)==0:
            raise  Exception("位置错误")
        ct2+=float(t[0])
        if lx not in dic.keys():
            #没有这个跨度的
            dic[lx]=1
        else:#已经有这个类型了
            dic[lx] = 1+dic[lx]

    for lx in xgg:
        lx="其他类型"+lx
        #计算孔跨数
        lx=lx+"m系杆拱"
        ct3+=1
        if lx not in dic.keys():
            #没有这个跨度的
            dic[lx]=1
        else:#已经有这个类型了
            dic[lx] = 1+dic[lx]

    #交叉检查
    nbtotal=ct0+ct1+ct2+ct3
    nbtotal1=get_number_of_span(txt)
    if nbtotal!=nbtotal1:
        raise Exception("交叉检查失败 %d vs %d \n %s"%(nbtotal1,nbtotal,txt))

    return dic,nbtotal

class TestC(TestCase):
    def test1(self):
        target_hang = "2×32+1×27+19×32+(32+56+32)m单线连续梁1×24+1×29+12×32+(44+80+44)连续梁+(36+64+36)m连续梁+9×32+1×27+4×32+2×24+(68+128+68)m单线连续梁+1×24+1×32+2×24+1×32"
        self.assertEqual(69,get_number_of_span(target_hang))
        target_hang="15×32+1×31+2×24+1×32+(48+80+48)m连续梁+2×32+1×24+1×32+1×24+1×32+2×24+9×32+2×24+1×32+2×24+28×32+2×24+(40+56+40)m连续梁+20×32+1×24+12×32+1×24+2×32+(48+80+48)m连续梁+12×32+1×24+18×32+2×24+2×32+(40+56+40)m连续梁+36×32+(42+64+40)m连续梁+3×32+1×24+34×32+1×24+2×32+(60+2×100+60)m连续梁+14×32+(48+2×80+46)m连续梁+(40+56+40)m连续梁+14×32+2×24+10×32+2×24+1×27+144m系杆拱+5×32+2×24+(40+64+40)m连续梁+1×25+1×32+1×24+47×32+3×24+60×32+1×28+20×32+1×24+14×32+(48+88+48)m连续梁+6×32"
        self.assertEqual(457, get_number_of_span(target_hang))
        target_hang="7×32+1×24+6×32+3×24+6×32+1×24+62×32"
        self.assertEqual(86, get_number_of_span(target_hang))

    def test2(self):
        dic,s=collect_girder_type("1×24+（6×32.7）连续梁+10×32+2×24+1×32+2×24+1×31+21×32")
        dic1={'简支24':5,
              '简支32':32,
              '简支31':1,
              '连续6×32.7':1}
        self.assertEqual(dic1,dic)
        self.assertEqual(44, s)

    def test3(self):
        target_hang = "2×32+1×27+19×32+(32+56+32)m单线连续梁1×24+1×29+12×32+(44+80+44)连续梁+(36+64+36)m连续梁+9×32+1×27+4×32+2×24+(68+128+68)m单线连续梁+1×24+1×32+2×24+1×32"

        dic,s=collect_girder_type(target_hang)
        dic1={'简支32': 48.0, '简支27': 2.0, '简支24': 6.0, '简支29': 1.0, '连续32+56+32': 1, '连续44+80+44': 1, '连续36+64+36': 1, '连续68+128+68': 1}
        self.assertEqual(dic1,dic)
        self.assertEqual(69,s)
if __name__ == '__main__':
    main()