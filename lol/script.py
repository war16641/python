from copy import deepcopy
from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type
import numpy as np
from enum import unique,Enum
import itertools
class UpgradeDistribution:
    def __init__(self,strategy):
        assert isinstance(strategy,str)
        assert len(strategy)==3
        strategy=strategy.lower()
        self.strategy=strategy

        #初始化18个等级的技能加点
        self.dicts=[]#type:List[dict]#存放技能加点情况的列表 18个字典 每个字典代表一个等级

        #前三级
        dict1={}
        dict1[self.strategy[0]]=1
        dict1[self.strategy[1]] = 0
        dict1[self.strategy[2]] = 0
        dict1['r']=0
        self.dicts.append(dict1)
        dict1 = deepcopy(dict1)
        dict1[self.strategy[1]] = 1
        self.dicts.append(dict1)
        dict1 = deepcopy(dict1)
        dict1[self.strategy[2]] = 1
        self.dicts.append(dict1)

        #后面4~18
        for level in range(4,19):
            dict1=deepcopy(dict1)
            if level in (6,11,16,):#加大招的等级
                dict1['r']+=1
                self.dicts.append(dict1)
            else:#加小技能点
                if dict1[self.strategy[0]]<4:
                    dict1[self.strategy[0]]+=1
                    self.dicts.append(dict1)
                elif dict1[self.strategy[0]]==4 and dict1[self.strategy[1]]==1:
                    # 最优先加点技能为4 次最优先为1时
                    dict1[self.strategy[1]] += 1
                    self.dicts.append(dict1)
                elif dict1[self.strategy[0]]==4 and dict1[self.strategy[1]]!=1:
                    dict1[self.strategy[0]] += 1
                    self.dicts.append(dict1)#此时 最优先加点已到5
                elif dict1[self.strategy[1]]<5:
                    dict1[self.strategy[1]] += 1
                    self.dicts.append(dict1)
                else:
                    dict1[self.strategy[2]] += 1
                    self.dicts.append(dict1)


    def print(self):
        for i,v in enumerate(self.dicts):
            level=i+1
            print('等级%d,q%d,w%d,e%d,r%d'%(level,v['q'],v['w'],v['e'],v['r']))

    def query(self, level:int, ability_str:str)->int:
        """
        查询某个等级下某个技能的等级
        :param level:
        :param ability_str: q w e r
        :return:
        """
        assert isinstance(level,int)
        assert isinstance(ability_str, str)
        return self.dicts[level-1][ability_str]

ud_dict={}
for a,b,c in itertools.permutations('qwe',3):
    s=a+b+c
    ud_dict[s]=UpgradeDistribution(s)


class Ability:
    def __init__(self,name,max_level,co_ad,co_ap,co_hp,rare_damage,co_all=None):
        assert isinstance(name,str)
        assert max_level in (3,5,)
        self.name,self.max_level=name,max_level
        self.co_ad,self.co_ap,self.co_hp=co_ad,co_ap,co_hp
        assert is_sequence_with_specified_type(rare_damage,list)
        self.rare_damage=rare_damage
        assert max_level==len(rare_damage),'最高等级和裸伤害内列表个数一致'

        if co_all is None:#伤害系数 有的技能说明是造成双倍伤害之类的话
            self.co_all=[1.0,1.0]
        else:
            self.co_all=co_all


    def query(self,level):
        #返回指定技能等级下三个系数和裸伤害的范围
        assert level<=self.max_level
        if level==0:
            return [0.,0.],[0.,0.],[0.,0.],[0.,0.]
        return self.co_ad,self.co_ap,self.co_hp,self.rare_damage[level-1]


