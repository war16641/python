"""
这个包放置一些工具函数
"""
import itertools
import time
from typing import Union, Tuple,Type
import numpy as np
from nose.tools import assert_raises

from GoodToolPython.vector3d import Vector3D


class ZeroLengthException(Exception):
    """
    序列长度为0异常 is_sequence_with_specified_type，is_vector_like
    使用is_sequence_with_one_type时，可能会遇到sequence为0长度序列，这时候返回true或者false都是有可能 所以把它做成了异常
    """
    pass


def is_sequence_with_specified_type(sequence: Union[tuple, list], tp: Union[type, Tuple[type]] = None) -> bool:
    """
    判断sequence是否是指定的类型的对象组成的序列
    :param sequence:序列
    :param tp:类型 如果是none 则取第一个元素的类型
    :return:
    """
    # assert isinstance(sequence,(list,tuple)),'sequnce必须为元组或者列表'
    if not isinstance(sequence, (list, tuple)):  # sequnce必须为元组或者列表,否则返回false
        return False
    if len(sequence) == 0:
        raise ZeroLengthException('序列长度为0')
    if tp is None:
        tp = type(sequence[0])

    if not isinstance(tp, tuple):
        tp = (tp,)  # 使其成为tuple
    for t in tp:
        assert isinstance(t, type), 'tp必须为类或类组成的tuple'
    # assert isinstance(tp,type),'tp必须为类'

    for i in sequence:
        if not isinstance(i, tp):
            return False
    return True


def factorial(n):
    # 计算阶乘
    assert n >= 0 and isinstance(n, int), 'n必须为自然数'
    if n == 0:
        return 1
    p = 1
    for i in range(1, n + 1):
        p *= i
    return p


def print_elapse_time(func):
    # 装饰器函数 打印消耗时间
    def wrapper(*args):
        start_time = time.time()
        r = func(*args)
        print('耗时%fs' % (time.time() - start_time))
        return r

    return wrapper


class Benchmark:
    """
    性能测试函数 全为静态函数
    """

    @staticmethod
    @print_elapse_time
    def run1(n=11):
        """
        计算数字的全排列耗时 测试性能
        :param n:
        :return:
        """
        numbers = []
        for i in range(1, n + 1):
            numbers.append(i)
        counter = 0
        counter_max = factorial(n)
        print_coutner = 0
        print_coutner_max = 0.05 * counter_max
        for i in itertools.permutations(numbers, len(numbers)):
            counter += 1
            print_coutner += 1
            if print_coutner >= print_coutner_max:
                print('%f' % (counter / counter_max))
                print_coutner = 0
        assert counter == counter_max, '计数出错'


def is_vector_like(data)->bool:
    """
    判断是否为类向量
    :param data:
    :return:
    """
    if isinstance(data,(list,tuple)):
        #序列
        return is_sequence_with_specified_type(data,(float,int))
    elif isinstance(data,np.ndarray):
        #数组
        if data.size==0:
            raise ZeroLengthException('数组大小为0')
        if len(data.shape)==1:
            return True
        if len(data.shape)==2:
            if sum(data.shape)==data.size+1:
                return True
    return False#其他情况返回false


def format_vector(vector_like,tp='oneD')->Union[list,np.ndarray]:
    """
    把类向量转化为指定的类型
    :param vector_like:
    :param tp: 'list' 列表
                'oneD' 一维数组
                'column_vector','row_vector' 二维数组
    :return:
    """
    assert tp in ['list','oneD','column_vector','row_vector'],'参数错误'
    assert is_vector_like(vector_like),'参数必须为类向量'
    if isinstance(vector_like, (list, tuple)):
        if tp=='list':
            return list(vector_like)
        elif tp=='oneD':
            return np.array(vector_like)
        elif tp=='column_vector':
            t=np.array(vector_like)
            return t.reshape((t.size,1))
        elif tp=='row_vector':
            t = np.array(vector_like)
            return t.reshape((1,t.size))
    elif isinstance(vector_like,np.ndarray):
        if len(vector_like.shape) == 1:
            #一维数组
            if tp == 'list':
                r=[]
                for v in vector_like:
                    r.append(v)
                return r
            elif tp == 'oneD':
                return vector_like
            elif tp == 'column_vector':
                return vector_like.reshape((vector_like.size, 1))
            elif tp == 'row_vector':
                return vector_like.reshape((1, vector_like.size))
        if len(vector_like.shape) == 2:
            #二维数组
            if tp == 'list':
                r=[]
                tmp=vector_like.reshape((vector_like.size,))
                for v in tmp:
                    r.append(v)
                return r
            elif tp == 'oneD':
                return vector_like.reshape((vector_like.size,))
            elif tp == 'column_vector':
                return vector_like.reshape((vector_like.size, 1))
            elif tp == 'row_vector':
                return vector_like.reshape((1, vector_like.size))

# 以下为测试函数 名称为test_开头
def test_is_sequence_with_specified_type():
    assert not is_sequence_with_specified_type(1, Vector3D)
    v1 = Vector3D()
    v2 = Vector3D(1)
    i1 = 1.
    i2 = 2.
    assert is_sequence_with_specified_type([i1, i2], float)
    assert not is_sequence_with_specified_type([i1, i2, v1], float)
    assert is_sequence_with_specified_type([i1, i2])
    assert not is_sequence_with_specified_type([i1, i2, v1])
    assert_raises(ZeroLengthException, is_sequence_with_specified_type, [])


def test_factorial():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(3) == 6

def test_is_vector_like():
    A=np.random.randint(-100,100,(3,1))
    assert True==is_vector_like(A)
    A = np.random.randint(-100, 100, (1,3))
    assert True == is_vector_like(A)
    A=np.random.randint(-100,100,(3,))
    assert True==is_vector_like(A)
    assert True == is_vector_like([1,2.0])
    A = np.random.randint(-100, 100, (3,2))
    assert  False==is_vector_like(A)
    assert  False==is_vector_like([1,2,[1]])
    A=np.array([[]])
    assert_raises(ZeroLengthException,is_vector_like,A)

def test_format_vector():
    A=[1,2,3]
    A1=A
    A2=np.array(A)
    A3=A2.reshape((3,1))
    A4=A2.reshape((1,3))
    assert format_vector(A,'list')==A1
    assert (format_vector(A, 'oneD') == A2).all()
    assert (format_vector(A, 'column_vector') == A3).all()
    assert (format_vector(A, 'row_vector') == A4).all()

    assert format_vector(A1,'list')==A1
    assert (format_vector(A1, 'oneD') == A2).all()
    assert (format_vector(A1, 'column_vector') == A3).all()
    assert (format_vector(A1, 'row_vector') == A4).all()

    assert format_vector(A2,'list')==A1
    assert (format_vector(A2, 'oneD') == A2).all()
    assert (format_vector(A2, 'column_vector') == A3).all()
    assert (format_vector(A2, 'row_vector') == A4).all()

    assert format_vector(A3,'list')==A1
    assert (format_vector(A3, 'oneD') == A2).all()
    assert (format_vector(A3, 'column_vector') == A3).all()
    assert (format_vector(A3, 'row_vector') == A4).all()

    assert format_vector(A4,'list')==A1
    assert (format_vector(A4, 'oneD') == A2).all()
    assert (format_vector(A4, 'column_vector') == A3).all()
    assert (format_vector(A4, 'row_vector') == A4).all()
if __name__ == '__main__':
    test_is_sequence_with_specified_type()
    test_factorial()
    # Benchmark.run1()
    test_is_vector_like()
    test_format_vector()