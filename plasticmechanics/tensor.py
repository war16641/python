from copy import deepcopy
from typing import Union

import numpy as np
from math import *
from numpy.core._multiarray_umath import ndarray
from numpy.linalg import norm,det  # 求二范数

from GoodToolPython.mybaseclasses.singleton import Singleton
from GoodToolPython.mybaseclasses.todoexception import ToDoException
from GoodToolPython.plasticmechanics.usefulscripts import *
from GoodToolPython.vector3d import Vector3D

tol_for_eq = 1e-6  # 判断相等的误差


class LetterDistributor(Singleton):
    """
    字母分配机
    将字母按letters中的顺序一一分配出去
    """

    def init(self):
        # # 如果已经构造过一次了，不执行首次初始化
        # if 'letters' in self.__dict__.keys():
        #     return
        self.letters = ['i', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's']
        self.max_index = len(self.letters) - 1
        self.used_number = 0

    def initial(self):
        self.used_number = 0  # 已经使用的字母个数

    def get_letters(self, number=1):
        """
        获取字母 多个字母形成字符串
        :param number: 字母个数
        :return: str
        """
        if number + self.used_number > self.max_index + 1:
            raise Exception("字母表的剩余个数不够。")
        r = ''
        for i in range(self.used_number, self.used_number + number):
            r += self.letters[i]
        self.used_number += number
        return r

    def last_letters(self, number=1):
        # 上一个分配出去的字母
        assert self.used_number - number >= 0, '字母还未分配'
        r = ''
        for i in range(self.used_number - number, self.used_number):
            r += self.letters[i]
        return r

    def next_letters(self, number=1):
        # 即将分配出去的字母
        assert self.used_number + number - 1 < self.max_index + 1, '字母表中字母分配完毕。'
        r = ''
        for i in range(self.used_number, self.used_number + number):
            r += self.letters[i]
        return r


class SubscriptIteration:
    """
    下标迭代器 每一个下标可取0 1 2
    order指定有多少个下标

    """

    def __init__(self, order=1):
        # assert order>0
        self.order = order

    def initial(self):
        self.current = []
        for i in range(self.order):
            self.current.append(0)
        self.current[-1] -= 1

    def add_one(self, index):
        if self.current[index] == 2:
            if index == 0:
                raise StopIteration
            self.current[index] = 0
            return self.add_one(index - 1)
        self.current[index] += 1
        return self.current

    def __iter__(self):
        self.initial()
        return self

    def __next__(self):  # 返回的是下标组成的列表
        return self.add_one(self.order - 1)


def count_each_char(string):
    """
    对字符串中各个字母出现的次数计数
    :param string:
    :return: counter,sequence
            counter:字典 各个字母出现次数
            sequence:列表 各个字母出现顺序
    """
    counter = {}
    sequence = []
    for i in string:
        if i not in counter:
            counter[i] = 1
            sequence.append(i)
        else:
            counter[i] += 1
    return counter, sequence


