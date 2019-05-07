from GoodToolPython.vector3d import Vector3D
from GoodToolPython.plasticmechanics.usefulscripts import *
from GoodToolPython.mybaseclasses.todoexception import ToDoException
from math import *
import numpy as np
from copy import deepcopy


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
    sequence=[]
    for i in string:
        if i not in counter:
            counter[i] = 1
            sequence.append(i)
        else:
            counter[i] += 1
    return counter,sequence

class CartesianCoordinateSystem:
    """简单笛卡尔坐标系 标准正交基 右手法则
    :type basic_vectors:tuple[Vector3D]
    """


    def __init__(self,basic_vectors:tuple):

        assert isinstance(basic_vectors,tuple)
        assert len(basic_vectors)==3
        for v in basic_vectors:
            assert abs(v.modulus-1)<Vector3D.tol_for_eq,'模要求为1'
        v1,v2,v3=basic_vectors
        assert abs(v1.mixed_product(v2,v3)-1)<Vector3D.tol_for_eq
        self.basic_vectors=deepcopy(basic_vectors)

    def get_coordinates(self,v):
        assert isinstance(v,Vector3D)
        return v.get_coordinates_under_cartesian_coordinates_system(self.basic_vectors)

    def get_inverse_conversion_coefficient(self,new)->np.ndarray:
        """
        获取逆变转换系数
        :param new: 新坐标系
        :return:
        """
        icc=np.zeros((3,3))
        # icc[0,0]=cos(self.basic_vectors[0].angle(new.basic_vectors[0]))
        for i in range(3):
            for j in range(3):
                icc[i,j]=cos(self.basic_vectors[i].angle(new.basic_vectors[j]))
        return icc


#世界坐标系
global_ccs=CartesianCoordinateSystem((Vector3D(1,0,0),
                                   Vector3D(0,1,0),
                                   Vector3D(0,0,1),))
class SummationMultiplier:
    """爱因斯坦求和 乘子"""
    def __init__(self,tensor,index):
        self.tensor=tensor
        self.index=index
        _,self._sequence=count_each_char(index)#记录字母出现的顺序

    def get_component_value(self,dic)->float:
        """
        返回tensor中元素
        :param dic: 键是字母 值是索引 键
        :return:
        """
        assert isinstance(dic,dict)
        index_list=[]
        for k in self._sequence:
            assert k in dic.keys(),'dic中未找到key'
            index_list.append(dic[k])
        if len(index_list)==1:
            return self.tensor[index_list[0]]
        elif len(index_list)==2:
            return self.tensor.__getitem__(tuple(index_list))
        else:
            raise Exception("参数错误")

def summation(muliplier_list):
    assert isinstance(muliplier_list,list)
    index_list=[x.index for x in muliplier_list]
    index_string=''#把所有的index放进一个字符串
    for index in index_list:
        index_string+=index
    counter,seq=count_each_char(index_string)
    free_index_list=[ind for ind in counter.keys() if counter[ind]==1]#自由标
    fake_index_list = [ind for ind in counter.keys() if counter[ind] == 2]#哑标
    t=[ind for ind in counter.keys() if counter[ind] > 2]
    if len(t)>0:
        raise Exception("指标次数不能出现三次及以上")
    if len(free_index_list)>2:
        raise ToDoException("暂不支持三阶及以上的张量计算")
    order=len(free_index_list)#生成张量的阶数
    r=Tensor.zeros(order=order)#先生成零元素张量

    num_of_fake=len(fake_index_list)#亚指标个数
    free_iter = SubscriptIteration(order=order)
    fake_iter = SubscriptIteration(order=num_of_fake)
    if order==0:#零阶张量
        sumv = 0.
        for j in fake_iter:
            dic = dict(zip(free_index_list + fake_index_list, [] + j))
            prod = 1.
            for mul in muliplier_list:
                prod *= mul.get_component_value(dic)
            sumv += prod
        r.component = sumv
    else:
        #生成的张量为一阶或者二阶

        for i in free_iter:
            sumv=0.
            for j in fake_iter:
                dic=dict(zip(free_index_list+fake_index_list,i+j))
                prod=1.
                for mul in muliplier_list:
                    prod*=mul.get_component_value(dic)
                sumv+=prod
            r[i]=sumv
    return r



