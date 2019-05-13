"""
这个文件放一些统计函数
"""
from typing import Union, List, Tuple

import numpy as np

from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type,is_vector_like,format_vector


def return_func0(v, i):
    return v


def return_func1(v, i):
    return v, i


def absmax(data: Union[List[float], Tuple[float], np.ndarray], mode='value') -> Union[float, tuple]:
    """
    返回绝对值最大值
    :param data:必须为类向量
    :param mode:
    :return:
    """

    value = 0.
    index = 0
    # 处理返回模式
    if mode == 'value':
        return_func = return_func0
    elif mode == 'value_and_index':
        return_func = return_func1
    else:
        raise Exception("参数错误。")
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

def absmin(data: Union[List[float], Tuple[float], np.ndarray], mode='value') -> Union[float, tuple]:
    """
    返回绝对值最小值
    :param data:必须为类向量
    :param mode:
    :return:
    """

    value = 0.
    index = 0
    # 处理返回模式
    if mode == 'value':
        return_func = return_func0
    elif mode == 'value_and_index':
        return_func = return_func1
    else:
        raise Exception("参数错误。")
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

if __name__ == '__main__':
    data = [1, 3, -2, -4]
    assert absmax(data, 'value_and_index') == (-4, 3)
    data=np.array(data)
    assert absmax(data, 'value_and_index') == (-4, 3)
    data.reshape((4,1))
    assert absmax(data, 'value_and_index') == (-4, 3)
    data.reshape((1,4))
    assert absmax(data, 'value_and_index') == (-4, 3)

    data = [1, 3, -2, -4]
    assert absmin(data, 'value_and_index') == (1, 0)
    data=np.array(data)
    assert absmin(data, 'value_and_index') == (1, 0)
    data.reshape((4,1))
    assert absmin(data, 'value_and_index') == (1, 0)
    data.reshape((1,4))
    assert absmin(data, 'value_and_index') == (1, 0)
