"""
把cad中object按组分
并设定新的组间距

"""


from pyautocad import Autocad,APoint

acad=Autocad(create_if_not_exists=True)
acad.prompt("Hello,Autocad from Python\n")
print (acad.doc.Name)

all_objs=[]
for text in acad.iter_objects():
    text.leftdown=text.GetBoundingBox()[0]
    text.rightup = text.GetBoundingBox()[1]#两个角点
    all_objs.append(text)

#按x坐标排序
all_objs.sort(key=lambda x:x.leftdown)

#开始分组
class MyGroup:
    def __init__(self):
        self.objects=[]
        self.max_x=None
        self.min_x=None
    def __str__(self):
        return "共%d个:%f->%f"%(len(self.objects),self.min_x,self.max_x)
groups=[] #type:list
max_x=all_objs[0].rightup[0]#当前组的最大x坐标
min_x=all_objs[0].leftdown[0]#当前组的最大x坐标
valve_x=5#超过这个值 被认为是下一组
cur_group=[]
while True:
    if len(all_objs)>0:
        cur_obj=all_objs[0]#取第一个
    else:
        if len(cur_group)!=0:
            mg = MyGroup()
            mg.objects = cur_group
            mg.max_x = max_x
            mg.min_x = min_x
            groups.append(mg)
        break

    if cur_obj.rightup[0]<max_x+valve_x:#同一组
        cur_group.append(cur_obj)
        all_objs.remove(cur_obj)
    else:
        mg=MyGroup()
        mg.objects=cur_group
        mg.max_x=max_x
        mg.min_x=min_x
        groups.append(mg)
        min_x=cur_obj.leftdown[0]
        cur_group=[cur_obj]#开始新的分组
        all_objs.remove(cur_obj)
    max_x = cur_obj.rightup[0] if cur_obj.rightup[0] > max_x else max_x  # 更新当前组最大x
    min_x = cur_obj.leftdown[0] if cur_obj.leftdown[0] < min_x else min_x  # 更新当前组最大x
pass

#开始移动
new_distance_x=3#新的间距
sum_x=0#后续的group位移会越来越大
for i,g in enumerate(groups):
    if i==0:
        continue
    this_x=g.min_x-new_distance_x-groups[i-1].max_x
    sum_x+=this_x
    p1=APoint(sum_x,0,0)
    p2=APoint(0,0,0)
    for o in g.objects:
        o.move(p1,p2)