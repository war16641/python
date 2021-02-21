from unittest import TestCase,main
import os
import matplotlib.pyplot as plt
from code2021.MyGeometric import algorithm
from code2021.MyGeometric.algorithm import Algo1
from mybaseclasses.mylogger import MyLogger
from vector3d import Vector3D
from code2021.MyGeometric.map import mylogger


class TestAlgo1(TestCase):
    def test_show(self):
        mylogger.setLevel("debug")
        a = Algo1.load_from_datafile(os.path.join(os.getcwd()+"/测试文件/","1.txt"))

        a.set_bk()
        # a.mm.show()
        # plt.show()
        r=a.solve(dist_func=Algo1.default_dist_func1,
                valve_func=Algo1.default_valve_func1)
        # print(r)
        diff=Vector3D(1924.023975,1353.127288)-r.xy
        # axes = a.show()
        # a.add_rect_to_axes(r, axes, color='b')
        # plt.show()
        self.assertTrue(abs(diff)<a.sense_size)

    def test_batch(self):
        # MyLogger.disable_all_logger = False
        MyLogger.only = algorithm.mylogger
        rts,_=Algo1.solve_batch_from_batch(filepath=os.path.join(os.getcwd()+"/测试文件/","2.txt"),delete_used_bk=True)
        self.assertTrue(abs(Vector3D(54.241140,-817.864460)-rts[0].xy)<1 or abs(Vector3D(51.952740,-817.864460)-rts[0].xy)<1)
        self.assertTrue(abs(Vector3D(86.524720,-816.092540) - rts[1].xy) < 1 or abs(Vector3D(85.609360,-817.465580) - rts[1].xy) < 1)
        self.assertTrue(abs(Vector3D(119.731240,-816.620540) - rts[2].xy) < 1 or abs(Vector3D(117.442840,-817.535900) - rts[2].xy) < 1)

if __name__ == '__main__':
    main()