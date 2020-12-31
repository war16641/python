import re


class Capacity:
    def __init__(self,casename="",design=0.0,allowable=0.0,desc=""):
        self.casename=casename
        self.design=design
        self.allowable=allowable
        self.desc=desc

    @property
    def safety_factor(self):
        if self.allowable==0.0:
            return 0.0
        else:
            return self.allowable/self.design

class Stress:
    def __init__(self):
        self.casename=""
        self.branch=""
        self.sigma_conc=0.0
        self.sigma_steel1=0.0
        self.sigma_steel2=0.0

class TZ_result:
    def __init__(self):
        self.No=-1#墩台号
        self.K=0.0#线刚度
        self.H=0.0#桩长
        self.caps=[]#type:list[Capacity]
        self.strs=[]#type:list[Stress]
        self.type=""

    def __str__(self):
        return "墩台号：%s,桩长：%f"%(self.No,self.H)

class ExceptionTZ(Exception):
    pass
def read_tz(tztxt:str)->TZ_result:

    tz=TZ_result()
    #是否是摩擦桩
    pt = "桩            型: 钻（挖）孔摩擦桩"
    l = re.findall(pt, tztxt)
    if len(l)==0:
        raise ExceptionTZ("不是摩擦桩")
    tz.type="摩擦桩"

    #读取墩台号
    pt = "(\d+) 墩  \(台\)  桩  基  设  计  计  算  书"
    l = re.findall(pt, tztxt)
    if len(l)==0:
        raise ExceptionTZ("没找到墩台号")
    tz.No=int(l[0])

    #读取纵向刚度
    pt = "纵向水平线刚度 K=\s*(\d+\.?\d*)"
    l = re.findall(pt, tztxt)  # 匹配桥名
    if len(l)==0:
        raise ExceptionTZ("没找到线刚度")
    tz.K=float(l[0])

    #读取桩长
    pt="冲刷线以下桩身长度\s+Hz=\s+(\d+\.?\d*)"
    l=re.findall(pt,tztxt) #匹配桥名
    if len(l) == 0:
        raise ExceptionTZ("没找到桩长度")
    tz.H=float(l[0])

    #读取承载力
    pt = "荷载组合:\s+([\u4e00-\u9fa5\+\(\)]+)\n\s+P\s*=\s*(\d+\.?\d*)\(kN\)\s*\[P\]\s*=\s*(\d+\.?\d*)"
    l = re.findall(pt, tztxt)  # 匹配桥名
    for ln in l:
        c=Capacity(ln[0],float(ln[1]),float(ln[2]),"承载力")
        tz.caps.append(c)


    #读取应力
    pt = "荷载组合\s+:\s*([\u4e00-\u9fa5\+\(\)]+)\s*\n\s+控制截面.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*).*\n.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*)"
    l = re.findall(pt, tztxt)  # 匹配桥名
    for ln in l:
        s=Stress()
        s.casename=ln[0]
        s.branch=ln[1]
        s.sigma_conc=float(ln[2])
        s.sigma_steel1 = float(ln[3])
        s.sigma_steel2 = float(ln[4])
        tz.strs.append(s)
        s=Stress()
        s.casename=ln[0]
        s.branch=ln[5]
        s.sigma_conc=float(ln[6])
        s.sigma_steel1 = float(ln[7])
        s.sigma_steel2 = float(ln[8])
        tz.strs.append(s)



    return tz

if __name__ == '__main__':

    pathname=r"E:\我的文档\Tencent Files\973916531\FileRecv\38ZJ.RST"
    with open(pathname) as f:
        content=f.read()

    # tz=read_tz(content)
    #
    # print(tz)
    #
    pt="荷载组合\s+:\s*([\u4e00-\u9fa5\+\(\)]+)\s*\n\s+控制截面.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*).*\n.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*)"
    l=re.findall(pt,content) #匹配桥名
    print(len(l))
    for i in l:
        print(i)
    #
#
#
# pt="纵向水平线刚度 K=\s*(\d+\.?\d*)"
# l=re.findall(pt,content) #匹配桥名
# print(l)
#
#
#
# pt="荷载组合:\s+([\u4e00-\u9fa5\+\(\)]+)\n\s+P\s*=\s*(\d+\.?\d*)\(kN\)\s*\[P\]\s*=\s*(\d+\.?\d*)"
# l=re.findall(pt,content) #匹配桥名
# print(l)
#
#
#
# pt="冲刷线以下桩身长度\s+Hz=\s+(\d+\.?\d*)"
# l=re.findall(pt,content) #匹配桥名
# print(l)
#
#
# pt="# (\d+) 墩  \(台\)  桩  基  设  计  计  算  书"
# l=re.findall(pt,content) #匹配桥名
# print(l)

