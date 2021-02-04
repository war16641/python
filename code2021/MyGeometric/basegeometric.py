

import abc

class BaseGeometric(metaclass=abc.ABCMeta):
    """
    所有图素的基类
    必须实现下列方法
    """
    @property
    @abc.abstractmethod
    def length(self):
        pass

    @property
    @abc.abstractmethod
    def start_point(self):
        pass

    @property
    @abc.abstractmethod
    def end_point(self):
        pass
