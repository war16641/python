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


class TemplateUnit:
    """
    随从模板的基函数
    """

    def __init__(self, name: str, unit: 'Unit', hp, ad, shild=False, windfury=False, superwindfury=False, taunt=False,
                 utype=UnitType.none):
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
        self.unit = unit  # 模板需要挂一个随从

    def on_battlecry(self):
        print("%s(%x):on battlecry"%(self.name,id(self)))
        pass

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
        Unit(MechKangarooSon, self.unit.filed, self.unit.fieldindex)  # 召唤儿子


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
        Unit(FemaleTiger, self.unit.filed, self.unit.fieldindex + 1)  # 召唤母的


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
        print("field name:%s" % self.name)
        print("number of units:%d" % self.num)
        print("___detail info on units___________")
        for i, u in enumerate(self.lineup):
            print("%d->%s" % (i, u))
        print("___info  end _____________________")


class Unit:
    """
    放到场上战斗的随从
    """

    def __init__(self, template: 'TemplateUnit', field: Field, fieldindex: int):
        """
        生成场上战斗随从
        @param template:模板的类 不是对象
        @param field:
        @param fieldindex:
        """
        assert isinstance(template, type), "template必须为类名"
        self.template, self.filed, self.fieldindex = template(self), field, fieldindex
        self.hp, self.ad, self.shild, self.windfury, self.superwindfury, self.taunt = self.template.hp, self.template.ad, self.template.shild, self.template.windfury, self.template.superwindfury, self.template.taunt
        self.filed.lineup.insert(fieldindex, self)  # 场上添加自己
        self.template.on_battlecry()
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

    def attack_field(self,field:Field):
        """
        进攻场地
        @param field:
        @return:
        """
        if field.num==0:
            raise Exception("对方场地无随从")
        assert self.filed is not field,"不能进攻自己场地"

        #随机选择一个随从进攻
        target=random.choice(field.lineup)
        self.attack_unit(target)



    def on_death(self):
        self.filed.lineup.remove(self)  # 从场上移除
        self.template.on_deathrattle()  # 触发亡语

    def __str__(self):
        return "%s(%x):%d hp with %d ad" % (self.template.name, id(self), self.hp, self.ad)


if __name__ == '__main__':
    filed_red = Field('red')
    field_blue = Field('blue')
    u1 = Unit(MechKangaroo, filed_red, 0)
    u2 = Unit(MaleTiger, field_blue, 0)
