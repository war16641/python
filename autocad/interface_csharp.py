import sys

from code2021.MyGeometric.algorithm import Algo1

if __name__ == '__main__':
    # a = Algo1.load_from_datafile(filepath=sys.argv[1],
    #                              ignore_lines=int(sys.argv[2]))
    # rt = a.solve(dist_func=Algo1.default_dist_func1,
    #              valve_func=Algo1.default_valve_func1)
    # v = rt.xy - a.target.xy
    try:
        a=Algo1.load_from_datafile(filepath=sys.argv[1],
                                   ignore_lines=int(sys.argv[2]))
        rt=a.solve(dist_func=Algo1.default_dist_func1,
                valve_func=Algo1.default_valve_func1)
        v=rt.xy-a.target.xy
        with open("d:/python_return.txt",'w') as f:
            f.write("success bool 1\n")
            f.write("ret vector %s\n"%v)

    except Exception:
        with open("d:/python_return.txt",'w') as f:
            f.writelines("success bool 0")
