from copy import deepcopy
class SmallDimension:
    """描述某一类量纲的单位和阶数"""
    def __init__(self,dim,unit):
        self.dim=dim
        self.order=unit
    def __eq__(self, other):
        """判断阶数是否相同"""
        if self.order==other.order:
            return True
        return False
        # if self.order==0 and other.order==0:
        #     return True
        # if self.dim==other.dim and self.order == other.order:
        #     return True
        # return False

    def __ne__(self, other):
        return not self.__eq__(other)

class ValueWithDimension:
    length_dimension={'mm':1,
                      'cm':10,
                      'm':1000}
    mass_dimension={'kg':1,
                    't':1000}
    valid_dimension={'length':length_dimension,
                     'mass':mass_dimension}

    def __init__(self,value=0,*args):
        """args是两个一组的，第一个指定单位类型可以是length mass 第二个指定阶数"""
        self.value=value
        self.dimension={'length':SmallDimension('m',0),
                        'mass':SmallDimension('kg',0)}
        if 0!=len(args) % 2:
            if 1==len(args) and isinstance(args[0],str):
                dtext=args[0]
                dimension_setup=self.dimension_text_interpreter(dtext)
            elif 1==len(args) and isinstance(args[0],ValueWithDimension):
                self.value=args[0].value
                self.dimension=deepcopy(args[0].dimension)
                return
            else:
                raise Exception("必须两个一组")
        else:
            dimension_setup=list(args)

        for i in range(0,len(dimension_setup)-1,2):
            dim=dimension_setup[i]
            od=dimension_setup[i+1]
            self.dimension[self.dimension_interpreter(dim)].dim=dim
            if self.dimension[self.dimension_interpreter(dim)].order != 0:
                raise Exception("重复指定同一个量纲")
            self.dimension[self.dimension_interpreter(dim)].order = od


    def switch_dimension(self,*args):
        """args为多个单位 也可以是字符串"""
        if len(args)==1 and isinstance(args[0],str):
            args=args[0].split(",")
        else:
            args=list(args)

        for ut in args:
            tp=self.dimension_interpreter(ut)
            old_un=self.dimension[tp].dim
            if old_un != ut:
                self.value=self.value*(self.valid_dimension[tp][old_un]/self.valid_dimension[tp][ut])**self.dimension[tp].order
                self.dimension[tp].dim=ut

    def is_same_dimension(self,x):
        """判断两个数是否有相同的量纲"""
        for k in self.dimension.keys():
            if self.dimension[k]!=x.dimension[k]:
                return False
        return True

    def __add__(self, other):
        assert self.is_same_dimension(other)
        # 单位会向第一个看齐
        other.switch_dimension(self.dimension_text_exclude_order)
        c=deepcopy(self)
        c.value+=other.value
        return c

    def __sub__(self, other):
        assert self.is_same_dimension(other)
        # 单位会向第一个看齐
        other.switch_dimension(self.dimension_text_exclude_order)
        c = deepcopy(self)
        c.value -= other.value
        return c

    def __truediv__(self, other):
        c = deepcopy(self)
        if isinstance(other, (float, int)):
            c.value = c.value / other
            return
        if isinstance(other, ValueWithDimension):
            other.switch_dimension(self.dimension_text_exclude_order)  # 统一单位
            c.value = self.value / other.value
            for k in c.dimension.keys():
                c.dimension[k].order -= other.dimension[k].order
            return c
        raise Exception("类型错误")

    def __mul__(self, other):
        c=deepcopy(self)
        if isinstance(other,(float,int)):
            c.value=c.value*other
            return
        if isinstance(other,ValueWithDimension):
            other.switch_dimension(self.dimension_text_exclude_order) # 统一单位
            c.value=self.value*other.value
            for k in c.dimension.keys():
                c.dimension[k].order+=other.dimension[k].order
            return c
        raise Exception("类型错误")

    def __eq__(self, other):
        if isinstance(other,(float,int)):# 与数比较
            tmp=[x.order for x in self.dimension.values()]
            print(tmp)


        other.switch_dimension(self.dimension_text_exclude_order)  # 统一单位
        if self.value!=other.value:
            return False
        for k in self.dimension.keys():
            if self.dimension[k].order != other.dimension[k].order:
                return False
        return True





    @property
    def dimension_text(self):
        """返回单位字符串"""
        line = [v.dim + "^%d" % v.order for v in self.dimension.values()]
        line = "*".join(line)
        return line

    @property
    def dimension_text_exclude_order(self):
        """返回字符串 不含阶数 用，连接"""
        line=[v.dim for v in self.dimension.values()]
        return ",".join(line)


    def __str__(self):
        return "%f %s"%(self.value,self.dimension_text)

    @staticmethod
    def dimension_interpreter(dim):
        """根据具体的单位返回单位的类别"""
        if dim in ValueWithDimension.length_dimension.keys():
            return "length"
        if dim in ValueWithDimension.mass_dimension.keys():
            return "mass"
        raise Exception("无效单位")

    @staticmethod
    def dimension_text_interpreter(text):
        """将单位字符串转化为可以识别的列表
        a="mm*t^2"
        b="m^3*kg^1"
        print(ValueWithDimension.dimension_text_interpreter(a))
        print(ValueWithDimension.dimension_text_interpreter(b))"""
        id1=text.split("*")
        lst=[]
        for v in id1:
            if '^' in v:
                idline = v.split('^')
                assert len(idline) == 2
                idline[1] = float(idline[1])
                lst = lst + idline
            else:
                idline = [v]
                idline.append(1.0)
                lst = lst + idline
        return lst



if __name__=="__main__":
    # a=ValueWithDimension(10,'mm',1,'t',2)
    # print(a)
    # a.switch_dimension('kg')
    # print(a)
    # a.switch_dimension('kg','m')
    # print(a)
    # print(a.dimension_text)
    # b=ValueWithDimension(1.1,"mm*t^2")
    # print(b)
    # b = ValueWithDimension(1.1, "mm^4*t^2")
    # print(b)
    # print(b.dimension_text_exclude_order)
    # b.switch_dimension("mm,kg")
    # print(b)

    # a=ValueWithDimension(1.1,"mm*t")
    # b = ValueWithDimension(2, "m*t")
    # print(a)
    # print(b)
    # print(a.is_same_dimension(b))
    # c=a+b
    # print(c)
    # print(a)
    # print(b)
    # a.value=6
    # print(a)
    # print(b)
    # print(c)
    #
    # a=ValueWithDimension(1.1,"kg")
    # b = ValueWithDimension(2, "mm*t")
    # c=a/b
    # print(c)

    a=ValueWithDimension(1.1)
    print(a==1.1)








    pass
