"""这个包是一些和文件操作相关的类"""
import os
import sys
import re
from enum import Enum, unique
import numpy as np

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

def is_number(s):
    """
    判断字符串能否转化为数值
    s前后可以有空白字符 空格 \t \n等等
    :param s:
    :return: flag,number
            flag
            number 转换的数 不能转化时为None
    """
    number=None
    try:
        number=float(s)
        flag= True
    except ValueError:
        flag=False
    return flag,number
def get_numbers_from_line(line,additional_separator=''):
    """
    从字符串中得到所有的数
    数之间以空白字符连接
    :param line:
    :arg additional_separator: 额外的分隔符
    :return: 数组成的列表 没有时返回空列表
    """
    numbers=[]
    line=line.strip()
    for item in re.split('[\\s'+ additional_separator+']+', line):
        # print(item)
        flag,number=is_number(item)
        numbers.append(number)
        # if flag==True:
        #     numbers.append(number)
    return numbers

def read_file(pathname,omit_lines='auto',column_expected=0,separator=''):
    """
    从文件中读取数据
    :param separator: 额外的分隔符 默认以空白字符风格
    :param pathname:
    :param omit_lines: 'auto' 或者是大于0的整数
            'auto' 自动舍弃数据头的非数据行
            整数 跳过的行数 之后的每一行都认为是有效行
    :param column_expected: 数据的列数 0为取第一行的数据列数
    :return: ndarray
    """
    @unique
    class TypeOfLine(Enum):
        Valid=0
        Null=1
        Invalid=2

    def print_error_info(row,line):#打印出错时的信息
        print("行数:%d"%row)
        print("该行:%s"%line)
    def handle_line(line,separator):
        """
        处理行
        :param line:
        :return: tpe,lst
                tpe 行的类型
                lst 提取到的数据列表 只有当tpe=valid时，才有用
        """
        lst=get_numbers_from_line(line,separator)
        if len(lst)==0:#空行 或者 空白行
            tpe=TypeOfLine.Null
            return tpe,lst
        elif None in lst:#有非数值字符串存在
            tpe = TypeOfLine.Invalid
            return tpe, lst
        else:#有效行
            tpe = TypeOfLine.Valid
            return tpe, lst
    data_list=[]
    row=0#指示当前行
    f=open(pathname,'r')
    #先处理数据头
    flag,number=is_number(omit_lines)
    if flag:#指定跳过行
        for i in range(omit_lines):
            row+=1
            f.readline()
    elif omit_lines=='auto':
        while True:
            row += 1
            line=f.readline()
            tpe,lst=handle_line(line,separator)
            if tpe is not TypeOfLine.Valid:#有非数字文本 或者 空行
                continue
            else:
                break
    else:
        raise Exception("参数错误")
    #检查是否和期望的列数一致
    if column_expected != 0 and column_expected!= len(lst):
        print_error_info(row,line)
        raise Exception("和期望的列数不一致")
    else:
        #设定期望列数
        column_expected=len(lst)
        #保存数据
        data_list.append(lst)
    #读取下一行
    row+=1
    line=f.readline()
    while line:
        tpe, lst = handle_line(line,separator)
        if tpe is TypeOfLine.Valid:#有效行
            if len(lst)!=column_expected:
                print_error_info(row,line)
                raise Exception("和期望的列数个数不一致")
        else:
            print_error_info(row, line)
            raise Exception("非有效数据行")
        #保存数据
        data_list.append(lst)
        #下一行
        row += 1
        line = f.readline()
    f.close()
    mat=np.array(data_list)
    return mat





    #检查
    # if column_expected>0:
    #     if column_expected!=len(tmp):
    #         print_error_info(row,line)
    #         raise Exception("该行读到的个数与期望不一致")
    #
    #
    #
    #
    # with open(pathname,'r') as f:
    #     row+=1
    #     line=f.readline()
    #
    #     while line:
    #         if row<omit_lines:
    #             row += 1
    #             line = f.readline()
    #             continue
    #         print(get_numbers_from_line(line))
    #         row += 1
    #         line = f.readline()



if __name__ == '__main__':
    # print(is_number(' -.123E-12 '))
    # print(is_number('-.1'))
    # print(is_number('   -.1e2'))
    # print(is_number('   -1.1e 2  '))
    print(get_numbers_from_line(',  1.1e-1   ,    .2e+2    3e1 \t \n',additional_separator=','))
    mat=read_file("F:\\的t1.txt",column_expected=3,separator=',')
    print(mat)

