"""
分析ansys错误文件 识别各个消息 统计各个消息类型
"""
from typing import List,Union
import re
import time
import hashlib

def get_re_expression(st: str):
    """
    通过字符串获得其re的pattern
    具体做法：去除两端空白
            将数字转化为\d+
            将空白字符转化为\s+
            . ( )前加\
    """
    st = st.strip()  # 去除两边空白
    p = re.compile("\d+")
    while True:  # 替换数字
        r = p.search(st)
        print(r)
        if r is not None:
            t = r.span()
            st = st[0:t[0]] + "\d+" + st[t[1]:]
        else:
            print(st)
            break

    p = re.compile("\s+")
    while True:  # 替换空白字符
        r = p.search(st)
        print(r)
        if r is not None:
            t = r.span()
            st = st[0:t[0]] + "\s+" + st[t[1]:]
        else:
            print(st)
            break

    # 替换点号
    st = st.replace(".", "\.")
    print(st)

    # 替换()
    st = st.replace("(", "\(")
    st = st.replace(")", "\)")
    print(st)
    return st



# 已知消息类型
class InfoType:
    id_counter = 0  # 标识此infotype在known_infotype的位置

    def __init__(self, name: str, pattern: str, description: str):
        self.name = name
        self.pattern = pattern
        self.description = description
        self.id = InfoType.id_counter
        InfoType.id_counter += 1


known_infotype = []
known_infotype.append(InfoType(name='ceintf warning 不重要',
                               pattern=r"Node\s+\d+\s+does\s+not\s+lie\s+on\s+or\s+near\s+the\s+selected\s+elements.\s+\s+The\s+CEINTF\s+operation\s+produced\s+no\s+results\s+for\s+this\s+node",
                               description="不重要"))
known_infotype.append(InfoType(name='divide by zero',
                               pattern=r"Attempt\s+to\s+divide\s+by\s+zero\s+in\s+parameter\s+expression",
                               description="除以0错误"))
known_infotype.append(InfoType(name='ceintf warning2 重要',
                               pattern=r"Constraint\s+equation\s+\d+\s+has\s+specified\s+degree\s+of\s+freedom\s+\(dof\)\s+constraint\s+at\s+all\s+nodes/dof.\s+Constraint\s+equation\s+deleted",
                               description="该ce指定了所有节点，ce被删除.这个错误必须要消除"))
known_infotype.append(InfoType(name='link180定义歧义',
                               pattern=r"Element\s+\d+\s+\(LINK180\)\s+accesses\s+both\s+real\s+constant\s+set\s+\d+\s+and\s+section\s+ID\s+\d+",
                               description="link180定义时同时指定了real constant和section ID，建议移除实常数"))
known_infotype.append(InfoType(name='ce方程中含未激活的自由度',
                               pattern=r"Term\s+\d+\s+\(node\s+\d+\s+ROT[XYZ]\)\s+on\s+CE\s+number\s+\d+\s+is\s+not\s+active\s+on\s+any\s+element\.\s+This\s+term\s+is\s+ignored\.",
                               description="大多数情况下由cerig命令产生，大多数情况下是转动自由度未激活"))
known_infotype.append(InfoType(name='ce方程中含未激活的自由度2',
                               pattern=r"The\s+first\s+term\s+of\s+constraint\s+equation\s+number\s+\d+\s+refers\s+to\s+degree\s+of\s+freedom\s+ROT[XYZ]\s+at\s+node\s+\d+\.\s+This\s+degree\s+of\s+freedom\s+is\s+not\s+active,\s+so\s+therefore,\s+this\s+constraint\s+equation\s+is\s+ignored\.",
                               description="大多数情况下由cerig命令产生，大多数情况下是转动自由度未激活"))

known_infotype.append(InfoType(name='combin14两个节点不重合',
                               pattern=r"Nodes\s+I\s+and\s+J\s+of\s+element\s+\d+\s+\(\s+COMBIN\d+\s+\)\s+are\s+not\s+coincident\.",
                               description="不重要"))
known_infotype.append(InfoType(name='有命令未执行 重要',
                               pattern=r"is\s+not\s+a\s+recognized\s+POST\d+\s+command,\s+abbreviation,\s+or\s+macro\.\s+This\s+command\s+will\s+be\s+ignored\.",
                               description="大多数情况下是未进入PREP7或SOL"))
known_infotype.append(InfoType(name='有组合未定义 重要',
                               pattern=r"Component\s+\S+\s+is\s+not\s+defined\.",
                               description="有组合未定义，但却引用了这个组合"))
known_infotype.append(InfoType(name='系数比例异常 不重要',
                               pattern=r"Coefficient\s+ratio\s+exceeds\s+\d+\.\d+e\d+\s+-\s+Check\s+results\.",
                               description="刚度矩阵主对角元素相差过大，导致数值计算不准。这个没办法解决，忽略"))
