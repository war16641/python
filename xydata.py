import numpy as np
from typing import overload,TypeVar
from copy import deepcopy
from GoodToolPython.mybaseclasses.tools import is_vector_like,format_vector,is_matrix_like,format_matrix
import matplotlib.pyplot as plt
from matplot_examples.snaptocursor import SnaptoCursor
from myfile import read_file
from math import pi
from nose.tools import assert_raises
from statistics_nyh import absmax

Vector=TypeVar('Vector',list,np.ndarray)
from myfile import read_file
from mybaseclasses.tools import linear_interpolation
import unittest


class XYData:

    @overload
    def __init__(self,name:str,xy:np.ndarray):
        self.name = None  # type:str
        self.data=None # type:np.ndarray

    @overload
    def __init__(self,name:str,x:Vector,y:Vector):
        pass

    def  __init__(self,name:str='',
                  xy:np.ndarray=None,
                  x:Vector=None,y:Vector=None):

        #处理名称
        assert isinstance(name,str),'name必须为str对象'
        self.name = name  # type:str
        if xy is not None:
            #第一种初始化方式
            xy=format_matrix(xy,'ndarray')
            assert xy.shape[1]==2,'xy必须为双列'
            self.data=deepcopy(xy)#type:np.ndarray
        elif x is not None and y is not None:
            #第二种初始化方式
            #给定两个向量 代表 x y数据行
            assert is_vector_like(x) and is_vector_like(y),'x,y必须为类向量对象'
            x=format_vector(x,'column_vector')
            y=format_vector(y,'column_vector')#转为列向量
            self.data=np.hstack((x,y))
        else:
            raise Exception("参数错误。")

    def __str__(self):
        return "%s 共%d个数据点"%(self.name,len(self))

    def  __len__(self):
        if self.data is None:
            return 0
        return len(self.data)

    def print_in_detail(self):
        #详细显示
        print(self)
        #打印数据点
        if self.data is  None:
            print('无数据点')
            return
        for xy in self.data:
            print("%f,%f"%(xy[0],xy[1]))

    # def plot(self):
    #     if len(self) == 0:
    #         print('无数据点，做图取消')
    #         return
    #     plt.plot(self.data[:,0],self.data[:,1])
    #     plt.title(self.name)
    #     plt.show()

    def interpolation(self,points_number=1)->None:
        """
        线性内插点
        :param points_number: 插入点的个数
        :return:
        """
        def script(start,end,points_number)->np.ndarray:
            indexs=range(0,points_number+2)
            dv=(end-start)/(points_number+1)
            return np.array(indexs)*dv+start
        assert len(self)>1,'无数据点，无法内插'
        data=np.array([[]])
        data=data.reshape((0,2))
        for i in range(1,len(self)):
            x1=self.data[i-1,0]
            x2=self.data[i,0]
            xx=script(x1,x2,points_number)[0:-1]
            y1 = self.data[i - 1, 1]
            y2 = self.data[i, 1]
            yy = script(y1, y2, points_number)[0:-1]
            add=np.hstack((xx.reshape(points_number+1,1),yy.reshape(points_number+1,1)))
            data=np.vstack((data,add))
        data=np.vstack((data,self.data[-1,:]))
        self.data=data

    def psd(self,flag_logy=True):
        """
        求频谱图 还不太准确
        :param flag_logy:
        :return:
        """
        time=self.data[:,0]
        signal=self.data[:,1]
        freqs = np.fft.fftfreq(time.size, time[1]-time[0])
        # ps = np.abs(np.fft.fft(signal)) ** 2
        ps = abs(np.fft.fft(signal))/(len(signal)/2)
        print(len(freqs))
        idx=freqs>=0
        f=plt.figure()
        plt.plot(freqs[idx], ps[idx])
        plt.title(self.name)
        plt.xlabel('frequency/Hz')
        plt.ylabel('PSD')
        if flag_logy is True:
            f.axes[0].set_yscale('log')
        plt.show()

    @property
    def x(self)->np.ndarray:
        """x"""
        return self.data[:,0]
    @x.setter
    def x(self,v):
        assert is_vector_like(v),'v必须为类数列'
        assert len(v)==len(self),'大小不一致'
        self.data[:,0]=v


    @property
    def y(self)->np.ndarray:
        """y"""
        return self.data[:,1]
    @y.setter
    def y(self,v):
        assert is_vector_like(v),'v必须为类数列'
        assert len(v)==len(self),'大小不一致'
        self.data[:,1]=v

    def __getitem__(self, *args,**kwargs):
        """重写类的【】索引"""
        if len(args)==1:#如果是单索引 且是 数字 返回在这附近的值
            id=args[0]
            if isinstance(id,(float,int)):
                return self.get_similar_value(id)
            else:
                return self.data.__getitem__(*args, **kwargs)
        else:
            return self.data.__getitem__(*args,**kwargs)
    def __setitem__(self,*args,**kwargs):
        self.data.__setitem__(*args,**kwargs)

    def to_list(self):
        """转换为二维list"""
        return format_matrix(self.data,'list')

    def get_similar_value(self,x:float)->float:
        """
        获取在x处的值 如果没有x 按最近的两个点线性插值
        x必须在在范围内
        :param x:
        :return:
        """
        assert x>=self.x[0] and x<=self.x[-1],"x必须在在范围内"
        tol=1e-10
        if abs(x-self.x[0])<tol:
            return self.y[0]
        if abs(x-self.x[-1])<tol:
            return self.y[-1]
        for i in range(len(self)):
            if self.x[i]>x:
                return linear_interpolation(x,self[i-1:i+1,:])
        raise Exception("错误：不应该执行到这儿")

    def save_to_file(self,fullname,txtformat=None,write_name=True):
        """
        写入到文件
        @param fullname:
        @param txtformat: 每行格式 注意要用\n结尾 有默认值
        @param write_name:
        @return:
        """
        if txtformat is None:
            txtformat="%f\t%f\n"#设置自动格式
        with open(fullname, 'w') as file_object:
            if write_name:  # 写入name
                file_object.write("%s\n"%self.name)
            for u in self:
                file_object.write(txtformat%tuple(u))

    def __iter__(self):
        #返回data字段的迭代器
        return self.data.__iter__()

    def show_in_figure(self):
        #在fig中显示
        fig1, ax = plt.subplots()
        assert len(self)>0,'没有数据'
        ax.plot(self.x,self.y,'o-')
        snap_cursor1 = SnaptoCursor(ax)
        plt.title(self.name)
        plt.show()

    @property
    def peak_point(self):
        v,i=absmax(self.y,flag_return_index=True)
        return self.x[i],self.y[i]

