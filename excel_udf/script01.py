"""
放一些xlwings 下 excel的udf函数
"""
import re
import unittest
import xlwings as xw
import numpy as np
import autocad.about_tz as tz
@xw.func
def get_mileage(label:str)->float:
    """
    #获取里程
    #从字符串中获取里程 类似于D1K892+123.345
    @param label: 字符串，也可以是数字
    @return:
    """

    if isinstance(label,(float,int)):
        return label#如果已经是数字了，直接返回这个数字
    assert isinstance(label,str),'参数必须为str'
    p1 = re.compile(r'K(\d+)\+(\d+\.?\d+)', re.S)
    rt = re.findall(p1, label)
    if len(rt)==0:
        raise Exception("错误的里程格式")
    rt=rt[0]
    return float(rt[0])*1000+float(rt[1])
    pass

@xw.func
def get_cp_fp(data):
    """
    取出摩擦桩桩号
    @param data: 矩阵 第一行是#桩号 第二行是摩擦桩或者柱桩
    @return:
    """
    b=np.array(data)
    lst = []
    for i in range(b.shape[1]):
        if b[1, i] == '摩擦桩':
            lst.append(b[0, i])
    print(lst)
    pt = "\d+"
    lst1 = []
    for i in lst:
        l = re.findall(pt, i)
        lst1.append(int(l[0]))
    # for row in data:
    #
    #     r+=row[1]
    return fold_numbers(lst1)

def fold_numbers(lst1)->str:
    """
    合并数字
    如1 2 3 5 7 合并为1~3、5、7
    @param lst1:
    @return:
    """
    pts = []
    i = 1
    lastnb = lst1[0]  # 上一个数
    head = lastnb
    while i < len(lst1):
        thisnb = lst1[i]
        if thisnb == lastnb + 1:  # 连续
            lastnb = thisnb
            i += 1
            continue
        else:  # 不连续
            if head == lastnb:  # 单个号码
                pts.append("%d" % head)
            else:  # 多个号吗
                pts.append("%d~%d" % (head, lastnb))
            lastnb = thisnb
            head = lastnb
            i += 1
            continue
    # 最后处理
    if head == lst1[-1]:
        pts.append("%d" % head)
    else:
        pts.append("%d~%d" % (head, lst1[-1]))
    return "、".join(pts)

def arange_inteval(L,itv)->str:
    """
    自动获取钢筋的调整间距
    算法介绍：根据经验，余数通过调整最两侧钢筋间距实现去除余数
    @param L: 总长
    @param itv: 间距
    @return:
    """
    def geshi(x):
        #处理输出格式
        if x%1<=1e-5:#整数
            return "%d"
        else:
            return "%.1f"#小数
    n1=L//itv#取整 向下
    Y=L%itv #取余
    if Y==0:
        return ("%d×"+geshi(itv))%(n1,itv)
    if Y>=0.5*itv:
        n1+=-1
        t=(itv+Y)/2.
        # return "%f+%d×%d+%f"%(t,n1,itv,t)
        if n1<=0:
            raise Exception("L太小")
        return (geshi(t) + "+%d×" + geshi(itv) + "+" + geshi(t)) % (t, n1, itv, t)
    else:
        n1+=-2#拿出两个
        t=(2*itv+Y)/2.
        # return "%.1f+%d×%d+%.1f"%(t,n1,itv,t)
        if n1<=0:
            raise Exception("L太小")
        return (geshi(t)+"+%d×"+geshi(itv)+"+"+geshi(t)) % (t, n1, itv, t)
    pass


@xw.func
def test1(fullname):
    return [1,1]

class TestCase(unittest.TestCase):
    def test_get_mileage(self):
        self.assertEqual(892*1000+123.345,get_mileage('D1K892+123.345'))
        self.assertEqual(892 * 1000 + 123.345, get_mileage('DK892+123.345'))
        self.assertEqual(892 * 1000 + 123., get_mileage('DK892+123.'))
        self.assertEqual(892 * 1000 + 123., get_mileage('DK892+123'))
        self.assertEqual(0 * 1000 + 123., get_mileage('DK000+123.'))
        self.assertEqual(85 * 1000 + 0., get_mileage('DK85+000.'))

    def test_arange_inteval(self):
        t=arange_inteval(708,15)
        self.assertEqual("16.5+45×15+16.5",t)
        t=arange_inteval(709,15)
        self.assertEqual("17+45×15+17",t)
        t=arange_inteval(714,15)
        self.assertEqual("12+46×15+12",t)
        t=arange_inteval(715,15)
        self.assertEqual("12.5+46×15+12.5",t)
        t = arange_inteval(45, 15)
        self.assertEqual("3×15", t)
if __name__ == '__main__':
    unittest.main()
