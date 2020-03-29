import unittest
from GoodToolPython.HearthStone.unit import *

#rockpool hunter
#vulgar homunculus 爱猎魔
#tidehunter
#tidecaller
#micro machine
#fiendish servant
#dire wolf alpha
#selfless hero
#rightness protector
#dragonspawn lieutenant
#red whelp
#wrath waver
class MyTestCase(unittest.TestCase):
    def test1(self):
        filed_red = Field('red')
        field_blue = Field('blue')
        u1 = Unit(MechKangaroo, filed_red, 0)
        u2 = Unit(MaleTiger, field_blue, 0)
        field_blue.print_info()
        filed_red.print_info()
        self.assertEqual(field_blue.num,2)
        self.assertEqual(filed_red.num, 1)

        #进攻
        u2.attack_field(filed_red)
        self.assertEqual(field_blue.num,1)
        self.assertEqual(filed_red.num, 1)

        #再次进攻
        u=random.choice(filed_red.lineup)
        u.attack_field(field_blue)
        self.assertEqual(field_blue.num,0)
        self.assertEqual(filed_red.num, 0)

if __name__ == '__main__':
    unittest.main()
