from GoodToolPython.ocr.myknn import SampleManager
import unittest
class Test_SampleManage(unittest.TestCase):
    def test_init(self):
        t=SampleManager("D:\\knn_models\\knn_12")