"""
自动计算钢筋间距 并绘出对齐标注
"""

from excel_udf.script01 import arange_inteval
from pyautocad import Autocad,APoint,distance

def this_order():
    acad = Autocad(create_if_not_exists=True)
    p1=acad.doc.Utility.getpoint(APoint(0,0),'拾取起点：')
    p2 = acad.doc.Utility.getpoint(APoint(p1[0], p1[1]), '拾取终点：')
    p3 = acad.doc.Utility.getpoint(APoint(p1[0], p1[1]), '拾取标注线位置：')
    dim=acad.doc.modelspace.AddDimAligned(APoint(p1[0], p1[1]), APoint(p2[0], p2[1]), APoint(p3[0], p3[1]))
    # dim=acad.best_interface(dim)
    L = acad.doc.Utility.getstring(0, '输入标注长度（如果不输入取实际长度）：')
    itv = acad.doc.Utility.getreal('输入间距：')
    if len(L)==0:
        L=distance(p1,p2)
    else:
        L=float(L)
    dim.TextOverride=arange_inteval(L,itv)


if __name__ == '__main__':
    this_order()