# def test1():
#     A=np.array([[1, 1],[2, 1],[3 ,2]])
#     xy=XYData('数据集',A)
#     print(xy)
#     xy.print_in_detail()
#
#     x=[1,2,3]
#     y=[1,1,2]
#     xy=XYData('第二种',x=x,y=y)
#     xy.print_in_detail()
#
#     x = np.array([1, 2, 3])
#     y = np.array([1, 1, 2])
#     xy = XYData('第二种', x=x, y=y)
#     xy.print_in_detail()
#
#     x = np.array([1, 2, 3])
#     y = np.array([1, 1, 2])
#     x=x.reshape((1,3))
#     xy = XYData('第二种', x=x, y=y)
#     xy.print_in_detail()
#     xy.interpolation(2)
#     xy.print_in_detail()
#
#     ori=read_file(r"E:\市政院\施工招标上部出图-王博-20190706\22号\BC社区双层拱桥抗震\地震波-用\E2-(4).Txt")
#     xy=XYData(name='kobe',xy=ori)
#     # xy.plot()
#     # xy.plot()
#     # xy.psd(False)
#
# def test_fft():
#     fs=600
#     time=np.arange(0.,1.5,1/fs)
#     y=np.sin(2*pi*100*time)+np.sin(2*pi*45*time)
#     N=time.size
#     df=fs/(N-1)
#     f=np.arange(0,N)*df
#     Y=np.fft.fft(y)/N*2
#     am=abs(Y)
#     plt.figure()
#     plt.plot(f, am)
#     plt.show()
#
# def test_fft2():
#     fs = 600
#     time = np.arange(0., 1.5, 1 / fs)
#     y = np.sin(2 * pi * 100 * time) + np.sin(2 * pi * 45 * time)
#     xy=XYData(name='sin',x=time,y=y)
#     xy.psd(False)
#
# def test3():
#     xy=XYData(name='yi',x=[1,2 ,3],y=[1.1,2.1,3.1])
#     xy.print_in_detail()
#     print(xy.x)
#     xy.x=[1,1,1]
#     assert xy.data[1, 0] == 1
#     xy.print_in_detail()
#     x=xy.x
#     print(x)
#     xy.print_in_detail()
#     x[1]=3
#     xy.print_in_detail()
#     assert xy.data[1,0]==3
#     assert xy[1,1]==2.1
#     xy[1,1]=10
#     assert xy[1, 1] == 10
#
# def test4():
#     xy = XYData(name='yi', x=[1, 2, 3], y=[1.1, 2.1, 3.1])
#     assert abs(xy.get_similar_value(1.5)-1.6)<1e-8

