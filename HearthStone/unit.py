from enum import unique, Enum
import random
from typing import Tuple, List


@unique
class UnitType(Enum):  # 随从类型
    none = 1  # 无属性
    all = 2  # 所有属性
    mech = 3
    demon = 4
    dragon = 5
    beast = 6
    murloc = 7


@unique
class SummonType(Enum):  # 随从产生类型
    User = 1  # 打牌
    Card = 2  # 其他卡牌产生


@unique
class MessageType(Enum):  # 消息类型
    none = 1  # 无类型
    summon = 2  # 随从产生（不分card或者user）
    death = 3  # 随从死亡
    turn_start=4
    turn_end=5 #回合开始 结束


@unique
class HaloType(Enum):  # 光环类型
    nearby = 1  # 周围的两个 恐狼
    singlefield = 2  # 自己场
    bothfield = 3  # 两个场


class TemplateUnit:
    """
    随从模板的基函数
    """

    def __init__(self, name: str, unit: 'Unit', hp, ad, shild=False, windfury=False, superwindfury=False, taunt=False,
                 utype=UnitType.none,
                 mana=1,
                 htype=None):
        """

        @param unit:
        @param hp:
        @param ad:
        @param shild:
        @param windfury:
        @param superwindfury:
        @param taunt:
        """
        self.name, self.hp, self.ad, self.shild, self.windfury, self.superwindfury, self.taunt, self.utype = name, hp, ad, shild, windfury, superwindfury, taunt, utype
        self.mana = mana  # 费
        self.unit = unit  # 模板需要挂一个随从
        self.halotype = htype  # type:HaloType#如果能提供halo，halo的类型

    def on_battlecry(self):
        print("%s(%x):on battlecry" % (self.name, id(self)))
        pass

    def on_summon(self):
        # 战吼执行完成后，广播summon信息
        self.unit.field.broadcast_msg(self.unit, MessageType.summon)
        # 如果自身有halo
        if self.halotype is not None:
            self.unit.field.units_with_halo.append(self.unit)  # field的units_with_halo加入自己
        self.unit.field.on_unit_posiont_change(self.unit)

    def on_deathrattle(self):
        print("%s(%x):on deathrattle" % (self.name, id(self)))
        # 如果自身有halo
        if self.halotype is not None:
            self.unit.clear_halo_follwers()  # 消除自身halo的影响
            self.unit.field.units_with_halo.remove(self.unit)  # field的units_with_halo加入自己
        self.unit.field.on_unit_posiont_change(self.unit)
        pass

    def on_attack(self):
        """攻击前"""
        print("%s(%x):on attack" % (self.name, id(self)))
        pass

    def on_damaged(self, dg):
        """
        收到伤害dg
        """
        print("%s(%x):on damaged by %d" % (self.name, id(self), dg))
        pass

    def on_msg(self, orgin: 'Unit', msgtype=MessageType.none,*args):
        """
        获得消息并处理
        @param orgin:
        @param msgtype:
        @return:
        """
        print("%s(%x):on msg by %s(%x)" % (self.name, id(self), orgin.template.name, id(orgin)))

    @staticmethod
    def is_in_halo(obj: 'Unit', origin: 'Unit', htype: HaloType):
        """
        判断obj是否在halo内
        @param obj:
        @param origin:
        @param htype:
        @return:
        """
        if htype == HaloType.nearby:
            return abs((origin.fieldid - obj.fieldid)) == 1 and origin.field == obj.field
        elif htype == HaloType.singlefield:
            return origin.field == obj.field
        elif htype == HaloType.bothfield:
            return origin.field == obj.field or origin.field.opponent == obj.field
        else:
            raise Exception("参数错误")

    def halo_in_func(self, obj: 'Unit', *args):
        """
        当obj处于self的halo内时，触发的函数
        一般是对ad_buff,hp_buff进行操作
        @param obj:
        @param args:
        @return:
        """
        print("%s(%x):halo in function by %s(%x)" % (self.name, id(self), obj.template.name, id(obj)))

    def halo_out_func(self, obj: 'Unit', *args):
        """
        当obj处从self的halo移除时，触发的函数
        一般是对ad_buff,hp_buff进行操作
        @param obj:
        @param args:
        @return:
        """
        print("%s(%x):halo out function by %s(%x)" % (self.name, id(self), obj.template.name, id(obj)))


