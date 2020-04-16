"""
ansys利用get读取单元对节点的力 的和
接续 提取单元对节点的力.txt
"""
from excel.excel import FlatDataModel

def txt_func(u):
    """从unit生成每一行文本的方法"""
    st="%18.9e%18.9e%18.9e%18.9e%18.9e%18.9e%18.9e\n"%(u['node'],u['fx'],u['fy'],u['fz'],u['mx'],u['my'],u['mz'])
    return st

def get_element_force(fullname):
    #提取单元对节点的力.txt 生成的文件
    fdm=FlatDataModel.load_from_file(pathname=fullname,
                                     vn_style=['node','ele','fx','fy','fz','mx','my','mz'],
                                     separator=' ')
    #求和
    o = fdm.flhz("node", [["fx", lambda x: sum(x)], ["fy", lambda x: sum(x)],["fz", lambda x: sum(x)],
                            ["mx", lambda x: sum(x)], ["my", lambda x: sum(x)],["mz", lambda x: sum(x)]])
    #写入
    o.save_to_txt(r"C:\Users\niyinhao\Desktop\eforce2.txt",txt_func=txt_func)
if __name__ == '__main__':
    get_element_force()