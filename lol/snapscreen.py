import time
import numpy as np
from PIL import ImageGrab
# import pytesseract
from PIL import Image
import random
# from knn import MyKNN
from GoodToolPython.myfile import is_number
# # 每抓取一次屏幕需要的时间约为1s,如果图像尺寸小一些效率就会高一些
# im=ImageGrab.grab()
#
# im.save("d:/123.bmp")
# import pytesseract
# from PIL import Image
# pytesseract.pytesseract.tesseract_cmd = "D:\Program Files\Tesseract-OCR\\tesseract.exe"
# # text = pytesseract.image_to_string(Image.open("D:\\t2b.bmp"))
# text = pytesseract.image_to_string(Image.open("D:\\t4_py.bmp"))
# print(text)


# bbox_hp=(600,732,668,744,)#hp所在范围
# bbox_level=(441,741,455,753)
# bbox_ad=(976,679,1010,691)
# bbox_ap=(1042,679,1080,691)
# bbox_hp_emy=(155,28,237,40)
# bbox_armor_ad=(23,30,48,42)
# bbox_armor_ap=(67,30,92,42)

bbox_ap=(1463,951,1517,972)
bbox_level=(623,1043,637,1060)
bbox_hp=(840,1030,948,1045)



def snap_screen(wait_time=3,bbox=(640, 732, 668, 744,)):
    time.sleep(wait_time)
    # im = ImageGrab.grab(bbox=(640, 732, 661, 744,))
    # im = ImageGrab.grab(bbox=(640, 732, 671, 744,))
    if bbox=='full':
        im=ImageGrab.grab()
    else:
        im = ImageGrab.grab(bbox)
    return im

def do_with_image(im,threshold = 68):
    width, height = im.size
    # 扔掉绿色通道的信息
    source = im.split()
    R, G, B = 0, 1, 2
    mtr = np.array(source[G])
    r = source[R]
    tmp = Image.new("RGB", (width, height,), "black")  # 用纯黑图片的绿色通道信息覆盖原图片的绿色通道信息
    tmp_r, tmp_g, tmp_b = tmp.split()
    t1 = Image.merge('RGB', [source[R], tmp_g, source[B]])
    # 阈值转化 转化为2值图像
    t2 = t1.convert("L")
    #  setup a converting table with constant threshold

    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    t2 = t2.point(table, "1")
    #在转化为灰度图 矩阵中个元素值为0-255
    t2=t2.convert("L")
    return t2

def do_with_image2(im,threshold = 68):
    """
    把位图（含颜色信息）转换为2值图，同时把高度缩放到12
    :param im:
    :param threshold:
    :return:
    """
    width, height = im.size
    #高度调整为12
    im=im.resize((int(width*12/height),12))
    width, height = im.size
    # 扔掉绿色通道的信息
    source = im.split()
    R, G, B = 0, 1, 2
    mtr = np.array(source[G])
    r = source[R]
    tmp = Image.new("RGB", (width, height,), "black")  # 用纯黑图片的绿色通道信息覆盖原图片的红色通道信息
    tmp_r, tmp_g, tmp_b = tmp.split()
    t1 = Image.merge('RGB', [tmp_r, source[G], source[B]])
    # 阈值转化 转化为2值图像
    t2 = t1.convert("L")
    #  setup a converting table with constant threshold

    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    t2 = t2.point(table, "1")
    #在转化为灰度图 矩阵中个元素值为0-255
    t2=t2.convert("L")
    return t2


def do_with_image3(im,threshold = 68):
    """
    把位图（含颜色信息）转换为2值图，同时把高度缩放到12
    :param im:
    :param threshold:此值越大，白色的点越少
    :return:
    """
    width, height = im.size
    #高度调整为12
    im=im.resize((int(width*12/height),12))
    width, height = im.size
    # 扔掉绿色通道的信息
    source = im.split()
    R, G, B = 0, 1, 2
    mtr = np.array(source[G])
    r = source[R]
    tmp = Image.new("RGB", (width, height,), "black")  # 用纯黑图片的绿色通道信息覆盖原图片的红色通道信息
    tmp_r, tmp_g, tmp_b = tmp.split()
    t1 = Image.merge('RGB', [source[R], tmp_g, source[B]])
    # 阈值转化 转化为2值图像
    t2 = t1.convert("L")
    #  setup a converting table with constant threshold

    table = []
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    t2 = t2.point(table, "1")
    #在转化为灰度图 矩阵中个元素值为0-255
    t2=t2.convert("L")
    return t2

