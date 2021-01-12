"""
里程
"""
import re
from typing import overload, Tuple


class Mileage:

    @overload
    def __init__(self):
        pass

    @overload
    def __init__(self, string: str):
        pass

    def __init__(self, string: str = None):
        self.guanhao = ""
        self.number = 0.0
        if string is None:
            return
        assert isinstance(string, str), "必须为str"
        self.guanhao, self.number = Mileage.get_guanhao_and_mileage(string)

    @staticmethod
    def get_guanhao_and_mileage(string: str) -> Tuple[str, float]:
        """
        从文本中读取里程和冠号
        如：DZ1k100+123.1  DZ1k100
        @param string:
        @return:
        """
        p1 = re.compile(r'([\w]+[kK])(\d+)\+?(\d*\.?\d*)', re.S)
        rt = re.findall(p1, string)
        if len(rt) == 0:
            raise Exception("错误的里程格式:%s" % string)
        rt = rt[0]
        rt = list(rt)
        if len(rt[2]) == 0:  # 如果没有读到千米下的数值
            rt[2] = "0"
        return rt[0], float(rt[1]) * 1000 + float(rt[2]),

    pass
