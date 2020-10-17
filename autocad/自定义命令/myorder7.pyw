"""
调整标志线的对象
标志线最多可以拥有两个单行文字
使用时，可以选择多个需要调整的对象
如果标志线附近发现多个文字（3个及以上） 取最近的两个
"""
import time
from math import pi, cos, sin, e
from statistics import mean

from autocad.mapmesh import MapMesh, find_whiterect
from autocad.toapoint import to_Apoint, MyRect, get_trans_func, make_myrect_from_obj
from autocad.自定义命令.myorder6 import get_best_rect, select_by_window
import numpy as np
from pyautocad import Autocad, APoint
from vector3d import Vector3D, Line3D


def haircut(myobj):
    """
    给原生的cad对象理发
    添加一些便于计算和操作的变量
    需分类型
    @param myobj:
    @return:
    """
    if 'acdbtext' in myobj.ObjectName.lower() or 'blockref' in myobj.ObjectName.lower():  # 文字 块参照
        myobj.leftdown = myobj.GetBoundingBox()[0]
        myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
        myobj.leftdown = Vector3D(myobj.leftdown[0:2])
        myobj.rightup = Vector3D(myobj.rightup[0:2])
        myobj.centerpoint = (myobj.rightup + myobj.leftdown) * 0.5
        myobj.myrect = MyRect(xy=myobj.leftdown, width=myobj.rightup.x - myobj.leftdown.x,
                              height=myobj.rightup.y - myobj.leftdown.y)  # 生成对应myrect 不考虑旋转，以bouding生成rect
    elif 'acdbline' in myobj.ObjectName.lower():  # 直线
        myobj.p1 = Vector3D(myobj.startpoint[0:2])
        myobj.p2 = Vector3D(myobj.endpoint[0:2])  # 保留原坐标下的坐标
        myobj.centerpoint = (myobj.p1 + myobj.p2) / 2.0  # 中心点 原坐标系
        myobj.myline = Line3D.make_line_by_2_points(myobj.p1, myobj.p2)
        myobj.rotation = Vector3D.calculate_angle_in_xoy(myobj.myline.direction.x, myobj.myline.direction.y)
        myobj.tf, myobj.tfi = get_trans_func(
            theta=Vector3D.calculate_angle_in_xoy(myobj.myline.direction.x, myobj.myline.direction.y))
        # 计算自己的两个端点在这个坐标系下的坐标
        myobj.x1 = myobj.tf(myobj.p1)
        myobj.x2 = myobj.tf(myobj.p2)
    else:
        pass


