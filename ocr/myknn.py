from GoodToolPython.mybaseclasses.singleton import Singleton
from GoodToolPython.myfile import collect_all_filenames,del_file
from GoodToolPython.lol.snapscreen import *
from GoodToolPython.ocr.imagtools import snap_screen,throw_green,split_image,bbox_ap
from PIL import Image
import random
import numpy as np
import os
from itertools import combinations
import time
import winsound
import unittest

def open_image_file(fullname):
    """
    从文件中生成Image文件 这个函数为了解除Image。open(fullname)导致的文件占用问题
    :param fullname:
    :return: PIL。Image对象
    """
    fp = open(fullname, 'rb')
    img = Image.open(fp) # 这里改为文件句柄
    im=img.convert("L")
    fp.close()
    return im

class SampleManager:
    def __init__(self,model_path="D:\\knn_models\\knn_12"):
        if os.path.isdir(model_path+"\\classified") and \
            os.path.isdir(model_path + "\\OnlbvnChar") and \
            os.path.isdir(model_path + "\\unclassified"):
            self.path=model_path
        else:
            raise Exception("要求模型路径下必须有这三个文件夹")

    def classify_samples(self):
        lst=[]
        collect_all_filenames(self.path+"\\unclassified",".",lst)
        valid_answer=('0','1','2','3','4','5','6','7','8','9','f',)
        for im_path in lst:
            im=Image.open(im_path)
            im.show()
            result=input("该图片为:")
            if result in  valid_answer:
                random_name=random.randint(0,1e6)
                im.save(self.path+"\\classified\\"+result+"_"+str(random_name)+".bmp")
            else:
                print("舍弃该图片")

    def record_images(self,bbox=bbox_ap):
        """
        在lol里面记录生命值的图片 一旦发现特征值与上一张不同就记录下来
        :return:
        """
        count = 0
        last_im_crt=None #照片的特征矩阵
        save_path=self.path+"\\unclassified"
        while True:
            time.sleep(5)
            try:
                im=snap_screen(0,bbox=bbox)
                im=throw_green(im)
                #判断是否与上一张一样
                if last_im_crt is not None:
                    im_crt=np.asarray(im)
                    print(MyKNN.smc(im_crt,last_im_crt,"L"))
                    if MyKNN.smc(im_crt,last_im_crt,'L')<0.95: #不匹配
                        #分割并保存
                        im_lst=split_image(im)
                        for i in im_lst:
                            count += 1
                            i.save(save_path + "/" + str(count) + ".bmp")
                            print("保存第%d个样本"%count)
                        last_im_crt=im_crt
                    else:
                        print("当前样本与上一样本相同，舍弃")
                else:#没有第一张 直接保存
                    im_crt = np.asarray(im)
                    im_lst = split_image(im)
                    for i in im_lst:
                        count += 1
                        i.save(save_path + "/" + str(count) + ".bmp")
                        print("保存第%d个样本" % count)
                    last_im_crt = im_crt
            except Exception:
                print("创建当前样本失败")
                continue
class _DataPoint:#即classified下的已识别样本
    def __init__(self,image,characteristic,classification,filename=""):
        """

        :param image: 图片
        :param characteristic:特征值 2值矩阵
        :param classification: 类别
        """
        self.image=image
        self.characteristic=characteristic#type:np.ndarray
        self.classification=classification
        self.filename=filename


class _DistanceToDataPoint:#用于预测时，被预测的图片到knn数据点的距离
    def __init__(self,point,similarity):
        self.point=point
        self.similarity=similarity #通常为smc

class OCR_FAIL(Exception):
        pass