def ocr_until_success(im):
    raise Exception("已经舍弃了")
    # pytesseract.pytesseract.tesseract_cmd = "D:\Program Files\Tesseract-OCR\\tesseract.exe"
    # attempt_throshold=[50,51,55,60,65,70, 75, 80 ,85]
    # attempt_throshold=np.arange(50,80,2)
    # for t in attempt_throshold:
    #     im1=do_with_image(im,t)
    #     string= pytesseract.image_to_string(im1)
    #     flag,number=is_number(string)
    #     if flag==True:
    #         return number
    # return 0

class Separate_Image_Error(Exception):
    pass
def separate_image(im):
    #传入的im大小为28*12 分割为4个7*12  (1,8,15,21,)
    width,height=im.size
    lst=[]
    for st in (0,7,14,21,):
        lst.append(im.crop((st,0,st+7,12)))
    return lst
def auto_separate_image(im):
    """
    把含一串数字的二值图自动分割为一系列只含一个数字的二值图
    :param im: 二值图
    :return:列表
    """
    def process_mat(im_seq_mt):
        black_col = np.zeros(shape=(height, 1))  # 用于补充矩阵
        width_ind=im_seq_mt.shape[1]
        if width_ind == 5:
            # 左右各加宽1
            im_seq_mt = np.hstack((black_col, im_seq_mt, black_col))
            # im_sep=im.crop((a-1,0,b+1,12))
        elif width_ind == 6:
            # 右边加宽
            im_seq_mt = np.hstack((im_seq_mt, black_col))
            # im_sep = im.crop((a , 0, b + 1, 12))
        elif width_ind == 3:
            # 斜杆 左右加宽2
            im_seq_mt = np.hstack((black_col, black_col, im_seq_mt, black_col, black_col))
            # im_sep = im.crop((a-2, 0, b + 2, 12))
        elif width_ind == 4:
            # 左1 右2
            im_seq_mt = np.hstack((black_col, im_seq_mt, black_col, black_col))
            # im_sep = im.crop((a - 1, 0, b + 2, 12))
        elif width_ind == 7:
            pass
        elif width_ind==8:
            #分析0列 7列 谁的信息少就扔掉谁
            t1=np.sum(im_seq_mt[:,0])
            t2 = np.sum(im_seq_mt[:, 7])
            if t1<t2:
                im_seq_mt=im_seq_mt[:,1:]
            else:
                im_seq_mt = im_seq_mt[:, 0:7]
        else:
            print("错误:")
            print(im_seq_mt)
            raise Separate_Image_Error("错误的宽度,%d" % width_ind)
        return im_seq_mt



    mt=np.asarray(im)/255.0
    if np.sum(mt)<=3:
        print("有效点过少")
        return []
    width=mt.shape[1]
    height=mt.shape[0]
    black_col=np.zeros(shape=(height,1))#用于补充矩阵
    flag_find=False#是否发现切割对象
    a=0
    b=0
    im_sep_lst=[]
    for i in range(width):
        col=mt[:,i]
        # print(mt[:,i])
        he=np.sum(col)
        if he>=1:#发现图像
            if flag_find==False:
                a=i
                flag_find=True
            else:
                pass
        else:#未发现图像
            if flag_find==True:
                b=i
                flag_find=False
                #切割图片
                width_ind=b-a
                if width_ind<=2:
                    raise Separate_Image_Error("太窄")
                #去除噪点
                im_seq_mt=mt[:,a:b]
                side_num=np.sum(im_seq_mt[:,0])
                in_num = np.sum(im_seq_mt[:, 1])
                # if in_num-side_num==6:#超过6个 认为是噪点
                #     width_ind-=1
                #     im_seq_mt=mt[:,a+1:b]
                side_num = np.sum(im_seq_mt[:, -1])
                in_num = np.sum(im_seq_mt[:, -2])
                # if in_num-side_num>=6:#超过6个 认为是噪点
                #     width_ind-=1
                #     im_seq_mt=mt[:,a:b-1]

                im_seq_make=Image.fromarray(im_seq_mt*255)


                #截取
                if width_ind>=15:
                    half=int(width_ind/2)
                    m1=im_seq_mt[:,0:half]
                    m2=im_seq_mt[:,half:]
                    mt_lst=[m1,m2]
                else:
                    mt_lst=[im_seq_mt]
                # im_seq_mt = process_mat(im_seq_mt)
                # if width_ind ==5:
                #     #左右各加宽1
                #     im_seq_mt=np.hstack((black_col,im_seq_mt,black_col))
                #     # im_sep=im.crop((a-1,0,b+1,12))
                # elif width_ind==6:
                #     #右边加宽
                #     im_seq_mt = np.hstack(( im_seq_mt, black_col))
                #     # im_sep = im.crop((a , 0, b + 1, 12))
                # elif width_ind==3:
                #     #斜杆 左右加宽2
                #     im_seq_mt = np.hstack((black_col, black_col,im_seq_mt,black_col, black_col))
                #     # im_sep = im.crop((a-2, 0, b + 2, 12))
                # elif width_ind==4:
                #     #左1 右2
                #     im_seq_mt = np.hstack((black_col, im_seq_mt, black_col, black_col))
                #     im_sep = im.crop((a - 1, 0, b + 2, 12))
                # elif width_ind==7:
                #     pass
                # elif width_ind>=10:#对半分
                #     pass
                # else:
                #     print("错误:")
                #     print(im_seq_mt)
                #     raise Separate_Image_Error("错误的宽度,%d"%width_ind)
                for mt1 in mt_lst:
                    im_seq=Image.fromarray(process_mat(mt1)*255)
                    im_seq=im_seq.convert("L")
                    im_sep_lst.append(im_seq)
            else:
                pass
    return im_sep_lst

