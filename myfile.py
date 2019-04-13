"""这个包是一些和文件操作相关的类"""
import os
import sys
import re


def rename_file(fullname: str, newname: str) -> None:
    """
    重命名文件
    :param fullname:文件全路径名 如"D:\测试文件\mydata.txt"
    :param newname: 新文件名newdata.txt
    :return:
    """
    assert os.path.isfile(fullname)
    assert isinstance(newname, str)
    (pathname, tmpfilename) = os.path.split(fullname)
    newfullname = os.path.join(pathname, newname)
    try:
        os.rename(fullname, newfullname)
    except FileExistsError:
        print("警告：新文件名已存在，重命名失败。(" + __file__ + " " + sys._getframe().f_code.co_name + ")")


def retype_file(fullname: str, newtype: str) -> None:
    """
    重新制定文件的后缀名
    :param fullname:
    :param newtype: 后缀名 如  .txt 如果没有点 会自动加点
    :return:
    """
    assert isinstance(newtype, str)
    # 分解全路径文件名
    (pathname, tmpfilename) = os.path.split(fullname)
    (filename, extension) = os.path.splitext(tmpfilename)
    if newtype[0] != '.':
        newtype = '.' + newtype
    try:
        rename_file(fullname, filename + newtype)
    except FileExistsError:
        print("警告：新文件名已存在，更改文件类型失败。(" + __file__ + " " + sys._getframe().f_code.co_name + ")")


def del_file(fullname: str) -> None:
    """
    删除文件
    :param fullname:
    :return:
    """
    if not os.path.isfile(fullname):
        print("警告：文件不存在，取消删除文件操作。(" + __file__ + " " + sys._getframe().f_code.co_name + ")")
        return
    os.remove(fullname)


def search_directory(directory: str, rex: str, func: callable, *args, **kwargs) -> None:
    """
    对文件夹下所有文件 含子文件夹 进行筛选 
    筛选规则 使用正则表达式rex进行匹配
    :param directory: 
    :param rex: 正则表达式
    :param func: 筛选成功后 进行的操作
    :param args: 
    :param kwargs: 
    :return: 
    """
    assert os.path.exists(directory)
    assert callable(func)
    for filename in os.listdir(directory):
        curent_full_name = os.path.join(directory, filename)
        print(curent_full_name, end='')
        if os.path.isfile(curent_full_name):  # 文件
            flag = len(re.findall(rex, filename)) > 0
            if flag is True:
                print("->命中")
                func(fullname=curent_full_name,
                     *args, **kwargs)
            else:
                print("->未命中")
        else:  # 文件夹
            print("->文件夹")
            search_directory(directory=curent_full_name,
                             rex=rex,
                             func=func,
                             *args, **kwargs)


if __name__ == '__main__':
    line = 'test.txt'
    m = 'txdt'
    print(re.findall(m, line))
    # print(re.match(m,line).group(0))
    search_directory(directory="D:\测试文件",
                     func=retype_file,
                     rex='.txt$',
                     newtype='txt1')
