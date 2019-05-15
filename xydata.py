import numpy as np
from typing import overload,TypeVar
from copy import deepcopy
from GoodToolPython.mybaseclasses.tools import is_vector_like,format_vector
import matplotlib.pyplot as plt
from myfile import read_file


Vector=TypeVar('Vector',list,np.ndarray)

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
            assert isinstance(xy,np.ndarray),'xy必须为数组'
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

    def plot(self):
        if len(self) == 0:
            print('无数据点，做图取消')
            return
        plt.plot(self.data[:,0],self.data[:,1])
        plt.title(self.name)
        plt.show()

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



if __name__ == '__main__':
    A=np.array([[1, 1],[2, 1],[3 ,2]])
    xy=XYData('数据集',A)
    print(xy)
    xy.print_in_detail()

    x=[1,2,3]
    y=[1,1,2]
    xy=XYData('第二种',x=x,y=y)
    xy.print_in_detail()

    x = np.array([1, 2, 3])
    y = np.array([1, 1, 2])
    xy = XYData('第二种', x=x, y=y)
    xy.print_in_detail()

    x = np.array([1, 2, 3])
    y = np.array([1, 1, 2])
    x=x.reshape((1,3))
    xy = XYData('第二种', x=x, y=y)
    xy.print_in_detail()
    xy.interpolation(2)
    xy.print_in_detail()

    ori=read_file("F:\X撑1\地震波\Kobe.txt")
    xy=XYData(name='kobe',xy=ori)
    # xy.plot()
    # xy.plot()
    xy.psd(False)
