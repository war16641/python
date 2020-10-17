"""这个包是一些和文件操作相关的类"""
import os
import sys
import re
import shutil
from enum import Enum, unique
import numpy as np

def rename_file(fullname: str, newname: str) -> str:
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
        return newfullname
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


def del_file(fullname: str) -> bool:
    """
    删除文件
    :param fullname:
    :return:成功删除返回true
    """
    if not os.path.isfile(fullname):
        print("警告：文件不存在，取消删除文件操作。(" + __file__ + " " + sys._getframe().f_code.co_name + ")")
        return False
    try:
        os.remove(fullname)
        return True
    except Exception as e:
        print(e)
        return False


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
def get_elements_from_line(line, additional_separator='', number_only=True):
    """
    从字符串中得到所有的元素
    如果元素是数，会优先化为float，如果不能化为float就保留为str
    数之间以空白字符或指定的分隔符连接
    元素之间的空格会被抹除
    :param line:
    :arg additional_separator: 额外的分隔符
    :arg number_only: 如果分割的结果里面 有非数字，true：用none代替； false：保留字符串
    :return: 数组成的列表 没有时返回空列表
    """
    numbers=[]
    line=line.strip()
    for item in re.split('[\\s'+ additional_separator+']+', line):
        # print(item)
        flag,number=is_number(item)
        if not flag:
            if number_only:
                numbers.append(number)
            else:
                numbers.append(item)
        else:
            numbers.append(number)
        # if flag==True:
        #     numbers.append(number)
    return numbers