class Dog(TemplateUnit):
    def __init__(self, unit: 'Unit'):
        super(Dog, self).__init__(name='dog',
                                  unit=unit,
                                  hp=2,
                                  ad=1,
                                  )

    def on_battlecry(self):
        print("dog(%x) is on field" % (id(self.unit)))

    def on_deathrattle(self):
        print("dog(%x) is dead" % (id(self.unit)))

    def on_attack(self):
        print("dog(%x) is about to attack_unit" % (id(self.unit)))

    def on_damaged(self, dg):
        print("dog(%x) is hurted by %d" % (id(self.unit), dg))


class MechKangarooSon(TemplateUnit):
    """
    机械袋鼠儿子
    """

    def __init__(self, unit: 'Unit'):
        super(MechKangarooSon, self).__init__(unit=unit,
                                              hp=1,
                                              ad=1,
                                              utype=UnitType.mech,
                                              name='MechKangarooSon'
                                              )


class MechKangaroo(TemplateUnit):
    """
    机械袋鼠
    """

    def __init__(self, unit: 'Unit'):
        super(MechKangaroo, self).__init__(unit=unit,
                                           hp=1,
                                           ad=1,
                                           utype=UnitType.mech,
                                           name='MechKangaroo'
                                           )

    def on_deathrattle(self):
        super(MechKangaroo, self).on_deathrattle()
        Unit(MechKangarooSon, self.unit.field, self.unit.fieldid, stype=SummonType.Card)  # 召唤儿子


class FemaleTiger(TemplateUnit):
    """

    """

    def __init__(self, unit: 'Unit'):
        super(FemaleTiger, self).__init__(unit=unit,
                                          hp=1,
                                          ad=1,
                                          utype=UnitType.beast,
                                          name='FemaleTiger'
                                          )


class MaleTiger(TemplateUnit):
    """

    """

    def __init__(self, unit: 'Unit'):
        super(MaleTiger, self).__init__(unit=unit,
                                        hp=1,
                                        ad=1,
                                        utype=UnitType.beast,
                                        name='MaleTiger'
                                        )

    def on_battlecry(self):
        super(MaleTiger, self).on_battlecry()
        Unit(FemaleTiger, self.unit.field, self.unit.fieldid + 1)  # 召唤母的


class DragonspawnLieutenant(TemplateUnit):
    """
        带嘲讽的龙
    """

    def __init__(self, unit: 'Unit'):
        super(DragonspawnLieutenant, self).__init__(unit=unit,
                                                    hp=3,
                                                    ad=2,
                                                    utype=UnitType.dragon,
                                                    name='DragonspawnLieutenant',
                                                    taunt=True
                                                    )


class RightnessProtector(TemplateUnit):
    """
        圣盾 嘲讽
    """

    def __init__(self, unit: 'Unit'):
        super(RightnessProtector, self).__init__(unit=unit,
                                                 hp=1,
                                                 ad=1,
                                                 utype=UnitType.none,
                                                 name='RightnessProtector',
                                                 taunt=True,
                                                 shild=True
                                                 )


class FiendishServant(TemplateUnit):
    """
    亡语：转移攻击力
    """

    def __init__(self, unit: 'Unit'):
        super(FiendishServant, self).__init__(unit=unit,
                                              hp=1,
                                              ad=2,
                                              utype=UnitType.demon,
                                              name='FiendishServant'
                                              )

    def on_deathrattle(self):
        super(FiendishServant, self).on_deathrattle()
        target = self.unit.field.get_random_unit(ignore_taunt=True, ignore_unit=self.unit)
        if target is not None:
            target.ad += self.unit.ad  # 转移攻击力


