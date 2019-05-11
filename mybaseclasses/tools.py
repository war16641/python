"""
这个包放置一些工具函数
"""
from GoodToolPython.vector3d import Vector3D
from typing import Union
def is_sequence_with_one_type(sequence:Union[Vector3D,list], tp:type=None)->bool:
    """
    判断sequence是否是某一个类型的对象组成的序列
    :param sequence:序列
    :param tp:类型 如果是none 则取第一个元素的类型
    :return:
    """
    # assert isinstance(sequence,(list,tuple)),'sequnce必须为元组或者列表'
    if not isinstance(sequence,(list,tuple)):#sequnce必须为元组或者列表,否则返回false
        return False
    if tp is None:
        tp=type(sequence[0])
    assert isinstance(tp,type),'tp必须为类'

    for i in sequence:
        if not isinstance(i,tp):
            return False
    return True

if __name__ == '__main__':
    assert not is_sequence_with_one_type(1,Vector3D)
    v1=Vector3D()
    v2=Vector3D(1)
    i1=1.
    i2=2.
    assert is_sequence_with_one_type([i1,i2],float)
    assert not is_sequence_with_one_type([i1, i2,v1], float)