class CartesianCoordinateSystem:
    """简单笛卡尔坐标系 标准正交基 右手法则
    :type basic_vectors:tuple[Vector3D]
    """

    def __init__(self, basic_vectors: Union[tuple, np.ndarray]):
        """

        :param basic_vectors: 可以是3个向量组成的元组 可以是3*3array 每一列为一个向量
        """

        # 如果参数为数组
        if isinstance(basic_vectors, np.ndarray):
            if basic_vectors.shape == (3, 3):
                v1 = Vector3D.make_from_array(basic_vectors[:, 0])
                v2 = Vector3D.make_from_array(basic_vectors[:, 1])
                v3 = Vector3D.make_from_array(basic_vectors[:, 2])
                basic_vectors = (v1, v2, v3,)
            else:
                raise Exception("参数错误")

        assert isinstance(basic_vectors, tuple)
        assert len(basic_vectors) == 3
        for v in basic_vectors:
            assert abs(v.modulus - 1) < Vector3D.tol_for_eq, '模要求为1'
        v1, v2, v3 = basic_vectors
        assert abs(v1.mixed_product(v2, v3) - 1) < Vector3D.tol_for_eq,'不是右手法则下的标准正交基'
        self.basic_vectors = deepcopy(basic_vectors)

    def get_coordinates(self, v):
        """
        v是在世界坐标系下的坐标
        :param v:
        :return:
        """
        assert isinstance(v, Vector3D)
        return v.get_coordinates_under_cartesian_coordinates_system(self.basic_vectors)

    def get_inverse_conversion_coefficient(self, new) -> np.ndarray:
        """
        获取逆变转换系数 从旧坐标系到新坐标系
        :param new: 新坐标系
        :return:
        """
        icc = np.zeros((3, 3))
        # icc[0,0]=cos(self.basic_vectors[0].angle(new.basic_vectors[0]))
        for i in range(3):
            for j in range(3):
                icc[i, j] = cos(self.basic_vectors[i].angle(new.basic_vectors[j]))
        return icc

    def __eq__(self, other):
        # 判断两个坐标系是否相等 other 可以是空
        if other == None:
            return False
        assert isinstance(other, CartesianCoordinateSystem)
        for i in range(3):
            if self.basic_vectors[i] != other.basic_vectors[i]:
                return False
        return True

    def __str__(self):
        return "%s\n%s\n%s" % (self.basic_vectors[0], self.basic_vectors[1], self.basic_vectors[2])


# 世界坐标系
global_ccs = CartesianCoordinateSystem((Vector3D(1, 0, 0),
                                        Vector3D(0, 1, 0),
                                        Vector3D(0, 0, 1),))


class SummationMultiplier:
    """爱因斯坦求和 乘子"""

    def __init__(self, tensor, index):
        self.tensor = tensor
        self.index = index
        _, self._sequence = count_each_char(index)  # 记录字母出现的顺序

    def get_component_value(self, dic) -> float:
        """
        返回tensor中元素
        :param dic: 键是字母 值是索引 键
        :return:
        """
        assert isinstance(dic, dict)
        index_list = []
        for k in self._sequence:
            assert k in dic.keys(), 'dic中未找到key'
            index_list.append(dic[k])
        if len(index_list) == 1:
            return self.tensor[index_list[0]]
        elif len(index_list) == 2:
            return self.tensor.__getitem__(tuple(index_list))
        else:
            raise Exception("参数错误")


def summation(muliplier_list):
    """
    爱因斯坦求和
    :param muliplier_list: 乘子组成的列表
    :rtype:Tensor
    """
    assert isinstance(muliplier_list, list)
    # 检查张量的坐标系是否相同
    last_ccs = None
    for m in muliplier_list:
        this_ccs = m.tensor.ccs
        if last_ccs == None:
            last_ccs = this_ccs
            continue
        assert last_ccs == this_ccs, '坐标系不同，不能进行爱因斯坦求和运算。'
        last_ccs = this_ccs

    index_list = [x.index for x in muliplier_list]
    index_string = ''  # 把所有的index放进一个字符串
    for index in index_list:
        index_string += index
    counter, seq = count_each_char(index_string)
    free_index_list = [ind for ind in counter.keys() if counter[ind] == 1]  # 自由标
    fake_index_list = [ind for ind in counter.keys() if counter[ind] == 2]  # 哑标
    t = [ind for ind in counter.keys() if counter[ind] > 2]
    if len(t) > 0:
        raise Exception("指标次数不能出现三次及以上")
    if len(free_index_list) > 2:
        raise ToDoException("暂不支持三阶及以上的张量计算")
    order = len(free_index_list)  # 生成张量的阶数
    r = Tensor.zeros(order=order)  # 先生成零元素张量

    num_of_fake = len(fake_index_list)  # 亚指标个数
    free_iter = SubscriptIteration(order=order)
    fake_iter = SubscriptIteration(order=num_of_fake)
    if order == 0:  # 零阶张量
        sumv = 0.
        for j in fake_iter:
            dic = dict(zip(free_index_list + fake_index_list, [] + j))
            prod = 1.
            for mul in muliplier_list:
                prod *= mul.get_component_value(dic)
            sumv += prod
        r.component = sumv
    else:
        # 生成的张量为一阶或者二阶

        for i in free_iter:
            sumv = 0.
            for j in fake_iter:
                dic = dict(zip(free_index_list + fake_index_list, i + j))
                prod = 1.
                for mul in muliplier_list:
                    prod *= mul.get_component_value(dic)
                sumv += prod
            r[i] = sumv
    return r


