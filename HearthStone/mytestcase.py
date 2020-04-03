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
# red whelp 1
# wrath waver 1
#二本怪
# unstable ghoul 1/3 taunt 亡语全场打1  √
#pogo hopper 1/1 mech √
#rat pack 2/2    √
#old mark eye 2/4  √
# zoobat 3/3 mech 给鱼人 野兽 龙 +1+1 对
#steward of time  3/4 龙 √
# murloc warleader 3/3 其他鱼+2 攻击力 勾
# imprisoner 3/3 taunt 亡语 恶魔   √
#kaboom bat 2/2 机械 造成4点伤害 勾
# nathrezim overseer 2/4 恶魔 +2+2
# waxrider togwaggle 1/2 无属性 龙
# kindly grandmother 1/1 野兽
# metaltooth leaper 3/3机械 +2
# spawn of Nzoth 2/2 无属性
# glyph guardian 2/4 龙 翻倍
# harvest golem 2/3 机械
# scavenging hyena 2/2 野兽 死亡+2+1
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
        self.assertEqual(1,u2.ad)
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

    def test11(self):  # 测试redwhelp
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(RightnessProtector, filed_red, 0)
        u2 = Unit(RedWhelp, field_blue, 0)
        self.assertEqual(1, u1.hp)
        self.assertEqual(True, u1.shield)
        field_blue.on_turn_start(filed_red)
        self.assertEqual(1, u1.hp)
        self.assertEqual(False, u1.shield)
        field_blue.on_turn_start(filed_red)
        self.assertEqual(0, filed_red.num)

        #两个redwhelp 喷死所有
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(MaleTiger, filed_red, 0)
        u2 = Unit(RedWhelp, field_blue, 0)
        u3 = Unit(RedWhelp, field_blue, 0)
        field_blue.on_turn_start(filed_red)
        self.assertEqual(0, filed_red.num)

        #两个redwhelp 喷死所有
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(DragonspawnLieutenant, filed_red, 0)
        u2 = Unit(RedWhelp, field_blue, 0)
        u3 = Unit(RedWhelp, field_blue, 0)
        field_blue.on_turn_start(filed_red)
        self.assertEqual(0, filed_red.num)


    def test12(self):  # 测试redwhelp
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = Unit(RightnessProtector, filed_red, 0)
        u2 = Unit(MicroMachine, field_blue, 0)
        self.assertEqual(1, u2.ad)
        field_blue.on_turn_start(filed_red)
        self.assertEqual(1, u2.ad)
        field_blue.on_turn_start('shop')
        self.assertEqual(2, u2.ad)
        field_blue.on_turn_start('shop')
        self.assertEqual(3, u2.ad)

    def test13(self):  # UnstableGhoul
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        # u1 = Unit(RightnessProtector, filed_red, 0)
        u1=filed_red.make_unit(RightnessProtector,0)
        # u2 = Unit(MaleTiger, filed_red, 0)
        u2=filed_red.make_unit(MaleTiger,0)
        # u3=Unit(TideHunter, filed_red, 0)
        u3=filed_red.make_unit(TideHunter,0)
        # u4=Unit(UnstableGhoul, field_blue, 0)
        u4=field_blue.make_unit(UnstableGhoul,0)
        # u5=Unit(RedWhelp, field_blue, 0)
        u5=field_blue.make_unit(RedWhelp,0)
        u4.on_death()
        self.assertEqual(1,filed_red.num)
        self.assertEqual(1, field_blue.num)
        self.assertEqual(1, u5.hp)

    def test14(self):  # pogohopper
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        # u1 = Unit(RightnessProtector, filed_red, 0)
        u1=filed_red.make_unit(RightnessProtector,0)
        print(PogoHopper.counteri)
        # u4 = Unit(PogoHopper, field_blue, 0)
        u4=field_blue.make_unit(PogoHopper,0)
        print(PogoHopper.counteri)
        self.assertEqual(1,u4.ad)
        u4 = field_blue.make_unit(PogoHopper, 0)
        print(PogoHopper.counteri)
        self.assertEqual(3,u4.ad)
        u4=field_blue.make_unit(PogoHopper,0)
        self.assertEqual(5,u4.ad)
        # u4 = Unit(PogoHopper, field_blue, 0,stype=SummonType.Card)
        u4 = field_blue.make_unit(PogoHopper, 0,stype=SummonType.Card)
        self.assertEqual(1,u4.ad)

    def test15(self):  # ratpack
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
         # Unit(RatPack, filed_red, 0)
        u1 =filed_red.make_unit(RatPack,0)
        u1.on_death()
        self.assertEqual(2,filed_red.num)


        setnum=8
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        # u1 = Unit(RatPack, filed_red, 0)
        u1=filed_red.make_unit(RatPack,0)
        u2 = field_blue.make_unit(SelflessHero, 0)
        u1.ad = setnum
        u2.ad=100
        u2.attack_field()

        self.assertEqual(7,filed_red.num)


    def test16(self):  # old mark eye
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
         # Unit(RatPack, filed_red, 0)
        u1 =filed_red.make_unit(OldMarkEye,0)
        u2=filed_red.make_unit(TideCaller,0)
        self.assertEqual(3,u1.ad)
        u2 = filed_red.make_unit(TideHunter, 0)
        self.assertEqual(5, u1.ad)
        u2.on_death()
        self.assertEqual(4, u1.ad)

    def test16(self):  # zoobat
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = filed_red.make_unit(OldMarkEye, 0)
        u2 = filed_red.make_unit(RedWhelp, 0)
        u3 = filed_red.make_unit(DireWolfAlpha, 0)
        u4 = filed_red.make_unit(Zoobat, 1)
        self.assertEqual(3,u1.ad)
        self.assertEqual(2, u2.ad)
        self.assertEqual(3, u3.hp)

        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1 = filed_red.make_unit(OldMarkEye, 0)
        u2 = filed_red.make_unit(RedWhelp, 0)
        u4 = filed_red.make_unit(Zoobat, 1)
        self.assertEqual(3,u1.ad)
        self.assertEqual(2, u2.ad)

        #缺少测试融合怪的

    def test17(self):  # murloc warleader
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1=filed_red.make_unit(MurlocWarleader,0)
        u2=filed_red.make_unit(TideCaller,0)
        self.assertEqual(3,u2.ad)
        u1.on_death()
        self.assertEqual(1, u2.ad)

    def test18(self):  # impriosoner
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1=filed_red.make_unit(Imprisoner,0)
        u2=field_blue.make_unit(RedWhelp,0)
        u2.ad=100
        u2.attack_unit(u1)
        for i in range(6):
            filed_red.make_unit(Imp, 0)
        self.assertEqual(7,filed_red.num)

    def test18(self):  # kaboom
        filed_red, field_blue = Field.make_twin_fields('red', 'blue')
        u1=filed_red.make_unit(KaboomBat,0)
        u11 = filed_red.make_unit(KaboomBat, 0)
        u2=field_blue.make_unit(RightnessProtector,0)
        u1.on_death()
        self.assertEqual(1,field_blue.num)
        u11.on_death()
        self.assertEqual(0,field_blue.num)
if __name__ == '__main__':
    unittest.main()
