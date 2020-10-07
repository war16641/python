"""
清楚带括号的标高中的括号，需先打开2018cad
"""
from pyautocad import Autocad,APoint
import re
pt1="\((.+)\)" #英文括号
pt1=re.compile(pt1)
pt2="（(.+)）" #中文匹括号
pt2=re.compile(pt2)
acad=Autocad()
acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)
for text in acad.iter_objects('Text'):
    r = pt1.findall(text.TextString)
    if len(r)!=0:
        newtxt=r[0]
        print('text: %s at: %s--->%s' %(text.TextString,text.InsertionPoint,newtxt))
        text.TextString=newtxt
        continue
    r=pt2.findall(text.TextString)
    if len(r)!=0:
        newtxt=r[0]
        print('text: %s at: %s--->%s' %(text.TextString,text.InsertionPoint,newtxt))
        text.TextString=newtxt
        continue