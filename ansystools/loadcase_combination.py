
"""
利用两个excel表格 自动生成组合工况的ansys命令流
"""
from excel.excel import FlatDataModel

if __name__ == '__main__':
    fdm1=FlatDataModel.load_from_excel_file(fullname=r"E:\研究生\项目\进贤门\sjgj_cst工况表0508a.xlsx",
                                            sheetname='工况'
                                            )
    fdm2=FlatDataModel.load_from_excel_file(fullname=r"E:\研究生\项目\进贤门\sjgj_cst工况表0508a.xlsx",
                                            sheetname='工况组合'
                                            )
    print('/post1')

    for u in fdm2:
        print("!工况：%s"%u['组合名'])
        print('lczero')
        print('lcsel,none')
        if u['函数'] =='fromload':#直接从结果中定义
            lcnm=u['工况名']
            t=fdm1.find(lambda x: x['工况名'] == lcnm)
            assert t is not None, '%s工况不存在' % lcnm
            print('lcdef,%d,%d'%(u['lcnum'],t['lstep'])) #直接定义这个工况
        elif u['函数'] =='max':#最大
            st = u['工况名']
            lcnms = st.split(',')  # 用于求最大的各个工况名必须用逗号隔开
            scs=u['系数'].split(',')
            assert len(lcnms)==len(scs),'工况名与系数的个数不一致'
            for i, nm in enumerate(lcnms):
                t = fdm2.find(lambda x: x['组合名'] == nm)
                assert t is not None, '%s工况不存在' % nm
                print('lcsel,a,%d' % t['lcnum'])  # 加选工况
                print('lcfact,%d,%s' % (t['lcnum'],scs[i])) #设置系数

            print('lcoper,max,all')
            print('lcwrite,%d'%u['lcnum'])
        elif u['函数'] =='min':#最大
            st = u['工况名']
            lcnms = st.split(',')  # 用于求最大的各个工况名必须用逗号隔开
            scs = u['系数'].split(',')
            assert len(lcnms) == len(scs), '工况名与系数的个数不一致'
            for i, nm in enumerate(lcnms):
                t = fdm2.find(lambda x: x['组合名'] == nm)
                assert t is not None, '%s工况不存在' % nm
                print('lcsel,a,%d' % t['lcnum'])  # 加选工况
                print('lcfact,%d,%s' % (t['lcnum'],scs[i]))
            print('lcoper,min,all')
            print('lcwrite,%d'%u['lcnum'])

        elif u['函数'] =='add':#最大
            st = str(u['工况名'])
            lcnms = st.split(',')  # 用于求最大的各个工况名必须用逗号隔开
            st = str(u['系数']) #有时候系数是单个数字
            scs = st.split(',')
            for nm,sc in zip(lcnms,scs):
                t = fdm2.find(lambda x: x['组合名'] == nm)
                assert t is not None, '%s工况不存在' % nm
                print('lcsel,a,%d' % t['lcnum'])  # 加选工况
                print('lcfact,%d,%s' % (t['lcnum'], sc))
            print('lcoper,add,all')
            print('lcwrite,%d' % u['lcnum'])
        else:
            raise TypeError('数据错误')
        print('')
    #开始生成ansys命令


    # t = list(filter(lambda x: x['工况名'] == '人群1', fdm1))
    # print(t)
    pass