class MyKNN:

    @staticmethod
    def smc(p1,p2,method='2')->float:
        """
        计算简单匹配系数
        :param p1:
        :param p2:
        :param method:2 代表p1 p2只有0 和255
                        L 代表 有0~255
        :return:
        """
        def inner_script1():
            #这个代码段是处理二值图像的匹配的
            nonlocal f11,f10,f01,f00,m1,m2,fz,fm
            for i in range(size[0]):
                for j in range(size[1]):
                    a = m1[i, j]
                    b = m2[i, j]
                    # 以下代码段 在a b只能是0 或者255设计
                    if a == b:
                        if a == 255:
                            f11 += 1
                        elif a == 0:
                            f00 += 1
                        else:
                            raise Exception("出现了不是0或者255的值")
                    else:
                        if a == 0:
                            f01 += 1
                        elif b == 0:
                            f10 += 1
                        else:
                            raise Exception("出现了不是0或者255的值")
            fz=f00+f11
            fm=f00+f01+f10+f11

        def inner_script2():
            #这个代码段是处理灰度图像的匹配的
            nonlocal f11,f10,f01,f00,m1,m2,fz,fm
            for i in range(size[0]):
                for j in range(size[1]):
                    a = m1[i, j]
                    b = m2[i, j]
                    # 以下代码段 在a b只能是0 或者255设计
                    if a == b:
                        fz+=1
                        fm+=1
                    else:
                        fm+=1








        if isinstance(p1,_DataPoint) and isinstance(p2,_DataPoint):
            m1=p1.characteristic
            m2=p2.characteristic #m1 m2都是最大值为255的矩阵
        elif isinstance(p1,np.ndarray) and isinstance(p2,np.ndarray):
            m1=p1
            m2=p2
        if m1.shape!=m2.shape:#"形状不同不能比较" 直接返回0.0 的匹配系数
            return 0.0
        #选定计算方法
        if method is "2":
            func=inner_script1
        elif method is "L":
            func=inner_script2
        else:
            raise Exception("参数错误")
        size=m1.shape
        f00,f01,f10,f11=0.,0.,0.,0.
        fz,fm=0.,0. #分子 分母

        func()
        return fz/fm

    def __init__(self,model_path="D:\\knn_models\\knn_12"):
        if os.path.isdir(model_path+"\\classified") and \
            os.path.isdir(model_path + "\\OnlbvnChar") and \
            os.path.isdir(model_path + "\\unclassified"):
            self.path=model_path
        else:
            raise Exception("要求模型路径下必须有这三个文件夹")
        all_samples_pathname=[]
        collect_all_filenames(self.path+"\\classified",".",all_samples_pathname)
        #载入图像 生成数据点
        self.data_points=[]
        for ph in all_samples_pathname:
            # im=Image.open(ph)
            im=open_image_file(ph)
            characteristic=np.asarray(im)
            _, tmpfilename = os.path.split(ph)
            self.data_points.append(_DataPoint(im,characteristic,tmpfilename[0],tmpfilename))

    def predict(self,im,min_similarity=0.8 ,inspection=False,print_info=False,valid_distance_num=9,save_failed_sample=False):
        """

        :param im: 只能是二值图
        :param min_similarity:
        :param inspection:
        :param print_info:
        :param valid_distance_num:
        :param save_failed_sample:保存识别失败的图
        :return:
        """
        if im.mode!='L':
            im=im.convert("L")#化为灰度图
        width = im.width
        height = im.height
        # if width!=7 or height!=12:#化为标注尺寸
        #     im=im.resize((7,12))

        length=len(self.data_points)
        distance_lst=[]
        im_crt=np.asarray(im)
        for pt in self.data_points:
            s=self.smc(pt.characteristic,im_crt)
            distance_lst.append(_DistanceToDataPoint(pt,s))
        distance_lst.sort(key=lambda x:x.similarity,reverse=True)
        valid_distance_lst=distance_lst[0:valid_distance_num]#只取前五个分析
        stat_sum=[0,0,0,0,0,0,0,0,0,0,0]#统计相似度的和
        stat_count=[0,0,0,0,0,0,0,0,0,0,0]#统计出现的次数
        stat_max=[0,0,0,0,0,0,0,0,0,0,0]#统计匹配系数最大值
        chars=['0','1','2','3','4','5','6','7','8','9','f']
        if print_info is True:
            print("有效距离列表：")
        for d in valid_distance_lst:
            if print_info is True:
                print("%s,%f" %(d.point.classification,d.similarity))
            stat_sum[chars.index(d.point.classification)]+=d.similarity
            stat_count[chars.index(d.point.classification)]+=1
            if d.similarity>stat_max[chars.index(d.point.classification)]:#更新最大匹配系数
                stat_max[chars.index(d.point.classification)]=d.similarity
        stat_mean=[0,0,0,0,0,0,0,0,0,0,0]
        for i in range(len(chars)):
            if stat_count[i]==0:
                continue
            else:
                stat_mean[i]=stat_sum[i]/stat_count[i]
        if print_info is True:
            print("各结果平均值：")
            for i in range(len(stat_mean)):
                print("\t%s\t%f"%(chars[i],stat_mean[i]))
            print("各结果最佳值:")
            for i in range(len(stat_mean)):
                print("\t%s\t%f"%(chars[i],stat_max[i]))
        # print(stat_mean)
        if stat_mean.count(1.0)>=2 or stat_max.count(1.0)>=2:
            raise Exception("出现了两个相似度为1的数字")
        #以stat_max最高的值作为预测结果
        max_s=max(stat_max)
        # assert max_s>min_similarity,"最好的匹配结果低于预定的最低相似度，预测失败"
        if max_s<min_similarity:
            if save_failed_sample is True:
                im.save(self.path+"\\unclassified\\0.bmp")
                winsound.Beep(1100, 1000)#发出声音 可以注释掉
            raise OCR_FAIL("最好的匹配结果低于预定的最低相似度的要求，预测失败")
        if inspection is False:
            return chars[stat_max.index(max_s)]
        else:
            return chars[stat_mean.index(max_s)],valid_distance_lst


    def check_for_repetition(self):
        """
        检查重复的 已经识别的图像
        :return:
        """
        lst=[]
        for d1,d2 in combinations(self.data_points,2):
            if self.smc(d1,d2)==1.0:
                if d1 in lst or d2 in lst:
                    continue
                lst.append(d1)
        for i in lst:
            print("删除：%s"%i.filename)
            del_file(self.path+"/classified/"+i.filename)

    def _script(self,d0):
        #d0 与剩下所有点的距离
        #仅做测试用
        print("d0:%s"%d0.filename)
        print("____________________")
        for d in self.data_points:
            print("%s---%f"%(d.filename,self.smc(d0,d)))


def script1():#记录样本
    sm=SampleManager("D:\\knn_models\\knn_18")
    sm.record_images()
def script2():#人工识别样本 并归入classified
    sm=SampleManager("D:\\knn_models\\knn_18")
    sm.classify_samples()

def script3():  # 删除重复已识别样本
    sm = MyKNN("D:\\knn_models\\knn_18")
    # sm._script(sm.data_points[1])
    sm.check_for_repetition()

def script4():#抓取一个图片 进行识别
    knn = MyKNN("D:\\knn_models\\knn_18")
    while True:
        im = snap_screen(wait_time=3, bbox=bbox_ap)
        im = throw_green(im)
        im_lst = split_image(im)
        for i in im_lst:
            print(knn.predict(i,save_failed_sample=True))

if __name__ == '__main__':
    script4()
    # knn = MyKNN("D:\\knn_models\\knn_18")
    # im=Image.open(r"D:\knn_models\knn_18\classified\7_912475.bmp")
    # print(knn.predict(im,print_info=True))