from typing import Tuple

from code2021.MyGeometric.basegeometric import BaseGeometric
from vector3d import Vector3D, Line3D, get_trans_func, ParametricEquationOfLine
import matplotlib.pyplot as plt
import numpy as np


class Ray:
    def __init__(self,base_pt:Vector3D,direct:Vector3D):
        assert isinstance(base_pt,Vector3D) and isinstance(direct,Vector3D)\
        ,"类型错误"
        self.base_pt=base_pt.copy()
        self.direct=direct.copy()
        self.line=Line3D(direct.copy(),base_pt.copy())#射线对应的直线

    def __contains__(self, item):
        assert isinstance(item,Vector3D),"类型错误"
        t=item in self.line
        if t is False:
            return False
        p=self.line.get_parameter(item)
        if p>=0:
            return True
        else:
            return  False#在射线的反向上