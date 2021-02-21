
import re
import os

from code2021.MyGeometric.arc import Arc
from code2021.MyGeometric.linesegment import LineSegment
from code2021.MyGeometric.polyline import PolyLine
from code2021.MyGeometric.rect import Rect
from vector3d import Vector3D

stringPatern="^\s*(\S+)\s+(\S+)\s+(.+)$" #识别行的正则表达
def read_single_line(cur_line):
    """
    从单行string中读取数据
    @param cur_line:
    @return: 数据类型(s或m),名称,数据
    """
    rert = re.findall(stringPatern, cur_line)
    if len(rert) == 0:
        raise Exception("错误的行：%s" % cur_line)
    rert = rert[0]
    if rert[1] == "float":
        # rt[rert[0]] = float(rert[2])
        return 's', rert[0], float(rert[2])
    elif rert[1] == "string":
        # rt[rert[0]] = rert[2]
        return 's', rert[0], rert[2]
    elif rert[1] == "vector":
        nbs = rert[2].split(",")
        nbs = [float(x) for x in nbs]
        # rt[rert[0]] = Vector3D.make_from_list(nbs)
        return 's', rert[0], Vector3D.make_from_list(nbs)
    elif rert[1] == "rect":
        parts = rert[2].split(",")
        # rect 有两种格式
        if len(parts) == 4:  # 已有vector的标识，长，宽，转角
            raise Exception("请改用6个数的rect格式")
            # assert parts[0] in rt.keys(), "rect引用了一个不存在的vector %s" % parts[0]
            # width = float(parts[1])
            # height = float(parts[2])
            # rotation = float(parts[3])
            # # rt[rert[0]] = Rect(xy=rt[parts[0]], width=width, height=height,
            # #                    rotation=rotation)
            # return 's', rert[0], Rect(xy=rt[parts[0]], width=width, height=height,
            #                           rotation=rotation)
        elif len(parts) == 6:  # x，y，z，长，宽，转角
            # rt[rert[0]] = Rect(xy=Vector3D(float(parts[0]), float(parts[1]), float(parts[2])),
            #                    width=float(parts[3]), height=float(parts[4]),
            #                    rotation=float(parts[5]))
            return 's', rert[0], Rect(xy=Vector3D(float(parts[0]), float(parts[1]), float(parts[2])),
                                      width=float(parts[3]), height=float(parts[4]),
                                      rotation=float(parts[5]))
        else:
            raise Exception("rect的数据格式不正确 %s" % rert[2])

    elif rert[1] == "lineseg":
        nbs = rert[2].split(",")
        nbs = [float(x) for x in nbs]
        assert len(nbs) == 6, "linesegment格式错误 %s" % rert[2]
        # rt[rert[0]] = LineSegment(Vector3D(nbs[0], nbs[1], nbs[2]), Vector3D(nbs[3], nbs[4], nbs[5]))
        return 's', rert[0], LineSegment(Vector3D(nbs[0], nbs[1], nbs[2]), Vector3D(nbs[3], nbs[4], nbs[5]))
    elif rert[1] == "arc":
        nbs = rert[2].split(",")
        nbs = [float(x) for x in nbs]
        assert len(nbs) == 6, "arc格式错误 %s" % rert[2]
        # rt[rert[0]] = Arc(Vector3D(nbs[0], nbs[1], nbs[2]), nbs[3], nbs[4], nbs[5])
        return 's', rert[0], Arc(Vector3D(nbs[0], nbs[1], nbs[2]), nbs[3], nbs[4], nbs[5])
    elif rert[1] == "polyline":
        nb = int(rert[2])
        return 'm', rert[0], nb  # 返回name和行数
    else:
        raise Exception("未知的数据类型%s" % rert[1])

def make_data_from_paragraph(paragraph:str,ignore_lines=3)->dict:

    hanghao_start=ignore_lines+1
    hanghao=0
    rt={}
    stringPatern="^\s*(\S+)\s+(\S+)\s+(.+)$"
    lines=paragraph.split("\n")
    num_of_line=0
    cur_line=""
    while True:
        if num_of_line==len(lines):
            break
        cur_line=lines[num_of_line]
        num_of_line+=1
        if num_of_line<=ignore_lines:
            continue#忽略的行
        if len(cur_line.replace(' ',''))==0:
            continue#空行跳过
        out=read_single_line(cur_line)
        if out[0] is 's':
            rt[out[1]]=out[2]
        else:
            name,cd=out[1:]
            segs=[]
            for i in range(1,cd+1):
                cur_line = lines[num_of_line]
                num_of_line += 1
                out1 = read_single_line(cur_line)
                assert  's' is out1[0],"已经是多行数据了，不允许在读取多行数据的时候，返回另一个多行数据"
                segs.append(out1[2])
            rt[name]=PolyLine(segs)

    return rt


def make_data_from_file(filepath,ignore_lines=3)->dict:
    assert os.path.isfile(filepath),"%s不存在"%filepath
    with open(filepath,'r') as f:
        return make_data_from_paragraph(f.read(),ignore_lines)

def toline(geomtric,name:str):
    assert isinstance(name,str),"类型错误"
    if isinstance(geomtric,Vector3D):
        return "%s vector %f,%f,%f"%(name,geomtric.x,geomtric.y,geomtric.z)
    elif isinstance(geomtric,LineSegment):
        return "%s lineseg %f,%f,%f,%f,%f,%f"%(name,
                                               geomtric.p1.x,geomtric.p1.y,geomtric.p1.z,
                                               geomtric.p2.x,geomtric.p2.y,geomtric.p2.z)
    elif isinstance(geomtric,Arc):
        return "%s arc %f,%f,%f,%f,%f,%f"%(name,geomtric.center.x,geomtric.center.y,geomtric.center.z,
                                           geomtric.radius,geomtric._angle1,geomtric.da)
    elif isinstance(geomtric,PolyLine):
        rt="%s polyline %d"%(name,len(geomtric.segs))
        for seg in geomtric:
            t=toline(seg,"_")
            rt+="\n"+t
        return rt
    else:
        raise Exception("未知的geometric类型")
    pass

if __name__ == '__main__':

    paragraph="""
    
    
    a1 float 12.32
    s1 string iam a dog
    v1 vector 123,23.1,3"""
    d=make_data_from_paragraph(paragraph)
    for i in d.items():
        print(i)
    print(d['v1'])