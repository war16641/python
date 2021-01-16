import unittest
from unittest import TestCase

from autocad.about_tz import TZ_result, TZDiagnosisMethods


class TestTZ_result(TestCase):
    def test1(self):
        tz=TZ_result.load_from_file(r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38ZJ.RST")
        self.assertEqual(38,tz.No)
        self.assertEqual(17, tz.H)
        self.assertAlmostEqual(3420, tz.K,delta=1)
        self.assertAlmostEqual(3502., tz.caps[2].design, delta=1)
        self.assertAlmostEqual(4110., tz.caps[2].allowable, delta=1)
        self.assertAlmostEqual(1.17, tz.caps[2].safety_factor, delta=0.01)
        self.assertEqual("主力", tz.caps[0].casename)
        self.assertAlmostEqual(5.024, tz.strs[3].sigma_conc, delta=0.01)
        self.assertAlmostEqual(43.540, tz.strs[3].sigma_steel1, delta=0.01)
        self.assertAlmostEqual(26.841, tz.strs[3].sigma_steel2, delta=0.01)
        self.assertEqual("主力+横向地震力",tz.strs[3].casename)
        self.assertAlmostEqual(38.26, tz.soils[1].soil_stress, delta=0.01)
        self.assertAlmostEqual(230.98, tz.soils[1].allowable_stress, delta=0.01)
        self.assertAlmostEqual(1, tz.D, delta=0.01)
        pass

    # def test2(self):
    #     # tz = TZ_result.load_from_file(
    #     #     r"E:\我的文档\python\GoodToolPython\autocad\测试环境\19柱.RST")
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38ZJ.RST")
    #     tz.run_diagnosis([Diagnosis.check_capacity,
    #                       Diagnosis.check_K,
    #                       Diagnosis.check_soil,
    #                       Diagnosis.check_stress])
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.1ZJ.RST")
    #     funcs=[Diagnosis.check_capacity,
    #                       Diagnosis.check_K,
    #                       Diagnosis.check_soil,
    #                       Diagnosis.check_stress]
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("刚度不足",e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.2ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("承载力不足", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.3ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("承载力不足", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.4ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("承载力过小", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.5ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("承载力过大", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.6ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("砼应力超限", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.7ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("砼应力超限", e.brief)
    #
    #     tz = TZ_result.load_from_file(
    #         r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.8ZJ.RST")
    #     try:
    #         tz.run_diagnosis(funcs)
    #         self.fail("应当抛出错误")
    #     except TZDiagnosis as e:
    #         self.assertEqual("砼应力超限", e.brief)


    def test3(self):
        tzs=[]
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.1ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.2ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.3ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.4ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.5ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.6ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.7ZJ.RST")
        tzs.append(tz)
        tz = TZ_result.load_from_file(
            r"E:\我的文档\python\GoodToolPython\autocad\测试环境\38.8ZJ.RST")
        tzs.append(tz)

        fdm=TZ_result.run_TZDiagnosis_batch(tzs,[TZDiagnosisMethods.check_K,
                                                 TZDiagnosisMethods.check_capacity,
                                                 TZDiagnosisMethods.check_soil,
                                                 TZDiagnosisMethods.check_stress])
        self.assertEqual("刚度不足",fdm[1].data["刚度"])
        self.assertEqual("承载力不足", fdm[2].data["承载力"])
        self.assertEqual("承载力不足", fdm[3].data["承载力"])
        self.assertEqual("承载力过小", fdm[4].data["承载力"])
        self.assertEqual("承载力过大", fdm[5].data["承载力"])
        self.assertEqual("砼应力超限", fdm[6].data["砼和钢筋应力"])
        self.assertEqual("砼应力超限", fdm[7].data["砼和钢筋应力"])
        self.assertEqual("砼应力超限", fdm[8].data["砼和钢筋应力"])

if __name__ == '__main__':
    unittest.main()