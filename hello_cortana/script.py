import psutil,os
from ocr.windows_automation import find_process_by_name
import time
import subprocess

if __name__ == '__main__':
    while True:
        t = find_process_by_name(name='acad1.exe')
        if t is None:
            break
        else:
            print("等待cad关闭。。。")
            time.sleep(0.2)
    #开始关闭 autodesk desktop app
    t = find_process_by_name(name='AdAppMgrSvc.exe')
    os.system("taskkill /pid %d /f" % t.pid)  # 强制终止
    ct=0
    while True:
        t = find_process_by_name(name='AdAppMgrSvc.exe')
        if t is None:
            break
        else:
            ct+=1
            if ct>=10:
                raise Exception("无法关闭 autodesk desktop app")
            time.sleep(0.1)

    #开始关闭 Autodesk infocenter
    t = find_process_by_name(name='WSCommCntr4.exe')
    os.system("taskkill /pid %d /f" % t.pid)  # 强制终止
    ct = 0
    while True:
        t = find_process_by_name(name='WSCommCntr4.exe')
        if t is None:
            break
        else:
            ct += 1
            if ct >= 10:
                raise Exception("无法关闭Autodesk infocenter")
            time.sleep(0.1)

    print('两个进程完全关闭，程序结束。')