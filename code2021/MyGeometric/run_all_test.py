import unittest
import time

import os

from mybaseclasses.mylogger import MyLogger

case_path=os.path.dirname(r'E:\我的文档\python\GoodToolPython\code2021\MyGeometric')
# report_path=os.path.dirname(__file__)+"/unittest_case/unittest_log"

def all_case():
    discover=unittest.defaultTestLoader.discover(case_path,
                                                pattern='test_*.py',
                                                top_level_dir=None)
    return discover
if __name__=="__main__":
    MyLogger.disable_all_logger=True
    runner=unittest.TextTestRunner()
    runner.run(all_case())