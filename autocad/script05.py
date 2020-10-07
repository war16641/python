"""
清楚带括号的标高中的括号，需先打开2018cad，打开绘制好的dwg
用于计算用地面积的标注需要使用对齐标注，并且放置在土地类别指定图层（dimaligned_layers）中
并且同一个桥的相邻标注保持连续（距离不得大于valve_dist）
不同桥的相邻标注距离必须大于line_dist
描述桥名的文字放在bridgename_layer图层中，并且必须严格符合“XXX桥 桥梁用地： 1.23 亩”
其位置（插入点，一般是最左端）必须位于这个桥的正中间附近。
脚本能正确执行需要：指定第一个对齐标注. 第一个对齐标注，一定是线路的第一个且方向不能错
"""
import unittest
from typing import List

from bridge.mymileage import MyMileage
from excel.excel import FlatDataModel, DataUnit, bisection_method
from myfile import is_number
from pyautocad import Autocad,APoint
import re
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D, Line3D
import math
logger=MyLogger()
logger.hide_level=True
logger.hide_name=True
logger.setLevel('info')


class SegLine:
    """
    对应cad里面的对齐标注
    """
    def __init__(self,p1,p2,measurement,la):
        self.p1=Vector3D(p1[0],p1[1],p1[2])
        self.p2=Vector3D(p2[0],p2[1],p2[2])
        self.measurement=measurement
        self.layer=la#图层 用于标识用地类别
        self.pp1=None
        self.pp2=None#新坐标系下的坐标 如果需要识别里程，才会使用到这两个变量

    def switch_dir(self):#逆向
        p3=self.p1
        self.p1=self.p2
        self.p2=p3

    def __str__(self):
        return "距离，起点，终点：%f,%s,%s"%(self.measurement,self.p1,self.p2)

def dist(p1,p2):#返回距离
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5



#识别桥名和面积
class BridgeName:#桥名
    """
    包括：桥名文本 桥名文本插入点位置  该桥对应的chain
    """
    def __init__(self,text):
        self.textstring=text.TextString
        self.inserrtionpoint=text.InsertionPoint#插入点
        self.bridgename="识别错误"
        self.bridgearea=0.0#默认为错误的信息
        self.chainbox=None #与之对应的chain 后续会识别
        #re 得到桥名和面积
        pt = "([\u4e00-\u9fa5\d]+桥).+?"  # 中文匹配的符号 （）.+？表示非贪婪匹配
        l = re.findall(pt, self.textstring)  # 匹配桥名
        if len(l)!=0:
            self.bridgename=l[0]
        pt = "(桥梁用地：\s*)(-?\d+\.?\d*e?-?\d*?)(\s*亩)"  # 中文匹配的符号
        l = re.findall(pt, self.textstring)  # 匹配桥后面的面积
        if len(l)!=0:
            l=l[0][1]#提取出面积
            l=float(l)
            self.bridgearea=l

    def __str__(self):
        return "%s(%f)"%(self.bridgename,self.bridgearea)

class ChainBox:
    """
    对应连续的对齐标注（segline）
    """
    def __init__(self,chain):
        self.chain=chain
        xs=[]
        ys=[]#所有的xy坐标
        for ln in chain:
            xs.append(ln.p1[0])
            xs.append(ln.p2[0])
            ys.append(ln.p1[1])
            ys.append(ln.p2[1])
        self.leftbot=(min(xs),min(ys),)
        self.righttop = (max(xs), max(ys),)#定出矩形框

    def isin(self,bri_name:BridgeName,xtol,ytol):
        if bri_name.inserrtionpoint[0]>self.leftbot[0]-xtol and \
            bri_name.inserrtionpoint[0] < self.righttop[0] + xtol and \
            bri_name.inserrtionpoint[1] > self.leftbot[1] - ytol and \
            bri_name.inserrtionpoint[1] < self.righttop[1] + ytol :
            return True
        else:
            return False

class MileageSamplingPoint:#里程线放样点
    def __init__(self,p,new_basic_vectors):
        self.p=Vector3D(p[0],p[1],p[2])
        #利用线路走向生成的基向量，得到新坐标。新坐标的x坐标基本代表该点的位置
        self.pp=self.p.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)

class MileageLabel:#里程标识 包含里程和cad中的坐标
    def __init__(self,p=None,pp=None):
        self.p=p
        self.pp=pp#新坐标系下坐标
        self.mileage=None#里程

