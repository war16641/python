from GoodToolPython.mybaseclasses.singleton import Singleton
from GoodToolPython.myfile import collect_all_filenames
from GoodToolPython.lol.snapscreen import *
from PIL import Image
import random
import numpy as np
import os
import time
class SampleManager(Singleton):
    def init(self):
        pass
    def classify_samples(self):
        lst=[]
        collect_all_filenames("d:/knn/unclassified",".",lst)
        valid_answer=('0','1','2','3','4','5','6','7','8','9','f',)
        for im_path in lst:
            im=Image.open(im_path)
            im.show()
            result=input("该图片为:")
            if result in  valid_answer:
                random_name=random.randint(0,1e6)
                im.save("d:/knn/classified/"+result+"_"+str(random_name)+".bmp")
            else:
                print("舍弃该图片")

    def record_images(self):
        """
        在lol里面记录生命值的图片 一旦发现特征值与上一张不同就记录下来
        :return:
        """
        count = 0
        save_path="D:\\knn\\unclassified"
        last_im=None
        last_im_crt=None
        while True:
            time.sleep(5)
            im=snap_screen(0,bbox=bbox_hp_emy)
            im=do_with_image(im)
            if last_im is  None:
                last_im=im
                last_im_crt=np.asarray(last_im)/255.0
                #保存图片
                try:
                    lst=auto_separate_image(last_im)
                except Separate_Image_Error:
                    pass
                except:
                    raise
                for i in lst:
                    count+=1
                    i.save(save_path+"/"+str(count)+".bmp")
            else:
                im_crt=np.asarray(im)/255.0
                if MyKNN.smc(last_im_crt,im_crt)<0.99:
                    #新图片
                    last_im=im
                    last_im_crt=im_crt
                    # 保存图片
                    try:
                        lst = auto_separate_image(last_im)
                    except Separate_Image_Error:
                        pass
                    except:
                        raise
                    for i in lst:
                        count += 1
                        i.save(save_path + "/" + str(count) + ".bmp")

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
class _DistanceToDataPoint:
    def __init__(self,point,similarity):
        self.point=point
        self.similarity=similarity

class OCR_FAIL(Exception):#识别出错时抛出
    pass

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

    @staticmethod
    def smc(p1,p2)->float:
        """
        计算简单匹配系数
        :param p1:
        :param p2:
        :return:
        """
        if isinstance(p1,_DataPoint) and isinstance(p2,_DataPoint):
            m1=p1.characteristic
            m2=p2.characteristic
        elif isinstance(p1,np.ndarray) and isinstance(p2,np.ndarray):
            m1=p1
            m2=p2
        assert m1.shape==m2.shape,"形状不同不能比较"
        size=m1.shape
        f00,f01,f10,f11=0.,0.,0.,0.
        for i in range(size[0]):
            for j in range(size[1]):
                a=m1[i,j]
                b=m2[i,j]
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

    def predict(self,im,min_similarity=0.85 ):
        length=len(self.data_points)
        distance_lst=[]
        im_crt=np.asarray(im)/255.0
        for pt in self.data_points:
            s=self.smc(pt.characteristic,im_crt)
            distance_lst.append(_DistanceToDataPoint(pt,s))
        distance_lst.sort(key=lambda x:x.similarity,reverse=True)
        valid_distance_lst=distance_lst[0:4]#只取前五个分析
        stat_sum=[0,0,0,0,0,0,0,0,0,0,0]#统计相似度的和
        stat_count=[0,0,0,0,0,0,0,0,0,0,0]#统计出现的次数
        chars=['0','1','2','3','4','5','6','7','8','9','f']
        for d in valid_distance_lst:
            print("%s,%f" %(d.point.classification,d.similarity))
            stat_sum[chars.index(d.point.classification)]+=d.similarity
            stat_count[chars.index(d.point.classification)]+=1
        stat_mean=[0,0,0,0,0,0,0,0,0,0,0]
        for i in range(len(chars)):
            if stat_count[i]==0:
                continue
            else:
                stat_mean[i]=stat_sum[i]/stat_count[i]
        print(stat_mean)
        if stat_mean.count(1.0)>=2:
            raise Exception("出现了两个相似度为1的数字")
        #以最高的值作为预测结果
        max_s=max(stat_mean)
        print("平均相似度 ：")
        print(stat_mean)
        # assert max_s>min_similarity,"最好的匹配结果低于预定的最低相似度，预测失败"
        if max_s<min_similarity:
            raise OCR_FAIL("最好的匹配结果低于预定的最低相似度的要求，预测失败")
        return chars[stat_mean.index(max_s)]

def ocr_script(im,knn):
    """

    :param im: 截屏图片
    :param knn:
    :return:
    """
    assert im.size==(28,12),"尺寸不对"
    im=do_with_image(im)
    im_lst=separate_image(im)
    #判断最后一位是不是数
    mt=np.asarray(im_lst[-1])/255.0
    if np.sum(mt)==0:
        im_lst.pop(3)
    jieguo=""
    for im1 in im_lst:
        p=knn.predict(im1)
        jieguo+=p
    return jieguo

def ocr_script2(im,knn):
    """

    :param im: 截屏图片
    :return:
    """
    assert im.size[1]==12,"高度必须为12"
    im1=do_with_image(im,threshold=60)
    im_sep_lst=auto_separate_image(im1)
    jieguo=""
    for im2 in im_sep_lst:
        p=knn.predict(im2)
        jieguo+=p
    return jieguo

def ocr_script3(im,knn):
    try:
        tmp= ocr_script2(im,knn)
    except (Separate_Image_Error,OCR_FAIL):
        return None
    return tmp

def detect_my_hero(knn):
    time.sleep(2)
    # for bbox in (bbox_hp,bbox_level,bbox_ad,bbox_ap):
    #     im=snap_screen(wait_time=0,bbox=bbox)
    im = snap_screen(wait_time=0, bbox=bbox_hp)
    hp=ocr_script3(im,knn)
    im = snap_screen(wait_time=0, bbox=bbox_level)
    level=ocr_script3(im,knn)
    im = snap_screen(wait_time=0, bbox=bbox_ad)
    ad=ocr_script3(im,knn)
    im = snap_screen(wait_time=0, bbox=bbox_ap)
    ap=ocr_script3(im,knn)
    return hp,level,ad,ap

def detect_enemy(knn):
    time.sleep(3)
    im = snap_screen(wait_time=0, bbox=bbox_hp_emy)
    hp=ocr_script3(im,knn)
    im = snap_screen(wait_time=0, bbox=bbox_armor_ad)
    armor_ad=ocr_script3(im,knn)
    im = snap_screen(wait_time=0, bbox=bbox_armor_ap)
    armor_ap=ocr_script3(im,knn)
    return hp,armor_ad,armor_ap

if __name__ == '__main__':
    # knn=MyKNN()
    # im=Image.open("d:/v1.bmp")
    # print(ocr_script2(im,knn))

    # knn=MyKNN()
    # # im=snap_screen(bbox=bbox_level)
    # im=Image.open("d:/a1.bmp")
    # print(ocr_script2(im,knn))


    # im=snap_screen(wait_time=3)
    # print(ocr_script(im,knn))
    # print(knn.smc(knn.data_points[0],knn.data_points[0]))
    # print(knn.smc(knn.data_points[0], knn.data_points[3]))
    # print(knn.smc(knn.data_points[1], knn.data_points[22]))
    # knn.predict(im=knn.data_points[14].image)


    man=SampleManager()
    # man.record_images()
    man.classify_samples()


    # knn=MyKNN()
    # print(detect_my_hero(knn))
