import re
import unittest
from typing import List
from unittest import TestCase

from excel.excel import FlatDataModel, DataUnit
from myfile import collect_all_filenames


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
        self.casename=""#荷载组合名
        self.branch=""#最大 最小轴力组合
        self.sigma_conc=0.0
        self.sigma_steel1=0.0#钢筋有两个应力
        self.sigma_steel2=0.0


class SoilStress:#桩侧土压力
    def __init__(self,casename="",soil_stress=0.0,allowable_stress=0.0):
        self.casename=casename
        self.soil_stress=soil_stress
        self.allowable_stress=allowable_stress


class ExceptionTZ(Exception):#tz中产生的错误
    pass

class TZ_result:
    def __init__(self):
        self.No=-1#墩台号
        self.K=0.0#线刚度
        self.H=0.0#桩长
        self.D=0.0#桩径
        self.caps=[]#type:list[Capacity]
        self.strs=[]#type:list[Stress]
        self.soils=[]#type:list[SoilStress]
        self.type=""

    def __str__(self):
        return "墩台号：%s,桩长：%.2f"%(self.No,self.H)


    @staticmethod
    def load_from_string(tztxt)->'TZ_result':
        """
        从文本中载入
        @param tztxt:
        @return:
        """
        tz = TZ_result()
        # 是否是摩擦桩
        #pt = "桩            型: 钻（挖）孔摩擦桩"
        pt = "桩            型: .+摩擦桩"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            l1 = re.findall("桩            型: .+柱桩", tztxt)
            if len(l1)==0:
                raise ExceptionTZ("不是摩擦桩")
            else:
                tz.type="柱桩"
        else:
            tz.type = "摩擦桩"

        # 读取墩台号
        pt = "(\d+) 墩  \(台\)  桩  基  设  计  计  算  书"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("没找到墩台号")
        tz.No = int(l[0])

        #读取桩径
        pt = "设计桩身直径\s+Dz=\s*(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("没找到桩径")
        tz.D = int(l[0])


        # 读取纵向刚度
        pt = "纵向水平线刚度 K=\s*(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("没找到线刚度")
        tz.K = float(l[0])

        # 读取桩长
        pt = "冲刷线以下桩身长度\s+Hz=\s+(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("没找到桩长度")
        tz.H = float(l[0])

        # 读取承载力
        pt = "荷载组合:\s+([\u4e00-\u9fa5\+\(\)]+)\n\s+P\s*=\s*(\d+\.?\d*)\(kN\)\s*\[P\]\s*=\s*(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("读取承载力失败")
        for ln in l:
            c = Capacity(ln[0], float(ln[1]), float(ln[2]), "承载力")
            tz.caps.append(c)

        # 读取应力
        pt = "荷载组合\s+:\s*([\u4e00-\u9fa5\+\(\)]+)\s*\n\s+控制截面.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*).*\n.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("读取应力失败")
        for ln in l:
            s = Stress()
            s.casename = ln[0]
            s.branch = ln[1]
            s.sigma_conc = float(ln[2])
            s.sigma_steel1 = float(ln[3])
            s.sigma_steel2 = float(ln[4])
            tz.strs.append(s)
            s = Stress()
            s.casename = ln[0]
            s.branch = ln[5]
            s.sigma_conc = float(ln[6])
            s.sigma_steel1 = float(ln[7])
            s.sigma_steel2 = float(ln[8])
            tz.strs.append(s)

        #读取桩侧土压力
        pt = "荷载组合\s*:\s*([\u4e00-\u9fa5\+\(\)]+)\s*\n\s+σmax=\s*(\d+\.?\d*).+\[σ\]=\s*(\d+\.?\d*)"
        l = re.findall(pt, tztxt)
        if len(l) == 0:
            raise ExceptionTZ("读取桩侧土压力失败")
        for ln in l:
            ss=SoilStress(ln[0],float(ln[1]),float(ln[2]))
            tz.soils.append(ss)
        return tz

    @staticmethod
    def load_from_file(fullname)->'TZ_result':
        """
        从文件中读取 并生成tz result
        @param fullname:
        @return:
        """
        #pathname = r"E:\我的文档\Tencent Files\973916531\FileRecv\38ZJ.RST"
        with open(fullname) as f:
            content = f.read()
        return TZ_result.load_from_string(content)

    def run_diagnosis(self,funcs:List[callable]):
        """
        运行测试
        @param funcs: 测试函数列表 要求每个函数 只接受一个tz参数
        @return:
        """
        if not isinstance(funcs,list):
            funcs=[funcs]
        for i in funcs:
            i(self)



class TZDiagnosis(Exception):#如果诊断有问题，就抛出这个异常
    def __init__(self,brief="",tz=None,msg=""):
        """

        @param brief:
        @param tz:
        @param msg:
        """
        self.brief=brief
        self.tz=tz#type:TZ_result
        self.msg=msg
    pass

