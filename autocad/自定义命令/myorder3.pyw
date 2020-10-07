"""
先打开2018cad，新建一个空白文档，或者打开一个文档就可以运行,2016cad不行。

"""
from autocad.toapoint import to_Apoint, myaddarc
from pyautocad import Autocad,APoint
from vector3d import Vector3D, Line3D
from math import pi, sqrt
from math import tan,cos,sin



def draw_abutment():
    #指定斜率 起点 画射线 只支持画 从下方到上方的斜线



    def script(x)->Vector3D:
        #将x点放到平移旋转后的坐标系上，就是最开始的脚本都是以左上点为原点做的，现在需要这个函数吧原点移动到任意位置并且旋转任意角度
        nonlocal new_basic_vectors,o
        return x.get_coordinates_under_cartesian_coordinates_system(new_basic_vectors)+o

    acad=Autocad(create_if_not_exists=True)
    # acad.prompt("Hello,Autocad from Python\n")
    # print (acad.doc.Name)
    allobjects=[]#所有在本函数中生成的图素
    p1 = acad.doc.Utility.getpoint(APoint(0, 0), '拾取台尾角点：')
    o=Vector3D(p1[0],p1[1])
    p2 = acad.doc.Utility.getpoint(to_Apoint(o), '拾取台前角点：')
    xuanz=Vector3D.calculate_angle_in_xoy(p1[0]-p2[0],p1[1]-p2[1])
    l2 = acad.doc.Utility.getreal('输入1:1.25坡面顺桥向长度：')
    if p1[0]<p2[0]:
        mirror_flag=True
        mirrorpts=[Vector3D(p1[0],p1[1]) ,Vector3D(p2[0],p2[1])]
    else:
        mirror_flag=False#是否需要安装P1 P2线旋转
    new_basic_vectors=(Vector3D(cos(xuanz),sin(-xuanz)),#图像旋转，相当于坐标系反向转
                       Vector3D(-sin(-xuanz),cos(xuanz)),
                       Vector3D(0,0,1))
    center=Vector3D( 1.1685   ,0.4840   , 0.0000)
    tt=myaddarc(acad,center=script(center),sp=script(Vector3D(-0.75,0,0)),theta=40/180*pi)
    allobjects.append(tt)
    # acad.model.addarc(to_Apoint(script(center)),1.9786,194/180*pi+xuanz,234/180*pi+xuanz)
    center = Vector3D(4.7071 , 1.9497  , 0.0000)
    tt=myaddarc(acad,center=script(center), sp=script(Vector3D(-6.75, 0, 0)), theta=56 / 180 * pi)
    allobjects.append(tt)
    # acad.model.addarc(to_Apoint(script(center)), 11.6218, 190 / 180 * pi+xuanz, 246 / 180 * pi+xuanz)
    # l2=5#1:1.25坡度的水平长度
    sp=Vector3D(-6.75-l2,0,0)
    radius=(sp-center).modulus#半径
    ep=Vector3D(0,center.y-sqrt(radius**2-center.x**2))
    sa=sp-center
    ea=ep-center
    tt=myaddarc(acad,center=script(center), sp=script(sp), theta=ea.calculate_angle_in_xoy(ea.x,ea.y)-sa.calculate_angle_in_xoy(sa.x,sa.y))
    allobjects.append(tt)
    # acad.model.addarc(to_Apoint(script(center)), radius, sa.calculate_angle_in_xoy(sa.x,sa.y)+xuanz,
    #                   ea.calculate_angle_in_xoy(ea.x,ea.y)+xuanz)
    #表示坡的线
    poxian=[]
    t=Vector3D(-0.7401  , -0.3395  ,0.0000)
    t1=Vector3D(-2.3219 ,-0.6201   ,0.0000)
    elo=Line3D(point=t,direction=(t1-t).get_standard_copy())
    poxian.append(elo)
    t=Vector3D(-0.5694 ,-0.6747 , 0.0000)
    t1=Vector3D( -1.6758  , -1.5326   , 0.0000)
    elo=Line3D(point=t,direction=(t1-t).get_standard_copy())
    poxian.append(elo)
    t=Vector3D(-0.2653   ,-0.9794  ,0.0000)
    t1=Vector3D(-0.8221   , -2.1732 , 0.0000)
    elo=Line3D(point=t,direction=(t1-t).get_standard_copy())
    poxian.append(elo)
    len_poxian=1.6#坡线长
    for i in poxian:
        tt=acad.model.addline(to_Apoint(script(i.point)),to_Apoint(script(i.point+len_poxian*i.direction)))
        allobjects.append(tt)

    #另一个坡线
    poxian2=[    ]
    t=Vector3D( -6.6357    ,-0.9348   ,0.0000)
    t1=Vector3D( -7.1702   , -1.0133  ,0.0000)
    elo=Line3D(point=t,direction=(t1-t).get_standard_copy())
    poxian2.append(elo)

    # t = Vector3D(-6.4363   ,-1.6560 , 0.0000)
    # t1 = Vector3D(-6.9952   , -1.8065, 0.0000)
    # elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    # poxian2.append(elo)

    t = Vector3D(-6.1327    ,-2.4895   , 0.0000)
    t1 = Vector3D(-6.6522   , -2.7104 , 0.0000)
    elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    poxian2.append(elo)

    t = Vector3D( -5.6318    ,-3.6433     , 0.0000)
    t1 = Vector3D( -6.0486 ,-3.8683  , 0.0000)
    elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    poxian2.append(elo)

    t = Vector3D(-4.8511    ,-4.7814 , 0.0000)
    t1 = Vector3D(-5.4152    ,-5.1490, 0.0000)
    elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    poxian2.append(elo)

    t = Vector3D( -3.8488 ,-6.0440  , 0.0000)
    t1 = Vector3D(-4.4136  , -6.4991, 0.0000)
    elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    poxian2.append(elo)


    t = Vector3D( -2.2302 , -7.4871, 0.0000)
    t1 = Vector3D( -2.7008     , -8.1258, 0.0000)
    elo = Line3D(point=t, direction=(t1 - t).get_standard_copy())
    poxian2.append(elo)

    len_poxian2=l2*0.8#坡线长
    for i in poxian2:
        tt=acad.model.addline(to_Apoint(script(i.point)),to_Apoint(script(i.point+len_poxian2*i.direction)))
        allobjects.append(tt)


    #补边界
    tt=acad.model.addline(to_Apoint(script(Vector3D())), to_Apoint(script(sp)))
    allobjects.append(tt)
    tt=acad.model.addline(to_Apoint(script(Vector3D())), to_Apoint(script(ep)))
    allobjects.append(tt)

    if mirror_flag:
        for i in allobjects:
            i.Mirror(to_Apoint(mirrorpts[0]),to_Apoint(mirrorpts[1]))
            i.delete()
    # ratio = acad.doc.Utility.getreal('输入边坡率1：')
    # p1=acad.doc.Utility.getpoint(APoint(0,0),'拾取起点：')
    # p2 = acad.doc.Utility.getpoint(APoint(p1[0],p1[1]),'拾取大致方向点：')
    # if p2[0]>=p1[0]:#方向向右
    #     acad.model.AddRay(APoint(p1[0], p1[1]), APoint(p1[0]+ratio, p1[1]+1))
    # else:#方向向左
    #     acad.model.AddRay(APoint(p1[0], p1[1]), APoint(p1[0] - ratio, p1[1] + 1))
    # acad.prompt("\n")

if __name__ == '__main__':

    draw_abutment()