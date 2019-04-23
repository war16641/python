from copy import deepcopy
from nose.tools import assert_raises
class SelfDelete:
    """
    强制删除所有成员变量——delete函数
    python内部采用gc机制 当引用为0时才真正删除对象
    有时候需要在还有其他引用时仍删除对象 所以取名为自我删除
    delete只会删除实例变量 不会删除类变量
    """
    def delete(self):
        tmp=deepcopy(list(vars(self).keys()))
        for name in tmp:
            # print(name)
            delattr(self,name)


class A(SelfDelete):
    classvar1=0
    def __init__(self,a,b):
        self.a=a
        self.b=b

if __name__ == '__main__':
    a=A(1,2)
    print("%d,%d,%d"%(a.classvar1,a.a,a.b))
    a.delete()
    assert a.classvar1==0
    assert_raises(AttributeError,a.__getattribute__,'a')
    assert_raises(AttributeError, a.__getattribute__, 'b')
