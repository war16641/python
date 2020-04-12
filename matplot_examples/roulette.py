class  Roulette:
    """
    轮盘机
    给定数据序列，每到要求下一个数据时，数据序列给出从第一个开始逐个给出，如果给到最后一个，从头开始
    最初写这个类是为了：matplotlib的颜色 自定义轮转颜色
    """
    def __init__(self,datalist):
        self.datalist=datalist
        self.nextid=0#下一个将使用的数据索引

    @property
    def next_data(self):
        #返回下一个数据
        tid=self.nextid
        #修改nextid
        if tid==len(self.datalist)-1:
            self.nextid=0
        else:
            self.nextid+=1
        return self.datalist[tid]

class ColorRoulette(Roulette):#为matplotlib准备的颜色
    def __init__(self):
        dl=['k','b','r','g','cyan','yellow','m','orange','maroon','greenyellow','navy','lime']
        super(ColorRoulette,self).__init__(dl)

if __name__ == '__main__':
    rl=Roulette([0,1,2,3,4])
    for i in range(7):
        assert i %5 ==rl.next_data,'发生错误'
