import os
"""这个包是一些和文件操作相关的类"""

def change_file_type(path,oldtype,newtype):
    """
    更改文件目录下所有指定类型的文件 包含子文件夹
    :param path: 路径
    :param oldtype: 原文件类型 带点
    :param newtype: 新文件类型 带点
    :return:
    """
    assert isinstance(oldtype,str)
    assert isinstance(newtype, str)
    print("搜索目录:"+path)
    for file in os.listdir(path):
        str1=file
        if os.path.isfile(os.path.join(path, file)):# 是文件
            nm=os.path.splitext(file)[0]# 获取前名
            tp=os.path.splitext(file)[1]# 获取扩展名
            if tp==oldtype:
                str1+=" 命中"
                # 修改文件扩展名
                try:
                    os.rename(os.path.join(path, file), os.path.join(path, nm + newtype))
                except FileExistsError:
                    pass


            else:
                pass

        else:
            str1+=" 目录:"+path+"\\"+file
            # print(path+"\\"+file,oldtype,newtype)
            change_file_type(os.path.join(path, file),oldtype,newtype)
        print(str1)

def remove_file_type(path,filetype):
    """
    删除文件夹下指定类型的文件 含子文件夹
    :param path:
    :param filetype: 文件类型 带点
    :return:
    """

    assert isinstance(filetype,str)
    print("搜索目录:"+path)
    for file in os.listdir(path):
        str1=file
        if os.path.isfile(os.path.join(path, file)):# 是文件
            nm=os.path.splitext(file)[0]# 获取前名
            tp=os.path.splitext(file)[1]# 获取扩展名
            if tp==filetype:
                str1+=" 命中"
                # 修改文件扩展名
                os.remove(os.path.join(path, file))
            else:
                pass

        else:
            str1+=" 目录:"+path+"\\"+file
            # print(path+"\\"+file,oldtype,newtype)
            remove_file_type(os.path.join(path, file),filetype)
        print(str1)

if __name__ == '__main__':
    path = "E:\我的文档\py\lib"
    # remove_file_type(path,'.pyc')
    # change_file_type(path,'.pyc_dis','.py')
    # count = 1

    # for file in os.listdir(path):
    #     print(file)
    #     if os.path.isfile(file):
    #         print('file')
    #         print(os.path.splitext(file)[1])
    #     else:
    #         print('dir')
    #     count += 1