class TestCase(unittest.TestCase):
    def test1(self):
        A = np.array([[1, 1], [2, 1], [3, 2]])
        xy = XYData('数据集', A)
        print(xy)
        # xy.print_in_detail()

        x = [1, 2, 3]
        y = [1, 1, 2]
        xy = XYData('第二种', x=x, y=y)
        # xy.print_in_detail()

        x = np.array([1, 2, 3])
        y = np.array([1, 1, 2])
        xy = XYData('第二种', x=x, y=y)
        # xy.print_in_detail()

        x = np.array([1, 2, 3])
        y = np.array([1, 1, 2])
        x = x.reshape((1, 3))
        xy = XYData('第二种', x=x, y=y)
        # xy.print_in_detail()
        xy.interpolation(2)
        # xy.print_in_detail()
        # xy.show_in_figure()

    def test2(self):
        xy = XYData(name='yi', x=[1, 2, 3], y=[1.1, 2.1, 3.1])
        # assert abs(xy.get_similar_value(1.5) - 1.6) < 1e-8
        self.assertAlmostEqual(abs(xy.get_similar_value(1.5) - 1.6) ,0)
        self.assertAlmostEqual(xy[1.5],1.6)

    def test3(self):
        xy = XYData(name='yi', x=[1, 2, 3], y=[1.1, 2.1, 3.1])
        xy.print_in_detail()
        print(xy.x)
        xy.x = [1, 1, 1]
        assert xy.data[1, 0] == 1
        xy.print_in_detail()
        x = xy.x
        print(x)
        xy.print_in_detail()
        x[1] = 3
        xy.print_in_detail()
        assert xy.data[1, 0] == 3
        assert xy[1, 1] == 2.1
        xy[1, 1] = 10
        assert xy[1, 1] == 10
        self.assertEqual(xy[1,1],10.0)

    def test4(self):
        xy = XYData(name='yi', x=[1, 2, 3], y=[1.1, 2.1, 3.1])
        xy.print_in_detail()
        for i in xy:
            print(tuple(i))
            print(i)

    def test5(self):#测试极值点
        xy = XYData(name='yi', x=[1, 2, 3], y=[1.1, 2.1, -3.1])
        print(xy.peak_point)
        self.assertEqual((3,-3.1),xy.peak_point)

if __name__ == '__main__':
    unittest.main()
    #
    # x = [1, 2, 3]
    # y = [1, 1, 2]
    # xy = XYData('第二种', x=x, y=y)
    # a=xy[3]
    # print(a)
