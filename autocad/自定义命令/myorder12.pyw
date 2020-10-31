"""
选取一些直线
输出最短 最长和平均长度

"""
from statistics import mean

from pyautocad import Autocad,APoint

from autocad.toapoint import my_get_selection

acad=Autocad(create_if_not_exists=True)
# acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)


# lst=acad.get_selection("选择执行：")
lst=my_get_selection(acad,"选择zx：")
ls=[i.Length for i in lst]
minv=min(ls)
maxv=max(ls)
meanv=mean(ls)
print("%.3f~%.3f,平均%.3f"%(minv,maxv,meanv))
print("共%d个"%len(lst))
acad.prompt("%.3f~%.3f,平均%.3f"%(minv,maxv,meanv)+"共%d个\n"%len(lst))
