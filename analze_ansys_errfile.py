"""
分析ansys错误文件 识别各个消息 统计各个消息类型
"""
from typing import List
import re

class Message:
    """
    ansys err文件中的一条消息
    将原生消息处理 分为：头 时间 描述
    """
    pattern_header =re.compile(r"\*\*\*.+\*\*\*")
    pattern_time=re.compile(r"TIME= \d+:\d+:\d+")

    def __init__(self,msg:str):
        r=Message.pattern_header.findall(msg)
        if len(r)==1:
            self.header=r[0][4:-4]
        else:
            raise Exception("无效的msg。无法识别头。")
        r = Message.pattern_time.search(msg)
        if r is not None:
            self.time=r.group(0)[6:]
        else:
            raise Exception("无效的msg。无法识别时间。")
        desciption=msg[r.span(0)[1]:]
        self.description=desciption.replace("\n","") #去除换行符



#已知消息类型
class InfoType:
    id_counter=0 #标识此infotype在known_infotype的位置
    def __init__(self,name:str,pattern:str,description:str):
        self.name=name
        self.pattern=pattern
        self.description=description
        self.id=InfoType.id_counter
        InfoType.id_counter+=1

known_infotype=[]
known_infotype.append(InfoType(name='ceintf warning 不重要',
                               pattern=r"Node\s+\d+\s+does\s+not\s+lie\s+on\s+or\s+near\s+the\s+selected\s+elements.\s+\s+The\s+CEINTF\s+operation\s+produced\s+no\s+results\s+for\s+this\s+node",
                               description="不重要"))
known_infotype.append(InfoType(name='divide by zero',
                               pattern=r"Attempt\s+to\s+divide\s+by\s+zero\s+in\s+parameter\s+expression",
                               description="除以0错误"))
known_infotype.append(InfoType(name='ceintf warning2 重要',
                               pattern=r"Constraint\s+equation\s+\d+\s+has\s+specified\s+degree\s+of\s+freedom\s+\(dof\)\s+constraint\s+at\s+all\s+nodes/dof.\s+Constraint\s+equation\s+deleted",
                               description="该ce指定了所有节点，ce被删除.这个错误必须要消除"))
known_infotype.append(InfoType(name='unkown msg',
                               pattern=r".+",
                               description="未知消息类型 patter是一定能匹配上 这个infotype一定要放在最后"))



def judge_info_type(msg:Message)->InfoType:
    for it in known_infotype:
        p=re.compile(it.pattern)
        r=p.search(msg.description)
        if r is not None:
            return it
    # return None #代表未知类型



def make_msg_array(path:str)->List[Message]:
    """
    通过文件 生成Message列表
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
    msg_array=[] #message列表
    for i in msg_array_raw:
        msg_array.append(Message(i)) #将消息str转化为message对象
    return msg_array

def classify_msg_array(ma:List[Message])->List[int]:
    """
    对message_array按infotype分类
    统计各个infotype出现的次数
    """
    info_type_stat = [0] * len(known_infotype)  # 统计各个infotype出现的次数
    for m in ma:
        t=judge_info_type(m)
        info_type_stat[t.id] += 1
        # 可以打印未知类型的消息
        if t.id == len(known_infotype) - 1:
            print(m.description)
    for i in range(len(known_infotype)):
        print("%s    :      %d"%(known_infotype[i].name,info_type_stat[i]))
    return info_type_stat

def compare_info_type_stat(old:List[int],new:List[int]):
    """
    比较消息infotype统计次数的编号
    """
    diff=list(map(lambda x:x[0]-x[1],zip(new,old)))
    print("差异如下：\n_______________________________________________")
    for i in range(len(known_infotype)):
        print("%s    :      %d"%(known_infotype[i].name,diff[i]))
    print("差异结束。\n_______________________________________________")
if __name__ == '__main__':
    t=make_msg_array(r"E:\ansys_work\1.err")
    t1=classify_msg_array(t)
    t = make_msg_array(r"E:\ansys_work\job.err")
    t2 = classify_msg_array(t)
    compare_info_type_stat(t1,t2)