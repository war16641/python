"""
将vector3d变转换为apoint
"""
from math import cos, sin, pi
from typing import Tuple

from pyautocad import APoint, Autocad
from vector3d import Vector3D, Line3D


def to_Apoint(p):
    return APoint(p.x,p.y,p.z)

def myaddarc(acad, center:Vector3D, sp:Vector3D, theta:float):
    """
    画圆弧
    这个方法不受坐标系变换的影响 而pyautocad自带的addarc则会受到坐标系旋转的影响
    @param acad:
    @param center: 圆心坐标
    @param sp: 第一个端点坐标
    @param theta: 弧线对应圆心角（逆时针为正）
    @return:

    """
    r_vec= sp - center
    radius=r_vec.modulus#半径
    theta1=Vector3D.calculate_angle_in_xoy(r_vec.x,r_vec.y)
    return acad.model.addarc(to_Apoint(center),radius,theta1,theta1+theta)


def get_basic_vectors(theta):
    """
    经常要用到旋转theta（逆时针）后的坐标系基向量
    @param theta:
    @return:
    """
    return (Vector3D(cos(theta),sin(theta),0),
            Vector3D(-sin(theta),cos(theta),0),
            Vector3D(0,0,1))

class MyRect:
    """
    仿照matplotlib patch 中rectangle的定义
    """
    def __init__(self,xy:Vector3D,
                 width,
                 height,
                 rotation=0.):
        """
        使用方法：输入的四个变量 是不能在初始化后更改的，经过在语法上可以更改。更改后导致许多衍生量计算不正确。
        @param xy: 左下角的点或者插入点
        @param width:
        @param height:
        @param rotation: 旋转角 逆时针为正
        """
        self.xy=xy
        self.width=width
        self.height=height
        self.rotation=rotation
        #只能读取的
        self._tf,self._tfi=get_trans_func(self.xy,self.rotation)#坐标系变换函数
        self._center=self._tfi(Vector3D(self.width/2.0,self.height/2.0))#中心坐标 在原坐标系中
        self._corners=(self._tfi(Vector3D(0,0)),
                       self._tfi(Vector3D(self.width,0)),
                       self._tfi(Vector3D(self.width,self.height)),
                       self._tfi(Vector3D(0,self.height)))#四个角点 原坐标系
        self._bound_corners=tuple(Vector3D.get_bound_corner(self._corners))#范围角点

    def __str__(self):
        return "插入点%f,%f 宽%f 高%f 旋转%f"%(self.xy.x,self.xy.y,self.width,self.height,self.rotation)

    @property
    def center(self):
        return self._center
    @property
    def corners(self):
        return self._corners
    @property
    def bound_corners(self)->Tuple[Vector3D,Vector3D]:
        return self._bound_corners
    def draw_in_cad(self,acad_doc):
        #在cad中绘制rect
        #先得到在rotation坐标系中的四个点
        p1=self.xy.get_coordinates_under_cartesian_coordinates_system(get_basic_vectors(self.rotation))
        p2=p1+Vector3D(self.width,0,0)
        p3=p2+Vector3D(0,self.height,0)
        p4=p1+Vector3D(0,self.height,0)
        #在放回到原坐标系
        P1=p1.get_coordinates_under_cartesian_coordinates_system(get_basic_vectors(-self.rotation))
        P2 = p2.get_coordinates_under_cartesian_coordinates_system(get_basic_vectors(-self.rotation))
        P3 = p3.get_coordinates_under_cartesian_coordinates_system(get_basic_vectors(-self.rotation))
        P4 = p4.get_coordinates_under_cartesian_coordinates_system(get_basic_vectors(-self.rotation))
        acad_doc.modelspace.addline(to_Apoint(P1),to_Apoint(P2))
        acad_doc.modelspace.addline(to_Apoint(P2), to_Apoint(P3))
        acad_doc.modelspace.addline(to_Apoint(P3), to_Apoint(P4))
        acad_doc.modelspace.addline(to_Apoint(P4), to_Apoint(P1))

    def __contains__(self, item,tol=0.0):
        """
        点在矩形内
        @param item:
        @param tol:误差
        @return:
        """
        assert isinstance(item,Vector3D)
        newp=self._tf(item)
        if -tol<=newp.x<=self.width+tol and -tol<=newp.y<=self.height+tol:
            return True
        else:
            return False

    def draw_in_axes(self,ax,color='b'):
        """
        在ax中汇出自己的矩形
        @param ax:
        @return:
        """
        t=list(self.corners)
        t.append(t[0])
        xs=[x.x for x in t]
        ys=[x.y for x in t]
        ax.plot(xs,ys,color+'-')

    @staticmethod
    def make_by_two_corners(v1:Vector3D,v2:Vector3D)->'MyRect':
        """

        @param v1:
        @param v2:
        @return:
        """
        return MyRect(xy=v1,
                      width=v2.x-v1.x,
                      height=v2.y-v1.y)

    def get_dist_from_rect(self,other:'MyRect'):
        assert isinstance(other,MyRect)
        #先处理x
        if self.bound_corners[0].x<other.bound_corners[0].x:#谁的起点在前面
            before=self
            after=other
        else:
            before=other
            after=self
        t=before.bound_corners[1].x-before.bound_corners[0].x-(after.bound_corners[0].x-before.bound_corners[0].x)
        if t<0:
            x_dist=-t
        else:
            x_dist=0#两者接壤或者相交
        #先处理y
        if self.bound_corners[0].y<other.bound_corners[0].y:#谁的起点在前面
            before=self
            after=other
        else:
            before=other
            after=self
        t=before.bound_corners[1].y-before.bound_corners[0].y-(after.bound_corners[0].y-before.bound_corners[0].y)
        if t<0:
            y_dist=-t
        else:
            y_dist=0#两者接壤或者相交

        return x_dist,y_dist

