import unittest
from unittest import TestCase

from excel.railwayroute.mileage import Mileage


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


if __name__ == '__main__':
    unittest.main()