import unittest
from typing import List, Tuple

from excel.excel import FlatDataModel, DataUnit
import re

from mybaseclasses.mylogger import MyLogger

loger = MyLogger('creec_adsfw')
loger.setLevel('debug')
loger.hide_name = True
loger.hide_level = True

spans_txt = '11×32+(44+72+44)连续梁+55×32+53×32+1×24+33×32+3×24+(32+56+32)连续梁+10×32+2×24+1×29+(44+72+44)连续梁+1×32+20×32+2×24+5×32'

def get_center_pier(spans_strign: str) -> float:
    """
    返回中心墩号 根据跨径布置
    算法：有连续梁时，返回主跨跨径最大的那一个连续梁所在墩号 如果出现两个及以上的连续梁有共同的最大跨径，就打印这些连续梁
    只有简支梁时：返回首先是跨径最大，然后是联数最大所在墩号，如果有两个及以上的简支梁布置最大且相同时，打印这些连续梁
    @param spans_strign: 跨径布置的字符串
    @return:
    """
    # spans_strign = '57×32+(36+64+36)连续梁+3×32+(32+48+32)连续梁+33×32+2×24+14×32+1×24+1×29+16×32+3×24+(64+120+64)连续梁+2×32+1×24+6×32+1×24+1×25+13×32+2×24+21×32+1×28+(32+48+32)连续梁+1×24+(40+64+40)连续梁+8×32+2×24+1×28+20×32+1×24+1×29+26×32+1×27+(40+64+40)连续梁+3×32+2×24+28×32+1×32+1×29+8×32+1×24+10×32+1×24+6×32+2×24+1×27+63×32+1×24+24×32+3×24+20×32+2×24+5×32+24×32+1×24+15×32'
    # 先获取连续梁信息
    regex_str = "[(](.*?)[)]连续梁"
    match_obj = re.finditer(regex_str, spans_strign)
    ls = re.findall(regex_str, spans_strign)
    continue_brgs = [(x, y.span(), '连续梁') for x, y in zip(ls, match_obj)]  # 字符串与出现位置成为元组
    # 在获取简支梁信息
    regex_str = "\d+×\d+"
    match_obj = re.finditer(regex_str, spans_strign)
    ls = re.findall(regex_str, spans_strign)
    simple_brgs = [(x, y.span(), '简支梁') for x, y in zip(ls, match_obj)]  # 字符串与出现位置成为元组
    # 合并
    all_brgs = [x for x in continue_brgs]
    all_brgs.extend(simple_brgs)
    all_brgs.sort(key=lambda x: x[1][0])
    # print(all_brgs)
    # 生成跨径列表
    spans = []
    span_fdm=FlatDataModel()
    span_fdm.vn=['类型','跨径列表','孔跨数','主跨跨径','前置孔跨序数']#孔跨序数是1-based
    spans_number=0#孔跨序数
    for i in all_brgs:
        if i[2] == '简支梁':  # 简支
            thistxt = i[0]  # 获取字符串
            ls = re.findall('\d+', thistxt)#要求简支梁格式是 数量×跨径
            nb = int(ls[0])
            thisspan = int(ls[1])  # 数量和跨径
            u=DataUnit()
            u.data['类型']='简支梁'
            u.data['跨径列表']=[thisspan]*nb
            u.data['孔跨数']=nb
            u.data['主跨跨径']=thisspan
            u.data['前置孔跨序数']=spans_number
            u.model=span_fdm
            span_fdm.units.append(u)
            spans_number+=nb
        elif i[2] == '连续梁':  #
            thistxt = i[0]  # 获取字符串
            ts = [float(x) for x in thistxt.split('+')]  # 按加号分开 要求连续梁格式为 跨径+跨径+跨径
            u=DataUnit()
            u.data['类型']='连续梁'
            u.data['跨径列表']=ts
            u.data['孔跨数']=len(ts)
            u.data['主跨跨径']=max(ts)
            u.data['前置孔跨序数']=spans_number
            u.model=span_fdm
            spans_number+=len(ts)
            span_fdm.units.append(u)
        else:
            raise Exception("未知参数")
    # span_fdm.show_in_excel()
    #首先查找是否有连续梁
    lianxu=span_fdm.find(lambda x:x.data['类型']=='连续梁',flag_find_all=True)
    if len(lianxu)!=0:#有连续梁
        if not isinstance(lianxu,list):
            lianxu=[lianxu]
        lianxu.sort(key=lambda x:x.data['主跨跨径'],reverse=True)
        mainspan=lianxu[0]#找到主跨
        max_span = mainspan.data['主跨跨径']
        lianxu=list(filter(lambda x:x.data['主跨跨径']==max_span and x.data['类型']=='连续梁',lianxu))

        assert len(lianxu)>0,'未知错误'
        if len(lianxu)>1:#出现其他同主跨跨径连续梁
            lianxu.sort(key=lambda x: x.data['前置孔跨序数'])  # 以第一个出现的为准
            loger.warning('-'*50)
            loger.warning('出现其他同主跨跨径连续梁，需用户自行判断，暂定为第一个出现的。\n打印所有主跨跨径最大的连续梁：')
            for i in lianxu:
                loger.warning(i.data)
            mainspan=lianxu[0]
            loger.warning('-' * 50)
        center_pier=mainspan.data['孔跨数']/2.0+mainspan.data['前置孔跨序数']
        loger.info('中心墩号%f'%center_pier)

        return center_pier
    else:#全是简支梁
        span_fdm.sort(key=['主跨跨径','孔跨数'],reverse=True)#以 主跨跨径 为第一判据 以孔跨数为第二判据
        mains=span_fdm.units[0]
        mainspan=span_fdm.units[0].data['主跨跨径']
        mainnumber=span_fdm.units[0].data['孔跨数']#获取这两个的最大
        maxspans=span_fdm.find(lambda x:x.data['主跨跨径']==mainspan and x.data['孔跨数']==mainnumber,flag_find_all=True)
        assert len(maxspans)>0,'未知错误'
        if len(maxspans)>1:
            maxspans.sort(key=lambda x:x.data['前置孔跨序数'])
            loger.warning('出现主跨跨径相同，联数相同的简支梁，需用户自行判断，暂定为第一个出现的。\n打印此类简支梁:')
            for i in maxspans:
                loger.warning(i.data)
            mains=maxspans[0]
            loger.warning('-' * 50)
        center_pier=mains.data['孔跨数']/2.0+mains.data['前置孔跨序数']
        loger.info('中心墩号%f' % center_pier)
        return center_pier




