"""
按文件名中数字依次用ue打开
"""
import os
import re
import subprocess
import time

from myfile import collect_all_filenames, append_file

transition_txt="————————————————以下为TZ输出——————————————————————\n"
pn=r"E:\铁二院\工作\初步设计\DK100+066梁家庄大桥\t1"#路径名
fm1="^\d+$"
lst1=[]
collect_all_filenames(directory=pn,
                 rex=fm1,
                      lst=lst1,
                 )
pt=r"-?\d+\.?\d*e?-?\d*?"#匹配数字
jihe=[]
for f in lst1:
    (pathname, tmpfilename) = os.path.split(f)
    l = re.findall(pt, tmpfilename)  # 匹配桥名
    assert len(l)==1,"必须要找到数字"
    jihe.append((float(l[0]),f,))
jihe.sort(key=lambda x:x[0])
#打开ue
uefile=r"F:\other_software\UltraEdit\uedit64.exe"
for xuhao,i in enumerate(jihe):
    print("打开%s"%i[1])
    # os.system(uefile+ " "+i[1])
    subprocess.Popen(uefile+ " "+i[1], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if xuhao==0:
        time.sleep(5)
    else:
        time.sleep(1)