"""
角度处理
"""

from math import pi
pi2=2*pi






class AngleTool:

    @staticmethod
    def format(x):
        """
        x的等效角
        @param x:
        @return: [0,2PI)
        """
        return x % pi2

    @staticmethod
    def format1(x):#[-PI,PI)
        t=x%pi2
        if t>pi:
            return t-pi2
        else:
            return t

    #下面两个函数 转换弧度与角度
    @staticmethod
    def toR(x):
        return x/180.0*pi
    @staticmethod
    def toD(x):
        return x/pi*180.0








if __name__ == '__main__':
    print(AngleTool.toD(AngleTool.format1(AngleTool.toR(-100))))