class TestCase(unittest.TestCase):
    def test_01(self):
        self.assertEqual(37, get_center_pier('74×32+1×24'))
        self.assertEqual(1.5, get_center_pier('(32+56+32)连续梁'))
        self.assertEqual(2, get_center_pier('1×24+2×32'))
        self.assertEqual(25.5, get_center_pier('6×32+18×66+(44+80+44)连续梁+15×32'))
        self.assertEqual(14, get_center_pier('28×32+1×24+14×32'))
        self.assertEqual(43, get_center_pier('12×32+1×24+20×32+2×24+1×40+1×64+1×40+3×32+(48+80+80+48)连续梁+5×32'))
        self.assertEqual(9, get_center_pier('18×32'))
        self.assertEqual(3, get_center_pier('6×32+1×24+2×32'))
        self.assertEqual(11.5, get_center_pier('2×24+19×32'))
        self.assertEqual(12.5, get_center_pier('11×32+(44+72+44)连续梁+55×32+53×32+1×24+33×32+3×24+(32+56+32)连续梁+10×32+2×24+1×29+(44+72+44)连续梁+1×32+20×32+2×24+5×32'))
        self.assertEqual(6.5, get_center_pier('1×24+11×32+2×24'))
        self.assertEqual(32.5, get_center_pier('2×24+29×32+(40+64+40)连续梁+3×24+(32+48+32)连续梁+1×32+2×24+10×32'))
        # self.assertEqual(58.5, get_center_pier('57×32+(36+64+36)连续梁+3×32+(32+48+32)连续梁+33×32+2×24+14×32+1×24+1×29+16×32+3×24+(64+120+64)连续梁+2×32+1×24+6×32+1×24+1×25+13×32+2×24+21×32+1×28+(32+48+32)连续梁+1×24+(40+64+40)连续梁+8×32+2×24+1×28+20×32+1×24+1×29+26×32+1×27+(40+64+40)连续梁+3×32+2×24+28×32+1×32+1×29+8×32+1×24+10×32+1×24+6×32+2×24+1×27+63×32+1×24+24×32+3×24+20×32+2×24+5×32+24×32+1×24+15×32'))
        self.assertEqual(89, get_center_pier('4×32+1×24+33×32+3×24+28×32+1×24+38×32'))
        self.assertEqual(166.5, get_center_pier('31×32+1×24+9×32+3×24+61×32+1×24+57×32+1×24+1×32+(40+56+40)连续梁+85×32+1×24+1×32+1×24+15×32+1×24+1×28+1×32+1×24+35×32+(40+56+40)连续梁+26×32+(32+48+32)连续梁+12×32+1×28+1×32+(32+48+32)连续梁+24×32'))
if __name__ == '__main__':
    unittest.main()

    pass
    # get_center_pier(spans_txt)