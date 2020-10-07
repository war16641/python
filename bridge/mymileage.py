import re
import unittest
from math import floor
from typing import overload


class MyMileage:
    @overload
    def __init__(self):
        pass

    @overload
    def __init__(self,guanhao:str,number:float):
        pass

    @overload
    def __init__(self,text:str):
        pass

    def __init__(self,
                 guanhao:str=None,
                 number:float=0,
                 text:str=None):
        self._guanhao=None
        self.number=0.0
        if guanhao is not None:#指定冠号和数值
            self.guanhao=guanhao
            self.number=number
        elif text is not None:#从字符串中载入
            words=text
            p1 = re.compile(r'(.*[kK])(\d+)\+?(\d*\.?\d*)', re.S)
            rt = re.findall(p1, words)
            if len(rt) == 0:
                raise Exception("非法里程标签：" % words)
            else:
                rt = rt[0]
                if len(rt[2]) == 0:
                    self.guanhao = rt[0]
                    self.number = float(rt[1]) * 1000
                else:
                    self.guanhao = rt[0]
                    self.number = float(rt[1]) * 1000 + float(rt[2])
        else:#什么也不指定 或者只指定数值
            self.number=number

    @property
    def guanhao(self):
        return self._guanhao
    @guanhao.setter
    def guanhao(self,v):
        if v[-1]  not in ('k','K'):
            raise Exception("非法冠号%s"%v)
        self._guanhao=v

    def __str__(self):
        if self.guanhao is None:
            return '暂无冠号K%d+%f'%(floor(self.number/1000),self.number%1000)
        else:
            return '%s%d+%f'%(self.guanhao,floor(self.number/1000),self.number%1000)

class TestCase(unittest.TestCase):
    def test_1(self):
        mm=MyMileage()
        mm = MyMileage(guanhao='dk',number=1.1)
        self.assertEqual('dk',mm.guanhao)
        self.assertEqual(1.1,mm.number)
        mm=MyMileage(text='d2k100+200.1')
        self.assertEqual('d2k',mm.guanhao)
        self.assertEqual(100*1000+200.1,mm.number)
if __name__ == '__main__':
    unittest.main()