from typing import List, Tuple

from excel.excel import FlatDataModel
import re

from mybaseclasses.mylogger import MyLogger

loger = MyLogger('creec')
loger.setLevel('debug')
loger.hide_name=True
loger.hide_level=True

spans_txt='11×32+(44+72+44)连续梁+55×32+53×32+1×24+33×32+3×24+(32+56+32)连续梁+10×32+2×24+1×29+(44+72+44)连续梁+1×32+20×32+2×24+5×32'
bridges_txt="""
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
连续梁		44.75	0.1	0	3.6	3.6		
连续梁		72	0	0	3.6	3.6		
连续梁		44.75	0	0.1	3.6	3.6		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.07	0.07	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
连续梁		32.75	0.1	0	3.8	3.8		
连续梁		56	0	0	3.8	3.8		
连续梁		32.75	0	0.1	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		29.6	0.05	0.05	3.8	3.8		
连续梁		44.75	0.1	0	3.6	3.6		
连续梁		72	0	0	3.6	3.6		
连续梁		44.75	0	0.1	3.6	3.6		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		24.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		
简支梁		32.6	0.05	0.05	3.8	3.8		

"""
def get_spans_list(spans_strign:str)->List[Tuple]:
    import re
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
    for i in all_brgs:
        if i[2] == '简支梁':  # 简支
            thistxt = i[0]  # 获取字符串
            ls = re.findall('\d+', thistxt)
            nb = int(ls[0])
            thisspan = int(ls[1])  # 数量和跨径
            for i1 in range(nb):
                spans.append(('简支梁', thisspan, '',))  # 按跨径类型 跨径 补充信息 添加
        elif i[2] == '连续梁':  # 简支
            thistxt = i[0]  # 获取字符串
            ts = [float(x) for x in thistxt.split('+')]  # 按加号分开
            spans.append(('连续梁', ts[0], 'left',))  # 左边跨
            for i1 in ts[1:-1]:  # 中跨
                spans.append(('连续梁', i1, 'mid',))
            spans.append(('连续梁', ts[-1], 'right',))  # 右边跨
        else:
            raise Exception("未知参数")
    return spans


def script_analyze(spans_txt,brdges_txt)->FlatDataModel:
    """
    检查 普桥 中梁列表是否正确 以孔跨布置为依据
    1.比较梁列表的孔跨数是否正确
    2.检查简支梁的梁长是否正确 =孔跨+0.6
    3.检查简支梁梁缝是否正确 =0.05
    4.检查连续梁梁长是否正确 ，边跨梁长=孔跨+0.75
    5.检查连续梁梁缝是否正确 ，边跨有一端的梁缝=0.1

    @param spans_txt:
    @param brdges_txt:
    @return:出错的梁列表
    """
    fdm_error_bridge = FlatDataModel()#搜集错误的梁
    fdm_error_bridge.vn=['编号','梁类型','梁长','左侧梁缝','右侧梁缝','左线距左边缘','右线距右边缘']
    #获取跨径 桥梁信息
    spans=get_spans_list(spans_txt)

    bridges=FlatDataModel.load_from_string(brdges_txt,
                                   vn_syle=['梁类型','梁长','左侧梁缝','右侧梁缝','左线距左边缘','右线距右边缘'])
    for i,u in enumerate(bridges):
        u.data['编号']=i+1 #1-based
    bridges.vn.insert(0,'编号')
    #开始比对
    counter_error=0#错误计数
    if len(spans)!=len(bridges):
        counter_error+=1
        raise Exception("孔跨数不一致")
    #开始纤细比对
    for bianhao,(aspan,abridge,) in enumerate(zip(spans,bridges)):
        bianhao+=1#改为1-based
        #比较类型
        if aspan[0]!=abridge['梁类型']:
            counter_error += 1
            loger.error('_'*40)
            loger.error('第%d孔跨类型不一致'%bianhao)
            loger.error('aspan:\n%s\nabridge:\n%s'%(aspan.__str__(),abridge.data.__str__()))
            loger.error('_'*40)
            fdm_error_bridge.append_unit(abridge)
            # raise Exception("第%d孔跨类型不一致"%bianhao)

        #比较长度
        if aspan[0]=='简支梁':
            if aspan[1]+0.6!=abridge['梁长']:
                counter_error += 1
                loger.error('_' * 40)
                loger.error('第%d孔跨梁长不一致,简支梁' % bianhao)
                loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                loger.error('_' * 40)
                fdm_error_bridge.append_unit(abridge)
            if not (abridge['左侧梁缝'] == 0.05 and abridge['右侧梁缝'] == 0.05):
                counter_error += 1
                loger.error('_' * 40)
                loger.error('第%d孔跨梁缝不一致' % bianhao)
                loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                loger.error('_' * 40)
                fdm_error_bridge.append_unit(abridge)
        elif aspan[0]=='连续梁':
            if aspan[2] =='left':#边跨
                if not(aspan[1]+0.75==abridge['梁长']):
                    counter_error += 1
                    loger.error('_' * 40)
                    loger.error('第%d孔跨梁长不一致,连续梁 边跨' % bianhao)
                    loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                    loger.error('_' * 40)
                    fdm_error_bridge.append_unit(abridge)
                if not(abridge['左侧梁缝'] == 0.1 and abridge['右侧梁缝'] == 0.00):
                    counter_error += 1
                    loger.error('_' * 40)
                    loger.error('第%d孔跨梁缝不一致,连续梁 边跨' % bianhao)
                    loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                    loger.error('_' * 40)
                    fdm_error_bridge.append_unit(abridge)

            elif aspan[2] =='right':#边跨
                if not (aspan[1] + 0.75 == abridge['梁长']):
                    counter_error += 1
                    loger.error('_' * 40)
                    loger.error('第%d孔跨梁长不一致,连续梁 边跨' % bianhao)
                    loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                    loger.error('_' * 40)
                    fdm_error_bridge.append_unit(abridge)
                if not (abridge['左侧梁缝'] == 0.0 and abridge['右侧梁缝'] == 0.1):
                    counter_error += 1
                    loger.error('_' * 40)
                    loger.error('第%d孔跨梁缝不一致,连续梁 边跨' % bianhao)
                    loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                    loger.error('_' * 40)
                    fdm_error_bridge.append_unit(abridge)

            else:
                if not(aspan[1] == abridge['梁长']):
                    counter_error += 1
                    loger.error('_' * 40)
                    loger.error('第%d孔跨梁长不一致,连续梁 中跨' % bianhao)
                    loger.error('aspan:\n%s\nabridge:\n%s' % (aspan.__str__(), abridge.data.__str__()))
                    loger.error('_' * 40)
                    fdm_error_bridge.append_unit(abridge)

    loger.info('总结：共%d个错误'%counter_error)
    return fdm_error_bridge

if __name__ == '__main__':
    fdm_error_bridge=script_analyze(spans_txt,bridges_txt)
    assert len(fdm_error_bridge)==55,'程序出错了'#一个简单的testcase