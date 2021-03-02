from unittest import TestCase,main

from code2021.railway.route import make_route
from excel.excel import FlatDataModel
from vector3d import Vector3D


class Test(TestCase):
    def test_make_route(self):
        quxianbiao = FlatDataModel.load_from_excel_file(
            fullname=r"E:\我的文档\python\GoodToolPython\code2021\railway\测试文件\dk7-DK50.xlsx",
            sheetname='曲线表')
        duanlianbiao = FlatDataModel.load_from_excel_file(
            fullname=r"E:\我的文档\python\GoodToolPython\code2021\railway\测试文件\dk7-DK50.xlsx",
            sheetname='长短链表')
        route,sm,em = make_route(duanlianbiao=duanlianbiao, quxianbiao=quxianbiao)
        self.assertTrue(Vector3D(27098.416153, 27222.491174, 0.000000) == route.end_point)
        self.assertAlmostEqual(7900,sm.number,delta=0.00001)
        self.assertAlmostEqual(50500.000015,em.number,delta=0.000001)

if __name__ == '__main__':
    main()