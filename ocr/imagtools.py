import time
import numpy as np
from PIL import ImageGrab
from PIL import Image
import random
import GoodToolPython.lol.knn_gui as kg

def split_image(im):
    """
    分割图片
    :param im:pil图片
    :return:列表【pil.图片】 并且处理了四周的留白
    """
    # assert im.mode=='L','image必须为灰度图'
    if im.mode!='L':#非灰度图转换为灰度图
        im=im.convert("L")
    mt0 = np.asarray(im)
    width = mt0.shape[1]
    height = mt0.shape[0]

    threshold_value=100#二值图的界限值 大于的是白色 小于的为黑色
    mt_bn=mt0.copy()#二值图矩阵
    mt_bn[mt0<=threshold_value]=0
    mt_bn[mt0>threshold_value]=255
    #去除上下的留白
    hanghe=np.sum(mt_bn,axis=1)#对行求和
    for i,he in enumerate(hanghe):
        if he!=0:
            start=i
            break
        if i==height-1:
            raise Exception("图片为空白")
    for i in range(height-1,-1,-1):
        if hanghe[i]!=0:
            end=i
            break
        if i==0:
            raise Exception("图片为空白")
    mt_bn_short=mt_bn[start:end+1,:]#去除上下留白后的二值图矩阵

    #开始分割
    liehe=np.sum(mt_bn_short,axis=0)#对列求和
    flag_find=False#标志是否开始记录
    lst_mt_individual=[]#存储单个数字的矩阵
    for i in range(width):
        if liehe[i]==0:#空白列
            if flag_find is True:
                end=i
                lst_mt_individual.append(mt_bn_short[:,start:end])
                flag_find=False
            else:
                pass
        else:#有数据列
            if flag_find is True:
                pass
            else:
                start=i
                flag_find=True
    if flag_find is True:
        end=width
        flag_find = False
        lst_mt_individual.append(mt_bn_short[:, start:end])

    lst_im_individual=[]#存储分割好的图片
    # #由矩阵生成图片
    # for m in lst_mt_individual:
    #     tmp=Image.fromarray(m)
    #     tmp=tmp.convert("L")
    #     # tmp.show()
    #     lst_im_individual.append(tmp)

    #添加四周的留白 并保持到列表中
    margin_vertical=0.1#上下留白宽度占总高度的比例
    margin_horizontal=0.15#
    for m in lst_mt_individual:
        height1=m.shape[0]
        width1=m.shape[1]
        margin_height = height1 / (1 - margin_vertical) * margin_vertical / 2
        margin_height = round(margin_height)  # 单边上下留白的宽度
        tmp = np.zeros((margin_height,width1))
        m=np.vstack((tmp,m,tmp))#竖向连接

        height1 = m.shape[0]
        width1 = m.shape[1]
        margin_width = width1 / (1 - margin_horizontal) * margin_horizontal / 2
        margin_width = round(margin_width)  # 单边上下留白的宽度
        tmp = np.zeros((height1, margin_width))
        m = np.hstack((tmp, m, tmp))  # 水平连接


        #留白宽度再处理
        height1 = m.shape[0]
        width1 = m.shape[1]
        if height1/width1>2.0:#认为太窄了
            width2=height1/1.4#左右加宽留白 到比值为1.4
            t=(width2-width1)/2
            t=round(t)
            tmp = np.zeros((height1, t))
            m = np.hstack((tmp, m, tmp))  # 添加宽度到1.4左右的比例
        height1 = m.shape[0]
        width1 = m.shape[1]
        # print("%d,%d:%f" % (height1, width1, height1 / width1))

        #生成图片
        tmp = Image.fromarray(m)
        tmp = tmp.convert("L")
        # tmp.show()
        lst_im_individual.append(tmp)
        pass
    return lst_im_individual




    pass

if __name__ == '__main__':
    im=Image.open("e:/d3.bmp")
    lst=split_image(im)
    gp=kg.start_gui_for_knn()
    for im in lst:
        kg.make_gui_predict(im,gp)
        time.sleep(4)