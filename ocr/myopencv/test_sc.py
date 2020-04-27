
import os
import time

import ocr.windows_automation as wa
import cv2
import numpy as np
import win32gui
import win32con
import win32api
import ctypes
import ctypes.wintypes
import threading

from ocr.imagtools import snap_screen
from ocr.myopencv.scwaiguai import match_template


class myScreenShot(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("\n***start of " + str(self.name) + "***\n")
        sreenShotMain()
        print("\n***end of " + str(self.name) + "***\n")


class myHotKey(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print("\n***start of " + str(self.name) + "***\n")
        hotKeyMain()
        print("\n***end of " + str(self.name) + "***\n")

exitControl_command=False
shotControl_command=False
def sreenShotMain():
    global shotControl_command
    global exitControl_command
    print("start")
    template = cv2.imread(r"D:\a\protoss_bg0.png")
    while (True):
        if exitControl_command == True:
            exitControl_command = False
            print("exit this program!")
            return
        if shotControl_command == True:
            # screen shot
            print('开始新捕捉...')
            im = snap_screen(wait_time=0)
            # im.show()
            image = np.array(im)
            lcs = match_template(image, template, max_counter=30, val_valve=0.40, annotation=False,return_center=True)
            print("找到bb%d个：%s" % (len(lcs), lcs.__str__()))
            for pt in lcs:
                wa.mouse_click(pt[0], pt[1])
                time.sleep(0.005)
                wa.key_input('zzzzz', input_inteval=0.02)
            shotControl_command = False


def hotKeyMain():
    global shotControl_command
    global exitControl_command
    user32 = ctypes.windll.user32
    template98 = cv2.imread(r"D:\a\protoss_bg0.png")
    template99 = cv2.imread(r"D:\a\protoss_bg0.png")
    while (True):
        if not user32.RegisterHotKey(None, 98, 0, win32con.VK_F1):  # win+f9=screenshot
            print("Unable to register id", 98)
        if not user32.RegisterHotKey(None, 99, 0, win32con.VK_F2):  # win+f10=exit program
            print("Unable to register id", 99)
        try:
            msg = ctypes.wintypes.MSG()
            if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    if msg.wParam == 99:
                        print('99')
                        # screen shot
                        print('开始新捕捉...')
                        im = snap_screen(wait_time=0)
                        # im.show()
                        image = np.array(im)
                        lcs = match_template(image, template99, max_counter=30, val_valve=0.40, annotation=False,
                                             return_center=True)
                        print("找到bb%d个：%s" % (len(lcs), lcs.__str__()))
                        for pt in lcs:
                            wa.mouse_click(pt[0], pt[1])
                            time.sleep(0.005)
                            wa.key_input('zzzzz', input_inteval=0.02)
                        # exitControl_command = True
                        # return
                    elif msg.wParam == 98:
                        print('98')
                        # screen shot
                        print('开始新捕捉...')
                        im = snap_screen(wait_time=0)
                        # im.show()
                        image = np.array(im)
                        lcs = match_template(image, template98, max_counter=30, val_valve=0.40, annotation=False,
                                             return_center=True)
                        print("找到bb%d个：%s" % (len(lcs), lcs.__str__()))
                        for pt in lcs:
                            wa.mouse_click(pt[0], pt[1])
                            time.sleep(0.005)
                            wa.key_input('zzzzz', input_inteval=0.02)
                        # shotControl_command = True
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
        finally:
            del msg
            user32.UnregisterHotKey(None, 98)
            user32.UnregisterHotKey(None, 99)


if __name__ == "__main__":
    thread_screenShot = myScreenShot("thread_screenShot")
    thread_hotKey = myHotKey("thread_hotKey")
    thread_screenShot.start()
    thread_hotKey.start()

    thread_hotKey.join()
    thread_screenShot.join()
