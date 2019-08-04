import warnings
from copy import deepcopy
from typing import Union, Sequence, overload, List,Generic,TypeVar,Optional

import win32com
from openpyxl import *
from openpyxl.cell.cell import Cell
from win32com.client import constants as c  # 旨在直接使用VBA常数

from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type

# T_Model=TypeVar('T_Model')


# @overload
# class FlatDataModel:
#     pass


class DataUnit:
    """
    数据单元 指一行
    """

    @staticmethod
    def make(vn: Sequence[str], row: Sequence[Cell], model: 'FlatDataModel'):
        """
        这个函数用于从excel文件中生成数据单元
        :param vn:
        :param row:
        :param model:
        :return:
        """
        self = DataUnit()
        assert is_sequence_with_specified_type(row, Cell), 'row必须是Cell组成的列表'
        assert is_sequence_with_specified_type(vn, str), 'vn必须是str组成的序列'
        assert isinstance(model, FlatDataModel), 'model必须是FlatDataModel对象'
        assert len(vn) == len(row), 'vn与row必须大小一致'
        self.data = {}  # type: Union[int,str,float]#以字典的形式保存所有变量
        for name, value in zip(vn, row):
            self.data[name] = value.value
        self.model = model  # type:FlatDataModel   #保存模型
        return self

    def __init__(self, model=None):
        self.data = {}  # type: Union[int,str,float]#以字典的形式保存所有变量
        if model is not None:
            assert isinstance(model, FlatDataModel), '参数错误'
        self.model = model  # type:FlatDataModel   #保存模型

    def __len__(self):
        # 返回变量的个数
        return len(self.data.keys())

    def __getitem__(self, item):
        if is_sequence_with_specified_type(item, str):
            # 返回多个变量值
            r = []
            for name in item:
                r.append(self.data[name])
            return r
        else:
            return self.data.__getitem__(item)

    def __iter__(self):
        # 迭代器 依次返回该单元的所有变量值
        self.__iter_id = 0
        return self

    def __next__(self):
        id = self.__iter_id
        if id == len(self):
            raise StopIteration
        self.__iter_id += 1
        return self.data[self.model.vn[id]]


