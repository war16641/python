"""
先打开2018cad，新建一个空白文档，或者打开一个文档就可以运行,2016cad不行。
AcDbBlockReference
"""
import time

from autocad.mapmesh import MapMesh
from autocad.toapoint import make_myrect_from_obj, MyRect, to_Apoint
from pyautocad import Autocad,APoint
from vector3d import Vector3D
import numpy as np

def select_by_window(acad,doc,p1:Vector3D,p2:Vector3D)->list:
    """
    通过矩形框选取
    @param p1:
    @param p2:
    @return: object组成的列表

    """
    try:
        doc.SelectionSets.Item("Sa13").Delete()
    except:
        print("Delete selection failed")

    slt = doc.SelectionSets.Add("Sa13")
    slt.Select(0, to_Apoint(p1), to_Apoint(p2))
    lst=[]
    for o in slt:
        lst.append(acad.best_interface(o))
    return lst
def get_best_rect(outr,c1,c2):
    # 选择合适的算法 确定最优值
    #c1 c2是两个权重系数，代表goodcell和距离的权重
    for o in outr:
        o.append(o[3]*c1+ (1 - o[4])*c2)
    outr.sort(key=lambda x: x[-1], reverse=True)

def thisorder():

    acad=Autocad(create_if_not_exists=True)

    print (acad.doc.Name)
    slt=acad.get_selection(text="选择前景对象：按enter结束")
    target_obj = acad.best_interface(slt[0])
    target_mr=make_myrect_from_obj(target_obj)
    radius = acad.doc.Utility.getreal('输入计算的半径：')
    meshsize = acad.doc.Utility.getreal('输入mesh尺寸：')
    start_time=time.time()
    acad.prompt("正在执行命令...\n")
    t=Vector3D(radius,radius)
    wd_ld=target_mr.center-t
    wd_ru=target_mr.center+t
    objs=select_by_window(acad,acad.doc,wd_ld,wd_ru)#选择附近对象

    #根据对象 生成对应的rect
    rects=[]
    for oj in objs:
        try:
            mr=make_myrect_from_obj(oj)
            rects.append(mr)
            # mr.draw_in_cad(acad.doc)
        except TypeError:
            pass


    mm=MapMesh(wd_ld,wd_ru)
    mm.mesh(meshsize)
    #开始判断cell在不在这些rects中 是的话染成红色
    for c in mm.cells:
        for r in rects:
            if c.center in r:
                c.facecolor='r'
                break
    # mm.show()

    #开始计算最佳位置
    outr=[]
    for x in np.arange(mm.leftdown.x,mm.rightup.x-target_mr.width,mm.cell_length):
        for y in np.arange(mm.leftdown.y,mm.rightup.y-target_mr.height,mm.cell_length):
            thisrect=MyRect(Vector3D(x,y),target_mr.width,target_mr.height,0.0)#新位置
            number_goodcells=0
            dist=abs(target_mr.center-thisrect.center)#距离
            for c in mm.get_cells_in_rect_fast(thisrect):
                if c.facecolor=='g':
                    number_goodcells += 1
            # for c in mm.cells:
            #     if c.center in thisrect and c.facecolor=='g':
            #         number_goodcells+=1
            outr.append([thisrect,number_goodcells,dist,])
    #根据计算结果排序得出最优
    #归一化两个指标
    max_number=0
    max_dist=0.0
    for o in outr:
        max_number=o[1] if o[1]>max_number else max_number
        max_dist = o[2] if o[2] > max_dist else max_dist
    for o in outr:
        o.append(o[1]/max_number)
        o.append(o[2]/max_dist)

    get_best_rect(outr,0.8,0.2)
    #移动目标
    target_obj.move(to_Apoint(target_mr.xy), to_Apoint(outr[0][0].xy))
    duration_time=time.time()-start_time
    acad.prompt("命令完成。耗时%fs\n"%duration_time)


if __name__ == '__main__':
    thisorder()