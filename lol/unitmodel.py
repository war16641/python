from copy import deepcopy
from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type
import numpy as np
from enum import unique,Enum
import itertools
from typing import TypeVar, Generic,List
from enum import Enum, unique
from functools import reduce
@unique
class DamageType(Enum):
    """伤害的类型"""
    ad=0
    ap=1
    true=2

def calculate_actual_damage(damage:List[float],unit:'Unit'):
    """
    计算出发伤害经过物抗魔抗后 单位实际遭受的伤害 实际伤害
    :param damage: 3个数组成的列表 依次是物理 魔法 真实的出发伤害
                    也可以是三个列表组成的列表 子列表的长度相同
    :param unit: 被攻击者
    :return: 总伤害,3个数组成的列表（伤害细节）
            3个数组成的列表：对应的实际伤害
    """
    assert isinstance(damage,list) and len(damage)==3
    assert isinstance(unit,Unit)
    co_ad = 1 - unit.ad_armor / (100 + unit.ad_armor)
    co_ap = 1 - unit.ap_armor / (100 + unit.ap_armor)


    if isinstance(damage[0],(int,float)) and isinstance(damage[1],(int,float)) and isinstance(damage[2],(int,float)):
        ad_damage = damage[0]
        ap_damage = damage[1]
        true_damage = damage[2]
        tmp=[co_ad ,co_ap,1]
        actual_damage=[x*y for x,y in zip(damage,tmp)]
        return actual_damage[0]+actual_damage[1]+actual_damage[2],actual_damage
    elif isinstance(damage[0],list) and isinstance(damage[1],list) and isinstance(damage[2],list):
            if len(damage[0])==len(damage[1]) and len(damage[0])==len(damage[2]):#长度相等
                actual_damage_ad=[ad_damage1*co_ad for ad_damage1 in damage[0]]
                actual_damage_ap = [ap_damage1 * co_ap for ap_damage1 in damage[1]]
                actual_damage_sum=[x+y+z for x,y,z, in zip(actual_damage_ad,actual_damage_ap,damage[2])]
                return actual_damage_sum,[actual_damage_ad,actual_damage_ap,damage[2]]
            else:
                raise Exception("参数错误")
    else:
        raise Exception("参数错误")

class Ability:
    """
    技能 描述技能的裸伤害（无装备） 系数加成 伤害类型
    目前伤害类型只能是一种
    """
    def __init__(self,name,max_level,co_ad,co_ap,co_hp,rare_damage,co_mp=None,co_all=None,damage_type=DamageType.ad,extra_func=None):
        """

        :param name:
        :param max_level:
        :param co_ad:
        :param co_ap:
        :param co_hp:
        :param rare_damage:
        :param co_mp:
        :param co_all:
        :param damage_type:
        :param extra_func:
        """
        assert isinstance(name,str)
        assert max_level in (3,5,)
        assert isinstance(damage_type,DamageType)
        if co_mp is None:
            co_mp=[0,0]
        self.name,self.max_level=name,max_level
        self.co_ad,self.co_ap,self.co_hp,self.co_mp=co_ad,co_ap,co_hp,co_mp
        self.damage_type=damage_type
        self.extra_func=extra_func
        assert is_sequence_with_specified_type(rare_damage,list)
        self.rare_damage=rare_damage
        assert max_level==len(rare_damage),'最高等级和裸伤害内列表个数一致'

        if co_all is None:#伤害系数 有的技能说明是造成双倍伤害之类的话
            self.co_all=[1.0,1.0]
        else:
            self.co_all=co_all


    def query(self,level):
        """

        :param level:
        :return: 4个加成系数,裸伤害,额外函数 每一个都是含两个数的列表 代表最小值和最大值
        """
        #返回指定技能等级下三个系数和裸伤害的范围
        assert level<=self.max_level
        if level==0:
            return [0.,0.],[0.,0.],[0.,0.],[0.,0.]
        return self.co_ad,self.co_ap,self.co_hp,self.co_mp,self.rare_damage[level-1]

    def query_pre_damage(self,attacker:'Hero',defender:'Unit'=None):
        """

        :param attacker:
        :param defender:
        :return: [[ad伤害最小值,ad伤害最大值]，
                    [ap伤害最小值,ap伤害最大值]，
                    [tr伤害最小值,tr伤害最大值]，]
        """
        if defender is None:
            defender=Unit.get_sandbag()
        assert isinstance(attacker,Hero) and isinstance(defender,Unit)
        ability_level=attacker.upgrade_strategy.query(level=attacker.level,ability_str=self.name)
        if ability_level==0:
            return [[0,0],[0,0],[0,0]]
        tmp=[rare_damage1+co_ad1*attacker.ad+co_ap1*attacker.ap+co_hp1*attacker.hp+co_mp1*attacker.mp for \
             rare_damage1,co_ad1,co_ap1,co_hp1,co_mp1 in zip(self.rare_damage[ability_level-1],self.co_ad,self.co_ap,self.co_hp,self.co_mp)]
        r=[[0.,0.],[0.,0.],[0.,0.]]
        r[self.damage_type.value]=tmp
        r1=map(lambda x:[x[0]*self.co_all[0],x[1]*self.co_all[1]],r)
        r1=list(r1)
        return r1
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