class Tensor:
    """张量
    :type component:ndarray|float 当张量阶数为0时，component是float其余是个3*1 或3*3矩阵
    """

    def __init__(self, component, ccs: CartesianCoordinateSystem = global_ccs):
        """

        :param component: 可以是ndarray 要求其格式为长度是3 或者shape是3*3 还可以是长度为3数值列表
        :param ccs: 坐标系
        """

        # 先复制一份 当矩阵较大时可能会影响性能 这一条语句是偏于安全的做法
        component=deepcopy(component)
        ccs=deepcopy(ccs)

        assert isinstance(ccs, CartesianCoordinateSystem)

        # 长度为3数值列表
        if isinstance(component, list):
            if len(component) == 3 and isinstance(component[0], (int, float)):
                component = np.array(component)
            else:
                raise Exception("参数错误。")

        if isinstance(component, (float, int)):  # 零阶
            self.order = 0
            self.component = component
        elif isinstance(component, np.ndarray):
            if component.size == 3:  # 一阶
                self.order = 1
                self.component = component.reshape(3, 1)  # 一阶张量格式为3*1
            elif component.shape == (3, 3):  # 二阶  component.size==9 and len(component.shape)==2:
                self.order = 2
                self.component = component
            else:
                raise Exception("参数错误")
        else:
            raise Exception("参数错误")
        self._ccs = ccs

    def __str__(self):
        if self.order == 0:
            return "%f" % self.component
        elif self.order == 1:
            return "%f,%f,%f\n坐标系\n%s" % (self.component[0], self.component[1], self.component[2], self._ccs)
        elif self.order == 2:
            return "二阶\n%s\n坐标系\n%s" % (self.component.__str__(), self._ccs)

    @property
    def ccs(self):
        return self._ccs

    @ccs.setter
    def ccs(self, new_ccs):
        """设定新的坐标系"""
        assert isinstance(new_ccs, CartesianCoordinateSystem)
        new_ccs=deepcopy(new_ccs)#复制新的对象
        if new_ccs == self._ccs:
            return  # 与原坐标系相同
        # 不同就要进行分量的重新计算
        if self.order == 0:
            return  # 零阶张量与坐标系无关
        elif self.order == 1:
            beta1 = self._ccs.get_inverse_conversion_coefficient(new_ccs)
            beta = Tensor(component=beta1, ccs=new_ccs)
            self._ccs = new_ccs
            t = summation([beta['ji'], self['j']])
            self.component = t.component

        elif self.order == 2:
            beta1 = self._ccs.get_inverse_conversion_coefficient(new_ccs)
            beta = Tensor(component=beta1, ccs=new_ccs)
            self._ccs = new_ccs
            t = summation([beta['ri'], beta['sj'], self['rs']])
            self.component = t.component

        else:
            raise Exception("未知错误")

    def __getitem__(self, item):
        # print(item)
        # 如果item是数组成的list转换为tuple
        if isinstance(item, list):
            if isinstance(item[0], (int, float)):
                if len(item) == 1:
                    item = item[0]
                else:
                    item = tuple(item)

        if isinstance(item, int):
            if self.order == 1:
                return float(self.component[item])
            else:
                raise Exception("参数错误。单个索引只支持一阶张量。")
        elif isinstance(item, tuple) and len(item) == 2:
            i, j = item
            assert isinstance(i, int)
            assert isinstance(j, int)
            if self.order == 2:
                return float(self.component[i, j])
            else:
                raise Exception("参数错误。双索引支持二阶张量。")
        elif isinstance(item, str):  # 返回爱因斯坦求和乘子
            return SummationMultiplier(self, item)

    def __setitem__(self, item, value):
        """
        指定元素的值
        :param key:
        :param value:
        :return:
        """
        # 如果item是数组成的list转换为tuple
        if isinstance(item, list):
            if isinstance(item[0], (int, float)):
                if len(item) == 1:
                    item = item[0]
                else:
                    item = tuple(item)

        assert isinstance(value, (int, float))
        if isinstance(item, int):
            if self.order == 1:
                self.component[item] = value
            else:
                raise Exception("参数错误。单个索引只支持一阶张量。")
        elif isinstance(item, tuple) and len(item) == 2:
            i, j = item
            assert isinstance(i, int)
            assert isinstance(j, int)
            if self.order == 2:
                self.component[i, j] = value
            else:
                raise Exception("参数错误。双索引支持二阶张量。")

    @staticmethod
    def zeros(order=0, ccs=global_ccs):
        """
        生成0元素张量
        :param order:指定阶数 不能大于2
        :param ccs:
        :return: 张量
        """
        if order == 0:
            return Tensor(component=0,
                          ccs=ccs)
        elif order == 1:
            return Tensor(component=np.zeros((3, 1)),
                          ccs=ccs)
        elif order == 2:
            return Tensor(component=np.zeros((3, 3)),
                          ccs=ccs)
        else:
            raise Exception("参数错误。")

    def diagonalize(self) -> None:
        """
        对角化 只针对二阶张量
        :return:
        """
        assert self.order == 2, '只有2阶张量可以对角化'
        _, vector = eigenvalue_problem(self.component)
        new = CartesianCoordinateSystem(vector)
        self.ccs = new

    def __eq__(self, other):
        """

        :param other: tensor或者none
        :return:
        """
        if other == None:
            return False

        # 与数比较 此时只能是0阶
        if isinstance(other, (int, float)):
            if self.order != 0:
                return False
            return abs(self.component - other) < tol_for_eq

        assert isinstance(other, Tensor)
        item = deepcopy(other)
        item.ccs = self.ccs
        if self.order != item.order:
            return False
        if self.order == 0:
            return abs(self.component - item.component) < tol_for_eq
        elif self.order == 1 or self.order == 2:
            t = self.component - item.component
            return norm(t) < tol_for_eq
        else:
            raise Exception("未知错误")

    def __add__(self, other):
        assert isinstance(other, Tensor)
        assert self.order == other.order, '阶数不同不能加减'
        r = deepcopy(self)
        item = deepcopy(other)
        item.ccs = r.ccs
        r.component = r.component + item.component
        return r

    def __sub__(self, other):
        assert isinstance(other, Tensor)
        assert self.order == other.order, '阶数不同不能加减'
        r = deepcopy(self)
        item = deepcopy(other)
        item.ccs = r.ccs
        r.component = r.component - item.component
        return r

    def __rmul__(self, other):
        r = deepcopy(self)
        if isinstance(other, (float, int)):
            r.component = r.component * other
            return r
        else:
            raise Exception("参数错误")

    @staticmethod
    def kronecker(ccs=global_ccs):
        """
        2阶kronecker张量
        :param ccs: 默认是世界坐标系
        :return:
        """
        assert isinstance(ccs, CartesianCoordinateSystem)
        A = np.array([[1, 0, 0],
                      [0, 1, 0],
                      [0, 0, 1]])
        return Tensor(component=A, ccs=ccs)

    def contraction(self, other, arg1: str = '.'):
        """
        张量的缩并 这里只实现了点积 双点积
        计算的方式 使用kronecker张量实现
        :param other: 另一个张量
        :param arg1: 指定点积 . 或者 双点积 ..
        :return:
        :rtype: Tensor
        https://onedrive.live.com/redir?resid=C917E8FBBE646EE0%215516&page=Edit&wd=target%28%E6%9D%90%E6%96%99%E5%8A%9B%E5%AD%A6.one%7Ca99c90f4-9476-f94f-90db-e5b45d142dae%2F%E5%BC%A0%E9%87%8F%E8%BF%90%E7%AE%97%7C915b1112-2f09-c644-a2ba-d931cb24a94e%2F%29
        """
        assert isinstance(other, Tensor)
        assert other.order >= 1 and self.order >= 1, '参与缩并的张量阶数必须大于0'

        other = deepcopy(other)
        other.ccs = self.ccs  # 计算前统一坐标系
        ld = LetterDistributor()
        ld.initial()
        if arg1 == 'dot' or arg1 == '.':  # 点积
            m1 = self[ld.get_letters(self.order)]
            subscript_for_kronecker = ld.last_letters() + ld.next_letters()  # kronecker张量的下标 负责连接前面两个张量
            m2 = other[ld.get_letters(other.order)]
            return summation([m1,
                              m2,
                              Tensor.kronecker(self.ccs)[subscript_for_kronecker]])
        elif arg1 == 'double_dot' or arg1 == '..':  # 双点积
            m1 = self[ld.get_letters(self.order)]
            subscript_for_kronecker1 = ld.last_letters() + ld.next_letters()  # kronecker张量的下标 负责连接前面两个张量
            subscript_for_kronecker2 = ld.last_letters(2)[0] + ld.next_letters(2)[-1]  # kronecker张量的下标 负责连接前面两个张量
            m2 = other[ld.get_letters(other.order)]
            return summation([m1,
                              m2,
                              Tensor.kronecker(self.ccs)[subscript_for_kronecker1],
                              Tensor.kronecker(self.ccs)[subscript_for_kronecker2]])
        else:
            raise Exception("参数错误")

    def __mul__(self, other):
        """
        * 用作张量的点积 调用contraction函数
        :param other: 另一个张量
        :return:
        :rtype:Tensor
        """
        assert isinstance(other, Tensor), '点积运算的对象必须为张量'
        return self.contraction(other)

    def __pow__(self, power, modulo=None):
        """
        ** 用作双点积 调用contraction函数
        :param power:另一个张量
        :param modulo:
        :return:
        :rtype:Tensor
        """
        assert isinstance(power, Tensor), '双点积运算的对象必须为张量'
        return self.contraction(power, '..')

    def get_matrix(self):
        """
        返回对应的矩阵形式
        可能返回1*1 3*1 3*3的矩阵
        :return:
        :rtype:np.ndarray
        """
        if self.order==0:
            r=np.array(self.component)
            r=r.reshape(1,1)
            return r
        elif self.order in (1,2):
            r=deepcopy(self.component)
            return r
        else:
            raise Exception("未知错误")

    def get_invariant(self):
        """
        返回三个不变量 只有2阶张量才有不变量
        不变量为1、2、3阶主子式的和
        :return:
        :rtype:tuple[float]
        """
        assert self.order==2,'只有2阶张量才有不变量'
        i1=self[0,0]+self[1,1]+self[2,2]
        i2=self[0,0]*self[1,1]+self[0,0]*self[2,2]+self[2,2]*self[1,1]-self[0,1]**2-self[0,2]**2-self[1,2]**2
        # i2=0.5*summation([self['ij'],self['ji']]).component
        i3=det(self.component)
        return (i1,i2,i3,)

    def decompose(self,mode='deviator'):
        """
        分解张量
        :param mode: 分解模式
                        deviator:分解为球应力张量+应力偏量 sphere,deviator

        :return:两个张量
        :rtype: Tensor
        """
        if mode=='deviator':
            I=self.get_invariant()
            sphere=I[0]/3*self.kronecker(ccs=self.ccs)
            deviator=self-sphere
            return sphere,deviator
        else:
            raise Exception("参数错误")
