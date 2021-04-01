from collections.abc import Iterable
from math import pi
from typing import List
from GoodToolPython.code2021.pyansysexs.myansystool import select_kps, locate, node_coords
#import pyansys
from code2021.finiterangefunction import FiniteRangeFunction
from unittest import TestCase,main
#from feon.sa import *
import numpy as np
from mybaseclasses.emptyclass import EmptyClass
import unittest

from mybaseclasses.mylogger import MyLogger
from xydata import XYData

logger=MyLogger(name="pilefoundationasd234")
logger.setLevel('debug')





class Soil:
    """
    描述土体信息的
    """

    m0=XYData(name='桩底支撑力折减系数',
              x=[5,10,25,50],
              y=[0.7,0.5,0.4,0.3])
    def __init__(self,gamma=0,sigma0=0,fi=0,m=0):
        self.gamma=gamma
        self.sigma0=sigma0
        self.fi=fi
        self.m=m

        self.k2=5

    def __eq__(self, other):
        assert isinstance(other,Soil),"类型错误"
        if id(self)==id(other):
            return True
        return False


class SoilLayers:
    """
    土层信息：
    FiniteRangeFunction 描述土层厚度和土层信息 它的结构是[[高度，soil]，...] 从高程低的向高程高的排列
    dm_height 地面高度 也就是地面高程
    土层最上层到最下层高度是下降的 默认地面高度为0
    """
    def __init__(self,soillayers,dm_height=0):
        """

        @param soillayers: [[土层厚，soil]，...]  注意：这里是从上往下排列的
        @param dm_height: 地面高程
        """
        assert isinstance(soillayers,Iterable)
        pts=[]
        sumh=0#累计厚度
        totalh=0#总厚度
        for i,v in enumerate(soillayers):
            h=v[0]
            soil=v[1]
            assert isinstance(h,(int,float)) and isinstance(soil,Soil)\
            ,"类型错误"
            totalh+=h
        self.layers=soillayers
        for i in range(len(soillayers)-1,-1,-1):
            h=soillayers[i][0]
            soil = soillayers[i][1]
            if i==len(soillayers)-1:#最低层
                pts.append([-totalh, soil])
                pts.append([-totalh+h, soil])
                sumh+=h
            else:
                sumh+=h
                pts.append([-totalh+sumh,soil])
        #生成
        self.ff=FiniteRangeFunction(pts)
        assert isinstance(dm_height,(int,float))
        self.dm_height=dm_height

        pass

    def soil_at_height(self, height:float)->Soil:
        """获取高程处的土体信息"""
        assert isinstance(height,(int,float))
        height1=height-self.dm_height#折算为dm=0时的相等高度
        try:
            return self.ff.get_value(height1)
        except Exception as e:
            print(e.__str__())
            raise Exception("高度%f=相对高度%f，超出界限"%(height,height1))

    def stiff_of_soil(self,ht:float)->float:
        if ht>=self.dm_height:
            return 0
        ht1=ht-self.dm_height
        stiff=0.0
        last_ht=0.0
        for i in range(len(self.layers)):
            cur_ht=last_ht-self.layers[i][0]
            if ht1>=cur_ht:#ht的高度就在这一层
                stiff+=self.layers[i][1].m*(last_ht-ht1)
                # return stiff*1e3 #基本上输入的m单位时 kpa
                return stiff * 1  # 基本上输入的m单位时 kpa
            else:
                stiff += self.layers[i][1].m * self.layers[i][0]
                last_ht=cur_ht
        raise Exception("高度%f=相对高度%f，超出最低层土"%(ht,ht1))
class Pile:
    def __init__(self, d=0, H=0, x=0, y=0, sl:SoilLayers=None, pf: 'Platform'=None):
        self.d=d#直径 m
        self.H=H #桩长
        self.x,self.y=x,y#桩在承台平面的坐标
        self.sl=sl#土层信息
        self.pf=pf

        self.rsts=[]#type:List[PileRst]

    def print_rst(self):
        print("桩位%f,%f:"%(self.x,self.y))
        for lc in self.rsts:
            for i in lc.data:
                print("lc=%s,tab=%s,相对高度=%f,值=%f"%(lc.lc.name,i[0],i[3],i[1]))

    def calc_capacity(self):

        #求桩侧阻力side这一项
        #使用有限值域函数的积分方法求 fi*li
        #判断自由桩长
        ht_csx=self.pf.ctd_height-self.sl.dm_height
        if ht_csx>1e-6:
            logger.debug('存在%fm的自由桩长'%ht_csx)
            ht_csx=0

        side=self.sl.ff.integrate(self.pf.ctd_height-self.H-self.sl.dm_height,ht_csx,func=lambda x:x.fi)
        side=0.5*pi*self.d*side

        #桩端项end
        #识别桩端土层
        soil=self.sl.soil_at_height(self.pf.ctd_height-self.H)
        sigma0=soil.sigma0
        k2=soil.k2
        #桩侧土平均重度
        gama2=self.sl.ff.integrate(self.pf.ctd_height-self.H-self.sl.dm_height,ht_csx,
                                   func=lambda x:x.gamma)
        gama2=gama2/self.H#计算平均重度时未考虑自由桩长的情况
        if self.H<4*self.d:
            sigma=sigma0+k2*gama2*(self.H-3)
        elif self.H<10*self.d:
            sigma=sigma0+k2*gama2*(4*self.d-3)
        else:
            sigma=sigma0+k2*gama2*(4*self.d-3)+k2/2*gama2*6*self.d
        m0=Soil.m0.get_similar_value(self.H/self.d)
        end=m0*pi/4*self.d**2*sigma

        return side+end,side,end
        pass


