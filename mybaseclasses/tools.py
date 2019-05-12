"""
这个包放置一些工具函数
"""
from GoodToolPython.vector3d import Vector3D
from typing import Union
from nose.tools import assert_raises

class ZeroLengthException(Exception):
    """
    序列长度为0异常 由is_sequence_with_one_type抛出
    使用is_sequence_with_one_type时，可能会遇到sequence为0长度序列，这时候返回true或者false都是有可能 所以把它做成了异常
    """
    pass


def is_sequence_with_specified_type(sequence:Union[tuple, list], tp:type=None)->bool:
    """
    判断sequence是否是指定的类型的对象组成的序列
    :param sequence:序列
    :param tp:类型 如果是none 则取第一个元素的类型
    :return:
    """
    # assert isinstance(sequence,(list,tuple)),'sequnce必须为元组或者列表'
    if not isinstance(sequence,(list,tuple)):#sequnce必须为元组或者列表,否则返回false
        return False
    if len(sequence)==0:
        raise ZeroLengthException('序列长度为0')
    if tp is None:
        tp=type(sequence[0])

    if  not isinstance(tp,tuple):
        tp=(tp,)#使其成为tuple
    for t in tp:
        assert isinstance(t,type),'tp必须为类或类组成的tuple'
    # assert isinstance(tp,type),'tp必须为类'

    for i in sequence:
        if not isinstance(i,tp):
            return False
    return True

def factorial(n):
    #计算阶乘
    assert n>=0 and isinstance(n,int),'n必须为自然数'
    if n==0:
        return 1
    p=1
    for i in range(1,n+1):
        p*=i
    return p






#以下为测试函数 名称为test_开头
def test_is_sequence_with_specified_type():
    assert not is_sequence_with_specified_type(1, Vector3D)
    v1=Vector3D()
    v2=Vector3D(1)
    i1=1.
    i2=2.
    assert is_sequence_with_specified_type([i1, i2], float)
    assert not is_sequence_with_specified_type([i1, i2, v1], float)
    assert is_sequence_with_specified_type([i1, i2])
    assert not is_sequence_with_specified_type([i1, i2, v1])
    assert_raises(ZeroLengthException, is_sequence_with_specified_type, [])

def test_factorial():
    assert factorial(0)==1
    assert factorial(1)==1
    assert factorial(3)==6

if __name__ == '__main__':
    test_is_sequence_with_specified_type()
    test_factorial()