def test1():
    new = CartesianCoordinateSystem((Vector3D(0, 1, 0),
                                     Vector3D(0, 0, 1),
                                     Vector3D(1, 0, 0),))

    v = np.array([5, 5, 0])
    T = Tensor(component=[5, 5, 0])
    T.ccs = new
    T1 = Tensor(component=[5, 0, 5], ccs=new)
    assert T == T1


def test2():
    A = np.array([[-10, 9, 5],
                  [9, 0, 0],
                  [5, 0, 8]])
    T = Tensor(component=A)
    T.diagonalize()
    assert abs(T[0, 0] - 10.08) < 0.1 and abs(T[1, 1] - 4) < 0.1 and abs(T[2, 2] - -16.08) < 0.1
    ccs1 = T.ccs
    T.ccs = global_ccs
    A = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]])
    T1 = Tensor(component=A)
    A = np.array([[-9.00000000e+00, 9.00000000e+00, 5.00000000e+00],
                  [9.00000000e+00, 1.00000000e+00, -2.22044605e-16],
                  [5.00000000e+00, -4.44089210e-16, 9.00000000e+00]])
    T2 = Tensor(component=A)
    assert T2 == T1 + T, '相加测试'
    A = np.array([[-11, 9.00000000e+00, 5.00000000e+00],
                  [9.00000000e+00, -1, -2.22044605e-16],
                  [5.00000000e+00, -4.44089210e-16, 7.00000000e+00]])
    T3 = Tensor(component=A)
    assert T3 == T - T1, '相减测试'

    A = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, 1]])
    T = Tensor(component=A)
    A = np.array([[2, 0, 0],
                  [0, 2, 0],
                  [0, 0, 2]])
    T1 = Tensor(component=A)
    assert T1 == 2 * T, '与实数相乘测试'

    A = np.array([[-10, 9, 4],
                  [9, 0, 0],
                  [5, 0, 8]])
    T = Tensor(component=A)
    T1 = Tensor(component=[1, 1, 1])
    T0 = Tensor(component=[3, 9, 13])
    delta = Tensor.kronecker()
    assert T0 == summation([T['ij'], T1['k'], delta['jk']])
    assert T0 == T.contraction(T1), '点积测试'
    T1.ccs = ccs1
    assert T0 == T.contraction(T1), '点积测试'
    assert T0 == T * T1

    A = np.array([[-10, 9, 4],
                  [9, 0, 0],
                  [5, 0, 8]])
    T1 = Tensor(component=A)
    assert (A==T1.get_matrix()).all(),'返回矩阵不对'
    A[0,0]=1
    assert not (A == T1.get_matrix()).all(),'改动参数影响了之前生成的张量，是不是忘记使用copy'
    A = np.array([[1, 8, 4],
                  [9, 0, 0],
                  [5, 0, 1]])
    T2 = Tensor(component=A)
    assert T1.contraction(T2, arg1='..') == 191, '双点积测试'
    T1.ccs = ccs1
    assert T1.contraction(T2, arg1='..') == 191, '双点积测试'
    assert T1 ** T2 == 191

    t=Tensor(1.1)
    assert t.get_matrix().shape==(1,1),'返回矩阵不对'
    A = np.array([[-10, 9, 5],
                  [9, 0, 0],
                  [5, 0, 8]])
    T1 = Tensor(component=A)
    i1=T1.get_invariant()
    T1.diagonalize()
    i2=T1.get_invariant()
    i1=np.array(list(i1))
    i2 = np.array(list(i2))
    assert norm(i1-i2)<tol_for_eq,'不变量不应该随着坐标系变化'

    A = np.array([[-10, 9, 5],
                  [9, 0, 0],
                  [5, 0, 8]])
    T1 = Tensor(component=A)
    sphere, deviator=T1.decompose()
    assert sphere+deviator==T1,'张量分解错误'
    A = np.array([[1,2,4],
                  [2,2,1],
                  [4,1,3]])
    T1 = Tensor(component=A)
    sphere, deviator = T1.decompose()
    assert  T1==sphere+deviator


def test3():
    A = np.array([[3/2,-1/2/2**0.5,-1/2/2**0.5],
                  [-1/2/2**0.5, 11/4, -5/4],
                  [-1/2/2**0.5, -5/4, 11/4]])
    T1 = Tensor(component=A)
    I=[7,14,8]
    assert norm(np.array(I)-np.array(T1.get_invariant()))<tol_for_eq,'不变量计算测试'
    J=[0,-7/3.,20/27.]
    sphere, deviator = T1.decompose()
    assert  norm(np.array(J)-np.array(deviator.get_invariant()))<tol_for_eq,'不变量计算测试'
if __name__ == '__main__':
    test1()
    test2()
    test3()
