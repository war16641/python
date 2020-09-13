"""
清楚带括号的标高中的括号，需先打开2018cad，打开绘制好的dwg
用于计算用地面积的标注需要使用对齐标注，并且放置在土地类别指定图层（dimaligned_layers）中
并且同一个桥的相邻标注保持连续（距离不得大于valve_dist）
不同桥的相邻标注距离必须大于line_dist
描述桥名的文字放在bridgename_layer图层中，并且必须严格符合“XXX桥 桥梁用地： 1.23 亩”
其位置（插入点，一般是最左端）必须位于这个桥的正中间附近。
脚本能正确执行需要：指定第一个对齐标注. 第一个对齐标注，一定是线路的第一个且方向不能错
"""
from excel.excel import FlatDataModel, DataUnit
from pyautocad import Autocad,APoint
import re
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D
import math
logger=MyLogger()
logger.hide_level=True
logger.hide_name=True
logger.setLevel('debug')
dimaligned_layers=['nyh果园','nyh旱地','nyh乔木林地','nyh自然保留地','nyh公共管理与服务用地','nyh城镇用地','nyh河流水面','nyh集体建设用地','nyh设施农用地','nyh水浇地']#对齐标注所在图层名
bridgename_layer='nyh桥名'#桥名图层

class SegLine:
    def __init__(self,p1,p2,measurement,la):
        self.p1=Vector3D(p1[0],p1[1],p1[2])
        self.p2=Vector3D(p2[0],p2[1],p2[2])
        self.measurement=measurement
        self.layer=la#图层 用于标识用地类别

    def switch_dir(self):#逆向
        p3=self.p1
        self.p1=self.p2
        self.p2=p3

    def __str__(self):
        return "距离，起点，终点：%f,%s,%s"%(self.measurement,self.p1,self.p2)
lines=[]#存储所有的标注
acad=Autocad(create_if_not_exists=True)
acad.prompt("Hello,Autocad from Python\n")
logger.info (acad.doc.Name)
for x in acad.iter_objects('Dim'):
    # if "DimAligned" in str(type(x)):
    if x.Layer in dimaligned_layers:
        # logger.debug(x.ExtLine1Point)
        # logger.debug(x.ExtLine2Point)
        # logger.debug(x.Measurement)
        lines.append(SegLine(x.ExtLine1Point,x.ExtLine2Point,x.Measurement,x.Layer))
        logger.debug(lines[-1])

#排序
valve_dist=1#阈值距离，如果超过这个距离意味着没有找到相连的下一个线段
line_dist=20#超过这个距离 被认为是另一条线 而不是断线
lines1=[x for x in lines] #备份全部线段 需要把第一个标注（通常是线路最左端）放在第一个位置 并且方向不能错

#选择第一条segline 至关重要 由用于选择，通常是最左边的 而且整个线路的走向是近乎于向右的
logger.info('打印所有segl1ine')
logger.info('-'*40)
for i,oj in enumerate(lines1):
    logger.info("%d:%s"%(i,oj))
logger.info('-'*40)
fi=input('请输入第一个segline（通常是最左边）的序号（基于0）：')
thisline=lines1[int(fi)]
lines1.remove(thisline)
sortedlines=[thisline]#向后排序的线段
chains=[]#同一座桥的 排序好的 一系列lines组成一条chain

def dist(p1,p2):#返回距离
    return ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2)**0.5

has_reversed=False#判断是否整体逆向了

while True:

    outcome = []
    for x in lines1:
        outcome.append((x, 1, dist(thisline.p2, x.p1),))
        outcome.append((x, 2, dist(thisline.p2, x.p2),))  # 1 ，2代表是p1还是p2
    outcome.sort(key=lambda x: x[2])  # 按距离排序
    best = outcome[0]

    if best[2] > valve_dist and best[2]<line_dist:#超过阈值距离，断了 并且又不是下一条线的距离
        raise Exception("线段断裂,在此附近：\n%s"%(thisline))
    else:
        if best[1] == 1:  # 是否需要逆向
            sortedlines.append(best[0])
        else:
            best[0].switch_dir()
            sortedlines.append(best[0])
        thisline = best[0]  # 移除best并设定新的thisline
        lines1.remove(thisline)
        if len(lines1)==0:
            chains.append(sortedlines)
            break#结束
        if best[2]>=line_dist:
            chains.append(sortedlines[0:-1])
            sortedlines=[sortedlines[-1]]
            logger.debug("新桥的segline")