def analyze_mileage_label(words):
    """
    分析里程标文本
    @param words:
    @return: 第一个代表该字符串能否作为里程标文本
                第二个代表式百米标 还是千米标。这里的千米标不仅仅是千米标还是那种断链处的整个标识
                第三个代表 里程数值
    """
    if len(words)==1:
        f,nb=is_number(words)
        if f is False:
            return False,None
        else:
            return True,'百米标',nb*100
    p1=re.compile(r'(.*K)(\d+)\+?(\d*\.?\d*)', re.S)
    rt = re.findall(p1, words)
    if len(rt)==0:
        return False,None
    else:
        rt=rt[0]
        if len(rt[2])==0:
            return True,'千米标',rt[0],float(rt[1])*1000 #后面两个是冠号和里程
        else:
            return True,'千米标',rt[0],float(rt[1])*1000+float(rt[2]) #后面两个是冠号和里程

dimaligned_layers_0=['nyh水田',
'nyh水浇地',
'nyh旱地',
'nyh果园',
'nyh茶园',
'nyh其他园地',
'nyh乔木林地',
'nyh灌木林地',
'nyh苗圃',
'nyh其他林地',
'nyh牧草地',
'nyh养殖水面',
'nyh集体建设用地',
'nyh国有商服用地',
'nyh国有工矿仓储用地',
'nyh国有住宅用地',
'nyh公共管理与服务用地',
'nyh未利用地',
'nyh铁路既有用地',
'nyh河流水面',
'nyh设施农用地',
'nyh自然保留地',
'nyh其他草地',
'nyh其他独立建设用地',
'nyh特殊用地',
'nyh有林地',
'nyh沟渠',
'nyh内陆滩涂',
                   'nyh水工建筑用地',
                   'nyh农村道路',
                   'nyh风景名胜设施用地',
]#对齐标注所在图层名 默认值
bridgename_layer_0='nyh桥名'#桥名图层 默认值

