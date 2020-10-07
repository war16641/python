"""
先打开2018cad，新建一个空白文档，或者打开一个文档就可以运行,2016cad不行。

"""


from pyautocad import Autocad,APoint
from vector3d import Vector3D
from math import pi
from math import tan

def calc_slope():
    #计算两个点的坡率1：slope
    acad=Autocad(create_if_not_exists=True)
    # acad.prompt("Hello,Autocad from Python\n")
    # print (acad.doc.Name)

    p1=acad.doc.Utility.getpoint(APoint(0,0),'拾取第一个点：')
    p2=acad.doc.Utility.getpoint(APoint(p1[0],p1[1]),'拾取第二个点：')
    dx=p2[0]-p1[0]
    dy=p2[1]-p1[1]
    jd=Vector3D.calculate_angle_in_xoy(dx,dy)
    if jd<=-1/2*pi:
        alpha=jd-pi
    elif jd<=0:
        alpha=2*pi-jd
    elif jd<=1/2*pi:
        alpha=jd
    else:
        alpha=pi-jd
    acad.prompt("边坡率1:%.3f\n"%(1/tan(alpha)))
    print(1/tan(alpha))
    print(Vector3D.calculate_angle_in_xoy(dx,dy))

if __name__ == '__main__':
    calc_slope()