known_infotype.append(InfoType(name='单元形状畸形  不重要',
                               pattern=r"Previous\s+testing\s+revealed\s+that\s+\d+\s+of\s+the\s+\d+\s+selected\s+elements\s+violate\s+shape\s+warning\s+limits\.\s+To\s+review\s+warning\s+messages,\s+please\s+see\s+the\s+output\s+or\s+error\s+file,\s+or\s+issue\s+the\s+CHECK\s+command\.",
                               description="单元形状畸形 畸形比例小于5%可以忽略"))

# 下面这个infotype一定要放到最后
known_infotype.append(InfoType(name='unkown msg',
                               pattern=r".+",
                               description="未知消息类型 patter是一定能匹配上 这个infotype一定要放在最后"))

#
# def judge_info_type(msg: Message) -> InfoType:
#     for it in known_infotype:
#         p = re.compile(it.pattern)
#         r = p.search(msg.description)
#         if r is not None:
#             msg.infotype_id=it
#             return it
#     # return None #代表未知类型
#
#
# def make_msg_array(path: str) -> List[Message]:
#     """
#     通过文件 生成Message列表
#     """
#     pattern = re.compile(r"\*\*\*.+\*\*\*")  # 查找数字
#     msg = ""
#     rcd_flag = 0
#     msg_array_raw = []  # 分隔好的单个消息str 放入这个数组中
#     with open(path) as f:
#         for line in f:
#             result = pattern.findall(line)
#             if len(result) != 0:  # 有头
#                 if len(msg) != 0:
#                     msg_array_raw.append(msg)
#                     msg = ""
#                 msg += line
#                 if rcd_flag == 0:
#                     rcd_flag = 1
#
#             else:  # 没有头
#                 if rcd_flag == 1:
#                     msg += line
#     msg_array_raw.append(msg)
#     msg_array = []  # message列表
#     for i in msg_array_raw:
#         msg_array.append(Message(i))  # 将消息str转化为message对象
#     return msg_array
#
#
# def print_info_type_stat(info_type_stat:List[int]):
#     """
#     打印类型统计信息
#
#     """
#     for i in range(len(known_infotype)):
#         print("\t%s:\t\t%d" % (known_infotype[i].name, info_type_stat[i]))
#
# def classify_msg_array(ma: List[Message],print_flag=True) -> List[int]:
#     """
#     对message_array按infotype分类
#     统计各个infotype出现的次数
#     """
#     info_type_stat = [0] * len(known_infotype)  # 统计各个infotype出现的次数
#     for m in ma:
#         t = judge_info_type(m)
#         info_type_stat[t.id] += 1
#         # 可以打印未知类型的消息
#         if t.id == len(known_infotype) - 1:
#             print(m.description)
#     if print_flag is True:
#         print_info_type_stat(info_type_stat)
#     return info_type_stat


class Message:
    """
    ansys err文件中的一条消息
    将原生消息处理 分为：头 时间 描述
    """
    pattern_header = re.compile(r"\*\*\*.+\*\*\*")
    pattern_time = re.compile(r"TIME= \d+:\d+:\d+")

    def __init__(self, msg: str):
        r = Message.pattern_header.findall(msg)
        if len(r) == 1:
            self.header = r[0][4:-4]
        else:
            raise Exception("无效的msg。无法识别头。")
        r = Message.pattern_time.search(msg)
        if r is not None:
            self.time = r.group(0)[6:]
            self.time=time.strptime(self.time.strip(),"%H:%M:%S")
        else:
            raise Exception("无效的msg。无法识别时间。")
        desciption = msg[r.span(0)[1]:]
        self.description = desciption.replace("\n", "")  # 去除换行符
        self.infotype_id=0 #标识本msg的infotype索引 在judge_info_type赋值
        md5 = hashlib.md5()  # 用来标识msg的字段
        md5.update(self.description.encode("utf-8"))
        self.md5=md5.hexdigest() #用description的md5码作为消息的特征标识
        self.sequence=-1 #标识在AnsysErrorMessageManager.msg_array中位置


    def __eq__(self, other):
        """
        通过md5码判断相等
        @param other:
        @return:
        """
        if not isinstance(other,Message):
            return False
        if self.md5==other.md5:
            return True
        else:
            return False