class Hero:
    def __init__(self,name,health_seq,strategy,ability_lst):
        self.name=name
        assert len(health_seq)==18
        assert isinstance(strategy,UpgradeDistribution)
        assert len(ability_lst)==4
        self.health_seq=health_seq
        self.strategy=strategy
        self.abilities=dict(zip(['q','w','e','r'],ability_lst))

        self.ad=0
        self.ap=0
        self._level=1
        self._hp=0#代表总的生命值

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self,v):
        assert v>=1 and v<=18
        self._level=v
        # self.hp=self.health_seq[v-1]#更改生命值
    @property
    def hp(self):
        if self._hp==0:#如果没有设置总的生命值 就返回裸生命值
            return self.health_seq[self._level-1]
        assert self._hp>=self.health_seq[self._level-1],'生命值不能低于裸装生命值'
        return self._hp
    @hp.setter
    def hp(self,v):
        if v==0:
            return
        assert v >= self.health_seq[int(self._level) - 1], '生命值不能低于裸装生命值'
        self._hp=v
    def query_damage_for_one_ability(self,ability_str):
        #平a的处理
        if ability_str=='a':
            return self.ad,self.ad

        #技能的处理
        ability_level=self.strategy.query(level=self.level,ability_str=ability_str)
        co_ad, co_ap, co_hp, rare_damage=self.abilities[ability_str].query(level=ability_level)
        co_all=self.abilities[ability_str].co_all
        # rare_hp=self.health_seq[self.level-1]
        #暂时使用下面的属性值
        ad=self.ad
        ap=self.ap
        hp=self.hp

        low_damage=co_ad[0]*ad+co_ap[0]*ap+co_hp[0]*hp+rare_damage[0]
        high_damage=co_ad[1]*ad+co_ap[1]*ap+co_hp[1]*hp+rare_damage[1]
        return low_damage*co_all[0],high_damage*co_all[1]

    
    def print(self,magic_armor=0,ad=0,ap=0,hp=0):
        self.ad=ad
        self.ap=ap
        self.hp=hp

        print('裸装伤害,在ad=%d,ap=%d,敌方魔抗=%d下：'%(ad,ap,magic_armor))
        coeff_after_armor=1-magic_armor/(magic_armor+100.)
        for i in range(0,18):
            level=i+1
            self.level=level
            print('等级%d,'%level,end='')
            damage_total=[0,0]
            for istr in ('q','w','e','r'):
                damage=self.query_damage_for_one_ability(istr)
                damage_total[0]+=damage[0]
                damage_total[1]+=damage[1]
                print('%s技能%d-%d,'%(istr,damage[0]*coeff_after_armor,damage[1]*coeff_after_armor),end='')
            print('。合计%d-%d'%(damage_total[0]*coeff_after_armor,damage_total[1]*coeff_after_armor))

    def combo0(self, armor_ad=40,armor_ap=30):
        """平a+基本技能伤害"""
        coeff_after_ap = 1 - armor_ap / (armor_ap + 100.)
        coeff_after_ad = 1 - armor_ad / (armor_ad + 100.)
        damage0=self.query_damage_for_one_ability('a')
        damage1 = self.query_damage_for_one_ability('q')
        damage2 = self.query_damage_for_one_ability('w')
        damage3 = self.query_damage_for_one_ability('e')
        damage4 = self.query_damage_for_one_ability('r')
        damage0_after=[x*coeff_after_ad for x in damage0]
        damage1_after=[x*coeff_after_ap for x in damage1]
        damage2_after = [x * coeff_after_ap for x in damage2]
        damage3_after = [x * coeff_after_ap for x in damage3]
        damage4_after = [x * coeff_after_ap for x in damage4]
        return damage0_after,damage1_after,damage2_after,damage3_after,damage4_after
    def combo1(self,magic_armor=30):
        """qe"""
        coeff_after_armor=1-magic_armor/(magic_armor+100.)
        damage1 = self.query_damage_for_one_ability('q')
        damage2 = self.query_damage_for_one_ability('e')
        damage_total=map(lambda a,b:a+b,damage1,damage2)
        damage_total_after_armor=[x*coeff_after_armor for x in damage_total]
        # print(damage_total_after_armor)
        return damage_total_after_armor
    def combo2(self,magic_armor=30):
        """qer"""
        coeff_after_armor=1-magic_armor/(magic_armor+100.)
        damage1 = self.query_damage_for_one_ability('q')
        damage2 = self.query_damage_for_one_ability('e')
        damage3 = self.query_damage_for_one_ability('r')
        damage_total=map(lambda a,b,c:a+b+c,damage1,damage2,damage3)
        damage_total_after_armor=[x*coeff_after_armor for x in damage_total]
        # print(damage_total_after_armor)
        return damage_total_after_armor
    def combo3(self,magic_armor=30):
        """qerq
        q是平常q加暴怒q"""
        coeff_after_armor = 1 - magic_armor / (magic_armor + 100.)
        damage1 = self.query_damage_for_one_ability('q')
        damage2 = self.query_damage_for_one_ability('w')
        damage3 = self.query_damage_for_one_ability('e')
        damage4 = self.query_damage_for_one_ability('r')
        damage1_after=[x*coeff_after_armor for x in damage1]
        damage2_after = [x * coeff_after_armor for x in damage2]
        damage3_after = [x * coeff_after_armor for x in damage3]
        damage4_after = [x * coeff_after_armor for x in damage4]
        return [damage1_after[0]+damage1_after[1]+damage3_after[0]+damage4_after[1],damage1_after[0]+damage1_after[1]+damage3_after[1]+damage4_after[1]]

def get_xxg():
    """返回一个吸血鬼"""
    health_seq = [552, 626, 703, 783, 867, 954, 1044, 1138, 1235, 1335, 1439, 1546, 1657, 1770, 1888, 2008, 2132,
                  2260]  # 吸血鬼裸装生命值
    assert len(health_seq) == 18

    ability_q = Ability('q', 5,
                        co_ad=[0, 0],
                        co_ap=[0.6, 0.6],
                        co_hp=[0, 0],
                        rare_damage=[
                            [80, 80], [100, 100], [120, 120], [140, 140], [160, 160]],#[80, 148], [100, 185], [120, 222], [140, 259], [160, 296]],
                        co_all=[1,1.85]
                        )
    ability_w = Ability('w', 5,
                        co_ad=[0, 0],
                        co_ap=[0.0, 0.0],
                        co_hp=[0, 0],
                        rare_damage=[
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]
                        ])
    ability_e = Ability('e', 5,
                        co_ad=[0, 0],
                        co_ap=[0.35, 0.8],
                        co_hp=[0.015, 0.06],
                        rare_damage=[
                            [30, 60], [45, 90], [60, 120], [75, 150], [90, 180]
                        ])
    ability_r = Ability('r', 3,
                        co_ad=[0, 0],
                        co_ap=[0.7, 0.7],
                        co_hp=[0, 0],
                        rare_damage=[
                            [150, 150], [250, 250], [350, 350],],
                        co_all=[1.1,1.1])
    xxg = Hero('xixuegui', health_seq, ud_dict['qew'], [ability_q, ability_w, ability_e, ability_r])
    return xxg
if __name__ == '__main__':
    ud=UpgradeDistribution(strategy='qew')
    # ud.print()
    assert ud.query(6,'r')==1

    xxg=get_xxg()
    # xxg.print(magic_armor=30,ap=40)
    xxg.level=5
    xxg.ap=40
    print(xxg.combo1())
    print(xxg.combo2())