class RockpoolHunter(TemplateUnit):
    """
        给一个鱼人+1+1
    """

    def __init__(self, unit: 'Unit'):
        super(RockpoolHunter, self).__init__(unit=unit,
                                             hp=3,
                                             ad=2,
                                             utype=UnitType.murloc,
                                             name='RockpoolHunter',
                                             )

    def on_battlecry(self):
        super(RockpoolHunter, self).on_battlecry()
        # 给鱼人+1+1
        if self.unit.tarunit is None:
            return
        if self.unit.tarunit.template.utype is not UnitType.murloc:
            raise Exception("战吼目标应该是鱼人")
        else:
            self.unit.tarunit.ad += 1
            self.unit.tarunit.hp += 1


class TideHunterSon(TemplateUnit):
    """

    """

    def __init__(self, unit: 'Unit'):
        super(TideHunterSon, self).__init__(unit=unit,
                                            hp=1,
                                            ad=1,
                                            utype=UnitType.murloc,
                                            name='TideHunterSon',
                                            )


class TideHunter(TemplateUnit):
    """

    """

    def __init__(self, unit: 'Unit'):
        super(TideHunter, self).__init__(unit=unit,
                                         hp=1,
                                         ad=2,
                                         utype=UnitType.murloc,
                                         name='TideHunter',
                                         )

    def on_battlecry(self):
        super(TideHunter, self).on_battlecry()
        Unit(TideHunterSon, self.unit.field, self.unit.fieldid + 1, stype=SummonType.Card)


class TideCaller(TemplateUnit):
    """
        每召唤一个鱼人+1ad
    """

    def __init__(self, unit: 'Unit'):
        super(TideCaller, self).__init__(unit=unit,
                                         hp=2,
                                         ad=1,
                                         utype=UnitType.murloc,
                                         name='TideCaller',
                                         )

    def on_msg(self, orgin: 'Unit', msgtype=MessageType.none):
        super(TideCaller, self).on_msg(orgin, msgtype)
        if orgin is self.unit:
            return #跳过自己
        if msgtype == MessageType.summon:
            if orgin.template.utype == UnitType.murloc:
                self.unit.ad += 1


class SelflessHero(TemplateUnit):
    """
    亡语：转移攻击力
    """

    def __init__(self, unit: 'Unit'):
        super(SelflessHero, self).__init__(unit=unit,
                                           hp=1,
                                           ad=2,
                                           utype=UnitType.none,
                                           name='SelflessHero'
                                           )

    def on_deathrattle(self):
        super(SelflessHero, self).on_deathrattle()
        # 寻找一个没有护盾的随从
        pool = [x for x in self.unit.field.lineup]
        if self.unit in pool:
            pool.remove(self.unit)
        lst = []
        for i in pool:
            if not i.shield:  # 没有圣盾
                lst.append(i)
        if len(lst) == 0:
            return
        else:
            target = random.choice(lst)
            target.shield = True


class DireWolfAlpha(TemplateUnit):
    """
    亡语：转移攻击力
    """

    def __init__(self, unit: 'Unit'):
        super(DireWolfAlpha, self).__init__(unit=unit,
                                            hp=2,
                                            ad=2,
                                            utype=UnitType.beast,
                                            name='DireWolfAlpha',
                                            htype=HaloType.nearby
                                            )

    def halo_in_func(self, follower: 'Unit', *args):
        super(DireWolfAlpha, self).halo_in_func(follower)
        # ad+1
        ad1 = 1
        follower.ad += ad1
        follower.ad_buff += ad1

    def halo_out_func(self, follower: 'Unit', *args):
        super(DireWolfAlpha, self).halo_out_func(follower)
        # ad+1
        ad1 = 1
        follower.ad -= ad1
        follower.ad_buff -= ad1


class WrathWaver(TemplateUnit):
    """
    每当使用恶魔牌获得+2+2
    """

    def __init__(self, unit: 'Unit'):
        super(WrathWaver, self).__init__(unit=unit,
                                         hp=1,
                                         ad=1,
                                         utype=UnitType.none,
                                         name='WrathWaver',
                                         )

    def on_msg(self, orgin: 'Unit', msgtype=MessageType.none):
        if msgtype is MessageType.summon and orgin.summon_type is SummonType.User and orgin.template.utype is UnitType.demon:
            self.unit.ad += 2
            self.unit.hp += 2