def read_occupied_area_from_cad(dimaligned_layers:List[str]=None,
                                bridgename_layer:str=None,
                                first_dim_id=0,
                                mileage_point_layer=None,
                                mileage_label_layer=None)->FlatDataModel:
    if dimaligned_layers is None:
        dimaligned_layers=dimaligned_layers_0#使用默认值
    if bridgename_layer is None:
        bridgename_layer=bridgename_layer_0#使用默认值
    lines = []  # 存储所有的标注
    acad = Autocad(create_if_not_exists=True)
    acad.prompt("Hello,Autocad from Python\n")
    logger.info(acad.doc.Name)
    for x in acad.iter_objects('Dim'):
        # if "DimAligned" in str(type(x)):
        if x.Layer in dimaligned_layers:
            # logger.debug(x.ExtLine1Point)
            # logger.debug(x.ExtLine2Point)
            # logger.debug(x.Measurement)
            lines.append(SegLine(x.ExtLine1Point, x.ExtLine2Point, x.Measurement, x.Layer))
            logger.debug(lines[-1])

    # 排序
    valve_dist = 1  # 阈值距离，如果超过这个距离意味着没有找到相连的下一个线段
    line_dist = 5  # 10#20#超过这个距离 被认为是另一条线 而不是断线
    lines1 = [x for x in lines]  # 备份全部线段 需要把第一个标注（通常是线路最左端）放在第一个位置 并且方向不能错

    # 选择第一条segline 至关重要 由用于选择，通常是最左边的 而且整个线路的走向是近乎于向右的
    logger.info('打印所有segl1ine')
    logger.info('-' * 40)
    for i, oj in enumerate(lines1):
        logger.info("%d:%s" % (i, oj))
    logger.info('-' * 40)
    if first_dim_id == 0:
        fi=0#使用cad中第一个dim
        logger.info("第一个segline（通常是最左边）的序号（基于0）:0")
    elif first_dim_id=='user' or first_dim_id=='USER':
        fi = input('请输入第一个segline（通常是最左边）的序号（基于0）：')
    else:
        raise Exception("first_dim_id:%s参数错误"%first_dim_id)
    thisline = lines1[int(fi)]
    lines1.remove(thisline)
    sortedlines = [thisline]  # 向后排序的线段
    chains = []  # 同一座桥的 排序好的 一系列lines组成一条chain

    has_reversed = False  # 判断是否整体逆向了

    while True:

        outcome = []
        for x in lines1:
            outcome.append((x, 1, dist(thisline.p2, x.p1),))
            outcome.append((x, 2, dist(thisline.p2, x.p2),))  # 1 ，2代表是p1还是p2
        outcome.sort(key=lambda x: x[2])  # 按距离排序
        best = outcome[0]

        if best[2] > valve_dist and best[2] < line_dist:  # 超过阈值距离，断了 并且又不是下一条线的距离
            raise Exception("线段断裂,在此附近：\n%s" % (thisline))
        else:
            if best[1] == 1:  # 是否需要逆向
                sortedlines.append(best[0])
            else:
                best[0].switch_dir()
                sortedlines.append(best[0])
            thisline = best[0]  # 移除best并设定新的thisline
            lines1.remove(thisline)
            if len(lines1) == 0:
                chains.append(sortedlines)
                break  # 结束
            if best[2] >= line_dist:
                chains.append(sortedlines[0:-1])
                sortedlines = [sortedlines[-1]]
                logger.debug("新桥的segline")

    # 求线路走向
    dirsum = Vector3D()
    for i in sortedlines:
        thisdir = i.p2 - i.p1
        dirsum += thisdir
    rotate_theta = Vector3D.calculate_angle_in_xoy(dirsum[0], dirsum[1])  # 线路走向夹角
    logger.info('线路走向大致为：%f°(%s)，逆时针为正' % (rotate_theta / 3.14159 * 180, dirsum))

    new_basic_vectors=(Vector3D(math.cos(rotate_theta),math.sin(rotate_theta),0),
                       Vector3D(-math.sin(rotate_theta),math.cos(rotate_theta),0),
                       Vector3D(0,0,1),)#新的基向量

    # 打印
    for i, c in enumerate(chains):
        logger.info("第%d条线：" % i)
        for x in c:
            logger.info("%f:%s->%s" % (x.measurement, x.p1, x.p2))
    logger.info("共%d条线。" % len(chains))


    #处理桥名
    bridgenames = []  # 存储桥名的列表
    for x in acad.iter_objects('text'):
        if x.layer == bridgename_layer:
            bridgenames.append(BridgeName(x))
            logger.debug(bridgenames[-1])
            logger.debug(x.TextString)

    #联系bridgename和chainbox
    chainboxs = []
    for c in chains:
        chainboxs.append(ChainBox(c))

    # 开始识别
    xtol = 5
    ytol = 20  # 误差范围 在这个误差内 可认为在矩形框内
    tchainboxs = [x for x in chainboxs]
    bridge_to_exclu = []  # 找不到chainbox的桥 将会被移除
    for bd in bridgenames:
        targetcbox = None
        for cbox in tchainboxs:
            if cbox.isin(bd, xtol, ytol):
                targetcbox = cbox
                break
        if targetcbox is not None:  # 找到对应
            logger.info("桥名(%s)找到对应chainbox。" % bd)
            bd.chainbox = targetcbox
            # 计算全长
            ts = [x.measurement for x in bd.chainbox.chain]
            bd.length = sum(ts)
            tchainboxs.remove(targetcbox)
        else:
            logger.warning("桥名(%s)未找到对应chainbox，将它从桥的组中移除。" % bd.bridgename)
            bridge_to_exclu.append(bd)
            # raise Exception("bridgename未找到对应chainbox")
    for i in bridge_to_exclu:
        bridgenames.remove(i)
    # 开始计算各类用地
    for bd in bridgenames:
        cbox = bd.chainbox
        fdm = FlatDataModel()
        fdm.vn = ['用地类别', '长度']
        for i in cbox.chain:  # 遍历segline
            u = DataUnit()
            u.data['用地类别'] = i.layer
            u.data['长度'] = i.measurement
            u.model = fdm
            fdm.units.append(u)
        # 统计
        o = fdm.flhz("用地类别", [["长度", lambda x: sum(x)]])
        bd.stat_info = o  # 保存统计后的信息
        bd.original_info = fdm
        # 根据统计结果生成面积
        for u in bd.stat_info:
            u.data['面积'] = u.data['长度'] / bd.length * bd.bridgearea
        bd.stat_info.vn.append('面积')

    # 输出结果
    fdm = FlatDataModel()
    # soil_types=['nyh旱地','nyh水田','nyh园地','nyh沙漠']#有待补充
    soil_types = dimaligned_layers  # 有待补充
    fdm.vn = ['桥梁', '图上全长', '面积', ]
    fdm.vn.extend(soil_types)
    for bd in bridgenames:
        u = DataUnit()
        u.model = fdm
        u.data['桥梁'] = bd.bridgename
        u.data['图上全长'] = bd.length
        u.data['面积'] = bd.bridgearea
        for tn in soil_types:
            u.data[tn] = 0  # 先默认0
        for iu in bd.stat_info:
            u.data[iu['用地类别']] = iu['面积']
        fdm.units.append(u)

    #处理线路放样点MileageSamplingPoint
    if mileage_point_layer is None:
        return fdm
    msps=[]#放样点的列表
    for obj in acad.iter_objects('point'):
        if obj.layer == mileage_point_layer:
            msps.append(MileageSamplingPoint(p=obj.Coordinates,new_basic_vectors=new_basic_vectors))
    msps.sort(key=lambda x:x.pp.x)
    for i in sortedlines:#给segline求新坐标系下的坐标
        i.pp1=i.p1.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
        i.pp2 = i.p2.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)

    #处理线路上的里程标识
    mls=[]
    dist_valve_for_label=1#判断是不是里程标识短横线的点的阈值
    for obj in acad.iter_objects('dbline'):#遍历直线
        if obj.layer == mileage_label_layer:
            #起点
            t0=Vector3D(obj.StartPoint[0],obj.StartPoint[1])
            t1=t0.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            ind, lb, ub = bisection_method(sorted_list=msps,
                                         goal=t1.x,
                                         func=lambda x: x.pp.x)#求最近的两个放样点
            tl1=Line3D.make_line_by_2_points(msps[lb].pp,msps[ub].pp)#最近的两个放样点生成直线
            dist1=t1.distance_to_line(tl1)
            if dist1<=dist_valve_for_label:#是里程标识
                mls.append(MileageLabel(p=t0,pp=t1))
                continue
            #终点 这个点在线路上的概率不大，但还是试一试
            t0 = Vector3D(obj.EndPoint[0], obj.EndPoint[1])
            t1 = t0.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            ind, lb, ub = bisection_method(sorted_list=msps,
                                           goal=t1.x,
                                           func=lambda x: x.pp.x)  # 求最近的两个放样点
            tl1 = Line3D.make_line_by_2_points(msps[lb].pp, msps[ub].pp)  # 最近的两个放样点生成直线
            dist1 = t1.distance_to_line(tl1)
            if dist1 <= dist_valve_for_label:  # 是里程标识
                mls.append(MileageLabel(p=t0, pp=t1))
    mls.sort(key=lambda x:x.pp.x)#将里程标识排好序
    #识别里程文本
    mms=[]
    for obj in acad.iter_objects('text'):#遍历直线
        if obj.layer == mileage_label_layer:
            r=analyze_mileage_label(obj.TextString)
            if r[0] is False:
                continue
            else:
                if r[1]=='百米标':
                    mm=MyMileage()
                    mm.number=r[2]#先把冠号空着
                    mm.p=Vector3D(obj.InsertionPoint[0],obj.InsertionPoint[1])
                    mm.pp=mm.p.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
                    mms.append(mm)
                elif r[1]=='千米标':
                    mm=MyMileage(guanhao=r[2],number=r[3])
                    mm.p = Vector3D(obj.InsertionPoint[0], obj.InsertionPoint[1])
                    mm.pp = mm.p.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
                    mms.append(mm)
                else:
                    raise Exception("未知错误")
    mms.sort(key=lambda x:x.pp.x)#排序 按新坐标

    pass
class MyTest(unittest.TestCase):
    def test1(self):
        fdm = read_occupied_area_from_cad(dimaligned_layers=None,
                                          bridgename_layer=None)
        self.assertAlmostEqual(309.6,fdm[0]['图上全长'],delta=0.5)
        self.assertAlmostEqual(9.79, fdm[0]['面积'], delta=0.5)
        self.assertEqual('枣子村2号大桥', fdm[1]['桥梁'])
        self.assertAlmostEqual(152.63, fdm[2]['图上全长'], delta=0.5)
        self.assertAlmostEqual(5.38, fdm[2]['面积'], delta=0.5)
if __name__ == '__main__':
    unittest.main()
    # fdm=read_occupied_area_from_cad(dimaligned_layers=None,
    #                                 bridgename_layer=None)
    # fdm.show_in_excel()