class Diagnosis:
    @staticmethod
    def check_K(tz:TZ_result):
        """
        检查刚度
        @param tz:
        @return:
        """
        if tz.K<350.:
            raise TZDiagnosis(brief="刚度不足",
                              tz=tz,
                              )

    @staticmethod
    def check_capacity(tz:TZ_result):
        """
        检查承载力
        @param tz:
        @return:
        """
        for i in tz.caps:
            if i.design > i.allowable:
                raise TZDiagnosis(brief="承载力不足", tz=tz)
            if "主力" in i.casename and "附" not in i.casename and "地震" not in i.casename and\
                    "特殊" not in i.casename :#主力
                if i.safety_factor<1.05:
                    raise TZDiagnosis(brief="承载力过小", tz=tz)
                elif i.safety_factor > 1.2 and "摩擦桩"==tz.type:
                    raise TZDiagnosis(brief="承载力过大", tz=tz)





    @staticmethod
    def check_stress(tz:TZ_result):
        """
        检查砼和钢筋应力
        @param tz:
        @return:
        """
        for i in tz.strs:
            if "主力" in i.casename and "附" not in i.casename and "地震" not in i.casename and\
                    "特殊" not in i.casename :#主力
                if i.sigma_conc>=7.0:
                    raise TZDiagnosis(brief="砼应力超限", tz=tz)
                if i.sigma_steel1>=160 or i.sigma_steel2>=160:
                    raise TZDiagnosis(brief="钢筋应力超限", tz=tz)
            elif "主力" in i.casename and "附"  in i.casename:#主力+附
                if i.sigma_conc>=7.0*1.2:
                    raise TZDiagnosis(brief="砼应力超限", tz=tz)
                if i.sigma_steel1>=160 or i.sigma_steel2>=160:
                    raise TZDiagnosis(brief="钢筋应力超限", tz=tz)
            elif "地震" in i.casename or "特殊" in i.casename:
                if i.sigma_conc>=7.0*1.5:
                    raise TZDiagnosis(brief="砼应力超限", tz=tz)
                if i.sigma_steel1>=160 or i.sigma_steel2>=160:
                    raise TZDiagnosis(brief="钢筋应力超限", tz=tz)
            else:
                raise Exception("其他未知工况")

    @staticmethod
    def check_soil(tz:TZ_result):
        """
        检查土压力
        @param tz:
        @return:
        """
        for i in tz.soils:
            if i.soil_stress>=i.allowable_stress:
                raise TZDiagnosis(brief="桩侧土压力超限",tz=tz)



#这个函数可以删除
#遍历一个文件夹里的所有rst文件生成tz
#并进行诊断，通过fdm输出诊断结果
def test1():
    lst=[]
    collect_all_filenames(directory=r"E:\铁二院\济枣线北段\初步设计\DK9+309.4坞西村特大桥\基础检算",
                          rex=".+.RST",
                          lst=lst)
    check_results=FlatDataModel()
    check_results.vn=['墩号','结果','简报']
    for i,path in enumerate(lst):
        u=DataUnit(check_results)
        tz=TZ_result.load_from_file(path)
        u.data['墩号']=tz.No
        u.data['结果'] = ""
        u.data['简报'] = ""
        try:
            tz.run_diagnosis([Diagnosis.check_capacity,
                              Diagnosis.check_K,
                              Diagnosis.check_soil,
                              Diagnosis.check_stress])
            u.data['结果'] = "通过"
        except TZDiagnosis as e:
            u.data['结果'] = "不通过"
            u.data['简报'] = e.brief
        except Exception:
            u.data['结果'] = "未知错误"
        check_results.append_unit(u)
        print("已读取%d/%d"%(i+1,len(lst)))
    check_results.sort(key='墩号')
    check_results.show_in_excel()
if __name__ == '__main__':
    tz=TZ_result.load_from_file(r"E:\我的文档\Tencent Files\973916531\FileRecv\38ZJ.RST")
    tz.run_diagnosis([Diagnosis.check_capacity,Diagnosis.check_K,Diagnosis.check_soil,Diagnosis.check_stress])
    # pathname=r"E:\我的文档\Tencent Files\973916531\FileRecv\38ZJ.RST"
    # with open(pathname) as f:
    #     content=f.read()
    #
    # tz=read_tz(content)
    #
    # print(tz)

    # pt="荷载组合\s+:\s*([\u4e00-\u9fa5\+\(\)]+)\s*\n\s+控制截面.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*).*\n.*\n.*\n.*\n.*(最.*):\n.*\n.*\n.*\n.*\n.*\n.*σh=\s*(\d+\.?\d*).*\n.*\n.*σgi=\s*(\d+\.?\d*).*\n.*σgl=\s*(\d+\.?\d*)"
    # l=re.findall(pt,content)
    # print(len(l))
    # for i in l:
    #     print(i)



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

