"""
自动伸缩文字下方的多条直线，达到合适的长度
"""


from math import pi

from autocad.toapoint import my_get_selection, haircut, to_Apoint
from pyautocad import Autocad,APoint

def thisorder():
    acad = Autocad(create_if_not_exists=True)
    print(acad.doc.Name)
    slt = my_get_selection(acad=acad,text="选择文字和标志线：按enter结束")
    acad.prompt("正在执行命令...\n")
    text=None
    lines=[]
    for myobj in slt:
        if 'acdbtext' in myobj.ObjectName.lower():
            haircut(myobj)
            text=myobj
            # myobj.myrect.draw_in_cad(acad.doc)
        elif 'acdbline' in myobj.ObjectName.lower():  # 直线
            haircut(myobj)
            lines.append(myobj)


    #计算合适的直线长度
    for ln in lines:
        p1=text.leftdown.get_nearest_point_to_line(ln.myline)
        p2=text.rightup.get_nearest_point_to_line(ln.myline)
        #修改
        ln.StartPoint=to_Apoint(p1)
        ln.EndPoint = to_Apoint(p2)
    pass
    acad.prompt("命令完成\n")

if __name__ == '__main__':
    thisorder()
