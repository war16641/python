"""
存放一些动作
"""
import wmi
import ctypes
WM_APPCOMMAND=0X319
user32=ctypes.windll.user32
APPCOMMAND_VOLUME_DOWN=0X090000
APPCOMMAND_VOLUME_UP=0X080000







def shutdown_screen():
    """显示器亮度为0"""
    c = wmi.WMI(namespace='root\WMI')
    a = c.WmiMonitorBrightnessMethods()[0]
    a.WmiSetBrightness(Brightness=50, Timeout=480)



def set_speaker_volumn(flag="min"):
    """音量设置 min为0，max为100%"""
    hwnd=user32.GetForegroundWindow()
    if flag=="min":
        cmd=APPCOMMAND_VOLUME_DOWN
    elif flag=="max":
        cmd=APPCOMMAND_VOLUME_UP
    else:
        raise Exception("参数错误")
    for _ in range(50):
        user32.PostMessageA(hwnd,WM_APPCOMMAND,0,cmd)

if __name__ == '__main__':
    set_speaker_volumn("max")