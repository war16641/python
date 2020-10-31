"""
对text中的数字求和
用于算钢筋总长度
"""
from pyautocad import Autocad,APoint

from autocad.toapoint import my_get_selection
import re

def small_script(txt) -> float:
    """

    @param txt: 数字 或者 含有 均+数字
    @return: float
    """
    try:
        f = float(txt)
        return f
    except ValueError:
        l = re.findall("均(-?\d+\.?\d*e?-?\d*?)", txt)
        if len(l) > 0:
            return float(l[0])
        else:
            raise ValueError


acad=Autocad(create_if_not_exists=True)
# acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)


# lst=acad.get_selection("选择执行：")
lst=my_get_selection(acad,"选择文字：")
totallength=0.
for i in lst:
    f=small_script(i.TextString)
    totallength+=f
acad.prompt("和=%.3f"%totallength+"共%d个\n"%len(lst))
