from enum import unique, Enum
import random

@unique
class UnitType(Enum):  # 随从类型
    none = 1  # 无属性
    all = 2  # 所有属性
    mech = 3
    demon = 4
    dragon = 5
    beast = 6
    murloc=7

@unique
class SummonType(Enum):  # 随从产生类型
    User = 1  # 打牌
    Card = 2  # 其他卡牌产生

@unique
class MessageType(Enum):  # 消息类型
    none = 1  # 无类型
    summon = 2  # 随从产生（不分card或者user）
    death=3 #随从死亡



class TemplateUnit:
    """
    随从模板的基函数
    """

    def __init__(self, name: str, unit: 'Unit', hp, ad,shild=False, windfury=False, superwindfury=False, taunt=False,
                 utype=UnitType.none,
                 mana=1):
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
        self.mana=mana #费
        self.unit = unit  # 模板需要挂一个随从


    def on_battlecry(self):
        print("%s(%x):on battlecry"%(self.name,id(self)))
        pass

    def on_summon(self):
        #战吼执行完成后，广播summon信息
        self.unit.field.broadcast_msg(self.unit,MessageType.summon)

    def on_deathrattle(self):
        print("%s(%x):on deathrattle"%(self.name,id(self)))
        pass

    def on_attack(self):
        """攻击前"""
        print("%s(%x):on attack" % (self.name, id(self)))
        pass

    def on_damaged(self, dg):
        """
        收到伤害dg
        """
        print("%s(%x):on damaged by %d" % (self.name, id(self),dg))
        pass

    def on_msg(self,orgin:'Unit',msgtype=MessageType.none):
        """
        获得消息并处理
        @param orgin:
        @param msgtype:
        @return:
        """
        print("%s(%x):on msg by %s(%x)" % (self.name, id(self), orgin.template.name,id(orgin)))

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
        super(MechKangaroo,self).on_deathrattle()
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
        super(MaleTiger,self).on_battlecry()
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


class RightnessProtector (TemplateUnit):
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
        super(FiendishServant,self).on_deathrattle()
        target=self.unit.field.get_random_unit(ignore_taunt=True, ignore_unit=self.unit)
        if target is not None:
            target.ad+=self.unit.ad#转移攻击力

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
        super(RockpoolHunter,self).on_battlecry()
        #给鱼人+1+1
        if self.unit.tarunit is None:
            return
        if self.unit.tarunit.template.utype is not UnitType.murloc:
            raise Exception("战吼目标应该是鱼人")
        else:
            self.unit.tarunit.ad+=1
            self.unit.tarunit.hp+=1





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
        super(TideHunter,self).on_battlecry()
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

    def on_msg(self,orgin:'Unit',msgtype=MessageType.none):
        super(TideCaller,self).on_msg(orgin,msgtype)
        if msgtype==MessageType.summon:
            if orgin.template.utype==UnitType.murloc:
                self.unit.ad+=1
















class Field:
    """
    场地
    随从需要场地，还需要表示他们的位置
    """

    def __init__(self, name):
        self.name = name
        self.lineup = []

    @property
    def num(self):
        return len(self.lineup)

    def print_info(self):
        # print("field name:%s" % self.name)
        # print("number of units:%d" % self.num)
        print("___%s(num:%d) detail info on units___________"%(self.name,self.num))
        for i, u in enumerate(self.lineup):
            print("%d->%s" % (i, u))
        print("___info  end ___________________________")

    def get_random_unit(self,ignore_taunt=False,ignore_unit:'Unit'=None)->'Unit':
        """

        @param ignore_taunt:
        @param ignore_unit:忽略的随从，通常是忽略自己
        @return:
        """
        if ignore_taunt:#若忽视嘲讽 选择全部随从
            pool=[x for x in self.lineup]
        else:
            pool=[x for x in self.lineup if x.taunt==True]
            if len(pool)==0:#如果没有嘲讽 选择全部随从
                pool=self.lineup

        if len(pool)==0:
            return None #没有随从 返回none
        if ignore_unit is not None and ignore_unit in pool:#排除忽略的随从
            pool.remove(ignore_unit)
        target=random.choice(pool)
        return target

    def broadcast_msg(self,orgin:'Unit',msgtype=MessageType.none):
        """
        给全体随从广播消息
        @param orgin: 发起人
        @param msgtype:
        @return:
        """
        for i in self.lineup:
            if i==orgin:
                continue#跳过自己
            i.template.on_msg(orgin,msgtype)


class Unit:
    """
    放到场上战斗的随从
    """

    def __init__(self, template: 'TemplateUnit', field: Field, fieldindex: int,stype:SummonType=SummonType.User,tarunit:'Unit'=None):
        """
        生成场上战斗随从
        @param template:模板的类 不是对象
        @param field:
        @param fieldindex:
        """
        self.field = field  # type:Field
        assert isinstance(template, type), "template必须为类名"
        self.template=template(self) #type:TemplateUnit

        self.hp, self.ad, self.shild, self.windfury, self.superwindfury, self.taunt = self.template.hp, self.template.ad, self.template.shild, self.template.windfury, self.template.superwindfury, self.template.taunt
        self.summon_type=stype
        self.tarunit=tarunit #战吼目标 默认为none
        self.field.lineup.insert(fieldindex, self)  # 场上添加自己

        if self.summon_type==SummonType.User:
            self.template.on_battlecry()#如果是打出的 触发战吼

        self.template.on_summon()#广播summon消息
        pass

    def on_damage(self, dg):
        """

        @param dg:
        @return:
        """
        if dg == 0:
            return  # 无伤害产生
        if self.shild:
            self.shild = False
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

    def attack_field(self,field:Field,ignore_taunt=False):
        """
        进攻场地
        @param field:
        @param ignore_taunt:随机选择进攻对手时，是否忽略对方嘲讽随从
        @return:
        """
        if field.num==0:
            raise Exception("对方场地无随从")
        assert self.field is not field, "不能进攻自己场地"

        #随机选择一个随从进攻
        target=field.get_random_unit(ignore_taunt)
        if target is None:
            raise Exception("场地%s无随从"%field.name)
        self.attack_unit(target)



    def on_death(self):

        self.template.on_deathrattle()  # 触发亡语
        self.field.lineup.remove(self)  # 从场上移除

    def __str__(self):
        return "%s(%x):%d hp with %d ad" % (self.template.name, id(self), self.hp, self.ad)

    @property
    def fieldid(self):
        #自己在field中的位置 基于0
        return self.field.lineup.index(self)

if __name__ == '__main__':
    filed_red = Field('red')
    field_blue = Field('blue')
    u1 = Unit(MechKangaroo, filed_red, 0)
    u2 = Unit(MaleTiger, field_blue, 0)
