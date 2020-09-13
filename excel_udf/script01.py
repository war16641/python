"""
放一些xlwings 下 excel的udf函数
"""
import re
import unittest
import xlwings as xw

@xw.func
def get_mileage(label:str)->float:
    #获取里程
    #从字符串中获取里程 类似于D1K892+123.345
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
