"""
这个文件放一些统计函数
"""
from typing import Union, List, Tuple
from nose.tools import assert_raises
import numpy as np

from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type,is_vector_like,format_vector,is_matrix_like


def return_func0(v, i):
    return v


def return_func1(v, i):
    return v, i


def absmax(data: Union[List[float], Tuple[float], np.ndarray],
           flag_return_index=False
           ) -> Union[float, tuple]:
    """
    返回绝对值最大值
    :param data:必须为类向量
    :param flag_return_index:标志是否返回索引
    :return:
    """

    value = 0.
    index = 0
    # 处理返回模式
    if flag_return_index is False:
        return_func=return_func0
    else:
        return_func = return_func1



    assert is_vector_like(data),'参数必须为类向量'
    data=format_vector(data,'list')#转化为列表
    # 是序列
    value = data[0]
    index = 0
    for i, v in enumerate(data[1:]):
        if abs(v) > abs(value):
            value = v
            index = i + 1
    return return_func(value, index)

def absmin(data: Union[List[float], Tuple[float], np.ndarray], flag_return_index=False) -> Union[float, tuple]:
    """
    返回绝对值最小值
    :param data:必须为类向量
    :param flag_return_index:
    :return:
    """

    value = 0.
    index = 0
    # 处理返回模式
    if flag_return_index is False:
        return_func=return_func0
    else:
        return_func = return_func1


    assert is_vector_like(data), '参数必须为类向量'
    data = format_vector(data, 'list')  # 转化为列表
    # 是序列
    value = data[0]
    index = 0
    for i, v in enumerate(data[1:]):
        if abs(v) < abs(value):
            value = v
            index = i + 1
    return return_func(value, index)


def is_approximately_equal(x,y,tol=1e-3):
    """
    判断向量或者矩阵是否近似相等
    采用第二范数进行判断
    xy要求同为矩阵或向量
    :param x:
    :param y:
    :param tol: 误差允许值
    :return:
    """
    if is_vector_like(x):
        if is_vector_like(y):
            #两者都是向量
            s=0.
            for i,j in zip(x,y):
                s+=(i-j)**2
            if s<tol**2:
                return True
            else:
                return False
        else:
            raise Exception("x y类型错误")
    if is_matrix_like(x):
        if is_matrix_like(y):
            #两者都是矩阵
            s=0.
            for row_x,row_y in zip(x,y):
                for i,j in zip(row_x,row_y):
                    s+=(i-j)**2
            if s<tol**2:
                return True
            else:
                return False
        else:
            raise Exception("x y类型错误")
    raise Exception("x y类型错误")


def test1():
    data = [1, 3, -2, -4]
    assert absmax(data, True) == (-4, 3)
    data=np.array(data)
    assert absmax(data, True) == (-4, 3)
    data.reshape((4,1))
    assert absmax(data, True) == (-4, 3)
    data.reshape((1,4))
    assert absmax(data, True) == (-4, 3)

    data = [1, 3, -2, -4]
    assert absmin(data, True) == (1, 0)
    data=np.array(data)
    assert absmin(data, True) == (1, 0)
    data.reshape((4,1))
    assert absmin(data, True) == (1, 0)
    data.reshape((1,4))
    assert absmin(data, True) == (1, 0)

def test_is_approximately_equal():
    a=[4.896149,-1.566705,-10.331777]
    b=[4.89,-1.56,-10.33]
    # print(is_approximately_equal(a,b,1e-3))
    assert is_approximately_equal(a,b,1e-3)==False
    assert is_approximately_equal(a, b, 1e-2) == True

    a1=[[1,2],[3,4]]
    b1=np.array([[1.01,2.02],[2.99,3.98]])
    # print(is_approximately_equal(a1,b1,1e-1))
    assert is_approximately_equal(a1,b1,1e-1)==True
    assert is_approximately_equal(a1,b1,1e-2)==False
    assert_raises(Exception,is_approximately_equal,a1,b)
    assert_raises(Exception,is_approximately_equal,b1,a)
if __name__ == '__main__':
    test1()
    test_is_approximately_equal()
