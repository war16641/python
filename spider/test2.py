from urllib import request
from urllib.request import urlopen
from bs4 import BeautifulSoup
import os
import time
import re
import threading


# 全局声明的可以写到配置文件，这里为了读者方便看，故只写在一个文件里面
# 图片地址
picpath = r'E:\spider'
# 豆瓣地址
douban_url = "https://www.dbmeinv.com?cid=%s&pager_offset=%s"


# 保存路径的文件夹，没有则自己创建文件夹,不能创建上级文件夹
def setpath(name):
    path = os.path.join(picpath, name)
    if not os.path.isdir(path):
        os.mkdir(path)
    return path


# 获取html内容
def get_html(url):
    req = request.Request(url)
    return request.urlopen(req).read()


# 获取图片地址
def get_ImageUrl(html):
    data = BeautifulSoup(html, "lxml")
    r = r'(https://\S+\.jpg)'
    p = re.compile(r)
    return re.findall(p, str(data))


# 保存图片
def save_image(savepath, url):
    content = urlopen(url).read()
    # url[-11:] 表示截取原图片后面11位
    with open(savepath + '/' + url[-11:], 'wb') as code:
        code.write(content)


def do_task(savepath, cid, index):
    url = douban_url % (cid, index)
    html = get_html(url)
    image_list = get_ImageUrl(html)
    # 此处判断其实意义不大，程序基本都是人手动终止的，因为图片你是下不完的
    if not image_list:
        print(u'已经全部抓取完毕')
        return
    # 实时查看，这个有必要
    print("=============================================================================")
    print(u'开始抓取Cid= %s 第 %s 页' % (cid, index))
    for image in image_list:
        save_image(savepath, image)
    # 抓取下一页
    do_task(savepath, cid, index+1)


if __name__ == '__main__':
    # 文件名
    filename = "DouBan"
    filepath = setpath(filename)

    # 2-胸 3-腿 4-脸 5-杂 6-臀 7-袜子
    for i in range(2, 8):
        do_task(filepath, i, 1)

    # threads = []
    # for i in range(2, 4):
    #     ti = threading.Thread(target=do_task, args=(filepath, i, 1, ))
    #     threads.append(ti)
    # for t in threads:
    #     t.setDaemon(True)
    #     t.start()
    # t.join()