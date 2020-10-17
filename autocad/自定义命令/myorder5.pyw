"""
调整标志线的对象
标志线最多可以拥有两个单行文字
使用时，可以选择多个需要调整的对象
如果标志线附近发现多个文字（3个及以上） 取最近的两个
"""
from math import pi, cos, sin
from statistics import mean

from autocad.toapoint import to_Apoint
from numpy import std
from pyautocad import Autocad,APoint
from vector3d import Vector3D, Line3D


class BiaoZhi:
    def __init__(self):
        self.texts=[]
        self.geshixian=None
        self.zhishixian=None

    def __str__(self):
        if len(self.texts)==0:
            return "空"
        else:
            return self.texts[0].TextString
def clearnup_biaozhi():

    acad=Autocad(create_if_not_exists=True)
    slt=acad.get_selection(text="选择需要调整标志线的对象：按enter结束")
    acad.prompt("正在执行命令...\n")
    # acad.prompt("选择需要重新排列的对象：按enter结束\n")
    print (acad.doc.Name)

    text_objs=[]#所有文字
    line_objs=[]
    print('共选择%d个对象'%slt.Count)
    # valve_x = acad.doc.Utility.getreal('输入分组x距离：')
    # new_distance_x = acad.doc.Utility.getreal('输入新的组间x距离：')
    # acad.prompt("正在重新排列...\n")
    for i in range(slt.Count):
        myobj=acad.best_interface(slt[i])
        if 'acdbtext' in myobj.ObjectName.lower():#文字
            myobj.leftdown,myobj.rightup=myobj.GetBoundingBox()
            t=[(i1+i2)/2.0 for i1,i2 in zip(myobj.leftdown,myobj.rightup)]#文字的中心点
            myobj.centerpoint=Vector3D(t)
            myobj.leftdown = myobj.GetBoundingBox()[0]
            myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
            myobj.leftdown=Vector3D(myobj.leftdown[0:2])
            myobj.rightup = Vector3D(myobj.rightup[0:2])
            text_objs.append(myobj)
        elif 'acdbline' in myobj.ObjectName.lower():#直线
            if myobj.Length<0.1:
                continue#长度小于这个值的直线忽略
            myobj.myline=Line3D.make_line_by_2_points(Vector3D(myobj.startpoint[0:2]),Vector3D(myobj.endpoint[0:2]))
            myobj.rotation=Vector3D.calculate_angle_in_xoy(myobj.myline.direction[0],
                                                           myobj.myline.direction[1])#计算方向角
            #以自己的方向为新坐标系
            myobj.new_basic_vectors = (Vector3D(cos(myobj.rotation), sin(myobj.rotation), 0),
                                 Vector3D(-sin(myobj.rotation), cos(myobj.rotation), 0),
                                 Vector3D(0, 0, 1)
                                 )  # 以直线方向为新坐标系的基向量
            #计算自己的两个端点在这个坐标系下的坐标
            myobj.x1 = Vector3D(myobj.startpoint[0:2]).get_coordinates_under_cartesian_coordinates_system(myobj.new_basic_vectors)
            myobj.x2 = Vector3D(myobj.endpoint[0:2]).get_coordinates_under_cartesian_coordinates_system(
                myobj.new_basic_vectors)
            myobj.p1 = Vector3D(myobj.startpoint[0:2])
            myobj.p2 = Vector3D(myobj.endpoint[0:2])#保留原坐标下的坐标
            myobj.centerpoint=(myobj.p1+myobj.p2)/2.0#中心点 原坐标系
            line_objs.append(myobj)
        else:
            pass

    #获取文字方向
    #一般来说 文字方向都是一致的
    t=[x.rotation for x in text_objs]
    avg_rotation=mean(t)#平均文字
    std_rotation=std(t)
    # if std_rotation>3/180*pi:
    #     raise Exception("文字的旋转角不一致，程序终止。")


    #开始对line和text进行匹配对应
    valve_dist=1.4#在这个距离内被认为是一对 点到直线距离
    valve_dist1 = 1.0  # 在这个距离内被认为是一对 以直线方向为x坐标的距离
    t_lines=[x for x in line_objs]
    t_texts=[x for x in text_objs]#临时的集合
    bizhis=[]#type:list[BiaoZhi]
    for thisline in t_lines:
        dist_list=[]
        text_to_del=[]
        # new_basic_vectors=(Vector3D(cos(thisline.rotation),sin(thisline.rotation),0),
        #                    Vector3D(-sin(thisline.rotation),cos(thisline.rotation),0),
        #                    Vector3D(0,0,1)
        #                    )#以直线方向为新坐标系的基向量
        for text in t_texts:
            text.t_dist=text.centerpoint.distance_to_line(thisline.myline)#计算点到直线距离
            # x1=Vector3D(thisline.startpoint[0:2])
            # x1=x1.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            # x2=Vector3D(thisline.endpoint[0:2])
            # x2=x2.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            text.x3=text.centerpoint.get_coordinates_under_cartesian_coordinates_system(thisline.new_basic_vectors)#文字中心点在新坐标系的坐标
            #开始判别这个text是不是和直线对应的
            if abs(thisline.rotation-text.rotation)<5/180*pi:#文字和直线的方向不能大于5°
                if text.t_dist<valve_dist:#文字到直线的距离 有要求
                    if text.x3[0]>thisline.x1[0]-valve_dist1 and text.x3[0]<thisline.x2[0]+valve_dist1:#文字必须在这个直线附近 以直线为新坐标系
                        text_to_del.append(text)
        #开始处理结果 生成biaozhi
        if len(text_to_del)==1:#只有一个文字对象
            newbz=BiaoZhi()
            newbz.texts=text_to_del
            newbz.geshixian=thisline
            bizhis.append(newbz)
        elif len(text_to_del)==2:#有两个
            newbz = BiaoZhi()
            newbz.texts = text_to_del
            newbz.geshixian = thisline
            bizhis.append(newbz)
        elif len(text_to_del)==0:#一个也没有
            pass
        else:#过多的文字
            #此时 通过到中心点距离最近的两个被保留
            #或者缩小 valve_dist valve_dist1
            for text in text_to_del:
                text.t_dist=abs(thisline.centerpoint-text.centerpoint)
            text_to_del.sort(key=lambda x:x.t_dist)
            text_to_del=text_to_del[0:2]#只取前面两个
            # raise Exception("匹配上了过多文字，至少3个。")

        #删除已经匹配上的文字
        for tt in text_to_del:
            t_texts.remove(tt)
        if len(t_texts)==0:
            break#提前退出


    #开始自动调整右端的直线长度
    for bz in bizhis:
        xs=[]#保存所有text端点的坐标 直线方向坐标系下
        for text in bz.texts:
            #默认在原坐标系系 右边为结束端 这里以后可以更新 自动判断起始线在那一侧
            x4=text.rightup.get_coordinates_under_cartesian_coordinates_system(bz.geshixian.new_basic_vectors)
            xs.append(x4[0])#只记录x坐标
        #取出最大最小
        maxx=max(xs)
        minx=min(xs)
        #调整右边的直线端点
        #先获取直线在直线方向坐标系下的line3d
        t=bz.geshixian.myline
        t1=t.direction.get_coordinates_under_cartesian_coordinates_system(bz.geshixian.new_basic_vectors)
        t2=t.point.get_coordinates_under_cartesian_coordinates_system(bz.geshixian.new_basic_vectors)
        line1=Line3D(direction=t1,point=t2)
        #计算maxx在这个点上的直线上的点 新坐标系
        t3=line1.get_point(v=maxx)
        #把这个点在转移到原坐标系下
        new_basic_vectors1 = (Vector3D(cos(bz.geshixian.rotation), -sin(bz.geshixian.rotation), 0),
                                 Vector3D(sin(bz.geshixian.rotation), cos(bz.geshixian.rotation), 0),
                                 Vector3D(0, 0, 1)
                                 )  # 反向转动
        t4=t3.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors1)
        #更改线的属性
        bz.geshixian.EndPoint=to_Apoint(t4)

    acad.prompt("命令结束。\n")
if __name__ == '__main__':
    clearnup_biaozhi()