class RedWhelp(TemplateUnit):
    """
    小喷火龙
    """

    def __init__(self, unit: 'Unit'):
        super(RedWhelp, self).__init__(unit=unit,
                                         hp=2,
                                         ad=1,
                                         utype=UnitType.dragon,
                                         name='RedWhelp',
                                         )

    def on_msg(self, orgin: 'Unit', msgtype=MessageType.none,op=None):
        #回合开始就可以喷火 但是需要鉴别是不是战斗回合
        if msgtype is MessageType.turn_start:
            assert isinstance(op,Field),'op必须为field实例'
            #to do：鉴别是不是战斗回合
            #计算自己场上有几条龙
            t=0
            for u in self.unit.field.lineup:
                if u.template.utype is UnitType.dragon:
                    t+=1
            #随机选择一个地方随从
            tar=op.get_random_unit()
            if tar is not None:#有目标
                tar.on_damage(t)
        else:#其他消息
            pass


class MicroMachine(TemplateUnit):
    """
    每个购买回合开始时 +1攻击力
    """

    def __init__(self, unit: 'Unit'):
        super(MicroMachine, self).__init__(unit=unit,
                                         hp=2,
                                         ad=1,
                                         utype=UnitType.mech,
                                         name='MicroMachine',
                                         )

    def on_msg(self, orgin: 'Unit', msgtype=MessageType.none,op=None):

        if msgtype is MessageType.turn_start:
            if op =='shop':
                self.unit.ad+=1

        else:#其他消息
            pass




class UnstableGhoul(TemplateUnit):
    """
    亡语：群伤一点
    """

    def __init__(self, unit: 'Unit'):
        super(UnstableGhoul, self).__init__(unit=unit,
                                           hp=1,
                                           ad=3,
                                           utype=UnitType.none,
                                           name='UnstableGhoul',
                                            mana=2,
                                            taunt=True

                                           )

    def on_deathrattle(self):
        super(UnstableGhoul, self).on_deathrattle()
        for u in self.unit.field.allunits:
            if u is self.unit:
                continue
            u.on_damage(1)


class PogoHopper(TemplateUnit):
    """
    兔兔 +2+2 战吼
    """
    counteri=-1 #累计打出的量
    def __init__(self, unit: 'Unit'):
        super(PogoHopper, self).__init__(unit=unit,
                                           hp=1,
                                           ad=1,
                                           utype=UnitType.mech,
                                           name='PogoHopper',
                                            mana=2

                                           )


    def on_battlecry(self):
        super(PogoHopper,self).on_battlecry()
        PogoHopper.counteri+=1
        self.unit.hp+=PogoHopper.counteri*2
        self.unit.ad+=PogoHopper.counteri*2


class RatPackSon(TemplateUnit):
    """
    亡语 等于攻击力的儿子
    """
    counter=-1 #累计打出的量
    def __init__(self, unit: 'Unit'):
        super(RatPackSon, self).__init__(unit=unit,
                                           hp=1,
                                           ad=1,
                                           utype=UnitType.beast,
                                           name='RatPackSon',
                                            mana=1

                                           )

class RatPack(TemplateUnit):
    """
    亡语 等于攻击力的儿子
    """
    counter=-1 #累计打出的量
    def __init__(self, unit: 'Unit'):
        super(RatPack, self).__init__(unit=unit,
                                           hp=2,
                                           ad=2,
                                           utype=UnitType.beast,
                                           name='RatPack',
                                            mana=2

                                           )

    def on_deathrattle(self):
        super(RatPack,self).on_deathrattle()
        for i in range(self.unit.ad):
            self.unit.field.make_unit(RatPackSon,self.unit.fieldid+1,stype=SummonType.Card)
            # Unit(RatPackSon,self.unit.field,self.unit.fieldid+1,stype=SummonType.Card)