class LoadCase:
    def __init__(self,xuhao=0,name="",fx=0,fy=0,fz=0,mx=0,my=0,mz=0):
        self.xuhao,self.name=xuhao,name
        # self.fx,self.fy,self.fz=fx,fy,fz
        # self.mx,self.my,self.mz=mx,my,mz
        self.force={'fx':fx,'fy':fy,'fz':fz,
                    'mx':mx,'my':my,'mz':mz}
        self.time_InA=0#在ansys中的time

class PileRst:
    def __init__(self):
        self.pile=None
        self.pf=None
        self.lc=None
        self.data=None#[[table名，值，高程，相对高程],...]

class Platform:
    def __init__(self,x=0,y=0,z=0,ctd_height=0):
        self.x,self.y,self.z=x,y,z#zqx hqx 厚度
        self.ctd_height=ctd_height#承台低高程
        self.piles=[] #type:List[Pile]

        self.mapdl=None
        self.stiff_x=0
        self.stiff_y=0#刚度

    def add_pile(self, d=0, H=0, x=0, y=0, sl:SoilLayers=None):
        """添加桩"""
        self.piles.append(Pile(d,H,x,y,sl,self))

    def fem(self,lcs:List[LoadCase]=None):
        dl=0.1
        E=3.3e10
        G=1e10
        path = "e:\\ansysfile"
        mapdl = pyansys.launch_mapdl(run_location=path, interactive_plotting=False,
                                     override=True,
                                     loglevel="warning")
        mapdl.prep7()
        mapdl.n(1,0,0,self.ctd_height) #1号节点是承台中心 地面
        mapdl.et(1, 188)
        mapdl.mp('ex', 1, E)
        mapdl.mp('nuxy', 1, 0.2)
        mapdl.mp('dens', 1, 2700)
        mapdl.sectype(1, 'beam', 'csolid')
        mapdl.secoffset('cent')
        mapdl.secdata(self.piles[0].d/2.0)#piles一般是同桩径的 使用第一个桩径
        #建立桩的线
        knum=0
        knum_down=[]#柱底kp
        knum_up = []  # 柱底kp
        for pile in self.piles:
            knum += 1
            mapdl.k(knum,pile.x,pile.y,self.ctd_height)
            knum_up.append(knum)
            knum+=1
            mapdl.k(knum, pile.x, pile.y, self.ctd_height - pile.H)
            knum_down.append(knum)
            mapdl.l(knum-1,knum)
        mapdl.latt(1, 0, 1, 0, 0, 1)
        mapdl.lesize('all', dl)#单元大小默认0.1
        mapdl.esel('none')
        mapdl.lmesh('all')
        mapdl.cm('el_piles','elem')

        #给每一根桩编组
        for i,pile in enumerate(self.piles):
            mapdl.lsel('s','','',i+1)
            mapdl.esll()
            pile.cm_name='el_auto_pile%d'%(i+1)#给pile添加一个字段用于存储cm name
            mapdl.cm(pile.cm_name,'elem')
        #选择桩底节点 并约束
        select_kps(mapdl,knum_down)
        mapdl.nslk()
        mapdl.d('all','ux')
        mapdl.d('all', 'uy')
        mapdl.d('all', 'uz')

        #处理承台中心与桩顶连接
        select_kps(mapdl, knum_up)
        mapdl.nslk()
        mapdl.nsel('a','','',1)
        mapdl.cerig(1,'all','all')

        #处理承台中心单元
        mapdl.et(2, 21)
        mass_ct=self.x*self.y*self.z*2700 #承台质量
        # mapdl.r(1, mass_ct,mass_ct,mass_ct,10,10,10)
        mapdl.r(1, 10, 10, 10, 10, 10, 10)
        mapdl.nsel('s', '', '', 1)
        mapdl.type(2)
        mapdl.real(1)
        mapdl.e(1)

        #处理土弹簧
        mapdl.et(3, 180) #link180
        mapdl.mp('ex', 3, 1e8)
        mapdl.mp('nuxy', 3, 0.3) #暂时不知道这个会不会影响土弹簧
        mapdl.cmsel('s','el_piles')
        mapdl.nsle()
        mapdl.cm('nd_piles','node')
        num_nds=mapdl.get_value(entity="node", entnum=0, item1="count")#获取选择节点个数
        num_nds=int(num_nds)
        cur_nd=0
        for i in range(num_nds):
            mapdl.cmsel('s', 'nd_piles')
            cur_nd=mapdl.get_value(entity="node", entnum=cur_nd, item1="nxth")
            x,y,gc=node_coords(mapdl,cur_nd)
            # 根据高程计算土弹簧刚度
            stiff=self.piles[0].sl.stiff_of_soil(gc)
            print("%d %f %f"%(cur_nd,gc,stiff))
            if stiff<1e-6:
                continue
            max_sec=mapdl.get_value(entity="secp", entnum=0, item1="num",it1num='max')
            mapdl.sectype(max_sec+1,'link')
            mapdl.secdata(stiff/1e8)
            mapdl.seccontrol(0,0)
            max_nd=mapdl.get_value(entity="node", entnum=0, item1="num",it1num='maxd')
            mapdl.n(max_nd+1,x+1,y,gc)
            mapdl.n(max_nd + 2, x , y+1, gc)
            mapdl.type(3)
            mapdl.mat(3)
            mapdl.secnum(max_sec+1)
            mapdl.e(cur_nd,max_nd+1)
            mapdl.e(cur_nd, max_nd + 2)
            mapdl.d(max_nd+1,'all')
            mapdl.d(max_nd + 2, 'all')
        #进入求解模块
        mapdl.slashsolu()  # 进入求解模块
        #计算纵横刚度 分别在time1和time2上
        mapdl.nsel('s', '', '', 1)
        test_force=1000
        mapdl.f(1,'fx',test_force)
        mapdl.allsel()
        mapdl.solve()
        mapdl.fdele(1,'all')
        mapdl.f(1, 'fy', test_force)
        mapdl.time(2)
        mapdl.solve()
        mapdl.fdele(1, 'all')
        #lcs中的力 从time11开始
        cur_time=10
        for i,lc in enumerate(lcs):
            cur_time+=1
            mapdl.time(cur_time)
            lc.time_InA=cur_time
            for cp,v in lc.force.items():
                print(cp,v)
                mapdl.f(1,cp,v)
            mapdl.solve()

        #后处理
        mapdl.post1()
        #纵横刚度
        mapdl.set('','','','',1)
        dx=mapdl.get_value(entity="node", entnum=1, item1="u",it1num='x')
        # result = mapdl.result
        # ndnum, ndisp = result.nodal_displacement(0)  # 0代表第一个dataframe
        # dx=ndisp[locate(ndnum,1)][0] #节点1的ux
        self.stiff_x=test_force/dx
        mapdl.set('', '', '', '', 2)
        dy = mapdl.get_value(entity="node", entnum=1, item1="u", it1num='y')
        # ndnum, ndisp = result.nodal_displacement(1)  # 0代表第一个dataframe
        # dy=ndisp[locate(ndnum,1)][1] #节点1的ux
        self.stiff_y = test_force / dy
        print('刚度%f'%self.stiff_x)
        print('刚度%f' % self.stiff_y)

        if lcs is not None:#处理lcs的力 桩基
            mapdl.etable('fx', 'smisc', 1)
            mapdl.etable('myi', 'smisc', 2)
            mapdl.etable('myj', 'smisc', 15)
            mapdl.etable('mzi', 'smisc', 3)
            mapdl.etable('mzj', 'smisc', 16)
            ks = ['fx', 'myi', 'myj', 'mzi', 'mzj']
            for lc in lcs:
                mapdl.set('', '', '', '', lc.time_InA)
                eds=[]
                for pile in self.piles:
                    mapdl.cmsel('s',pile.cm_name)
                    mapdl.nsle()
                    mapdl.etable('refl')
                    cur_el=0
                    num_el=mapdl.get_value(entity="elem", entnum=0, item1="count")#获取选择节点个数
                    #收集每一个单元的结果
                    for i in range(int(num_el)):
                        cur_el = mapdl.get_value(entity="elem", entnum=cur_el, item1="nxth")
                        ed={}
                        for k in ks:
                            ed[k]=mapdl.get_value(entity="elem", entnum=cur_el, item1="etab",it1num=k)
                            #添加坐标
                            ed['x']=mapdl.get_value(entity="elem", entnum=cur_el, item1="cent",it1num='x')
                            ed['y'] = mapdl.get_value(entity="elem", entnum=cur_el, item1="cent", it1num='y')
                            ed['z'] = mapdl.get_value(entity="elem", entnum=cur_el, item1="cent", it1num='z')
                        eds.append(ed)
                    #处理收集到的结果 主要是统计最大值
                    pr=PileRst()
                    pr.pile=pile
                    pr.pf=self
                    pr.lc=lc
                    pr.data=[]
                    for k in ks:
                        eds.sort(key=lambda x:abs(x[k]),reverse=True)
                        tab_name=k
                        peak_v=eds[0][k]
                        gc_of_peak=eds[0]['z']
                        # print("%s 值=%f 位置=%f"%(k,eds[0][k],eds[0]['z']))
                        pr.data.append([tab_name,peak_v,gc_of_peak,gc_of_peak-self.ctd_height])
                    pile.rsts.append(pr)

        mapdl.save()
        self.mapdl=mapdl

    def print_pile_rsts(self):
        for pile in self.piles:
            pile.print_rst()