class BiaoZhi:
    def __init__(self):
        self.texts = []
        self.geshixian = None
        self.zhishixian = None
        self.zuankong = None

    def __str__(self):
        if len(self.texts) == 0:
            return "空"
        else:
            return self.texts[0].TextString

    def draw_frame(self, doc):
        # 在cad中画框线
        dajihe = []
        for i in self.texts:
            dajihe.append(i.leftdown)
            dajihe.append(i.rightup)
        if self.geshixian is not None:
            dajihe.append(self.geshixian.p1)
            dajihe.append(self.geshixian.p2)
        if self.zuankong is not None:
            dajihe.append(self.zuankong.leftdown)
            dajihe.append(self.zuankong.rightup)
        t1, t2 = Vector3D.get_bound_corner(dajihe)
        mr = MyRect(xy=t1, width=t2.x - t1.x, height=t2.y - t1.y)
        mr.draw_in_cad(doc)

    def move(self, p1: Vector3D, p2: Vector3D, acad_doc):
        # 移动文字和格式线 并自动调整指示线
        move_objs = [x for x in self.texts]
        move_objs.append(self.geshixian)
        for i in move_objs:
            i.move(to_Apoint(p1), to_Apoint(p2))  # 移动 文字和格式线
            haircut(i)  # 移动后 重新理发
        # 处理指示线
        if self.zhishixian is not None:
            self.zhishixian.erase()
        # 生成新的指示线
        goal_p = self.zuankong.centerpoint  # 暂时取中心点为目标点 可以选择其他点
        compare_lst = []
        compare_lst.append((self.geshixian.p1, abs(self.geshixian.p1 - goal_p)))
        compare_lst.append((self.geshixian.p2, abs(self.geshixian.p2 - goal_p)))  # 对格式线两个端点计算到目标点距离
        compare_lst.sort(key=lambda x: x[1])
        head = compare_lst[0]
        t = acad_doc.modelspace.addline(to_Apoint(goal_p), to_Apoint(head[0]))  # 添加标志线
        self.zhishixian = t
        self.zhishixian.layer = self.texts[0].layer  # 改变图层

    def clearup(self, acad_doc):
        """
        自动调整标志线
        标志线两端都剪掉
        不需要有转孔也可以执行
        @param acad_doc:
        @return:
        """
        t = self.geshixian.p2 - self.geshixian.p1
        theta = Vector3D.calculate_angle_in_xoy(t.x, t.y)
        tf, tfi = get_trans_func(theta=self.geshixian.rotation)  # 以指示线的方向建立新坐标系
        ep1 = tf(self.geshixian.p1)
        ep2 = tf(self.geshixian.p2)  # 计算格式线在新坐标系下的坐标
        lst = []
        for i in self.texts:
            lst.append(tf(i.rightup))
            lst.append(tf(i.leftdown))  # 计算文字角点在新坐标系下座板
        r1, r2 = Vector3D.get_bound_corner(lst)  # 获取角点
        newline = Line3D(direction=tf(self.geshixian.myline.direction),  # 在新坐标系下格式线的直线
                         point=tf(self.geshixian.myline.point))
        p1 = newline.get_point(v=r1.x)
        p2 = newline.get_point(v=r2.x)  # 得到角点在格式线上的投影
        p1 = tfi(p1)
        p2 = tfi(p2)  # 转换到原坐标系
        self.geshixian.StartPoint = to_Apoint(p1)
        self.geshixian.EndPoint = to_Apoint(p2)

        acad_doc.modelspace.addline(to_Apoint(self.texts[0].leftdown), to_Apoint(self.texts[0].rightup))  # 添加标志线

    def automove(self, acad, acad_doc, radius=25., meshsize=0.5):
        """

        @param acad_doc:
        @return:
        """
        # 计算前景内容框 主要是文字
        dajihe = []
        for i in self.texts:
            dajihe.append(i.leftdown)
            dajihe.append(i.rightup)
        t1, t2 = Vector3D.get_bound_corner(dajihe)
        target_mr = MyRect(xy=t1, width=t2.x - t1.x, height=t2.y - t1.y)
        t = Vector3D(radius, radius)
        wd_ld = target_mr.center - t
        wd_ru = target_mr.center + t
        objs = select_by_window(acad, acad.doc, wd_ld, wd_ru)  # 选择附近对象
        for i in self.texts:
            objs.remove(i)  # 移除自己
        # 根据对象 生成对应的rect
        rects = []
        for oj in objs:
            try:
                mr = make_myrect_from_obj(oj)
                rects.append(mr)
                # mr.draw_in_cad(acad.doc)
            except TypeError:
                pass
        mm = MapMesh(wd_ld, wd_ru)
        mm.mesh(meshsize)

        # 开始判断cell在不在这些rects中 是的话染成红色
        for c in mm.cells:
            for r in rects:
                if c.center in r:
                    c.facecolor = 'r'
                    break

        # 开始计算最佳位置
        t=myaddindex(self.zuankong)
        t1=mydistfunc(self.zuankong)
        r = find_whiterect(mm=mm, rects=rects, target_rect=target_mr,
                           valve_func=myfunc2,
                           additional_index=t.func,
                           dist_func=t1.func)
        # 移动
        self.move(target_mr.xy, r.xy, acad_doc)


def myfunc(a, b):
    # return (20*(a+1))*b+b
    p1 = 0.3
    p2 = 2.
    p3 = 300.
    if a <= p1:
        return ((p2 - 1) / p1 * a + 1) * b
    else:
        return ((p3 - p2) / (1 - p1) * (a - p1) + p2) * b

def myfunc1(a,b):
    return (e**(8*a)-1)*b
def myfunc2(a,b):
    return (e**(8*a)-1)*(b+1.0)



class myaddindex:#附加价值函数
    def __init__(self,zk):
        self.zuankong=zk
    def func(self,x):
        if x.bound_corners[0].x<self.zuankong.centerpoint.x<x.bound_corners[1].x:
            return 100
        else:
            # return abs(x.center-self.zuankong.centerpoint)#返回rect中心到zk中心距离
            return 0
class mydistfunc:#定义 以钻孔距离为距离函数
    def __init__(self,zk):
        self.zuankong = zk
    def func(self,target_rect,thisrect):
        return abs(thisrect.center-self.zuankong.centerpoint)
