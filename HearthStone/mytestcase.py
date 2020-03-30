import unittest
from GoodToolPython.HearthStone.unit import *


# rockpool hunter 1
# vulgar homunculus 爱猎魔
# tidehunter 1
# tidecaller
# micro machine
# fiendish servant 1
# dire wolf alpha
# selfless hero
# rightness protector 1
# dragonspawn lieutenant 1
# red whelp
# wrath waver
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
        self.assertEqual(u2.shild, True)

        # 进攻
        u1.attack_field(field_blue)
        self.assertEqual(field_blue.num, 3)
        self.assertEqual(filed_red.num, 1)
        self.assertEqual(u2.hp, 1)
        self.assertEqual(u2.shild, False)

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


if __name__ == '__main__':
    unittest.main()
