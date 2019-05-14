from openpyxl import *
from openpyxl.cell.cell import Cell
from openpyxl.worksheet.worksheet import Worksheet
from typing import Union,Tuple,Sequence,overload,List
from GoodToolPython.mybaseclasses.tools import is_sequence_with_specified_type
from  GoodToolPython.mybaseclasses.todoexception import ToDoException
from copy import copy,deepcopy


@overload
class FlatDataModel:
    pass


class DataUnit:
    """
    数据单元 指一行
    """
    @staticmethod
    def make(vn:Sequence[str],row:Sequence[Cell],model:FlatDataModel):
        self=DataUnit()
        assert is_sequence_with_specified_type(row,Cell),'row必须是Cell组成的列表'
        assert is_sequence_with_specified_type(vn, str), 'vn必须是str组成的序列'
        assert isinstance(model,FlatDataModel),'model必须是FlatDataModel对象'
        assert len(vn)==len(row),'vn与row必须大小一致'
        self.data={} # type: Union[int,str,float]#以字典的形式保存所有变量
        for name,value in zip(vn,row):
            self.data[name]=value.value
        self.model=model#type:FlatDataModel   #保存模型
        return self

    def __init__(self,model=None):
        self.data={} # type: Union[int,str,float]#以字典的形式保存所有变量
        if model is not None:
            assert isinstance(model,FlatDataModel),'参数错误'
        self.model = model  # type:FlatDataModel   #保存模型

    def __len__(self):
        #返回变量的个数
        return len(self.data.keys())

    def __getitem__(self, item):
        if is_sequence_with_specified_type(item,str):
            #返回多个变量值
            r=[]
            for name in item:
                r.append(self.data[name])
            return r
        else:
            return self.data.__getitem__(item)

    def __iter__(self):
        #迭代器 依次返回该单元的所有变量值
        self.__iter_id=0
        return self

    def __next__(self):
        id=self.__iter_id
        if id == len(self):
            raise StopIteration
        self.__iter_id+=1
        return self.data[self.model.vn[id]]


class FlatDataModel:
    """
    平面数据模型 excel文件中的数据 一行代表一个数据单元
    所有的序号都是从0数起
    """

    @staticmethod
    def load_from_file(fullname, sheetname=None, row_variable_name=0, row_caption=None, row_data_start=None):
        self=FlatDataModel()
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
        self.vn = [cell.value for cell in rows[row_variable_name]]# type: List[str]
        assert is_sequence_with_specified_type(self.vn, str), '变量名读取失败'

        # 读注释行
        self.caption = []  # type:List[List[str]]
        if row_caption is not None:
            if isinstance(row_caption,int):
                row_caption=[row_caption]
            for row_id in row_caption:
                tmp=[cell.value for cell in rows[row_id]]
                self.caption.append(tmp)

        # 读数据
        self.units=[]# type:list[DataUnit]
        if row_data_start is None:
            if row_caption is None:
                row_data_start=row_variable_name+1
            else:
                row_data_start=row_caption[-1]+1
        for row in rows[row_data_start:]:
            unit = DataUnit.make(self.vn, row,self)
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
        self.vn=[]#type:list[str]
        self.units=[]#type:list[DataUnit]
        self.caption=[]#type:list[list[str]]

    def __len__(self):
        #返回units的个数
        return len(self.units)

    def __getitem__(self, item)->Union[DataUnit,List[DataUnit]]:
        #切片 返回对应的unit
        return self.units.__getitem__(item)

    def save(self,fullname,sheetname=None):
        #保存到excel文件中
        wb=Workbook()
        if sheetname is None:
            sheet=wb[wb.sheetnames[0]]#默认第一张簿
        else:
            #创建
            assert isinstance(sheetname,str),'sheetname类型必须为str'
            sheet=wb.create_sheet(sheetname)

        #写入标题行
        for col in range(1,1+len(self.vn)):
            sheet.cell(row=1,column=col).value=self.vn[col-1]

        row_rd=2
        col_rd=1#下一个可以写入的位置
        #写入注释行
        for rowin in self.caption:
            for cellin in rowin:
                sheet.cell(row=row_rd,column=col_rd).value=cellin
                col_rd+=1
            row_rd+=1
            col_rd=1

        #写入数据
        for unit in self:
            for v in unit:
                sheet.cell(row=row_rd,column=col_rd).value=v
                col_rd+=1
            row_rd += 1
            col_rd = 1

        #保存文件
        wb.save(fullname)

    def __iter__(self):
        #依次返回每一个unit
        return self.units.__iter__()

    def flhz(self,
             classify_names:Union[str,List[str]],
             statistics_func:dict,
             flag_write_statistics_func=False)->FlatDataModel:
        #参数预处理
        if isinstance(classify_names,str):
            classify_names=[classify_names]
        assert is_sequence_with_specified_type(classify_names,str),'is_sequence_with_specified_type参数错误'
        assert isinstance(statistics_func,dict),'statistics_func必须为字典'
        for s_name,func in statistics_func.items():
            assert s_name in self.vn,'键必须为变量名'
            assert callable(func),'值必须为函数'

        model_copy=deepcopy(self)#复制
        return_model=FlatDataModel()#返回值
        #把classify_names做成函数

        #排序
        model_copy.units.sort(key=lambda x:x[classify_names])

        #按classify_names分类
        current_classify_value=model_copy[0][classify_names]
        bunch=[]#type:list[DataUnit]
        bunchs=[]#type:list[list[DataUnit]]
        for unit in model_copy:
            this_classify_value=unit[classify_names]
            if this_classify_value ==current_classify_value:
                bunch.append(unit)
            else:
                bunchs.append(bunch)
                bunch=[unit]
                current_classify_value=this_classify_value

        #按变量名提取值
        for bunch in bunchs:
            #对每一个bunch进行提值 统计 生成一个单元
            unit=DataUnit(return_model)
            #添加classify变量
            for c_name in classify_names:
                unit.data[c_name]=bunch[0][c_name]
            #添加统计变量
            for s_name in statistics_func.keys():
                value_list=[x[s_name] for x in bunch]
                statistics_value=statistics_func[s_name](value_list)
                unit.data[s_name]=statistics_value
            return_model.units.append(unit)

        #处理vn
        return_model.vn=classify_names+list(statistics_func.keys())

        return_model.save('t1.xlsx')






if __name__ == '__main__':
    model=FlatDataModel.load_from_file(fullname="F:\我的文档\python_file\\14个人工波RP50和2000固定.xlsx",
                                       row_variable_name=1,
                                       row_caption=2)
    u=model[0]
    print(u['文件名','间距'])
    model.flhz(classify_names=['工况名','拉杆刚度'],
               statistics_func={'P1底剪力':max})