class Tensor:
    """张量"""
    def __init__(self,component,ccs:CartesianCoordinateSystem):
        assert isinstance(ccs,CartesianCoordinateSystem)
        if isinstance(component,(float,int)):#零阶
            self.order=0
            self.component=component
        elif isinstance(component,np.ndarray):
            if component.size==3:#一阶
                self.order=1
                self.component=component.reshape(3,1)#一阶张量格式为3*1
            elif component.shape==(3,3):#二阶  component.size==9 and len(component.shape)==2:
                self.order=2
                self.component=component
            else:
                raise Exception("参数错误")
        else:
            raise Exception("参数错误")
        self._ccs=ccs

    def __str__(self):
        if self.order==0:
            return "%f"%self.component
        elif self.order==1:
            return "%f,%f,%f"%(self.component[0],self.component[1],self.component[2])
        elif self.order==2:
            return "二阶"

    @property
    def ccs(self):
        return self._ccs

    @ccs.setter
    def ccs(self,new_ccs):
        """设定新的坐标系"""
        assert isinstance(new_ccs,CartesianCoordinateSystem)
        if new_ccs==self._ccs:
            return#与原坐标系相同
        #不同就要进行分量的重新计算
        if self.order==0:
            return#零阶张量与坐标系无关
        elif self.order==1:
            pass
        elif self.order==2:
            pass
        else:
            raise Exception("未知错误")

    def __getitem__(self, item):
        # print(item)
        #如果item是数组成的list转换为tuple
        if isinstance(item,list):
            if isinstance(item[0],(int,float)):
                if len(item)==1:
                    item=item[0]
                else:
                    item=tuple(item)

        if isinstance(item,int):
            if self.order==1:
                return float(self.component[item])
            else:
                raise Exception("参数错误。单个索引只支持一阶张量。")
        elif isinstance(item,tuple) and len(item)==2:
            i,j=item
            assert isinstance(i,int)
            assert isinstance(j,int)
            if self.order==2:
                return float(self.component[i,j])
            else:
                raise Exception("参数错误。双索引支持二阶张量。")
        elif isinstance(item,str):#返回爱因斯坦求和乘子
            return SummationMultiplier(self,item)

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

        assert isinstance(value,(int,float))
        if isinstance(item, int):
            if self.order == 1:
                self.component[item]=value
            else:
                raise Exception("参数错误。单个索引只支持一阶张量。")
        elif isinstance(item, tuple) and len(item) == 2:
            i, j = item
            assert isinstance(i, int)
            assert isinstance(j, int)
            if self.order == 2:
                self.component[i, j]=value
            else:
                raise Exception("参数错误。双索引支持二阶张量。")

    @staticmethod
    def zeros(order=0,ccs=global_ccs):
        """
        生成0元素张量
        :param order:指定阶数 不能大于2
        :param ccs:
        :return: 张量
        """
        if order==0:
            return Tensor(component=0,
                          ccs=ccs)
        elif order==1:
            return Tensor(component=np.zeros((3,1)),
                          ccs=ccs)
        elif order==2:
            return Tensor(component=np.zeros((3,3)),
                          ccs=ccs)
        else:
            raise Exception("参数错误。")

if __name__ == '__main__':
    # t=Vector3D(1,0,0)
    # old=CartesianCoordinateSystem((t,
    #                                Vector3D(0,1,0),
    #                                Vector3D(0,0,1),))
    # # pass
    # # new=CartesianCoordinateSystem((Vector3D(0,1,0),
    # #                                Vector3D(0,0,1),
    # #                                Vector3D(1,0,0),))
    # # v=Vector3D(5,5)
    # # print(old.get_inverse_conversion_coefficient(new))
    # # print(old.get_coordinates(v))
    # # print(new.get_coordinates(v))
    #
    #
    # A = np.array([[-10,9,5],
    #               [9,0,0],
    #               [5,0,8]])
    # eigenvalue, eigenvector=eigenvalue_problem(A)
    # print(eigenvalue)
    # print(eigenvector)
    # d1=eigenvector[:,0]
    # d2=eigenvector[:,1]
    # d3=eigenvector[:,2]
    # d=[d1,d2,d3]
    # i=2
    # j=1
    # print(np.mat(d[i].reshape(1,3)*np.mat(A)*np.mat(d[j].reshape(3,1))))
    # new=CartesianCoordinateSystem((Vector3D.make_from_array(d1),
    #                                Vector3D.make_from_array(d2),
    #                                Vector3D.make_from_array(d3),))
    # print('逆变转换系数')
    # print(old.get_inverse_conversion_coefficient(new))
    # pass


    #tensor
    v=np.array([5,5,0])
    t1=Tensor(component=v,
             ccs=global_ccs)
    v=np.array([[-10,9,5],
                  [9,0,0],
                  [5,0,8]])
    t2=Tensor(component=v,
             ccs=global_ccs)
    print(summation([t1['i'],t2['ij']]))