#求线路走向
dirsum=Vector3D()
for i in sortedlines:
    thisdir=i.p2-i.p1
    dirsum+=thisdir
rotate_theta=Vector3D.calculate_angle_in_xoy(dirsum[0],dirsum[1])#线路走向夹角
logger.info('线路走向大致为：%f°(%s)，逆时针为正'%(rotate_theta/3.14159*180,dirsum))

###这段建议删除#################
# new_basic_vectors=(Vector3D(math.cos(rotate_theta),math.sin(rotate_theta),0),
#                    Vector3D(-math.sin(rotate_theta),math.cos(rotate_theta),0),
#                    Vector3D(0,0,1),)#新的基向量
# for i in sortedlines:
#     i.new_p1=i.p1.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)#在新的基向量下的坐标 用于排序
# #按照new_p1排序
# sortedlines.sort(key=lambda x:x.new_p1[0])
###这段建议删除jiesu#################

#打印
for i,c in enumerate(chains):
    logger.info("第%d条线："%i)
    for x in c:
        logger.info("%f:%s->%s"%(x.measurement,x.p1,x.p2))
logger.info("共%d条线。"%len(chains))

#识别桥名和面积
class BridgeName:#桥名
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
bridgenames=[]#存储桥名的列表
for x in acad.iter_objects('text'):
    if x.layer==bridgename_layer:
        bridgenames.append(BridgeName(x))
        logger.debug(bridgenames[-1])
        logger.debug(x.TextString)

#将chain与bridge对应
#算法：通过bridgename的插入点在chain的坐标矩形框内
class ChainBox:
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
chainboxs=[]
for c in chains:
    chainboxs.append(ChainBox(c))

#开始识别
xtol=5
ytol=20#误差范围 在这个误差内 可认为在矩形框内
tchainboxs=[x for x in chainboxs]
bridge_to_exclu=[]#找不到chainbox的桥 将会被移除
for bd in bridgenames:
    targetcbox=None
    for cbox in tchainboxs:
        if cbox.isin(bd,xtol,ytol):
            targetcbox=cbox
            break
    if targetcbox is not None:#找到对应
        bd.chainbox=targetcbox
        #计算全长
        ts=[x.measurement for x in bd.chainbox.chain]
        bd.length=sum(ts)
        tchainboxs.remove(targetcbox)
    else:
        logger.warning("桥名(%s)未找到对应chainbox，将它从桥的组中移除。"%bd.bridgename)
        bridge_to_exclu.append(bd)
        # raise Exception("bridgename未找到对应chainbox")
for i in bridge_to_exclu:
    bridgenames.remove(i)
#开始计算各类用地
for bd in bridgenames:
    cbox=bd.chainbox
    fdm=FlatDataModel()
    fdm.vn=['用地类别','长度']
    for i in cbox.chain:#遍历segline
        u=DataUnit()
        u.data['用地类别']=i.layer
        u.data['长度']=i.measurement
        u.model=fdm
        fdm.units.append(u)
    #统计
    o = fdm.flhz("用地类别", [["长度", lambda x: sum(x)]])
    bd.stat_info=o #保存统计后的信息
    bd.original_info=fdm
    #根据统计结果生成面积
    for u in bd.stat_info:
        u.data['面积']=u.data['长度']/bd.length*bd.bridgearea
    bd.stat_info.vn.append('面积')

#输出结果
fdm=FlatDataModel()
# soil_types=['nyh旱地','nyh水田','nyh园地','nyh沙漠']#有待补充
soil_types=dimaligned_layers#有待补充
fdm.vn=['桥梁','全长','面积',]
fdm.vn.extend(soil_types)
for bd in bridgenames:
    u=DataUnit()
    u.model=fdm
    u.data['桥梁']=bd.bridgename
    u.data['全长']=bd.length
    u.data['面积']=bd.bridgearea
    for tn in soil_types:
        u.data[tn]=0#先默认0
    for iu in bd.stat_info:
        u.data[iu['用地类别']]=iu['面积']
    fdm.units.append(u)
fdm.show_in_excel()


#与统计前的表联合
# fdm1=FlatDataModel.load_from_excel_file(r"C:\Users\niyinhao\Desktop\成渝中线 比较方案  用地统计.xlsx",
#                                        sheetname="Sheet2")
# fdm1.add_variables_from_other_model(fdm,'桥梁')
# fdm1.show_in_excel()