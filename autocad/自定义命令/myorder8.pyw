"""
自动添加图框
"""
from autocad.toapoint import to_Apoint, my_get_selection, safe_prompt
from pyautocad import Autocad, APoint
from vector3d import Vector3D
def thisorder():
    acad = Autocad(create_if_not_exists=True)
    acadoc=acad.doc
    # slt_draw = acad.get_selection(text="选择图面对象：")
    slt_draw=my_get_selection(acad,"选择图面对象：")
    # slt_desc= my_get_selection(acad,"选择说明对象：")
    slt_cp = my_get_selection(acad,"选择copyright对象：")
    papersize = acadoc.Utility.getreal('输入图纸大小A：')
    zoomscale = acadoc.Utility.getreal('输入图缩放比例：')
    # safe_prompt(acadoc,"正在执行命令...\n")

    print(acadoc.Name)



    xs=[]
    ys=[]
    for myobj in slt_draw:
        myobj=acad.best_interface(myobj)
        xs.append(myobj.GetBoundingBox()[0][0])
        xs.append(myobj.GetBoundingBox()[1][0])
        ys.append(myobj.GetBoundingBox()[0][1])
        ys.append(myobj.GetBoundingBox()[1][1])
    draw_ld=Vector3D(min(xs),min(ys))#得到角点
    draw_ru=Vector3D(max(xs),max(ys))


    # slt_cp = acad.get_selection(text="选择copyright对象：")


    xs=[]
    ys=[]
    for myobj in slt_cp:
        # # myobj = acad.best_interface(slt_draw[i])
        # myobj=acad.best_interface(i)
        xs.append(myobj.GetBoundingBox()[0][0])
        xs.append(myobj.GetBoundingBox()[1][0])
        ys.append(myobj.GetBoundingBox()[0][1])
        ys.append(myobj.GetBoundingBox()[1][1])
        # set_cp.append(myobj)
    cp_ld=Vector3D(min(xs),min(ys))#得到角点
    cp_ru=Vector3D(max(xs),max(ys))

    # slt_desc = acad.get_selection(text="选择说明对象：")

    xs=[]
    ys=[]
    # for myobj in slt_desc:
    #     # myobj = acad.best_interface(i)
    #     xs.append(myobj.GetBoundingBox()[0][0])
    #     xs.append(myobj.GetBoundingBox()[1][0])
    #     ys.append(myobj.GetBoundingBox()[0][1])
    #     ys.append(myobj.GetBoundingBox()[1][1])
    # desc_ld=Vector3D(min(xs),min(ys))#得到角点
    # desc_ru=Vector3D(max(xs),max(ys))

    left_margin=10*zoomscale
    right_margin=10*zoomscale#左右留白

    cp_width=cp_ru.x-cp_ld.x#签名栏的宽度
    cp_height=cp_ru.y-cp_ld.y
    # if right_margin-draw_ru.x<cp_width:#签名栏侵入图面
    #     right_margin=draw_ru.x+cp_width+0.1 #最后这个数为0 时，签名栏和图面完全相邻

    if papersize == 2:
        h1=205/0.5*zoomscale
        h2=210/0.5*zoomscale
    elif papersize==3:
        h1=143.5/0.5*zoomscale
        h2=148.5/0.5*zoomscale#A2 A3的图纸大小
    else:
        raise Exception("参数错误")

    #画内层线
    centerline_y=0.5*(draw_ld.y+draw_ru.y)#中心线完全由图面中心线决定
    frame1_ld=Vector3D(x=draw_ld.x-left_margin,
                    y=centerline_y-h1/2)
    frame1_ru=Vector3D(x=draw_ru.x+right_margin,
                    y=centerline_y+h1/2)
    # frame2_ld=frame1_ld-Vector3D(12.5,2.5)
    # frame2_ru=frame1_ru+Vector3D(2.5,2.5)#由内框线生成外框线
    frame2_ld=frame1_ld-Vector3D(12.5/0.5*zoomscale,2.5/0.5*zoomscale)
    frame2_ru=frame1_ru+Vector3D(2.5/0.5*zoomscale,2.5/0.5*zoomscale)#由内框线生成外框线

    t1=acadoc.modelspace.addline(APoint(frame1_ld.x,frame1_ld.y),APoint(frame1_ru.x,frame1_ld.y))
    t2=acadoc.modelspace.addline(APoint(frame1_ru.x,frame1_ld.y),APoint(frame1_ru.x,frame1_ru.y))
    t3=acadoc.modelspace.addline(APoint(frame1_ru.x,frame1_ru.y),APoint(frame1_ld.x,frame1_ru.y))
    t4=acadoc.modelspace.addline(APoint(frame1_ld.x,frame1_ru.y),APoint(frame1_ld.x,frame1_ld.y))
    for i in [t1,t2,t3,t4]:
        i.color=6#改变内框线颜色

    acadoc.modelspace.addline(APoint(frame2_ld.x,frame2_ld.y),APoint(frame2_ru.x,frame2_ld.y))
    acadoc.modelspace.addline(APoint(frame2_ru.x,frame2_ld.y),APoint(frame2_ru.x,frame2_ru.y))
    acadoc.modelspace.addline(APoint(frame2_ru.x,frame2_ru.y),APoint(frame2_ld.x,frame2_ru.y))
    acadoc.modelspace.addline(APoint(frame2_ld.x,frame2_ru.y),APoint(frame2_ld.x,frame2_ld.y))

    #移动签名

    newp=Vector3D(draw_ru.x+right_margin,frame1_ld.y+cp_height)
    for myobj in slt_cp:
        myobj.move(to_Apoint(cp_ru),to_Apoint(newp))
    acad.prompt("命令完成。\n")
if __name__ == '__main__':
    thisorder()