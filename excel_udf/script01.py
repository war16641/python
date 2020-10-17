"""
放一些xlwings 下 excel的udf函数
"""
import re
import unittest
import xlwings as xw
import numpy as np

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
class TestCase(unittest.TestCase):
    def test_get_mileage(self):
        self.assertEqual(892*1000+123.345,get_mileage('D1K892+123.345'))
        self.assertEqual(892 * 1000 + 123.345, get_mileage('DK892+123.345'))
        self.assertEqual(892 * 1000 + 123., get_mileage('DK892+123.'))
        self.assertEqual(892 * 1000 + 123., get_mileage('DK892+123'))
        self.assertEqual(0 * 1000 + 123., get_mileage('DK000+123.'))
        self.assertEqual(85 * 1000 + 0., get_mileage('DK85+000.'))
if __name__ == '__main__':
    unittest.main()
