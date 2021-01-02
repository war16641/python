import win32gui
import re


#
# def get_all_hwnd(hwnd, mouse):
#     if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
#         hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})
#
#
# def
#
# win32gui.EnumWindows(get_all_hwnd, 0)


class MyHwnd:
    hwnd_title={}#保存get_all_hwnd的结果

    @staticmethod
    def __get_all_hwnd(hwnd, mouse):
        if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
            MyHwnd.hwnd_title.update({hwnd: win32gui.GetWindowText(hwnd)})

    @staticmethod
    def get_all_hwnd()->dict:
        """
        获取所有标题及其句柄
        @return:
        """
        MyHwnd.hwnd_title.clear()
        win32gui.EnumWindows(MyHwnd.__get_all_hwnd, 0)
        return MyHwnd.hwnd_title.copy()


    @staticmethod
    def find_hwnd_by_title(rex:str)->int:
        """
        通过标题获取句柄
        @param rex: 标题的正则表达式
        @return:
        """
        d=MyHwnd.get_all_hwnd()
        for h,t in d.items():
            flag = len(re.findall(rex, t)) > 0
            if flag is True:
                return h
        return 0


# for h, t in hwnd_title.items():
#     if t is not "":
#         print(([h], [t]))