class Field:
    """
    场地
    随从需要场地，还需要表示他们的位置
    """

    def __init__(self, name, op=None,maxnum=7):
        self.name = name
        self.lineup = [] #type:List[Field]
        self._opponent = op  # type:Field#对手的field
        self.units_with_halo = []  # type:list[Unit]#带有halo的unit 场上
        self.maxnum=maxnum #最大随从

    @property
    def num(self):
        return len(self.lineup)

    @property
    def realnum(self):
        #抛去将死亡的
        lst=[x for x in self.lineup if x.hp>0 ]
        return len(lst)

    def print_info(self):
        # print("field name:%s" % self.name)
        # print("number of units:%d" % self.num)
        print("___%s(num:%d) detail info on units___________" % (self.name, self.num))
        for i, u in enumerate(self.lineup):
            print("%d->%s" % (i, u))
        print("___info  end ___________________________")

    def get_random_unit(self, ignore_taunt=False, ignore_unit: 'Unit' = None) -> 'Unit':
        """

        @param ignore_taunt:
        @param ignore_unit:忽略的随从，通常是忽略自己
        @return:
        """
        if ignore_taunt:  # 若忽视嘲讽 选择全部随从
            pool = [x for x in self.lineup]
        else:
            pool = [x for x in self.lineup if x.taunt == True]
            if len(pool) == 0:  # 如果没有嘲讽 选择全部随从
                pool = self.lineup

        if len(pool) == 0:
            return None  # 没有随从 返回none
        if ignore_unit is not None and ignore_unit in pool:  # 排除忽略的随从
            pool.remove(ignore_unit)
        target = random.choice(pool)
        return target

    def broadcast_msg(self, orgin: 'Unit', msgtype=MessageType.none,*args):
        """
        给全体随从广播消息
        会跳过msg的发起人
        @param orgin: 发起人 可以是unit实例 field实例
        @param msgtype:
        @return:
        """
        for i in self.lineup:
            # if i == orgin:
            #     continue  # 跳过自己
            i.template.on_msg(orgin, msgtype,*args)

    @property
    def opponent(self) -> 'Field':
        if self._opponent is None:
            raise Exception("没有对手场地")
        return self._opponent

    @opponent.setter
    def opponent(self, v):
        # assert isinstance(v, Field), "参数错误"
        self._opponent = v

    @staticmethod
    def make_twin_fields(name1='red', name2='blue') -> Tuple['Field','Field']:
        """
        制作一对互为对手的field
        @param name1:
        @param name2:
        @return:
        """

        field1 = Field(name1)
        field2 = Field(name2)
        field1.opponent = field2
        field2.opponent = field1
        return field1, field2

    @property
    def allunits(self) -> List['Unit']:
        # 返回场上所有的unit 包括对手场上
        x1 = [x for x in self.lineup]
        x2 = [x for x in self.opponent.lineup]
        return x1 + x2

    def recalculate_halo(self):
        # 重新计算halo的影响
        for render in self.units_with_halo:
            if render.template.halotype is HaloType.bothfield:
                continue  # 全场halo不改变
            elif render.template.halotype is HaloType.singlefield:
                continue  # 这里可能存在bug 只影响自己场的也跳过
            elif render.template.halotype is HaloType.nearby:
                render.clear_halo_follwers()
                # for fl in render.halo_follwers:
                #     render.template.halo_out_func(fl)#移除halo
                #     fl.halo_renders.remove(render)
                # render.halo_follwers=[]
                # 重新计算
                for u in self.allunits:
                    if TemplateUnit.is_in_halo(u, render, render.template.halotype):
                        # 在halo内
                        u.halo_renders.append(render)
                        render.halo_follwers.append(u)
                        render.template.halo_in_func(u)

    def on_unit_posiont_change(self, unit: 'Unit'):
        """
        当场上任何一个随从的位置发生改变，包括死亡，summon 触发此函数
        @param unit:
        @return:
        """
        self.recalculate_halo()

    def on_turn_start(self,opponent:'Field'):
        """
        回合开始
        @param opponent: 对手field实例,如果是购买回合，‘shop’
        @return:
        """
        self.opponent=opponent#设置opponent属性
        self.broadcast_msg(self,MessageType.turn_start,opponent)


    def make_unit(self,template:'TemplateUnit',fieldindex:int,stype=SummonType.User,tarunit:'Unit'=None)->'Unit':
        """
        在场上创建新的unit
        @param template:
        @param fieldindex:
        @param stype:
        @param tarunit:
        @return:
        """
        #检查场上随从是否已满
        if self.realnum==self.maxnum:
            print("units in field reaches max number")
            return None
        return Unit(template,self,fieldindex,stype,tarunit)