class AnsysErrorMessageManager:

    def __init__(self,msg_array=None):
        self.msg_array=msg_array #type:List[Message] #存放所有消息
        self.unknown_msg_array=None #type:List[Message] #存放未识别消息
        self.info_type_stat=None #type:List[int] #存放类型统计信息
        self.msgs={} #key是md5码 value是msg

        self.refresh()

    def refresh(self):
        """
        重新分类消息类型 并整理未知消息
        """
        if self.msg_array is None:
            return
        self._classify_infotype()
        self._update_unknown_msg_array()
        self._make_dict()

    def _classify_infotype(self):
        """
        对message_array按infotype分类
        统计各个infotype出现的次数
        """
        def judge_info_type(msg: Message) -> InfoType:
            for it in known_infotype:
                p = re.compile(it.pattern)
                r = p.search(msg.description)
                if r is not None:
                    msg.infotype_id = it.id
                    return it
        info_type_stat = [0] * len(known_infotype)  # 统计各个infotype出现的次数
        for m in self.msg_array:
            t = judge_info_type(m)
            info_type_stat[t.id] += 1
            # 可以打印未知类型的消息
            # if t.id == len(known_infotype) - 1:
            #     print(m.description)
        self.info_type_stat= info_type_stat

    def _update_unknown_msg_array(self):
        """
        更新未识别消息
        """
        t = self.msg_array
        self.unknown_msg_array = list(filter(lambda x: x.infotype_id == len(known_infotype) - 1, t))

    def _make_dict(self):
        """
        通过msg_array生成字典
        """
        for i in self.msg_array:
            self.msgs[i.md5]=i

    def set_sequence(self):
        """
        设定msg.sequence
        @return:
        """
        for s,i in enumerate(self.msg_array):
            i.sequence=s

    def print_stat(self):
        """
        打印类型统计信息

        """
        if len(self.msg_array)==0:
            print("无消息。")
            return
        print("打印统计信息：\n_______________________________________________")
        for i in range(len(known_infotype)):
            print("\t%s:\t\t%d" % (known_infotype[i].name, self.info_type_stat[i]))
        print("_______________________________________________\n打印统计信息结束。")
    def print_unknown_msg(self):
        """
        打印未识别的消息
        """
        if len(self.msg_array)==0:
            print("无消息。")
            return
        print("打印未识别信息：\n_______________________________________________")
        for i in self.unknown_msg_array:
            print("%s" % (i.description))
        print("_______________________________________________\n打印未识别信息结束。")

    def print_msgs(self):
        """
        打印所有消息
        @return:
        """
        print("打印所有信息：\n_______________________________________________")
        for i in self.msg_array:
            print(i.description)
        print("_______________________________________________\n打印所有信息结束。")

    @staticmethod
    def load_from_file(path):
        pass
        """
        从文件中载入
        并分解为message
        """
        pattern = re.compile(r"\*\*\*.+\*\*\*")  # 查找数字
        msg = ""
        rcd_flag = 0
        msg_array_raw = []  # 分隔好的单个消息str 放入这个数组中
        with open(path) as f:
            for line in f:
                result = pattern.findall(line)
                if len(result) != 0:  # 有头
                    if len(msg) != 0:
                        msg_array_raw.append(msg)
                        msg = ""
                    msg += line
                    if rcd_flag == 0:
                        rcd_flag = 1

                else:  # 没有头
                    if rcd_flag == 1:
                        msg += line
        msg_array_raw.append(msg)

        msg_array = []  # message列表
        for i in msg_array_raw:
            msg_array.append(Message(i))  # 将消息str转化为message对象
        return AnsysErrorMessageManager(msg_array=msg_array)

    def __sub__(self, other):
        """
        定义减法
        返回self比other多出的消息
        @param other:
        @return:
        """
        if isinstance(other,AnsysErrorMessageManager):
            t=[self.msgs[x] for x in self.msgs.keys() if x not in other.msgs.keys()]
            return AnsysErrorMessageManager(t)
        else:
            raise Exception("参数类型错误。")


if __name__ == '__main__':
    t1=AnsysErrorMessageManager.load_from_file(r"E:\ansys_work\1.err")
    t2 = AnsysErrorMessageManager.load_from_file(r"E:\ansys_work\2.err")
    t1.print_msgs()
    t2.print_msgs()
    t=t2-t1
    t.print_msgs()
    # t1.print_msgs()
    # for x in t1.msgs.keys():
    #     print(t1.msgs[x].description)
    # t=AnsysErrorMessageManager(r"E:\sjgj_cst_g.err")
    # t.print_stat()
    # t.print_unknown_msg()
    # t = make_msg_array(r"E:\sjgj_cst_g.err")
    # t1 = classify_msg_array(t)
    # t = make_msg_array(r"E:\ansys_work\job.err")
    # t2 = classify_msg_array(t,False)
    # compare_info_type_stat(t1,t2)
    # compare_info_type_stat(r"E:\sjgj_cst_g.err", r"E:\ansys_work\job.err")