def make_myrect_from_obj(myobj)->MyRect:
    """
    从cad中的obj生成块或者单行文字 生成矩形框
    对于块而言，要求其插入点必须在左下侧，否则会有较大误差
    @param myobj:
    @return:
    """

    # assert 'BlockReference'.lower() in myobj.ObjectName.lower() or \
    #     'acdbtext' in myobj.ObjectName.lower(),'不支持的类型：%s'% myobj.ObjectName
    if not ('BlockReference'.lower() in myobj.ObjectName.lower() or \
        'acdbtext' in myobj.ObjectName.lower() or \
            'polyline' in myobj.ObjectName.lower()):
        raise TypeError('不支持的类型：%s'% myobj.ObjectName)
    print(myobj.ObjectName)
    myobj.leftdown = myobj.GetBoundingBox()[0]
    myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
    # print(myobj.leftdown)
    # print(myobj.rightup)
    # # print(myobj.TextString)
    # print(myobj.InsertionPoint)
    # print(myobj.rotation)
    if  'BlockReference'.lower() in myobj.ObjectName.lower() or \
        'acdbtext' in myobj.ObjectName.lower() :
        if myobj.rotation <= 1e-6:  # 等于0
            w = myobj.rightup[0] - myobj.leftdown[0]
            h = myobj.rightup[1] - myobj.leftdown[1]
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        elif myobj.rotation <= pi / 2:
            h = (myobj.insertionpoint[0] - myobj.leftdown[0]) / sin(myobj.rotation)
            w = (myobj.rightup[1] - myobj.leftdown[1] - h * cos(myobj.rotation)) / sin(myobj.rotation)
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        elif myobj.rotation < pi - 1e-6:  # 不知道为什么 在这个区间，算出的框在末端偏大
            alpha = myobj.rotation - pi / 2
            w = (myobj.rightup[1] - myobj.insertionpoint[1]) / cos(alpha)
            h = (myobj.insertionpoint[1] - myobj.leftdown[1]) / sin(alpha)
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        elif myobj.rotation < pi + 1e-6:  # 单独处理180°
            w = myobj.insertionpoint[0] - myobj.leftdown[0]
            h = myobj.insertionpoint[1] - myobj.leftdown[1]
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        elif myobj.rotation < 3 / 2 * pi:
            alpha = myobj.rotation - pi;
            h = (myobj.rightup[0] - myobj.insertionpoint[0]) / sin(alpha)
            w = (myobj.insertionpoint[1] - myobj.leftdown[1] - h * cos(alpha)) / sin(alpha)
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        else:  # 第四象限
            alpha = myobj.rotation - 3 / 2 * pi
            w = (myobj.insertionpoint[1] - myobj.leftdown[1]) / cos(alpha)
            h = (myobj.rightup[0] - myobj.leftdown[0] - w * sin(alpha)) / cos(alpha)
            mr = MyRect(xy=Vector3D(myobj.insertionpoint),
                        width=w,
                        height=h,
                        rotation=myobj.rotation)
            # mr.draw_in_cad(acad.doc)
        return mr
    elif  'polyline' in myobj.ObjectName.lower():
        if myobj.closed is False or myobj.getwidth(0)[0] < 0.19:  # 没有闭合 或者 没什么宽度的多段线 跳过
            raise TypeError('没有闭合的多段线无法生成rect')
        if len(myobj.Coordinates)==8 or len(myobj.Coordinates)==10 :#有四个点 看是否能能生成矩形
            p1=Vector3D(myobj.Coordinates[0],myobj.Coordinates[1])
            p2 = Vector3D(myobj.Coordinates[2], myobj.Coordinates[3])
            p3 = Vector3D(myobj.Coordinates[4], myobj.Coordinates[5])
            p4 = Vector3D(myobj.Coordinates[6], myobj.Coordinates[7])
            v1=p2-p1
            v2=p3-p2
            v3=p4-p3
            v4=p1-p4
            if Vector3D.is_parallel(v1,v3) and Vector3D.is_parallel(v2,v4):#平行
                mr=MyRect(xy=p1,
                          width=abs(v2),
                          height=abs(v1),
                          rotation=Vector3D.calculate_angle_in_xoy(v2.x,v2.y))
                return mr
            pass
        myobj.leftdown=Vector3D(myobj.leftdown)
        myobj.rightup = Vector3D(myobj.rightup)
        mr=MyRect.make_by_two_corners(myobj.leftdown,myobj.rightup)
        return mr



