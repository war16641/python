"""单例类 通过重载new方法实现 来源：https://www.cnblogs.com/huchong/p/8244279.html"""
from abc import   ABCMeta, abstractmethod
from nose.tools import assert_raises
import re

def get_classname_str(obj:object)->str:
    """
    获取与类名相同的字符串
    :param obj:类型 type
    :return:
    """
    regexp=r"\.\D+\w*'"
    pat=re.compile(regexp)
    r=pat.findall(obj.__str__(obj))
    assert len(r)>=1,'匹配字符串时出错'
    return r[0][1:-1]


class Singleton(metaclass=ABCMeta):
    """
    单例类
    所有的单例类会按类名为键保存在字典singleton_instances中
    """
    singleton_instances={}
    def __new__(cls, *args, **kwargs):

        #首先寻找这个类名是否在singleton_instances中
        classname=get_classname_str(cls)
        if classname not in Singleton.singleton_instances.keys():#没有
            assert '__init__' not in cls.__dict__.keys(), \
                '单例对象不应该拥有构造函数__init__,否则该单例会多次初始化，请使用init函数代替。且建议init函数不带参数。'
            assert 'init' in cls.__dict__.keys(), \
                '单例必须实现init函数。'
            sg=object.__new__(cls)#创建实例
            tmp={classname:sg}
            sg.init()
            Singleton.singleton_instances.update(tmp)
        return Singleton.singleton_instances[classname]



        # if not hasattr(Singleton, "_instance"):
        #
        #
        #
        #     Singleton._instance=object.__new__(cls)
        #     Singleton._instance.init(*args,**kwargs)
        #     print(str(type(Singleton._instance)))
        #     # print(type(Singleton._instance).__dict__)
        #     assert '__init__' not in type(Singleton._instance).__dict__.keys(),\
        #         '单例对象不应该拥有构造函数__init__,否则该单例会多次初始化，请使用init函数代替。且建议init函数不带参数。'
        #     assert 'init' in type(Singleton._instance).__dict__.keys(),\
        #         '单例必须实现init函数。'
        # return Singleton._instance

    @abstractmethod
    def init(self,*args,**kwargs):
        raise NotImplementedError('请一定实现init函数')
        pass


class Foo(Singleton):

    # def __init__(self):
    #     self.a=-1

    def init(self):
        # self.a=args[0]
        self.a=0
    def test(self):
        pass


class A(Singleton):
    # def __init__(self):
    #     print('__init__')
    def init(self):
        self.a=10

if __name__ == '__main__':

    a=Foo()
    assert a.a==0
    a.a=1
    b=Foo()
    assert b.a==1
    b.a=2
    assert a.a==2
    c = A()
    assert c.a==10
    assert b.a==2
    # assert_raises(AssertionError,A)
