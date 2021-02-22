import unittest
from unittest import TestCase

from excel.excel import FlatDataModel
from excel.railwayroute.mileage import Mileage, ErrorMileage


class TestMileage(TestCase):
    def test1(self):
        guanhao,lc=Mileage.get_guanhao_and_mileage("d1k100+123.123")
        self.assertEqual("d1k",guanhao)
        self.assertEqual(lc,100*1000+123.123)

        guanhao, lc = Mileage.get_guanhao_and_mileage("DZ1k100+123.1")
        self.assertEqual("DZ1k", guanhao)
        self.assertEqual(lc, 100 * 1000 + 123.1)

        guanhao, lc = Mileage.get_guanhao_and_mileage("DZ1k100+123.")
        self.assertEqual("DZ1k", guanhao)
        self.assertEqual(lc, 100 * 1000 + 123.)

        guanhao, lc = Mileage.get_guanhao_and_mileage("DZ1k100+123")
        self.assertEqual("DZ1k", guanhao)
        self.assertEqual(lc, 100 * 1000 + 123.)

    def test2(self):

        guanhao, lc = Mileage.get_guanhao_and_mileage("DZ1k100")
        self.assertEqual("DZ1k", guanhao)
        self.assertEqual(lc, 100 * 1000 + 0.)

    def test3(self):

        m=Mileage("DZ1k100")
        m1=m+1
        self.assertEqual("DZ1k", m1.guanhao)
        self.assertEqual(100*1000+1, m1.number)

    def test4(self):
        string = """ID	等号左里程冠号	等号左里程数	等号右里程冠号	等号右里程数	断链长度
        0	DK	199500	DK	199500	0
        1	DK	236600	D1K	236600	0
        2	D1K	246000.3155	DK	248000	1999.6845
        3	DK	286259.754	DK	286259.754	0
        """
        fdm = FlatDataModel.load_from_string(stringtxt=string,
                                             vn_syle='fromstring',
                                             separator=' ')
        m = Mileage("DK200")
        m.duanlianbiao=fdm
        m1=m+100
        self.assertEqual(200 * 1000 + 100, m1.number)

        m1=m+36600
        self.assertEqual(236600, m1.number)
        self.assertEqual("DK", m1.guanhao)

        m1=m+36601
        self.assertEqual(236601, m1.number)
        self.assertEqual("D1K", m1.guanhao)

        m1=m+46000
        self.assertEqual(246000, m1.number)
        self.assertEqual("D1K", m1.guanhao)

        m1=m+46000+1
        self.assertEqual(248000+0.6845, m1.number)
        self.assertEqual("DK", m1.guanhao)

        m1=m+46000+1+100
        self.assertEqual(248000+0.6845+100, m1.number)
        self.assertEqual("DK", m1.guanhao)

        self.assertRaises(ErrorMileage,m.__add__,90000)

    def test5(self):
        string = """ID	等号左里程冠号	等号左里程数	等号右里程冠号	等号右里程数	断链长度
        0	DK	199500	DK	199500	0
        1	DK	236600	D1K	236600	0
        2	D1K	246000.3155	DK	248000	1999.6845
        3	DK	286259.754	DK	286259.754	0
        """
        fdm = FlatDataModel.load_from_string(stringtxt=string,
                                             vn_syle='fromstring',
                                             separator=' ')
        m = Mileage("DK200")
        m.duanlianbiao = fdm
        m1 = Mileage("DK201")
        m1.duanlianbiao = fdm
        # print(m1 > m)
        self.assertTrue(m1>m)
        m2 = Mileage("D1K237+800")
        m2.duanlianbiao = fdm
        # print(m2 > m)
        self.assertFalse(m2 < m)
        m3 = Mileage("D1K237+800")
        m3.duanlianbiao = fdm
        # print(m2 == m3)
        self.assertTrue(m2==m3)

    def test_sub(self):
        m = Mileage("DZ1k100")
        m1 = Mileage("DZ1k100+200.1")
        self.assertAlmostEqual(200.1,m1-m,delta=0.001)

        string = """ID	等号左里程冠号	等号左里程数	等号右里程冠号	等号右里程数	断链长度
        0	DK	199500	DK	199500	0
        1	DK	236600	D1K	236600	0
        2	D1K	246000.3155	DK	248000	1999.6845
        3	DK	286259.754	DK	286259.754	0
        """
        fdm = FlatDataModel.load_from_string(stringtxt=string,
                                             vn_syle='fromstring',
                                             separator=' ')
        m = Mileage("DK200")
        m.duanlianbiao = fdm
        m1 = Mileage("DK201")
        m1.duanlianbiao = fdm
        self.assertAlmostEqual(1000,m1-m,delta=0.1)

        m = Mileage("DK200+101")
        m.duanlianbiao = fdm
        m1 = Mileage("D1K240+001")
        m1.duanlianbiao = fdm
        self.assertAlmostEqual(240001-200101,m1-m,delta=0.1)

        m = Mileage("DK200+101")
        m.duanlianbiao = fdm
        m1 = Mileage("DK248+100")
        m1.duanlianbiao = fdm
        self.assertAlmostEqual(45999.3155,m1-m,delta=0.0001)
        self.assertAlmostEqual(-45999.3155, m - m1, delta=0.0001)

if __name__ == '__main__':
    unittest.main()