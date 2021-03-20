from collections.abc import Iterable
from math import pi
from typing import List
from GoodToolPython.code2021.pyansysexs.myansystool import select_kps, locate, node_coords
import pyansys
from code2021.finiterangefunction import FiniteRangeFunction
from unittest import TestCase,main
from feon.sa import *
import numpy as np
from mybaseclasses.emptyclass import EmptyClass


class Soil:
    """
    描述土体信息的
    """
    def __init__(self,gamma=0,sigma0=0,fi=0,m=0):
        self.gamma=gamma
        self.sigma0=sigma0
        self.fi=fi
        self.m=m


    def __eq__(self, other):
        assert isinstance(other,Soil),"类型错误"
        if id(self)==id(other):
            return True
        return False

class SoilLayer:
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
                return stiff
            else:
                stiff += self.layers[i][1].m * self.layers[i][0]
                last_ht=cur_ht
        raise Exception("高度%f=相对高度%f，超出最低层土"%(ht,ht1))
class Pile:
    def __init__(self,d=0,H=0,x=0,y=0,sl:SoilLayer=None,pf:'Platform'=None):
        self.d=d#直径 m
        self.H=H #桩长
        self.x,self.y=x,y#桩在承台平面的坐标
        self.sl=sl#土层信息
        self.pf=pf


class Platform:
    def __init__(self,x=0,y=0,z=0,ctd_height=0):
        self.x,self.y,self.z=x,y,z#zqx hqx 厚度
        self.ctd_height=ctd_height#承台低高程
        self.piles=[] #type:List[Pile]

        self.mapdl=None
        self.stiff_x=0
        self.stiff_y=0#刚度

    def add_pile(self,d=0,H=0,x=0,y=0,sl:SoilLayer=None):
        """添加桩"""
        self.piles.append(Pile(d,H,x,y,sl,self))

    # def fem(self):
    #     dl=0.1
    #     E=3.3e10
    #     G=1e10
    #     s = System()
    #     for pile in self.piles:
    #         pile.nodes=[]
    #         I=pi/64*pile.d**4 #惯距
    #         for z in np.arange(self.ctd_height,self.ctd_height-pile.H-dl,-dl):
    #             pile.nodes.append(Node(pile.x,pile.y,z))
    #         s.add_nodes(pile.nodes)
    #         pile.eles=[]
    #         for i in range(len(pile.nodes)-1):
    #             pile.eles.append(Beam3D11((pile.nodes[i],pile.nodes[i+1]),
    #                                       E=E,
    #                                       G=G,
    #                                       A=pi/4*pile.d**2,
    #                                       I=(2*I,I,I)))
    #         s.add_elements(pile.eles)
    #
    #     #处理各个桩顶到承台底中心
    #     scale=1000#使用梁来代替钢杆 其EA EI*scale作为钢杆
    #     nd_zx=Node(0,0,self.ctd_height)
    #     s.add_node(nd_zx)
    #     for pile in self.piles:
    #         t=Beam3D11((nd_zx,pile.nodes[0]),
    #                                       E=E,
    #                                       G=G,
    #                                       A=pi/4*pile.d**2*scale,
    #                                       I=(2*I*scale,I*scale,I*scale))
    #         s.add_element(t)
    #
    #     #边界条件
    #     for pile in self.piles:
    #         s.add_fixed_sup(pile.nodes[-1].ID) #给柱底施加约束
    #     s.add_node_force(nd_zx.ID, Fz=-4e5)
    #
    #     s.solve()
    #     for pile in self.piles:
    #         print(pile.nodes[0].disp['Uz'])
    def fem(self):
        dl=0.1
        E=3.3e10
        G=1e10
        path = "e:\\ansysfile"
        mapdl = pyansys.launch_mapdl(run_location=path, interactive_plotting=False,
                                     override=True,
                                     loglevel="warning")
        mapdl.prep7()
        mapdl.n(1,0,0,self.ctd_height) #1号节点是承台中心
        mapdl.et(1, 188)
        mapdl.mp('ex', 1, 3.5e10)
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
        mapdl.lesize('all', 0.1)#单元大小默认0.1
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
        mapdl.d('all','all')

        #处理承台中心与桩顶连接
        select_kps(mapdl, knum_up)
        mapdl.nslk()
        mapdl.nsel('a','','',1)
        mapdl.cerig(1,'all','all')

        #处理承台中心单元
        mapdl.et(2, 21)
        mapdl.r(1, 10,10,10,10,10,10)
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
        #加载力
        mapdl.nsel('s', '', '', 1)
        test_force=1000
        mapdl.f(1,'fx',test_force)
        #求解
        mapdl.slashsolu()  # 进入求解模块
        mapdl.allsel()
        mapdl.solve()
        mapdl.fdele(1,'all')
        mapdl.f(1, 'fy', test_force)
        mapdl.time(2)
        mapdl.solve()

        #后处理
        mapdl.post1()
        result = mapdl.result
        ndnum, ndisp = result.nodal_displacement(0)  # 0代表第一个dataframe
        dx=ndisp[locate(ndnum,1)][0] #节点1的ux
        self.stiff_x=test_force/dx
        ndnum, ndisp = result.nodal_displacement(1)  # 0代表第一个dataframe
        dy=ndisp[locate(ndnum,1)][1] #节点1的ux
        self.stiff_y = test_force / dy
        print('刚度%f'%self.stiff_x)
        print('刚度%f' % self.stiff_y)

        mapdl.etable('fx','smisc',1)
        mapdl.etable('myi', 'smisc', 2)
        mapdl.etable('myj', 'smisc', 15)
        mapdl.etable('mzi', 'smisc', 3)
        mapdl.etable('mzj', 'smisc', 16)
        ks=['fx','myi','myj','mzi','mzj']
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
            for k in ks:
                eds.sort(key=lambda x:abs(x[k]),reverse=True)
                print("%s 值=%f 位置=%f"%(k,eds[0][k],eds[0]['z']))
        mapdl.save()
        self.mapdl=mapdl



