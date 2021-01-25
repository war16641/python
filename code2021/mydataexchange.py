
import re

from vector3d import Vector3D


def make_data_from_paragraph(paragraph:str,ignore_lines=3)->dict:
    hanghao_start=ignore_lines+1
    hanghao=0
    rt={}
    stringPatern="^\s*(\S+)\s+(\S+)\s+(.+)$"
    for i,cur_line in enumerate(paragraph.split("\n")):
        if i<ignore_lines:
            continue#忽略的行
        rert = re.findall(stringPatern, cur_line)
        if len(rert)==0:
            raise Exception("错误的行：%s"%cur_line)
        rert=rert[0]
        if rert[1]=="float":
            rt[rert[0]]=float(rert[2])
        elif rert[1]=="string":
            rt[rert[0]] = rert[2]
        elif rert[1]=="vector":
            nbs=rert[2].split(",")
            nbs=[float(x) for x in nbs]
            rt[rert[0]]=Vector3D.make_from_list(nbs)
        else:
            raise Exception("未知的数据类型%s"%rert[1])
    return rt



if __name__ == '__main__':

    paragraph="""
    
    
    a1 float 12.32
    s1 string iam a dog
    v1 vector 123,23.1,3"""
    d=make_data_from_paragraph(paragraph)
    for i in d.items():
        print(i)
    print(d['v1'])