def read_file(pathname,omit_lines='auto',style='separator',column_expected=0,separator='',width=0)->np.ndarray:
    """
    从文件中读取数据
    :param style: 'separator' 'fixedwidth' 'matrix'
            'separator' 使用分隔符创建的文件
            'fixedwidth' 固定宽度
            'matrix' 矩阵格式 返回列矩阵
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
    def handle_line_on_separator(line,separator):
        """
        处理行
        :param line:
        :return: tpe,lst
                tpe 行的类型
                lst 提取到的数据列表 只有当tpe=valid时，才有用
        """
        lst=get_elements_from_line(line, separator)
        if len(lst)==0:#空行 或者 空白行
            tpe=TypeOfLine.Null
            return tpe,lst
        elif None in lst:#有非数值字符串存在
            tpe = TypeOfLine.Invalid
            return tpe, lst
        else:#有效行
            tpe = TypeOfLine.Valid
            return tpe, lst

    def handle_line_on_fixedwidth(line,width):
        #用固定宽度处理行
        if line[-1]=='\n':
            line=line[:-1]
        line_width=len(line)
        lst=[]
        if line_width%width!=0:
            tpe=TypeOfLine.Invalid
            return tpe,[]
        for i in range(0,line_width,width):
            flag,number=is_number(line[i:i+width])
            if flag==False:
                tpe = TypeOfLine.Invalid
                return tpe, []
            else:
                lst.append(number)
        return TypeOfLine.Valid,lst
    def read_file_on_matrix(f,data_list,width,column_expected,row):
        #处理data_list剥皮
        data_list=data_list[0]
        #已经读取了一行了
        row += 1
        line = f.readline()
        pardon_one_error=False#允许发生一次列数不符合期望的错误
        while line:
            tpe, lst=handle_line_on_fixedwidth(line,width)
            if tpe is TypeOfLine.Valid:  # 有效行
                if len(lst) != column_expected and pardon_one_error==True:
                    print_error_info(row, line)
                    raise Exception("和期望的列数个数不一致")
                elif len(lst) != column_expected and pardon_one_error==False:
                    pardon_one_error=True
            else:
                print_error_info(row, line)
                raise Exception("非有效数据行")
            # 保存数据
            data_list.extend(lst)
            # 下一行
            row += 1
            line = f.readline()
        f.close()
        return data_list

    data_list=[]
    row=0#指示当前行
    f=open(pathname,'r')
    #处理读取风格
    if style=='separator':
        handle_line_method=handle_line_on_separator
        handle_line_param=separator
    elif style=='fixedwidth':
        handle_line_method=handle_line_on_fixedwidth
        handle_line_param=width
    elif style=='matrix':
        handle_line_method = handle_line_on_fixedwidth
        handle_line_param = width
    else:
        raise Exception("参数错误")
    #先处理数据头
    flag,number=is_number(omit_lines)
    if flag:#指定跳过行
        for i in range(omit_lines):
            row+=1
            f.readline()
        #再读一行
        row += 1
        line=f.readline()
        tpe, lst = handle_line_method(line, handle_line_param)
        if tpe is not TypeOfLine.Valid:
            print_error_info(row,line)
            raise Exception("非有效行")
    elif omit_lines=='auto':
        while True:
            row += 1
            line=f.readline()
            tpe,lst=handle_line_method(line,handle_line_param)
            if tpe is not TypeOfLine.Valid:#有非数字文本 或者 空行
                continue
            else:
                break
    else:
        raise Exception("参数错误")
    #检查数据第一行是否和期望的列数一致
    if column_expected != 0 and column_expected!= len(lst):
        print_error_info(row,line)
        raise Exception("和期望的列数不一致")
    else:
        #设定期望列数
        column_expected=len(lst)
        #保存数据
        data_list.append(lst)
    #使用matrix风格时比较特殊 采用专写的函数
    if style=='matrix':
        data_list=read_file_on_matrix(f,data_list,width,column_expected,row)
        tmp= np.array(data_list)
        return tmp.reshape(len(tmp),1)
    #读取下一行
    row+=1
    line=f.readline()
    while line:
        tpe, lst = handle_line_method(line,handle_line_param)
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

def collect_all_filenames(directory,rex,lst,print_info=False):
    """
    将所有文件的路径名收集到lst中
    :param directory:
    :param rex:
    :param lst:
    :return:
    """
    assert os.path.exists(directory)
    for filename in os.listdir(directory):
        curent_full_name = os.path.join(directory, filename)
        if print_info is True:
            print(curent_full_name, end='')
        if os.path.isfile(curent_full_name):  # 文件
            flag = len(re.findall(rex, filename)) > 0
            if flag is True:
                if print_info is True:
                    print("->命中")
                lst.append(curent_full_name)
            else:
                if print_info is True:
                    print("->未命中")
        else:  # 文件夹
            if print_info is True:
                print("->文件夹")
            collect_all_filenames(directory=curent_full_name,
                             rex=rex,
                                  lst=lst)



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
    #         print(get_elements_from_line(line))
    #         row += 1
    #         line = f.readline()


def copy_file(fullname,to_path,new_name='',create_folder=False):
    """
    复制文件
    :param fullname: 源文件
    :param to_path: 目标文件夹
    :param new_name: 新文件名 可以空
    :param create_folder: 当目标文件夹不存在时 是否创建
    :return: 成功返回true
    """
    assert os.path.isfile(fullname),'文件%s不存在'%fullname
    if not os.path.isdir(to_path):
        if create_folder is True:
            os.makedirs(to_path) #创建文件夹
        else:
            print("目标文件夹不存在且不允许创建，文件复制操作取消。")
            return False
    #开始复制
    _, tmpfilename = os.path.split(fullname)
    if new_name == "":
        new_name=tmpfilename
    shutil.copyfile(fullname,os.path.join(to_path,new_name))
    return True #成功返回true

def append_file(file1:str,file2:str,transition_txt=""):
    """
    向file1中添加file2的内容 并且可以在中间插入文字
    @param file1:
    @param file2:
    @param transition_txt: 要插入的文字
    @return:
    """
    assert os.path.isfile(file1)
    assert os.path.isfile(file2)
    f1 = open(file1, 'a')
    f2 = open(file2, 'r')
    f1.write(transition_txt)
    conts = f2.readlines()
    for ln in conts:
        f1.write(ln)
    f1.close()
    f2.close()


if __name__ == '__main__':
    # mat=read_file("F:\\的t1.txt",column_expected=3,separator=',',omit_lines=1)
    # assert mat.shape==(3,3)
    # mat=read_file("F:\的t1 - 副本.txt",style='fixedwidth',width=5)
    # assert mat.shape==(2,3)
    # mat = read_file("F:\的t1 - 副本.txt", style='matrix', width=5)
    # assert mat.shape==(6,1)
    # mat = read_file("F:\编辑3.txt", style='matrix', width=5)
    # print(mat)
    # copy_file("D:\last.bmp","e:\\2",new_name='',create_folder=True)
    # st="SLIDINGBLOCK,0,22,250.000000,105.435608,0.000000,-9396.621094,-20758.029297"
    st = "  SLIDINGBLOCK  ,  0  ,  22,250.000000  ,105.435608,0.000000,-9396.621094,-20758.029297"
    ls=get_elements_from_line(st, additional_separator=',', number_only=False)
    print(ls)