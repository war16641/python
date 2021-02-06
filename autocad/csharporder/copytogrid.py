import sys
from typing import List

from code2021.MyGeometric.basegeometric import BaseGeometric
from code2021.MyGeometric.entitytool import Entitytool
from code2021.mydataexchange import make_data_from_file
from vector3d import Vector3D




class CopyToGrid:
    """
    计算网格的节点
     网格由两组线定义
    """
    @staticmethod
    def copy_to_grid(paras1: List[BaseGeometric], paras2: List[BaseGeometric]) -> List[Vector3D]:
        rt = []
        for i1 in paras1:
            for i2 in paras2:
                t = Entitytool.intersection_point(i1, i2)
                t = t[0] if isinstance(t, list) else t
                if isinstance(t, Vector3D):
                    rt.append(t)
        return rt
    @staticmethod
    def load_from_file(filepath,ignore_lines=0):
        d = make_data_from_file(filepath, ignore_lines)
        paras1=[]
        paras2=[]
        for k,v in d.items():
            if k[0]=='A':
                paras1.append(v)
            elif k[0]=='B':
                paras2.append(v)
            else:
                raise Exception("错误的key %s"%k)
        rt=CopyToGrid.copy_to_grid(paras1,paras2)

        #写入
        with open(r"D:\python_return.txt", 'w') as f:
            f.write("success bool 1\n")
            f.write('nb float %d\n'%len(rt))
            for i,v in enumerate(rt):
                f.write("vct%d vector %s\n"%(i,v.__str__()))

if __name__ == '__main__':
    # MyLogger.disable_all_logger=True
    try:
        CopyToGrid.load_from_file(filepath=sys.argv[1],ignore_lines=int(sys.argv[2]))
    except Exception:
        with open("d:/python_return.txt",'w') as f:
            f.writelines("success bool 0")