class TestC(TestCase):
    def test1(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayer(layers)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(-5.5))
        self.assertEqual(s0, sl.soil_at_height(-0.1))
    def test2(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=2500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayer(layers,dm_height=100)
        self.assertEqual(-6,sl.ff.qidian)
        self.assertEqual(0,sl.ff.zongdian)
        self.assertEqual(s2, sl.soil_at_height(94.5))
        self.assertEqual(s0, sl.soil_at_height(100))
        self.assertRaises(Exception,sl.soil_at_height,100.1)
        self.assertRaises(Exception, sl.soil_at_height, 93.9)
        self.assertAlmostEqual(0,sl.stiff_of_soil(100),delta=0.1)
        self.assertAlmostEqual(150, sl.stiff_of_soil(99.9), delta=0.1)
        self.assertAlmostEqual(1500+250, sl.stiff_of_soil(100-1.1), delta=0.1)

    def test_pf(self):
        s0 = Soil(gamma=15, sigma0=0, fi=0, m=1500)
        s1 = Soil(gamma=25, sigma0=0, fi=0, m=1500)
        s2 = Soil(gamma=35, sigma0=0, fi=0, m=1500)
        layers = [[1, s0], [2, s1], [3, s2]]
        sl = SoilLayer(layers,dm_height=100)
        pf=Platform(x=9,y=18,z=2,ctd_height=100)
        pf.add_pile(d=1,H=5,x=2,y=2,sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=2, sl=sl)
        pf.add_pile(d=1, H=5, x=-2, y=-2, sl=sl)
        pf.add_pile(d=1, H=5, x=2, y=-2, sl=sl)
        pf.fem()
        self.assertAlmostEqual(582795486,pf.stiff_x,delta=1)
        self.assertAlmostEqual(582795486, pf.stiff_x, delta=1)
if __name__ == '__main__':
    main()
