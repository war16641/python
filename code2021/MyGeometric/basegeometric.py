

import abc

from vector3d import Vector3D


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
    def start_point(self)->Vector3D:
        pass

    @property
    @abc.abstractmethod
    def end_point(self)->Vector3D:
        pass

    @property
    @abc.abstractmethod
    def mid_point(self)->Vector3D:
        pass

    @abc.abstractmethod
    def mirror(self,elo):
        pass

    @abc.abstractmethod
    def reverse(self):
        pass

    @abc.abstractmethod
    def copy(self):
        pass

    @abc.abstractmethod
    def offset(self):
        pass
