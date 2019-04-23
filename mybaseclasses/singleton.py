"""单例类 通过重载new方法实现 来源：https://www.cnblogs.com/huchong/p/8244279.html"""
class Singleton(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(Singleton, "_instance"):
            Singleton._instance=object.__new__(cls)
        return Singleton._instance


class A:
    def __init__(self,a):
        A.a=a


class B(Singleton):
    def __init__(self,a):
        B.a=a

if __name__ == '__main__':
    b1=B(1)
    print(b1.a)
    b2=B(2)
    print(b1.a)
    print(b2.a)
    assert b1==b2