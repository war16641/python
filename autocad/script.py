"""
清楚带括号的标高中的括号，需先打开2018cad
"""
from pyautocad import Autocad,APoint
import re
pt="\(\d+\.\d+\)"
pt=re.compile(pt)
acad=Autocad()
acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)
for text in acad.iter_objects('Text'):
    r = pt.findall(text.TextString)
    if len(r)!=0:
        newtxt=text.TextString[1:-1]
        print('text: %s at: %s--->%s' %(text.TextString,text.InsertionPoint,newtxt))
        text.TextString=newtxt