class Unit:
    def __init__(self):
        self._hp=0
        self._mp=0
        self.ad=0
        self.ap=0
        self._level=1#五个属性值： 生命 魔法 ad ap 等级
        self.ad_armor=0
        self.ap_armor=0#物抗 魔抗

    @property
    def hp(self):
        return self._hp
    @hp.setter
    def hp(self,v):
        assert v>0,'生命值不可以为负'
        self._hp=v
    @property
    def mp(self):
        return self._mp
    @mp.setter
    def mp(self,v):
        assert v>=0,'魔法值不可以为负'
        self._mp=v

    @property
    def level(self):
        return self._level
    @level.setter
    def level(self,v):
        assert isinstance(v,int) and v>0
        self._level=v

    @staticmethod
    def get_sandbag(hp=4000,ad_armor=50,ap_armor=50):
        """
        返回一个沙袋对象 用于测试攻击 它的部分属性可以设置
        :param hp:
        :param ad_armor:
        :param ap_armor:
        :return:
        """
        defender = Unit()
        defender.level = 1
        defender.ad = 0
        defender.ap = 0
        defender.ap_armor = ap_armor
        defender.ad_armor = ad_armor
        defender.hp = hp
        defender.mp = 0
        return defender


class Hero(Unit):
    def __init__(self,common_abilities,upgrade_strategy,raw_health_seq):
        super().__init__()
        self.abilities=dict(zip(['q','w','e','r'],common_abilities))
        self.upgrade_strategy=upgrade_strategy#type:UpgradeDistribution
        assert len(raw_health_seq)==18
        self.raw_health_seq=raw_health_seq

    @property
    def level(self):
        return self._level
    @level.setter
    def level(self,v):
        self._level=v
        #更改生命值
        self.hp=self.raw_health_seq[v-1]


    def attack_with_one_ability(self,ability_str='q',defender:Unit=None):
        """
        使用单个技能对目标造成的实际伤害
        :param ability_str: 技能名
        :param defender:
        :return: 总伤害，伤害细节
        """
        if defender is None:
            defender=Unit.get_sandbag()
        assert isinstance(defender,Unit)
        #计算出发伤害
        if ability_str is 'a':#平a
            pre_damage=[self.ad,0,0]
        elif ability_str in 'qwer':
            pre_damage=self.abilities[ability_str].query_pre_damage(attacker=self,defender=defender)
        else:
            raise Exception("参数错误")
        #计算实际伤害
        actual_damage=calculate_actual_damage(pre_damage,defender)
        return actual_damage

    def attack(self,combo:str,defender:Unit=None):
        """
        使用连招进行攻击 计算实际伤害
        :param combo: 连招名
        :param defender:
        :return: 总伤害的范围
        """
        if defender is None:
            defender=Unit.get_sandbag()
        assert isinstance(defender,Unit)
        assert isinstance(combo,str),'combo参数是字符'
        lst=[]#存放实际伤害和
        #如果只是单个技能
        if len(combo)==1:
            actual_damage_sum, actual_damage_detail = self.attack_with_one_ability(combo, defender)
            return actual_damage_sum

        for ability_str in combo:
            actual_damage_sum,actual_damage_detail=self.attack_with_one_ability(ability_str,defender)
            if isinstance(actual_damage_sum,(int,float)) :#格式化实际伤害和
                actual_damage_sum=[actual_damage_sum,actual_damage_sum]
            lst.append(actual_damage_sum)
        #求伤害总和
        t1=reduce(lambda x,y:x[0]+y[0],lst)
        t2=reduce(lambda x,y:x[1]+y[1],lst)
        return [t1,t2]
def test1():
    u=Unit()
    u.ad_armor=100
    u.ap_armor=50
    a,b=calculate_actual_damage([100,200,15],u)
    assert b[0]==50
    assert b[1]-400/3<1e-3
    assert b[2]==15
    assert a-65-400/3<1e-3

def test2():
    health_seq = [552, 626, 703, 783, 867, 954, 1044, 1138, 1235, 1335, 1439, 1546, 1657, 1770, 1888, 2008, 2132,
                  2260]  # 吸血鬼裸装生命值
    ability_q = Ability('q', 5,
                        damage_type=DamageType.ap,
                        co_ad=[0, 0],
                        co_ap=[0.6, 0.6],
                        co_hp=[0, 0],
                        rare_damage=[
                            [80, 80], [100, 100], [120, 120], [140, 140], [160, 160]],#[80, 148], [100, 185], [120, 222], [140, 259], [160, 296]],
                        co_all=[1,1.85]
                        )
    ability_w = Ability('w', 5,
                        damage_type=DamageType.ap,
                        co_ad=[0, 0],
                        co_ap=[0.0, 0.0],
                        co_hp=[0, 0],
                        rare_damage=[
                            [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]
                        ])
    ability_e = Ability('e', 5,
                        damage_type=DamageType.ap,
                        co_ad=[0, 0],
                        co_ap=[0.35, 0.8],
                        co_hp=[0.015, 0.06],
                        rare_damage=[
                            [30, 60], [45, 90], [60, 120], [75, 150], [90, 180]
                        ])
    ability_r = Ability('r', 3,
                        damage_type=DamageType.ap,
                        co_ad=[0, 0],
                        co_ap=[0.7, 0.7],
                        co_hp=[0, 0],
                        rare_damage=[
                            [150, 150], [250, 250], [350, 350],],
                        co_all=[1.1,1.1])
    xxg = Hero(common_abilities=[ability_q, ability_w, ability_e, ability_r],
               upgrade_strategy=ud_dict['qew'],
               raw_health_seq=health_seq)
    # t=xxg.abilities['q'].query_pre_damage(attacker=xxg,defender=None)
    xxg.level=5
    xxg.ap=40
    print(xxg.attack('qe',defender=Unit.get_sandbag(ap_armor=30)))
    # print(calculate_actual_damage(damage=t,unit=Unit.get_sandbag()))
    # print(t)
if __name__ == '__main__':
    test2()