def get_trans_func(p:Vector3D=None,theta=0.0):
    """
    得到坐标系平移旋转后的坐标变化函数
    坐标变化
    仅支持平面内的变化 z恒=0
    @param p: 在原坐标系下的从原坐标系原点指向新坐标系原点的向量
    @param theta: 旋转角度 逆时针为正
    @return: 函数和逆函数
    """
    class transfunc:
        def __init__(self,p:Vector3D=None,theta=0.):
            if p is None:
                p=Vector3D(0,0,0)
            self.p=p
            self.theta=theta

        def calc(self,v):
            """

            @param v: 在原始坐标系下的坐标
            @return: 在新坐标系下坐标
            """

            return Vector3D(x=cos(self.theta)*v.x+sin(self.theta)*v.y-self.p.x*cos(self.theta)-self.p.y*sin(self.theta),
                            y=-sin(self.theta) * v.x + cos(self.theta) * v.y + self.p.x * sin(self.theta) - self.p.y * cos(self.theta))

        def calci(self,v):
            """
            逆变换
            @param v:
            @return:
            """
            return Vector3D(
                x=cos(self.theta) * v.x - sin(self.theta) * v.y + self.p.x ,
                y=sin(self.theta) * v.x + cos(self.theta) * v.y + self.p.y )

    t=transfunc(p=p,theta=theta)
    return t.calc,t.calci


def my_get_selection(acad,text="")->list:
    """
    重写 在cad中拾取对象的方法
    如果要连续使用这个方法，一定注意不能单次选取的对象太多否则会意外中止
    @param acad:
    @param text:
    @return: 对象的列表 已实现best interface
    """
    slt = acad.get_selection(text=text)
    lst=[]
    for i in range(slt.Count):
        try:
            lst.append(acad.best_interface(slt[i]))
        except:#如果没有接口，直接返回原始对象。在后续阶段使用这个对象可能会出错
            lst.append(slt[i])

    return lst


def haircut(myobj):
    """
    给原生的cad对象理发
    添加一些便于计算和操作的变量
    需分类型
    @param myobj:
    @return:
    """
    if 'acdbtext' in myobj.ObjectName.lower() or 'blockref' in myobj.ObjectName.lower():  # 文字 块参照
        myobj.leftdown = myobj.GetBoundingBox()[0]
        myobj.rightup = myobj.GetBoundingBox()[1]  # 两个角点
        myobj.leftdown = Vector3D(myobj.leftdown[0:2])
        myobj.rightup = Vector3D(myobj.rightup[0:2])
        myobj.centerpoint = (myobj.rightup + myobj.leftdown) * 0.5
        myobj.myrect = MyRect(xy=myobj.leftdown, width=myobj.rightup.x - myobj.leftdown.x,
                              height=myobj.rightup.y - myobj.leftdown.y)  # 生成对应myrect 不考虑旋转，以bouding生成rect
    elif 'acdbline' in myobj.ObjectName.lower():  # 直线
        myobj.p1 = Vector3D(myobj.startpoint[0:2])
        myobj.p2 = Vector3D(myobj.endpoint[0:2])  # 保留原坐标下的坐标
        myobj.centerpoint = (myobj.p1 + myobj.p2) / 2.0  # 中心点 原坐标系
        myobj.myline = Line3D.make_line_by_2_points(myobj.p1, myobj.p2)
        myobj.rotation = Vector3D.calculate_angle_in_xoy(myobj.myline.direction.x, myobj.myline.direction.y)
        myobj.tf, myobj.tfi = get_trans_func(
            theta=Vector3D.calculate_angle_in_xoy(myobj.myline.direction.x, myobj.myline.direction.y))
        # 计算自己的两个端点在这个坐标系下的坐标
        myobj.x1 = myobj.tf(myobj.p1)
        myobj.x2 = myobj.tf(myobj.p2)
    else:
        pass



def safe_prompt(acad,txt,maxtime=3):
    """
    允许3次 被呼叫方无应答
    @param acad:
    @param txt:
    @param maxtime:
    @return:
    """
    ct=0
    while True:
        try:
            ct+=1
            acad.prompt(txt)
            return
        except Exception as e:
            if ct==maxtime:
                raise e
            pass
if __name__ == '__main__':
    mr1=MyRect.make_by_two_corners(Vector3D(0,0),Vector3D(1,1))
    mr2 = MyRect.make_by_two_corners(Vector3D(1.5, 0.9), Vector3D(10, 10))
    print(mr1.get_dist_from_rect(mr2))