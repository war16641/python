import logging
from typing import overload
from GoodToolPython.mybaseclasses.singleton import Singleton
from colorama import Fore, Style

logging.basicConfig(level=logging.INFO,  # 必须设置为debug，后面logger的设置才有效
                    # format='%(message)s')#只显示等级和内容
                    format='%(levelname)10s: %(message)s')  # 只显示等级和内容





class MyLogger:
    """
    自定义logger
    单例模式
    实现了不同level用不同颜色区分
    默认格式是 level名+内容
    level名可以隐藏

    """
    only=None #type:MyLogger#如果设置了only只有only能够输出debug信息
    disable_all_logger=False #当这个值为true时 没有人能输出debug消息
    fortxt={(False,False):"%(name)s:[%(levelname)10s] %(message)s",#第一个代表是否隐藏name 第二个代表是否隐藏levelname
            (False,True):"%(name)s:%(message)s",
            (True,False):"[%(levelname)10s] %(message)s",
            (True,True):"%(message)s",}
    levelname={'debug':logging.DEBUG,
               'info':logging.INFO,
               'warning':logging.WARNING,}

    _instance_dic={}

    @staticmethod
    def make(name='nyh'):
        """建议使用make获得mylogger 否则可能会导致在多次import后出错"""
        if name in MyLogger._instance_dic.keys():
            return MyLogger._instance_dic[name]#已经有了就返回这个实例
        else:
            t=MyLogger(name)
            MyLogger._instance_dic[name]=t
            return t

    def __init__(self,name='nyh'):
        self.logger = logging.getLogger(name)
        if len(self.logger.handlers) !=0:
            raise Exception("logger（%s）已存在。"%name)#要求新建时 name不一样
        self.logger.propagate=False
        self._hidelevel=True
        self._hidename=True
        format1 = logging.Formatter(MyLogger.fortxt[self.fortxt_key])
        sh=logging.StreamHandler()
        self.logger.addHandler(sh)
        self.logger.handlers[0].setFormatter(format1)

    def setLevel(self, lv):
        """

        @param lv: 只能是logging中的debug info等
        @return:
        """
        assert lv in MyLogger.levelname.keys(),'无效levelname'
        self.logger.setLevel(MyLogger.levelname[lv])

    def debug(self, txt):
        if MyLogger.disable_all_logger:
            return
        if MyLogger.only is not None and MyLogger.only != self:
            return#设置了only，只有only才能输出debug信息
        self.logger.debug(Fore.BLACK + txt.__str__() + Style.RESET_ALL)

    def info(self, txt):
        self.logger.info(Fore.BLACK + txt.__str__() + Style.RESET_ALL)#debug info 默认黑色

    def warning(self, txt):
        self.logger.warning(Fore.YELLOW + txt.__str__() + Style.RESET_ALL)#警告是黄色 比警告等级更高的错误 会使用raise就不在此处设置了
    def error(self, txt):
        self.logger.error(Fore.RED + txt.__str__() + Style.RESET_ALL)#警告是黄色 比警告等级更高的错误 会使用raise就不在此处设置了


    @property
    def fortxt_key(self):
        return (self._hidename,self.hide_level)

    @property
    def hide_name(self):
        return self._hidename
    @hide_name.setter
    def hide_name(self,v):
        if v == self._hidename:
            return
        else:
            self._hidename = v
            format1 = logging.Formatter(MyLogger.fortxt[self.fortxt_key])
            self.logger.handlers[0].setFormatter(format1)  # 这个默认的handler掌管屏幕输出


    @property
    def hide_level(self):
        return self._hidelevel
    @hide_level.setter #是否隐藏输出内容中的level名
    def hide_level(self,v):
        if v == self._hidelevel:
            return
        else:
            self._hidelevel = v
            format1 = logging.Formatter(MyLogger.fortxt[self.fortxt_key])
            self.logger.handlers[0].setFormatter(format1)  # 这个默认的handler掌管屏幕输出



if __name__ == '__main__':
    loger = MyLogger()
    loger.setLevel('debug')

    # logger.setLevel(logging.DEBUG)  # Log等级总开关

    loger.debug("苍井空")
    loger.info("麻生希")
    loger.warning("小泽玛利亚")
    # format1 = logging.Formatter('%(message)s')
    # loger.logger.handlers[0].setFormatter(format1)
    loger.hide_level=False
    loger.debug("苍井空")
    loger.info("麻生希")
    loger.error("小泽玛利亚")
    # logger.error(Fore.RED+"桃谷绘里香"+Style.RESET_ALL)
    # logger.critical("泷泽萝拉")