class FlatDataModel:
    """
    平面数据模型 excel文件中的数据 一行代表一个数据单元
    所有的序号都是从0数起
    """

    @staticmethod
    def load_from_list(vn_lst,data_lst)->'FlatDataModel':
        """
        从列表中生成
        :param vn_lst: 变量名列表
        :param data_lst: 数据列表 2维列表 每一个内层列表代表一个数据点
        :return:
        """
        assert is_sequence_with_specified_type(vn_lst,str),'必须为str列表'
        assert is_sequence_with_specified_type(data_lst,list),'必须为列表组成的列表'
        fdm=FlatDataModel()
        fdm.vn=vn_lst

        for row in data_lst:
            u = DataUnit(fdm)
            assert len(row)==len(vn_lst),'数据与变量个数必须一致'
            for nm,v in zip(vn_lst,row):
                u.data[nm]=v
            fdm.units.append(u)
        return fdm


    @staticmethod
    @overload
    def load_from_file(fullname)-> 'FlatDataModel':
        pass

    @staticmethod
    @overload
    def load_from_file(fullname,
                       sheetname:str=None,
                       row_variable_name:int=0,
                       row_caption:List[int]=None,
                       row_data_start:int=None)-> 'FlatDataModel':
        pass

    @staticmethod
    def load_from_file(fullname, sheetname=None, row_variable_name=0, row_caption=None,
                       row_data_start=None) -> 'FlatDataModel':
        """
        从excel'文件中载入平面数据模型
        :param fullname:
        :param sheetname:
        :param row_variable_name: 变量名所在行 0-based
        :param row_caption: 注释行 可以是列表，代表多行注释 默认为空
        :param row_data_start: 数据起始行 默认为变量名行下一行
        :return:
        """
        self = FlatDataModel()
        workbook = load_workbook(fullname, data_only=True)
        assert len(workbook.sheetnames) > 0, '此表无工作簿'
        if sheetname is None:
            sheetname = workbook.sheetnames[0]  # 默认为第一个工作簿
        else:
            assert sheetname in workbook.sheetnames, '工作簿不存在'
        pass
        worksheet = workbook[sheetname]
        rows = list(worksheet.rows)  # 将工作簿中所有数据转化为以行为单位的列表

        # 读变量名
        self.vn = [cell.value for cell in rows[row_variable_name]]  # type: List[str]
        assert is_sequence_with_specified_type(self.vn, str), '变量名读取失败'

        # 读注释行
        self.caption = []  # type:List[List[str]]
        if row_caption is not None:
            if isinstance(row_caption, int):
                row_caption = [row_caption]
            for row_id in row_caption:
                tmp = [cell.value for cell in rows[row_id]]
                self.caption.append(tmp)

        # 读数据
        self.units = []  # type:list[DataUnit]
        if row_data_start is None:
            if row_caption is None:
                row_data_start = row_variable_name + 1
            else:
                row_data_start = row_caption[-1] + 1
        for row in rows[row_data_start:]:
            unit = DataUnit.make(self.vn, row, self)
            self.units.append(unit)
        return self

    # def __init__(self,fullname, sheetname=None, row_variable_name=0, row_caption=None, row_data_start=None):
    #     workbook = load_workbook(fullname, data_only=True)
    #     assert len(workbook.sheetnames) > 0, '此表无工作簿'
    #     if sheetname is None:
    #         sheetname = workbook.sheetnames[0]  # 默认为第一个工作簿
    #     else:
    #         assert sheetname in workbook.sheetnames, '工作簿不存在'
    #     pass
    #     worksheet = workbook[sheetname]
    #     rows = list(worksheet.rows)  # 将工作簿中所有数据转化为以行为单位的列表
    #
    #     # 读变量名
    #     self.vn = [cell.value for cell in rows[row_variable_name]]# type: List[str]
    #     assert is_sequence_with_specified_type(self.vn, str), '变量名读取失败'
    #
    #     # 读注释行
    #     self.caption = []  # type:List[List[str]]
    #     if row_caption is not None:
    #         if isinstance(row_caption,int):
    #             row_caption=[row_caption]
    #         for row_id in row_caption:
    #             tmp=[cell.value for cell in rows[row_id]]
    #             self.caption.append(tmp)
    #
    #     # 读数据
    #     self.units=[]# type:list[DataUnit]
    #     if row_data_start is None:
    #         if row_caption is None:
    #             row_data_start=row_variable_name+1
    #         else:
    #             row_data_start=row_caption[-1]+1
    #     for row in rows[row_data_start:]:
    #         unit = DataUnit(self.vn, row,self)
    #         self.units.append(unit)

    def __init__(self):
        self.vn = []  # type:list[str]
        self.units = []  # type:list[DataUnit]
        self.caption = []  # type:list[list[str]]

    def __len__(self):
        # 返回units的个数
        return len(self.units)

    def __getitem__(self, item) -> Union[DataUnit, List[DataUnit]]:
        """
        获取部分数据点（切片） 或者获取所有数据点的某个变量信息
        :param item:
        :return:
        """
        if isinstance(item,str):#获取所有数据点的某个变量信息
            assert item in self.vn,'该变量名不存在'
            r=[]
            for u in self:
                r.append(u[item])
            return r
        else:
            return self.units.__getitem__(item)

    def save(self, fullname, sheetname=None):
        # 保存到excel文件中
        wb = Workbook()
        self.__add_to_workbook(wb, 'Sheet')

        # 保存文件
        wb.save(fullname)

    def __iter__(self):
        # 依次返回每一个unit
        return self.units.__iter__()

    def flhz(self,
             classify_names: Union[str, List[str]],
             statistics_func: List[List],
             flag_write_statistics_func=False) -> 'FlatDataModel':
        """
        分类汇总
        :param classify_names:
        :param statistics_func: 列表组成的列表 二级嵌套列表 子列表形如[字段名,统计函数]或[字段名,统计函数,新字段名]
        :param flag_write_statistics_func:
        :return:
        """
        # 参数预处理
        if isinstance(classify_names, str):
            classify_names = [classify_names]
        assert is_sequence_with_specified_type(classify_names, str), 'is_sequence_with_specified_type参数错误'
        assert isinstance(statistics_func, list), 'statistics_func必须为list'
        for i, line in enumerate(statistics_func):
            assert isinstance(line, list) and \
                   line[0] in self.vn and \
                   callable(line[1]), 'statistics_func中的元素必须为[str,函数,str]或者[str,函数]'
            if len(line) == 2:
                line.append(line[0])
        # assert isinstance(statistics_func,dict),'statistics_func必须为字典'
        #
        # for s_name,val in statistics_func.items():
        #     assert s_name in self.vn,'键必须为变量名'
        #     if callable(val):
        #         # val=[val,s_name]
        #         statistics_func[s_name]=[val,s_name]
        #     else:
        #         assert isinstance(val,list) and callable(val[0]) and isinstance(val[1],str),'值必须为[函数,str]'

        model_copy = deepcopy(self)  # 复制
        return_model = FlatDataModel()  # 返回值
        # 把classify_names做成函数

        # 排序
        model_copy.units.sort(key=lambda x: x[classify_names])

        # 按classify_names分类
        current_classify_value = model_copy[0][classify_names]
        bunch = []  # type:list[DataUnit]
        bunchs = []  # type:list[list[DataUnit]]
        for unit in model_copy:
            this_classify_value = unit[classify_names]
            if this_classify_value == current_classify_value:
                bunch.append(unit)
            else:
                bunchs.append(bunch)
                bunch = [unit]
                current_classify_value = this_classify_value
        if len(bunch) != 0:
            bunchs.append(bunch)

        # 按变量名提取值
        for bunch in bunchs:
            # 对每一个bunch进行提值 统计 生成一个单元
            unit = DataUnit(return_model)
            # 添加classify变量
            for c_name in classify_names:
                unit.data[c_name] = bunch[0][c_name]
            # 添加统计变量
            for line in statistics_func:
                # for s_name in [x[0] for x in statistics_func]:
                s_name = line[0]
                func = line[1]
                newname = line[2]
                value_list = [x[s_name] for x in bunch]
                statistics_value = func(value_list)
                unit.data[newname] = statistics_value
            return_model.units.append(unit)

        # 处理vn
        return_model.vn = classify_names + [line[2] for line in statistics_func]

        return return_model

    def append_to_file(self, fullname, sheetname):
        workbook = load_workbook(fullname, data_only=True)
        self.__add_to_workbook(workbook, sheetname)
        workbook.save(fullname)

    def __add_to_workbook(self, wb, sheetname):
        """
        将自身以sheet的形式添加到wb中，
        :param wb:
        :return:
        """
        assert isinstance(wb, Workbook), 'wb为workbook对象'
        if sheetname in wb.sheetnames:
            # raise Exception("该工作簿已存在")
            warnings.warn('原有工作簿被删除')
            wb.remove(wb[sheetname])
            sheet = wb.create_sheet(sheetname)
        else:
            # 创建
            assert isinstance(sheetname, str), 'sheetname类型必须为str'
            sheet = wb.create_sheet(sheetname)

        # 写入标题行
        for col in range(1, 1 + len(self.vn)):
            sheet.cell(row=1, column=col).value = self.vn[col - 1]

        row_rd = 2
        col_rd = 1  # 下一个可以写入的位置
        # 写入注释行
        for rowin in self.caption:
            for cellin in rowin:
                sheet.cell(row=row_rd, column=col_rd).value = cellin
                col_rd += 1
            row_rd += 1
            col_rd = 1

        # 写入数据
        for unit in self:
            for v in unit:
                sheet.cell(row=row_rd, column=col_rd).value = v
                col_rd += 1
            row_rd += 1
            col_rd = 1

    def add_variables_from_other_model(self,
                                       other: 'FlatDataModel',
                                       link_variable: str,
                                       add_variable: Union[str, List[str]] = None) -> None:
        # 参数处理
        assert isinstance(other, FlatDataModel), 'other必须为FlatDataModel对象'
        assert isinstance(link_variable, str) and \
               link_variable in self.vn and \
               link_variable in other.vn, \
            'link_variable必须是两个模型中均存在的变量名'
        if add_variable is None:
            # 默认添加全部, 除了连接变量
            add_variable = [x for x in other.vn if x != link_variable]
        elif isinstance(add_variable, str):
            add_variable = [add_variable]
        else:
            assert is_sequence_with_specified_type(add_variable, str), 'add_variable为字符串列表'

        # 开始添加
        for unit in self:
            link_variable_value = unit[link_variable]
            expr = lambda x: x[link_variable].__eq__(link_variable_value)
            cor_unit = other.find(expr)  # 找到此模型的unit对应的在另外一个unit
            if cor_unit is None:  # 没找到
                raise Exception("另外一个模型中未找到对应的unit")
            for name in add_variable:
                unit.data[name] = cor_unit[name]

        # 处理数变量名
        self.vn += add_variable

    def find(self, epxr, flag_find_all=False) -> Union[DataUnit, List[DataUnit]]:
        """
        查找满足epxr的unit
        :param epxr: 真假判断函数
        :param flag_find_all: 是否查找全部
        :return: 找不到的时候 返回None
        """
        assert callable(epxr), 'expr必须为函数'
        r = []
        for unit in self:
            if epxr(unit) is True:
                if flag_find_all is False:
                    return unit
                else:
                    r.append(unit)
        if flag_find_all is False:
            return None
        else:
            return r

    def show_in_excel(self):
        """
        在excel中显示 此方法不会阻塞
        :return:
        """
        xl_app = win32com.client.gencache.EnsureDispatch("Excel.Application")  # 若想引用常数的话使用此法调用Excel
        xl_app.Visible = False  # 是否显示Excel文件
        wb = xl_app.Workbooks.Add()
        sht = wb.Worksheets(1)
        row_rd, col_rd = 1, 1  # 记录下一个写入的位置
        for name in self.vn:
            sht.Cells(row_rd, col_rd).Value = name
            col_rd += 1
        row_rd = 2
        col_rd = 1
        for rowin in self.caption:
            for cellin in rowin:
                sht.Cells(row_rd, col_rd).Value = cellin
                col_rd += 1
            row_rd += 1
            col_rd = 1
        for unit in self:
            for v in unit:
                sht.Cells(row_rd, col_rd).Value = v
                col_rd += 1
            row_rd += 1
            col_rd = 1
        xl_app.Visible = True

    def __str__(self):
        s1='%d个变量'%len(self.vn)
        s2=self.vn.__str__()
        s3='%d个数据单元'%len(self.units)
        return "%s\n%s\n%s"%(s1,s2,s3)

def test_load_from_list():
    vnlst=['姓名','性别','年龄']
    datalst=[['迈克尔','男',1],['丹妮','女',3]]
    fdm=FlatDataModel.load_from_list(vnlst,datalst)
    print(fdm)
    assert len(fdm.units)==2
    assert len(fdm.vn)==3
    assert fdm.units[0]['年龄']==1
    assert fdm.units[1]['性别']=='女'
if __name__ == '__main__':
    test_load_from_list()
    # fullname = "test1.xlsx"
    # # fullname1 = "D:\新建 Microsoft Excel 工作表.xlsx"
    # model = FlatDataModel.load_from_file(fullname=fullname)
    # u = model[0]
    # print(u['文件名', '间距'])
    # print(model)
    # print(model['文件名'])


    # model.flhz(classify_names=['工况名','拉杆刚度'],
    #            statistics_func=[['P1底剪力',max,'p1底剪力'],
    #                             ['P1底剪力',len,'个数']])
    # model.flhz(classify_names=['工况名','拉杆刚度'],
    #            statistics_func=[['P1底剪力',max],
    #                             ]).append_to_file(fullname,'flhz')
