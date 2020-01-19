"""
测试平台 集合一些函数 实现一些功能
"""
from snapscreen import snap_screen,do_with_image2,auto_separate_image,bbox_ap,bbox_level,bbox_hp,do_with_image3
from knn import MyKNN
from PIL import Image

def test1():#从即时游戏界面中识别
    im=snap_screen(bbox=bbox_hp)
    im.show()
    im.save("d:\\snap.bmp")
    im=do_with_image2(im)
    # im.show()
    im_lst=auto_separate_image(im)
    if len(im_lst)!=0:
        knn=MyKNN()
        for i in im_lst:
            # i.show()
            print(knn.predict(i))

def test2():#从保存的位图中识别
    im=Image.open("d:\\snap.bmp")
    im=do_with_image3(im,threshold=40)
    # im.show()
    im_lst=auto_separate_image(im)
    if len(im_lst)!=0:
        knn=MyKNN()
        for i in im_lst:
            # i.show()
            print(knn.predict(i,min_similarity=0.6))
if __name__ == '__main__':
    test2()