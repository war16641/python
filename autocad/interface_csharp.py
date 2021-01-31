import sys

from code2021.MyGeometric import algorithm
from code2021.MyGeometric.algorithm import Algo1
from mybaseclasses.mylogger import MyLogger

def solve1(filepath,ignore_lines):
    a = Algo1.load_from_datafile(filepath=filepath,
                                 ignore_lines=ignore_lines)
    a.set_bk()
    rt = a.solve(dist_func=Algo1.default_dist_func1,
                 valve_func=Algo1.default_valve_func1)
    v = rt.xy - a.target.xy
    with open("d:/python_return.txt", 'w') as f:
        f.write("success bool 1\n")
        f.write("ret vector %s\n" % v)

def solve_batch(filepath,ignore_lines):
    MyLogger.disable_all_logger = False
    MyLogger.only = algorithm.mylogger
    #目地点
    des,ori=Algo1.solve_batch_from_batch(filepath=filepath,
                              ignore_lines=ignore_lines,
                                         delete_used_bk=True)
    #计算差值
    rt=[]
    for d,o in zip(des,ori):
        rt.append(d.xy-o.xy)
    with open("d:/python_return.txt", 'w') as f:
        f.write("success bool 1\n")
        for i,v in enumerate(rt):
            f.write("ret%d vector %s\n" % (i,v))

if __name__ == '__main__':
    # a = Algo1.load_from_datafile(filepath=sys.argv[1],
    #                              ignore_lines=int(sys.argv[2]))
    # rt = a.solve(dist_func=Algo1.default_dist_func1,
    #              valve_func=Algo1.default_valve_func1)
    # v = rt.xy - a.target.xy
    MyLogger.disable_all_logger=True
    try:
        if "single"==sys.argv[1]:
            solve1(filepath=sys.argv[2],
                   ignore_lines=int(sys.argv[3]))
        elif "batch"==sys.argv[1]:
            solve_batch(filepath=sys.argv[2],
                   ignore_lines=int(sys.argv[3]))
        else:
            raise Exception("未知参数")
    except Exception:
        with open("d:/python_return.txt",'w') as f:
            f.writelines("success bool 0")
