import unittest
from GoodToolPython.HearthStone.unit import *


# rockpool hunter 1
# vulgar homunculus 爱猎魔
# tidehunter 1
# tidecaller 1
# micro machine
# fiendish servant 1
# dire wolf alpha 1
# selfless hero 1
# rightness protector 1
# dragonspawn lieutenant 1
# red whelp
# wrath waver 1
class MyTestCase(unittest.TestCase):

    def test1(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(MaleTiger, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num, 2)
        self.assertEqual(filed_red.num, 1)

        # 进攻
        u2.attack_field(filed_red)
        self.assertEqual(field_blue.num, 1)
        self.assertEqual(filed_red.num, 1)

        # 再次进攻
        u = random.choice(filed_red.lineup)
        u.attack_field(field_blue)
        self.assertEqual(field_blue.num, 0)
        self.assertEqual(filed_red.num, 0)

    def test2(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(DragonspawnLieutenant, field_blue, 0)
        u3 = Unit(MaleTiger, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num, 3)
        self.assertEqual(filed_red.num, 1)

        # 进攻
        u1.attack_field(field_blue)
        self.assertEqual(field_blue.num, 3)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.hp, 2)

    def test3(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(RightnessProtector, field_blue, 0)
        u3 = Unit(MaleTiger, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num, 3)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.shield, True)

        # 进攻
        u1.attack_field(field_blue)
        self.assertEqual(field_blue.num, 3)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.hp, 1)
        self.assertEqual(u2.shield, False)

    def test4(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(RightnessProtector, field_blue, 0)
        u3 = Unit(FiendishServant, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num, 2)
        self.assertEqual(filed_red.num, 1)

        # 进攻
        u3.attack_field(filed_red)
        self.assertEqual(field_blue.num, 1)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.ad, 3)

    def test5(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u2 = Unit(RockpoolHunter, field_blue, 0, tarunit=None)
        u3 = Unit(RockpoolHunter, field_blue, 0, tarunit=u2)
        field_blue.print_info()
        self.assertEqual(field_blue.num, 2)
        self.assertEqual(u2.ad, 3)
        self.assertEqual(u2.hp, 4)
        self.assertEqual(u3.ad, 2)

    def test6(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u2 = Unit(TideCaller, field_blue, 0, tarunit=None)
        self.assertEqual(u2.ad, 1)
        u3 = Unit(RockpoolHunter, field_blue, 0, tarunit=None)
        self.assertEqual(u2.ad, 2)
        u4 = Unit(MechKangaroo, field_blue, 0, tarunit=None)
        self.assertEqual(u2.ad, 2)

    def test7(self):
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(RightnessProtector, field_blue, 0)
        u3 = Unit(FiendishServant, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num, 2)
        self.assertEqual(filed_red.num, 1)

        # 进攻
        u3.attack_field()
        self.assertEqual(field_blue.num, 1)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.ad, 3)

    def test8(self):
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(RightnessProtector, field_blue, 0)
        u3 = Unit(FiendishServant, field_blue, 0)
        u1 = Unit(SelflessHero, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(False, u3.shield)

        # 进攻
        u1.attack_field()
        self.assertEqual(True, u3.shield)

    def test9(self):  # 测试halo
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(RightnessProtector, field_blue, 0)
        u3 = Unit(FiendishServant, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(1, u2.ad)
        self.assertEqual(2, u3.ad)

        # 加入恐狼
        u4 = Unit(DireWolfAlpha, field_blue, 1)
        field_blue.print_info()
        self.assertEqual(2, u2.ad)
        self.assertEqual(3, u3.ad)

        # 移除恐狼
        u4.on_death()
        field_blue.print_info()
        self.assertEqual(1, u2.ad)
        self.assertEqual(2, u3.ad)

        # 加入恐狼
        u4 = Unit(DireWolfAlpha, field_blue, 1)
        field_blue.print_info()
        self.assertEqual(2, u2.ad)
        self.assertEqual(3, u3.ad)
        # 在中间插入新的随从
        u5 = Unit(MaleTiger, field_blue, 2)
        field_blue.print_info()
        self.assertEqual(1, u2.ad)
        self.assertEqual(3, u3.ad)
        self.assertEqual(2, u5.ad)
        # 再插入
        u6 = Unit(MaleTiger, field_blue, 1)
        field_blue.print_info()
        self.assertEqual(1, u2.ad)
        self.assertEqual(2, u3.ad)
        self.assertEqual(2, u5.ad)
        self.assertEqual(1, u6.ad)
        self.assertEqual(2, field_blue.lineup[2].ad)
        # 移除恐狼
        u4.on_death()
        field_blue.print_info()
        self.assertEqual(1, u2.ad)
        self.assertEqual(2, u3.ad)
        self.assertEqual(1, u5.ad)
        self.assertEqual(1, u6.ad)
        self.assertEqual(1, field_blue.lineup[2].ad)

    def test10(self):  # 测试wrathwaver
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(WrathWaver, field_blue, 0)
        self.assertEqual(1, u2.ad)
        self.assertEqual(1, u2.hp)
        Unit(SelflessHero, field_blue, 0)
        self.assertEqual(1, u2.ad)
        self.assertEqual(1, u2.hp)
        Unit(FiendishServant, field_blue, 0)
        self.assertEqual(3, u2.ad)
        self.assertEqual(3, u2.hp)


if __name__ == '__main__':
    unittest.main()
