def excel地址格式转换(x):
    if isinstance(x,tuple):
        x=list(x)
    if isinstance(x,str):#字符串模式
        x=x.upper()#大写
        #分离字母与数字
        pre=''#代表excel列标识 字母
        post=''#代表excel行标识 数字
        for c in x:#遍历字符
            if 65<=ord(c)<=90:#大写字母
                pre+=c
            elif 48<=ord(c)<=57:#数字
                post+=c
            else:
                raise Exception("无效字符%s"%c)
        #将pre转换为数字
        index1=0
        for i in range(len(pre)):
            c=pre[-1-i]#倒取
            num=ord(c)-64
            index1+=26**i*num
        index2=int(post)#行标识直接转换
        return (index2,index1)
    elif isinstance(x,list):
        assert len(x)==2,'长度必须为2'
        #处理列标识
        pre=x[1]
        index2=进制转换(pre,26)
        s2=''
        for i in index2:
            s2+=chr(i+64)
        return s2+str(x[0])
    else:
        raise Exception("参数错误")




def 进制转换(n,x):

    #n为待转换的十进制数，x为机制，取值为2-16
    a=[0,1,2,3,4,5,6,7,8,9,'A','b','C','D','E','F']
    b=[]
    while True:
        s=n//x  # 商
        y=n%x  # 余数
        b=b+[y]
        if s==0:
            break
        n=s
    b.reverse()
    return b
def test_进制转换():
    assert 进制转换(10,26)==[10]
    assert 进制转换(28, 26)==[1, 2]
    print(进制转换(10,26))
    print(进制转换(28, 26))
def test_excel地址格式转换():
    print(excel地址格式转换((3,2)))
    print(excel地址格式转换((5, 27)))
    print(excel地址格式转换('AB5'))
if __name__ == '__main__':
    test_excel地址格式转换()