def clearnup_biaozhi():
    acad = Autocad(create_if_not_exists=True)
    slt = acad.get_selection(text="选择需要调整标志线的对象：按enter结束")
    acad.prompt("正在执行命令...\n")
    start_time = time.time()
    # acad.prompt("选择需要重新排列的对象：按enter结束\n")
    print(acad.doc.Name)

    text_objs = []  # 所有文字
    line_objs = []
    block_objs = []
    print('共选择%d个对象' % slt.Count)
    # valve_x = acad.doc.Utility.getreal('输入分组x距离：')
    # new_distance_x = acad.doc.Utility.getreal('输入新的组间x距离：')
    # acad.prompt("正在重新排列...\n")
    for i in range(slt.Count):
        myobj = acad.best_interface(slt[i])
        if 'acdbtext' in myobj.ObjectName.lower():  # 文字
            myobj.leftdown, myobj.rightup = myobj.GetBoundingBox()
            t = [(i1 + i2) / 2.0 for i1, i2 in zip(myobj.leftdown, myobj.rightup)]  # 文字的中心点
            myobj.centerpoint = Vector3D(t)
            myobj.leftdown = myobj.GetBoundingBox()[0]
            myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
            myobj.leftdown = Vector3D(myobj.leftdown[0:2])
            myobj.rightup = Vector3D(myobj.rightup[0:2])
            text_objs.append(myobj)
        elif 'acdbline' in myobj.ObjectName.lower():  # 直线
            if myobj.Length < 0.1:
                continue  # 长度小于这个值的直线忽略
            # myobj.myline=Line3D.make_line_by_2_points(Vector3D(myobj.startpoint[0:2]),Vector3D(myobj.endpoint[0:2]))
            # myobj.rotation=Vector3D.calculate_angle_in_xoy(myobj.myline.direction[0],
            #                                                myobj.myline.direction[1])#计算方向角
            # #以自己的方向为新坐标系
            # myobj.new_basic_vectors = (Vector3D(cos(myobj.rotation), sin(myobj.rotation), 0),
            #                      Vector3D(-sin(myobj.rotation), cos(myobj.rotation), 0),
            #                      Vector3D(0, 0, 1)
            #                      )  # 以直线方向为新坐标系的基向量
            # #计算自己的两个端点在这个坐标系下的坐标
            # myobj.x1 = Vector3D(myobj.startpoint[0:2]).get_coordinates_under_cartesian_coordinates_system(myobj.new_basic_vectors)
            # myobj.x2 = Vector3D(myobj.endpoint[0:2]).get_coordinates_under_cartesian_coordinates_system(
            #     myobj.new_basic_vectors)
            # myobj.p1 = Vector3D(myobj.startpoint[0:2])
            # myobj.p2 = Vector3D(myobj.endpoint[0:2])#保留原坐标下的坐标
            # myobj.centerpoint=(myobj.p1+myobj.p2)/2.0#中心点 原坐标系
            haircut(myobj)
            line_objs.append(myobj)
        elif 'blockref' in myobj.ObjectName.lower():  # 块参照
            myobj.leftdown = myobj.GetBoundingBox()[0]
            myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
            myobj.leftdown = Vector3D(myobj.leftdown[0:2])
            myobj.rightup = Vector3D(myobj.rightup[0:2])
            myobj.centerpoint = (myobj.rightup + myobj.leftdown) * 0.5
            myobj.myrect = MyRect(xy=myobj.leftdown, width=myobj.rightup.x - myobj.leftdown.x,
                                  height=myobj.rightup.y - myobj.leftdown.y)  # 生成对应myrect 不考虑旋转，以bouding生成rect
            block_objs.append(myobj)
        elif 'polyline' in myobj.ObjectName.lower():  # 多段线
            if myobj.closed is False or myobj.getwidth(0)[0]<0.19:#没有闭合 或者 没什么宽度的多段线 跳过
                continue

        else:
            pass

    # 获取文字方向
    # 一般来说 文字方向都是一致的
    t = [x.rotation for x in text_objs]
    avg_rotation = mean(t)  # 平均文字
    std_rotation = np.std(t)
    # if std_rotation>3/180*pi:
    #     raise Exception("文字的旋转角不一致，程序终止。")

    # 开始对line和text进行匹配对应
    valve_dist = 1.4  # 在这个距离内被认为是一对 点到直线距离
    valve_dist1 = 1.0  # 在这个距离内被认为是一对 以直线方向为x坐标的距离
    t_lines = [x for x in line_objs]
    t_texts = [x for x in text_objs]  # 临时的集合
    bizhis = []  # type:list[BiaoZhi]
    for thisline in t_lines:
        dist_list = []
        text_to_del = []
        tf, _ = get_trans_func(
            theta=Vector3D.calculate_angle_in_xoy(thisline.myline.direction.x, thisline.myline.direction.y))
        # new_basic_vectors=(Vector3D(cos(thisline.rotation),sin(thisline.rotation),0),
        #                    Vector3D(-sin(thisline.rotation),cos(thisline.rotation),0),
        #                    Vector3D(0,0,1)
        #                    )#以直线方向为新坐标系的基向量
        for text in t_texts:
            text.t_dist = text.centerpoint.distance_to_line(thisline.myline)  # 计算点到直线距离
            # x1=Vector3D(thisline.startpoint[0:2])
            # x1=x1.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            # x2=Vector3D(thisline.endpoint[0:2])
            # x2=x2.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)
            # text.x3=text.centerpoint.get_coordinates_under_cartesian_coordinates_system(thisline.new_basic_vectors)#文字中心点在新坐标系的坐标
            text.x3 = tf(text.centerpoint)
            # 开始判别这个text是不是和直线对应的
            if abs(thisline.rotation - text.rotation) < 5 / 180 * pi:  # 文字和直线的方向不能大于5°
                if text.t_dist < valve_dist:  # 文字到直线的距离 有要求
                    if text.x3[0] > thisline.x1[0] - valve_dist1 and text.x3[0] < thisline.x2[
                        0] + valve_dist1:  # 文字必须在这个直线附近 以直线为新坐标系
                        text_to_del.append(text)
        # 开始处理结果 生成biaozhi
        if len(text_to_del) == 1:  # 只有一个文字对象
            newbz = BiaoZhi()
            newbz.texts = text_to_del
            newbz.geshixian = thisline
            bizhis.append(newbz)
        elif len(text_to_del) == 2:  # 有两个
            newbz = BiaoZhi()
            newbz.texts = text_to_del
            newbz.geshixian = thisline
            bizhis.append(newbz)
        elif len(text_to_del) == 0:  # 一个也没有
            pass
        else:  # 过多的文字
            # 此时 通过到中心点距离最近的两个被保留
            # 或者缩小 valve_dist valve_dist1
            for text in text_to_del:
                text.t_dist = abs(thisline.centerpoint - text.centerpoint)
            text_to_del.sort(key=lambda x: x.t_dist)
            text_to_del = text_to_del[0:2]  # 只取前面两个
            # raise Exception("匹配上了过多文字，至少3个。")

        # 删除已经匹配上的文字
        for tt in text_to_del:
            t_texts.remove(tt)
        if len(t_texts) == 0:
            break  # 提前退出

    # 将block和bizohi匹配
    valve_dist_for_zuankong = 5.  # 钻孔的block是属于biaozhi的极限距离 超过这个值 认为这个block是没有对应的
    for bz in bizhis:
        compare_lst = []
        for bl in block_objs:
            t1 = abs(bl.centerpoint - bz.geshixian.p1)
            t2 = abs(bl.centerpoint - bz.geshixian.p2)
            compare_lst.append((bl, min([t1, t2])))  # 以到格式线两个端点距离最小值为判据
        compare_lst.sort(key=lambda x: x[1])
        head = compare_lst[0]
        if head[1] < valve_dist_for_zuankong:
            bz.zuankong = head[0]
            block_objs.remove(head[0])  # 匹配上了就删除

    # #画框线
    # for bz in bizhis:
    #     bz.draw_frame(acad.doc)

    # #移动
    # bizhis[0].move(Vector3D(0,0,0),Vector3D(0,10,0),acad.doc)

    # #修剪格式线
    # bizhis[0].clearup(acad.doc)

    # 自动调整位置
    for i,o in enumerate(bizhis):
        o.automove(acad, acad.doc)
        acad.prompt("已完成%d/%d\n"%(i+1,len(bizhis)) )

    duration_time = time.time() - start_time
    acad.prompt("命令完成。耗时%fs\n" % duration_time)


if __name__ == '__main__':
    clearnup_biaozhi()