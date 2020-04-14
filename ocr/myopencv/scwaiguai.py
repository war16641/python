import time
from typing import List, Tuple

import cv2

import ocr.windows_automation as wa


import numpy as np
from ocr.imagtools import snap_screen

shuzifont = cv2.FONT_HERSHEY_SIMPLEX



def match_template(image,template,max_counter=20,val_valve=0.9, annotation=False,return_center=False,anno_txt='')->List[Tuple]:
    """
    在大图片image中寻找小图片template的位置
    @param image:
    @param template:
    @param max_counter: 最大匹配次数
    @param val_valve: 判断匹配成功的最小值
    @param annotation: 是否把匹配到的区域标注
    @param return_center:是否返回中心点坐标 默认是左上角
    @return: image中tempalte出现的位置们  左上角 若匹配失败返回空列表
    """


    def getNextMax(res, max_loc, min_val, h, w):
        # 将上一个max位置矩阵内的值都置为最小值，然后重新找最大值及其位置
        for i in range(max_loc[0], min(max_loc[0] + w, res.shape[1])):
            for j in range(max_loc[1], min(max_loc[1] + h, res.shape[0])):
                res[j][i] = min_val
                # print('change value')
        res = np.float32(res)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print('max_val:',max_val)
        return min_val, max_val, min_loc, max_loc, res
        pass

    def getNextMax1(res, max_loc, min_val, h, w):
        #改变策略：以最值点为中心 h*w的区域置为最小值
        for i in range(max((0,max_loc[0]-int(w/2),)), min(max_loc[0] + int(w/2), res.shape[1])):
            for j in range(max(0,max_loc[1]-int(h/2),), min(max_loc[1] + int(h/2), res.shape[0])):
                res[j][i] = min_val
                # print('change value')
        res = np.float32(res)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        # print('max_val:',max_val)
        return min_val, max_val, min_loc, max_loc, res
        pass

    # print(type(image), image.shape)
    # print(type(template), template.shape)
    ##以下可以将图片转换为黑白
    # image = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    # template = cv2.cvtColor(template,cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)#TM_CCOEFF_NORMED 匹配算法不能更改 会影响到匹配度依赖maxval或者minval
    h, w = template.shape[0], template.shape[1]
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    counter=0#标记找到的个数
    max_locs=[]
    while max_val > val_valve and counter<max_counter:
        if annotation:
            top_left = max_loc#max_loc是image匹配到template的坐标点
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(image, top_left, bottom_right, 255, 2)#添加矩形框
            cv2.putText(image, anno_txt+str(counter+1), top_left, shuzifont, 1.2, (0, 0, 255), 2)#添加文字 图像，文字内容， 坐标 ，字体，大小，颜色，字体厚度
            cv2.putText(image, "%.2f"%max_val, bottom_right, shuzifont, 0.8, (0, 0, 200), 1)#把匹配度标出
        t=max_val
        max_locs.append(max_loc)
        min_val, max_val, min_loc, max_loc, res = getNextMax1(res, max_loc, min_val, h, w)
        counter+=1
        print("第%d个:%f,%f"%(counter,t,max_val))

    if annotation:
        # cv2.imshow('res', res)
        cv2.imshow('compare', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        pass

    #是否返回中心点
    if return_center:
        t=[]
        for i in max_locs:
            t.append((i[0]+int(w/2),i[1]+int(h/2),))
        max_locs=t
    return max_locs

def match_templates(image, templates, max_counter=20, val_valve=0.9, annotation=False, return_center=False,final_anno=False) -> List:
    """
    在大图片image中寻找小图片template的位置
    @param image:
    @param template:
    @param max_counter: 最大匹配次数
    @param val_valve: 判断匹配成功的最小值
    @param annotation: 是否把匹配到的区域标注
    @param return_center:是否返回中心点坐标 默认是左上角
    @return: image中tempalte出现的位置们  左上角 若匹配失败返回空列表
    """
    many_locs=[]
    for i,templ in enumerate(templates):
        image1=image.copy()#复制一个新的image
        lcs=match_template(image1,templ,max_counter,val_valve,annotation,return_center=False,anno_txt=str(i)+"-")
        h, w = templ.shape[0], templ.shape[1] #当前templ的大小
        for lc in lcs:
            many_locs.append([i,lc])
            #给已识别的区域填上矩形
            top_left = lc  # max_loc是image匹配到template的坐标点
            bottom_right = (top_left[0] + w, top_left[1] + h)
            cv2.rectangle(image, top_left, bottom_right, [0,255,0], -1)  # 添加矩形框
    if final_anno:
        cv2.imshow('final result', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    return many_locs



def script_scv_build_gas(scv_pos,gas_pos):
    wa.mouse_click(scv_pos[0], scv_pos[1])
    time.sleep(0.01)
    wa.key_input('br', input_inteval=0.05)
    wa.mouse_click(gas_pos[0], gas_pos[1])
    pass

def find_in_image():
    image = cv2.imread(r"D:\a\bigmother1.png")
    template = cv2.imread(r"D:\a\terren_vs.png")
    lcs = match_template(image, template, max_counter=20, val_valve=0.4, annotation=True,return_center=False)
    for pt in lcs:
        print(pt)

def find_in_image1():
    image = cv2.imread(r"D:\a\bigmother1.png")
    template1 = cv2.imread(r"D:\a\terren_bb2.png")
    template = cv2.imread(r"D:\a\terren_vs.png")
    lcs = match_templates(image, [template,template1], max_counter=20, val_valve=0.4, annotation=False,return_center=False,final_anno=True)
    for pt in lcs:
        print(pt)

def find_in_image2():
    #scv valve 0.9
    #valve至少0.7 否则会把奇怪的东西纳入进来
    image = cv2.imread(r"D:\a\SCScrnShot_041420_145417.png")
    tps=[]
    for i in range(14):
        tps.append(cv2.imread(r"D:\a\terren_scv"+str(i)+".png"))
    lcs = match_templates(image, tps, max_counter=30, val_valve=0.7, annotation=False,return_center=False,final_anno=True)
    for pt in lcs:
        print(pt)

def find_in_image3():
    #gas valve 0.9
    image = cv2.imread(r"D:\a\SCScrnShot_041420_143939.png")
    tps=[]
    for i in range(2):
        tps.append(cv2.imread(r"D:\a\gas"+str(i)+".png"))
    lcs = match_templates(image, tps, max_counter=30, val_valve=0.7, annotation=False,return_center=False,final_anno=True)
    for pt in lcs:
        print(pt)

def test():
    #指挥scv造gas
    tps = []
    for i in range(14):
        tps.append(cv2.imread(r"D:\a\terren_scv" + str(i) + ".png"))
    tps1 = []
    for i in range(5):
        tps1.append(cv2.imread(r"D:\a\gas" + str(i) + ".png"))
    while True:
        im = snap_screen(wait_time=0)
        image = np.array(im)
        image1=image.copy()

        buildflag=True

        lcs_scv = match_templates(image, tps, max_counter=30, val_valve=0.85, annotation=False, return_center=False,
                              final_anno=False)
        for pt in lcs_scv:
            print(pt)
        if len(lcs_scv)!=0:
            scvpos = lcs_scv[0][1]
        else:
            print('没找到scv')
            buildflag = False


        lcs_gas = match_templates(image1, tps1, max_counter=30, val_valve=0.9, annotation=False, return_center=False,
                              final_anno=False)
        for pt in lcs_gas:
            print(pt)
        if len(lcs_gas)!=0:
            gaspos = lcs_gas[0][1]
        else:
            buildflag = False
            print('没找到gas')
        if buildflag:
            #准备造gas

            #用最小数量作为建造数量
            num=min(len(lcs_gas),len(lcs_scv))
            print('准备造%d个gas'%num)
            #挨个造
            for i in range(num):
                script_scv_build_gas(lcs_scv[i][1], lcs_gas[i][1])
                time.sleep(0.1)
            time.sleep(0.5)


if __name__ == '__main__':
    find_in_image2()
    # print("start")
    # template = cv2.imread(r"D:\a\son.png")
    # while True:
    #     print('开始新捕捉...')
    #     im = snap_screen(wait_time=3)
    #     # im.show()
    #     image = np.array(im)
    #     lcs = match_template(image, template, max_counter=40, val_valve=0.8, annotation=True,return_center=True)
    #     print("找到bb%d个：%s"%(len(lcs),lcs.__str__()))
    #     for pt in lcs:
    #         wa.mouse_click(pt[0],pt[1])
    #         time.sleep(0.005)
    #         wa.key_input('zz',input_inteval=0.05)
    #     break
