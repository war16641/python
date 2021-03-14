from excel.excel import bisection_method


def select_kps(mapdl,*args):
    """
    在mapdl中选择kp
    @param mapdl:
    @param args: 可以是单个kp 可以是kp组成的列表 也可以是kp1,kp2,kp3.。.的多参数输入
    @return:
    """
    if len(args)==1:
        arg=args[0]
        if isinstance(arg,int):
            mapdl.ksel('none')
            mapdl.ksel('a','','',arg)
        elif isinstance(arg,list):
            mapdl.ksel('none')
            for i in arg:
                mapdl.ksel('a', '', '', i)
    else:#多个
        mapdl.ksel('none')
        for i in args:
            assert isinstance(i,int),"只能是kp编号"
            mapdl.ksel('a', '', '', i)


def locate(nds,nd):
    """在节点坐标列表中找到为nd的索引"""
    i,_,_=bisection_method(nds,nd,lambda x:x)#二分法快速锁定
    if i is None:
        raise Exception("未在节点列表中发现节点%d"%i)
    return i