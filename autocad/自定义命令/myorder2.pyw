"""
先打开2018cad，新建一个空白文档，或者打开一个文档就可以运行,2016cad不行。

"""


from pyautocad import Autocad,APoint
from vector3d import Vector3D
from math import pi
from math import tan

def draw_slope():
    #指定斜率 起点 画射线 只支持画 从下方到上方的斜线
    acad=Autocad(create_if_not_exists=True)
    # acad.prompt("Hello,Autocad from Python\n")
    # print (acad.doc.Name)

    ratio = acad.doc.Utility.getreal('输入边坡率1：')
    p1=acad.doc.Utility.getpoint(APoint(0,0),'拾取起点：')
    p2 = acad.doc.Utility.getpoint(APoint(p1[0],p1[1]),'拾取大致方向点：')
    if p2[0]>=p1[0]:#方向向右
        acad.model.AddRay(APoint(p1[0], p1[1]), APoint(p1[0]+ratio, p1[1]+1))
    else:#方向向左
        acad.model.AddRay(APoint(p1[0], p1[1]), APoint(p1[0] - ratio, p1[1] + 1))
    acad.prompt("\n")

if __name__ == '__main__':

    draw_slope()