class TestC(TestCase):
    def test1(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(-5.5))
        self.assertEqual(s0, sl.soil_at_height(-0.1))
    def test2(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=2500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers, dm_height=100)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(94.5))
        self.assertEqual(s0, sl.soil_at_height(100))
        self.assertRaises(Exception,sl.soil_at_height,100.1)
        self.assertRaises(Exception, sl.soil_at_height, 93.9)
        self.assertAlmostEqual(0,sl.stiff_of_soil(100),delta=0.1)
        self.assertAlmostEqual(150, sl.stiff_of_soil(99.9), delta=0.1)
        self.assertAlmostEqual(1500+250, sl.stiff_of_soil(100-1.1), delta=0.1)

    @unittest.skip('pyansys')
    def test_pf(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers, dm_height=100)
        pf=Platform(x=9,y=18,z=2,ctd_height=100)
        pf.add_pile(d=1,H=5,x=2,y=2,sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=-2, sl=sl)
        pf.add_pile(d=1, H=5, x=2, y=-2, sl=sl)
        pf.fem()
        self.assertAlmostEqual(582795486,pf.stiff_x,delta=1)
        self.assertAlmostEqual(582795486, pf.stiff_x, delta=1)

    def test_pile_cacapity(self):
        s0 = Soil(gamma=15, sigma0=4, fi=3, m=150000)
        s1 = Soil(gamma=25, sigma0=7, fi=1, m=250000)
        s2 = Soil(gamma=35, sigma0=1, fi=2, m=150000)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers, dm_height=100)
        pf = Platform(x=9, y=18, z=2, ctd_height=100)
        pf.add_pile(d=1, H=5, x=2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=-2, sl=sl)
        pf.add_pile(d=1, H=5, x=2, y=-2, sl=sl)
        pile = pf.piles[0]
        cap,side,end=pile.calc_capacity()
        self.assertAlmostEqual(14.13716,side,delta=0.01)

        s0 = Soil(gamma=15, sigma0=0, fi=3, m=150000)
        s1 = Soil(gamma=25, sigma0=0, fi=1, m=250000)
        s2 = Soil(gamma=35, sigma0=0, fi=2, m=150000)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers, dm_height=100)
        pf = Platform(x=9, y=18, z=2, ctd_height=99)
        pf.add_pile(d=1, H=5, x=2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=-2, sl=sl)
        pf.add_pile(d=1, H=5, x=2, y=-2, sl=sl)
        pile = pf.piles[0]
        cap,side,end=pile.calc_capacity()
        self.assertAlmostEqual(12.56637061,side,delta=0.01)

        s0 = Soil(gamma=15, sigma0=0, fi=3, m=150000)
        s1 = Soil(gamma=25, sigma0=0, fi=1, m=250000)
        s2 = Soil(gamma=35, sigma0=0, fi=2, m=150000)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayers(layers, dm_height=100)
        pf = Platform(x=9, y=18, z=2, ctd_height=101)
        pf.add_pile(d=1, H=5, x=2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=-2, sl=sl)
        pf.add_pile(d=1, H=5, x=2, y=-2, sl=sl)
        pile = pf.piles[0]
        cap, side, end = pile.calc_capacity()
        self.assertAlmostEqual(10.9955742, side, delta=0.01)


if __name__ == '__main__':
    main()
