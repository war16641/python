import time
import numpy as np
from PIL import ImageGrab
import pytesseract
from PIL import Image
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

def snap_screen(wait_time=3,bbox=(640, 732, 668, 744,)):
    time.sleep(wait_time)
    # im = ImageGrab.grab(bbox=(640, 732, 661, 744,))
    # im = ImageGrab.grab(bbox=(640, 732, 671, 744,))
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

def ocr_until_success(im):
    pytesseract.pytesseract.tesseract_cmd = "D:\Program Files\Tesseract-OCR\\tesseract.exe"
    attempt_throshold=[50,51,55,60,65,70, 75, 80 ,85]
    attempt_throshold=np.arange(50,80,2)
    for t in attempt_throshold:
        im1=do_with_image(im,t)
        string= pytesseract.image_to_string(im1)
        flag,number=is_number(string)
        if flag==True:
            return number
    return 0

def separate_image(im):
    #传入的im大小为28*12 分割为4个7*12  (1,8,15,21,)
    width,height=im.size
    lst=[]
    for st in (0,7,14,21,):
        lst.append(im.crop((st,0,st+7,12)))
    return lst
def auto_separate_image(im):
    """

    :param im: 灰度图像
    :return:
    """
    mt=np.asarray(im)/255.0
    width=mt.shape[1]
    flag_find=False#是否发现切割对象
    a=0
    b=0
    im_sep_lst=[]
    for i in range(width):
        col=mt[:,i]
        print(mt[:,i])
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
                if width_ind ==5:
                    #左右各加宽1
                    im_sep=im.crop((a-1,0,b+1,12))
                    im_sep.show()
                elif width_ind==6:
                    #右边加宽
                    im_sep = im.crop((a , 0, b + 1, 12))
                    im_sep.show()
                elif width_ind==3:
                    #斜杆 左右加宽2
                    im_sep = im.crop((a-2, 0, b + 2, 12))
                    im_sep.show()
                else:
                    raise Exception("错误的宽度")
                im_sep_lst.append(im_sep)
            else:
                pass
    return im_sep_lst
            
        
                
            
            
if __name__ == '__main__':
    pathname="d:\\auto.bmp"
    im=snap_screen()
    im.save("d:\\a1.bmp")
    im=do_with_image(im)
    im.save("d:\\a2.bmp")
    # im.save(pathname)
    pytesseract.pytesseract.tesseract_cmd = "D:\Program Files\Tesseract-OCR\\tesseract.exe"
    text = pytesseract.image_to_string(im)
    print(text)