class Unit:
    """
    放到场上战斗的随从
    """

    def __init__(self, template: 'TemplateUnit', field: Field, fieldindex: int, stype: SummonType = SummonType.User,
                 tarunit: 'Unit' = None):
        """
        生成场上战斗随从
        @param template:模板的类 不是对象
        @param field:
        @param fieldindex:
        """
        self.field = field  # type:Field
        assert isinstance(template, type), "template必须为类名"
        self.template = template(self)  # type:TemplateUnit

        self.hp, self.ad, self.shield, self.windfury, self.superwindfury, self.taunt = self.template.hp, self.template.ad, self.template.shild, self.template.windfury, self.template.superwindfury, self.template.taunt
        self.summon_type = stype
        self.tarunit = tarunit  # 战吼目标 默认为none
        self.ad_buff, self.hp_buff = 0, 0  # 因halo产生的额外的ad，hp
        self.halo_renders = []  # type:List[Unit]#自己受到影响的halo的提供者
        self.halo_follwers = []  # type:List[Unit]#自己作为halo的render 影响的unit
        self.field.lineup.insert(fieldindex, self)  # 场上添加自己

        if self.summon_type == SummonType.User:
            self.template.on_battlecry()  # 如果是打出的 触发战吼

        self.template.on_summon()  # 广播summon消息
        pass

    def on_damage(self, dg):
        """

        @param dg:
        @return:
        """
        if dg == 0:
            return  # 无伤害产生
        if self.shield:
            self.shield = False
            return  # 有圣盾 ：去除神盾

        # 以下，确实受到伤害
        self.template.on_damaged(dg)
        self.hp -= dg

        # 检查是否死亡
        if self.hp <= 0:
            self.on_death()

    def attack_unit(self, enemy: 'Unit'):
        """
        进攻随从
        @param enemy:
        @return:
        """
        self.template.on_attack()

        # 先计算自己受到伤害
        dg = enemy.ad
        self.on_damage(dg)

        # 再计算对手受到伤害
        dg = self.ad
        enemy.on_damage(dg)

    def attack_field(self, field: Field = None, ignore_taunt=False):
        """
        进攻场地
        @param field:默认攻击对手field
        @param ignore_taunt:随机选择进攻对手时，是否忽略对方嘲讽随从
        @return:
        """
        if field is None:
            field = self.field.opponent
        if field.num == 0:
            raise Exception("对方场地无随从")
        assert self.field is not field, "不能进攻自己场地"

        # 随机选择一个随从进攻
        target = field.get_random_unit(ignore_taunt)
        if target is None:
            raise Exception("场地%s无随从" % field.name)
        self.attack_unit(target)

    def on_death(self):

        self.template.on_deathrattle()  # 触发亡语
        self.field.lineup.remove(self)  # 从场上移除

    def __str__(self):
        return "%s(%x):%d hp with %d ad" % (self.template.name, id(self), self.hp, self.ad)

    @property
    def fieldid(self):
        # 自己在field中的位置 基于0
        return self.field.lineup.index(self)

    def clear_halo_follwers(self):
        # 清楚自身halo对其他的unit的影响
        for u in self.halo_follwers:
            self.template.halo_out_func(u)
            u.halo_renders.remove(self)
        self.halo_follwers = []


if __name__ == '__main__':
    filed_red = Field('red')
    field_blue = Field('blue')
    u1 = Unit(MechKangaroo, filed_red, 0)
    u2 = Unit(MaleTiger, field_blue, 0)
