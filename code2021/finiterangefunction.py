from typing import List
from unittest import TestCase,main


class FiniteRangeFunction:
    """
    有限值域函数
    即：其函数值域为有限的、几个值的集合 其函数图像为多个水平线
    在这里 用pts描述这个函数
    pts的格式为：List[Tuple(object1,object2)、、、]
    其中要求object1实现了 ==  > < >= <=等比较运算，可以不为float
    """
    def __init__(self,pts):
        self.pts=pts #关键点列表 存储(X,Y)
        self.qidian=pts[0][0]
        self.zongdian=pts[-1][0]

    def get_value(self,x):
        assert x>=self.qidian,"x小于起点 %s"%x.__str__()
        for i in range(1,len(self.pts)):
            t=self.pts[i]
            if x<=t[0]:
                return t[1]
        raise Exception("x大于终点 %s"%x.__str__())


    def clearup(self):
        """清除多余的pt"""
        remove_ids=[]
        for i in range(2,len(self.pts)):
            cur=self.pts[i]
            bef=self.pts[i-1]
            #如果cur和bef一样则删除bef的点
            if cur[1]==bef[1]:
                remove_ids.append(i-1)
        if len(remove_ids)>0:
            for i in remove_ids[::-1]:
                self.pts.pop(i)

    def get_next_pt(self,x):
        """
        获取大于x的下一个关键点
        @param x:
        @return:
        """
        assert x>=self.qidian,"x小于起点 %s"%x.__str__()
        for i in range(1,len(self.pts)):
            t=self.pts[i]
            if x<t[0]:
                return t
        raise Exception("x大于终点 %s"%x.__str__())

    @staticmethod
    def fenglei(ffs:List['FiniteRangeFunction']):
        #首先验证有相同的起止点
        qd=ffs[0].qidian
        zd=ffs[0].zongdian
        for i in range(1,len(ffs)):
            assert qd==ffs[i].qidian,"要求有相同起止点"
            assert zd == ffs[i].zongdian, "要求有相同起止点"

        #开始计算
        lastx=qd
        lst_y=[[x.get_value(lastx) for x in ffs]]#存储pt上的值
        lst_x=[lastx]
        while True:
            lst_pt=[x.get_next_pt(lastx) for x in ffs]
            curx=min([x[0] for x in lst_pt ])
            lst_y.append([x.get_value(curx) for x in ffs])
            lst_x.append(curx)

            #检查是否结束
            if curx==zd:
                break
            else:
                lastx=curx
        return lst_x,lst_y

    def print(self):
        for i in self.pts:
            print(i[0].__str__(),i[1].__str__())

    def integrate(self,x1:float,x2:float,func=None)->float:
        """
        求积分
        要求func(object2)实现了 乘object1
        @param x1: 积分上下限
        @param x2:
        @param func:操作object2的函数 默认为自己
        @return:
        """
        assert x2<=self.zongdian,"积分上限不得超过终点"
        assert x2>x1,"积分上下限错误"
        if func is None:
            func=lambda x:x
        else:
            assert callable(func),"参数错误"
        cur_x = x1
        sumv = 0.0
        while 1:
            t = self.get_next_pt(cur_x)
            if t[0] <= x2:
                sumv +=  func(t[1])*(t[0] - cur_x)
            else:
                sumv +=  func(t[1]) *(t[0] - x2)
                break
            if t[0] == self.zongdian or abs(t[0]-x2)<1e-4:
                break
            cur_x = t[0]
        return sumv
class TestC(TestCase):
    def test1(self):
        pts = [(1, '一'),
               (2, '一'),
               (3, '三'),
               (4, '二'),
               (6, '三'),
               (7, '一'),
               ]

        ff = FiniteRangeFunction(pts)
        self.assertEqual('一',ff.get_value(1))
        self.assertEqual('一', ff.get_value(2))
        self.assertEqual('三', ff.get_value(3))
        self.assertEqual('二', ff.get_value(4))
        self.assertEqual('三', ff.get_value(5))
        self.assertEqual('三', ff.get_value(6))
        self.assertEqual('一', ff.get_value(7))


    def test2(self):
        pts = [(1, '一'),
               (2, '一'),
               (2.5, '三'),
               (3, '三'),
               (3.5, '二'),
               (4, '二'),
               (6, '三'),
               (6.5, '一'),
               (7, '一'),
               ]

        ff = FiniteRangeFunction(pts)
        self.assertEqual(9,len(ff.pts))
        ff.clearup()
        self.assertEqual(6, len(ff.pts))
        self.assertEqual('一',ff.get_value(1))
        self.assertEqual('一', ff.get_value(2))
        self.assertEqual('三', ff.get_value(3))
        self.assertEqual('二', ff.get_value(4))
        self.assertEqual('三', ff.get_value(5))
        self.assertEqual('三', ff.get_value(6))
        self.assertEqual('一', ff.get_value(7))
    pass

    def test3(self):
        pts = [[1, '一'],
               (2, '一'),
               (3, '三'),
               (4, '二'),
               (6, '三'),
               (7, '一'),
               ]

        ff = FiniteRangeFunction(pts)
        self.assertEqual(2,ff.get_next_pt(1)[0])
        self.assertEqual(3, ff.get_next_pt(2)[0])
        self.assertEqual(4, ff.get_next_pt(3)[0])
        self.assertEqual(6, ff.get_next_pt(4)[0])
        self.assertEqual(6, ff.get_next_pt(5)[0])
        self.assertEqual(7, ff.get_next_pt(6)[0])
        # self.assertEqual('一', ff.get_next_pt(7)[0])

    def test4(self):
        pts = [(1, '一'),
               (2, '一'),
               (3, '三'),
               (4, '二'),
               (6, '三'),
               (7, '一'),
               ]
        ff = FiniteRangeFunction(pts)

        pts = [(1, '香'),
               (3.5, '香'),
               (5.5, '桃'),
               (7, '橙'),
               ]

        ff1 = FiniteRangeFunction(pts)

        x, y = FiniteRangeFunction.fenglei([ff, ff1])
        self.assertEqual([1, 2, 3, 3.5, 4, 5.5, 6, 7],x)
        self.assertEqual([['一', '香'], ['一', '香'], ['三', '香'], ['二', '香'], ['二', '桃'], ['三', '桃'], ['三', '橙'], ['一', '橙']],
                         y)

    def test5(self):
        pts = [(1, 1),
               (2, 1),
               (3, 2),
               (4, 3),
               ]

        ff = FiniteRangeFunction(pts)
        self.assertAlmostEqual(4,ff.integrate(1.5,3.5),delta=0.001)
        self.assertAlmostEqual(5.5, ff.integrate(1.5, 4), delta=0.001)
        self.assertAlmostEqual(11, ff.integrate(1.5, 4,func=lambda x:2*x), delta=0.001)
if __name__ == '__main__':
    main()