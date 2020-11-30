"""
把tz输入输出合并到一个文件
要求它们在同一个文件夹内
通过正则表达式指定这两类文件
合并后的文件会在第一个文件中追加，执行前最好做一个备份
"""
import os
import re

from myfile import collect_all_filenames, append_file

transition_txt="————————————————以下为TZ输出——————————————————————\n"
pn=r"E:\铁二院\工作\初步设计\DK100+066梁家庄大桥\t1"#路径名
fm1="^\d+$"
lst1=[]
fm2="^\d+zj\.RST$"
lst2=[]
collect_all_filenames(directory=pn,
                 rex=fm1,
                      lst=lst1,
                 )
collect_all_filenames(directory=pn,
                 rex=fm2,
                      lst=lst2,
                 )
print(lst1)
print(lst2)
#开始匹配这两个列表
dic1={}
pt="\d+"
for pn1 in lst1:
    pathname, tmpfilename = os.path.split(pn1)
    l = re.findall(pt, tmpfilename)  # 查找数字
    assert len(l)>0,'必须在文件名（%s）中找到数字。'%tmpfilename
    nb=float(l[0])
    dic1[nb]=pn1#以数字为键，路径作为值
ct=0
for pn2 in lst2:
    pathname, tmpfilename = os.path.split(pn2)
    l = re.findall(pt, tmpfilename)  # 查找数字
    assert len(l)>0,'必须在文件名（%s）中找到数字。'%tmpfilename
    nb = float(l[0])
    if nb in dic1.keys():
        append_file(file1=dic1[nb],file2=pn2,transition_txt=transition_txt)
        ct+=1
    else:
        print("文件（%s）不存在对应文件"%pn2)
print("lst1中含有%d个文件"%len(lst1))
print("lst2中含有%d个文件"%len(lst2))
print("共匹配%d个文件。"%ct)