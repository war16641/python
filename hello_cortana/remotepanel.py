"""
这个文件自动打开remotepanle的相关程序
"""
import psutil,os
from ocr.windows_automation import find_process_by_name
import time
import subprocess
def foo(name,wait_time=3):
    t=find_process_by_name(name=name)
    if t is None:
        print('%s不存在'%name)
        return
    print('正在终止%s...'%name)
    os.system("taskkill /pid %d /f"%t.pid)#强制终止
    time.sleep(wait_time)#等
    if find_process_by_name(name=name) is None:
        print('成功终止%s'%name)
    else:
        print('终止%s失败'%name)



if __name__ == '__main__':
    foo(name='remotepanel.exe')
    foo(name='adb.exe')
    subprocess.Popen(r"G:\software\remotepanel\Remote Panel\RemotePanel.exe")
    time.sleep(1)
    os.system(r"G:\software\aida64extreme_build_5157_xbnj9z3mdy\aida64.exe")
