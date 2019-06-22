from GoodToolPython.mybaseclasses.singleton import Singleton
from GoodToolPython.myfile import collect_all_filenames
from PIL import Image
import random
import numpy as np
import os
class SampleManager(Singleton):
    def init(self):
        pass
    def classify_samples(self):
        lst=[]
        collect_all_filenames("d:/knn/unclassified",".",lst)
        valid_answer=('0','1','2','3','4','5','6','7','8','9',)
        for im_path in lst:
            im=Image.open(im_path)
            im.show()
            result=input("该图片为:")
            if result in  valid_answer:
                random_name=random.randint(0,1e6)
                im.save("d:/knn/classified/"+result+"_"+str(random_name)+".bmp")
            else:
                print("舍弃该图片")

class _DataPoint:
    def __init__(self,image,characteristic,classification):
        """

        :param image: 图片
        :param characteristic:特征值
        :param classification: 类别
        """
        self.image=image
        self.characteristic=characteristic#type:np.ndarray
        self.classification=classification

class MyKNN:
    def __init__(self):
        samples_path="D:\knn\classified"
        all_samples_pathname=[]
        collect_all_filenames(samples_path,".",all_samples_pathname)
        #载入图像 生成数据点
        self.data_points=[]
        for ph in all_samples_pathname:
            im=Image.open(ph)
            characteristic=np.asarray(im)/255.0
            _, tmpfilename = os.path.split(ph)
            self.data_points.append(_DataPoint(im,characteristic,tmpfilename[0]))

    def smc(self,p1:_DataPoint,p2:_DataPoint)->float:
        """
        计算简单匹配系数
        :param p1:
        :param p2:
        :return:
        """

        assert p1.characteristic.shape==p2.characteristic.shape,"形状不同不能比较"
        size=p1.characteristic.shape
        f00,f01,f10,f11=0.,0.,0.,0.
        for i in range(size[0]):
            for j in range(size[1]):
                a=p1.characteristic[i,j]
                b=p2.characteristic[i,j]
                if a==1:
                    if b==1:
                        f11+=1
                    else:
                        f10+=1
                else:
                    if b==1:
                        f01+=1
                    else:
                        f00+=1
        return (f00+f11)/(f00+f01+f10+f11)

if __name__ == '__main__':
    knn=MyKNN()
    print(knn.smc(knn.data_points[0],knn.data_points[0]))
    print(knn.smc(knn.data_points[0], knn.data_points[1]))
    print(knn.smc(knn.data_points[1], knn.data_points[2]))