def reverse_color(im):
    """
    反色
    :param im: 灰度图
    :return: 灰度图
    """
    assert im.mode=='L','必须为灰度图'
    for i in range(im.height):
        for j in range(im.width):
            im[i, j] = 255 - im[i, j]
    pass
def sampling(bbox):
    #实时采集并分割
    #返回截屏图片
    im=snap_screen(wait_time=3,bbox=bbox)
    im.save("d:/knn/unclassified/"+str(random.randint(0,1e4))+".bmp")
    im1=do_with_image(im,threshold=60)
    im1.show()
    lst=auto_separate_image(im1)
    c=1
    for im2 in lst:
        im2.save("d:/knn/unclassified/"+str(random.randint(0,1e4))+".bmp")
    return im
                
            
            
if __name__ == '__main__':
    # pathname="d:\\auto.bmp"
    # # im=snap_screen(bbox='full')
    # im = snap_screen(bbox=(1463,951,1517,972))
    # # im.show()
    # im.save("d:\\a2.bmp")
    # im1=im.resize((31,12))
    # im1.show()
    # im1.save("d:\\last.bmp")

    fp = open("d:\\snap.bmp", 'rb')
    img = Image.open(fp)  # 这里改为文件句柄
    img=do_with_image3(img,threshold=50)
    img.show()
    knn=MyKNN()
    for i in img:
        print(knn.predict(i))





    # im=do_with_image(im)
    # im.save("d:\\a2.bmp")
    # im.save(pathname)
    # pytesseract.pytesseract.tesseract_cmd = "D:\Program Files\Tesseract-OCR\\tesseract.exe"
    # text = pytesseract.image_to_string(im)
    # print(text)
