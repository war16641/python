from math import cos, sin
from typing import Tuple

from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from code2021.railway.huanhe import Huanhe
from excel.excel import FlatDataModel
from excel.railwayroute.mileage import Mileage
from vector3d import Vector3D


def make_route(duanlianbiao:FlatDataModel,
               quxianbiao:FlatDataModel)->Tuple[PolyLine,Mileage,Mileage]:
    def vector_from_angle(angle):
        """从方向角生成向量"""
        return Vector3D(cos(angle), sin(angle))

    assert isinstance(duanlianbiao,FlatDataModel) and\
        isinstance(quxianbiao ,FlatDataModel),"类型错误"
    angle = 0.0  # 上一行的方向角
    pieces = []  # 存储各个图素
    pos = Vector3D(0, 0)  # 当前的位置
    zd0 = Mileage()  # 上一行的终点
    zd0.duanlianbiao = duanlianbiao
    zd0.number = quxianbiao[0].data['终点里程']
    zd0.guanhao = quxianbiao[0].data['终点里程冠号']

    start_mileage=zd0.copy()#起点里程

    id = 1

    while True:
        if id > len(quxianbiao) - 1:
            end_mileage=Mileage()
            end_mileage.duanlianbiao = duanlianbiao
            end_mileage.number = quxianbiao[-1].data['终点里程']
            end_mileage.guanhao = quxianbiao[-1].data['终点里程冠号']
            break
        # 读取起点 终点
        qd = Mileage()
        qd.duanlianbiao = duanlianbiao
        qd.number = quxianbiao[id].data['起点里程']
        qd.guanhao = quxianbiao[id].data['起点里程冠号']
        zd = Mileage()
        zd.duanlianbiao = duanlianbiao
        zd.number = quxianbiao[id].data['终点里程']
        zd.guanhao = quxianbiao[id].data['终点里程冠号']
        # 得到直线
        changdu = qd - zd0  # 直线段的长度
        t = vector_from_angle(angle)
        t.modulus = changdu
        ZH = pos + t
        zhixian = LineSegment(pos, ZH)
        pieces.append(zhixian)
        # 计算曲线
        if quxianbiao[id].data['曲线半径'] > 1:  # 是曲线
            hhx = Huanhe()
            hhx.elo1 = quxianbiao[id].data['前缓和曲线']
            hhx.r1 = quxianbiao[id].data['曲线半径']
            hhx.length = quxianbiao[id].data['曲线长']
            if quxianbiao[id].data['偏角'] > 0:
                hhx.rotate_direction = 'R'
            else:
                hhx.rotate_direction = 'L'
            pl, _, _, HZ, angle1 = hhx.get_polyline_jiexu(ZH=ZH, angle0=angle)
            pieces.append(pl)
            # 重新设定起始条件
            pos = HZ
            angle = angle1
            zd0 = zd
        else:  # 不是曲线 一般就结束了
            assert id == len(quxianbiao) - 1, "错误的曲线表数据，当读取到直线时应该是最后一行才对。"
            pass
        id += 1

    # 整理结果
    whole_route = PolyLine(pieces)
    return whole_route,start_mileage,end_mileage


def draw_occupied_area(br_route:PolyLine,
                       qt_length:float)->PolyLine:
    assert isinstance(br_route,PolyLine) and isinstance(qt_length,(int,float)),"类型错误"
    zuo = you = br_route
    # 桥台
    qt_len = qt_length
    pt, _ = zuo.point_by_length_coord(qt_len)
    zuo1 = zuo.trim(pt, zuo.start_point)
    zuoa = zuo.trim(pt, zuo.end_point)
    pt, _ = zuo1.point_by_length_coord(zuo1.length - qt_len)
    zuo1 = zuo1.trim(pt, zuo1.end_point)
    pt, _ = zuo.point_by_length_coord(zuo.length - qt_len)
    zuob = zuo.trim(pt, zuo.start_point)

    pt, _ = you.point_by_length_coord(10)
    you1 = you.trim(pt, you.start_point)
    youa = you.trim(pt, zuo.end_point)
    pt, _ = you1.point_by_length_coord(you1.length - 10)
    you1 = you1.trim(pt, you1.end_point)

    pt, _ = you.point_by_length_coord(you.length - qt_len)
    youb = you.trim(pt, you.start_point)

    # 开始偏移6个
    zuoa = zuoa.offset(10.8, 'l')
    zuob = zuob.offset(10.8, 'l')
    zuo1 = zuo1.offset(5.8, 'l')

    youa = youa.offset(17.2, 'r')
    youb = youb.offset(17.2, 'r')
    you1 = you1.offset(12.2, 'r')

    zuo2 = PolyLine([zuoa,
                     LineSegment(zuoa.end_point, zuo1.start_point),
                     zuo1,
                     LineSegment(zuo1.end_point, zuob.start_point),
                     zuob])
    you2 = PolyLine([youa,
                     LineSegment(youa.end_point, you1.start_point),
                     you1,
                     LineSegment(you1.end_point, youb.start_point),
                     youb]
                    )

    # 拼接为整体
    you2 = you2.reverse()
    yongdixian = PolyLine([zuo2,
                           LineSegment(zuo2.end_point, you2.start_point),
                           you2,
                           LineSegment(you2.end_point, zuo2.start_point)])

    return yongdixian



def test():
    """
    这个是一个未完成的片段
    实现从excel表定义的断链表 曲线表 桥表中生成 路线(polyline) 桥的用地边界(polyline)
    @return:
    """
    quxianbiao = FlatDataModel.load_from_excel_file(fullname=r"C:\Users\niyinhao\Desktop\test\工作簿1.xlsx",
                                                    sheetname='曲线表')
    duanlianbiao = FlatDataModel.load_from_excel_file(fullname=r"C:\Users\niyinhao\Desktop\test\工作簿1.xlsx",
                                                      sheetname='断链表')
    qiaobiao = FlatDataModel.load_from_excel_file(fullname=r"C:\Users\niyinhao\Desktop\test\工作簿1.xlsx",
                                                  sheetname='桥表')
    route, sm, em = make_route(duanlianbiao=duanlianbiao, quxianbiao=quxianbiao)
    areas = []
    for u in qiaobiao:
        # 得到桥范围内的左线
        start_mil = Mileage(u.data['起里程'])
        start_mil.duanlianbiao = duanlianbiao
        end_mil = Mileage(u.data['止里程'])
        end_mil.duanlianbiao = duanlianbiao
        rou = route.copy()
        pt, _ = rou.point_by_length_coord(end_mil - sm)
        rou = rou.trim(pt, rou.end_point)
        pt, _ = rou.point_by_length_coord(start_mil - sm)
        rou = rou.trim(pt, rou.start_point)

        areas.append(draw_occupied_area(rou, 10))

    # for i,v in enumerate(areas):
    #     print(v.get_area())
    #     print(toline(v,'pl%d'%i))

    pl = areas[1]
    t = pl.get_area()
    print(t)
    print(pl.check_continuity())
    st = toline(pl, 'pl')
    print(st)
    # d = make_data_from_paragraph(st,ignore_lines=0)
    # yd=draw_occupied_area(route,10)
    # print(toline(yd,'pl1'))




