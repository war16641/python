from unittest import TestCase,main
import os

from code2021.MyGeometric.algorithm import Algo1
from vector3d import Vector3D


class TestAlgo1(TestCase):
    def test_show(self):
        a = Algo1.load_from_datafile(os.path.join(os.getcwd()+"/测试文件/","1.txt"))
        r=a.solve(dist_func=Algo1.default_dist_func1,
                valve_func=Algo1.default_valve_func1)
        diff=Vector3D(1926.493087,1350.869350)-r.xy
        self.assertTrue(abs(diff)<0.1*a.sense_size)


if __name__ == '__main__':
    main()