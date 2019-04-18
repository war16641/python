from GoodToolPython.vector3d import Vector3D,Line3D,T_Vector
from GoodToolPython.tree import *
from enum import Enum, unique
from enum import Enum, unique
import operator
import os
class SpecialPoint:
    """带有特殊花费的点 非特殊点的花费均为1
    模拟可以通过的障碍 但需要比一般格子更高的花费"""
    def __init__(self,vecotr:T_Vector,cost=1):
        assert isinstance(vecotr,Vector3D)
        self.vector=vecotr
        self.cost=cost
class RectMap:
    """
    带障碍的方块地图
    """
    @unique
    class PointPosition(Enum):#任意点与map的关系 严格互斥
        ValidPoint=0#不属于obstacle的内部点
        OutPoint=1#外部点
        Obstacle=2#障碍点
    def __init__(self, W:int, H:int, special_points:list=[],obstacles=[]):
        """

        :param W:
        :param H: 宽高 取值是0~W-1\H-1
        :param special_points: list of MapPoint
        """
        assert isinstance(special_points, list)
        self.Width=W
        self.Height=H
        self.obstacles=obstacles
        self.special_points=special_points
        self.topline=Line3D(direction=Vector3D(1,0,0),point=Vector3D())#四条边线
        self.bottomline = Line3D(direction=Vector3D(1,0, 0), point=Vector3D(0,H-1,0))
        self.rightline=Line3D(direction=Vector3D(0,1, 0), point=Vector3D(W-1,0,0))
        self.leftline = Line3D(direction=Vector3D(0, 1, 0), point=Vector3D(0, 0, 0))
        self.top_left_point=Vector3D(0,0)#四个角点 使用gui的坐标系系统
        self.top_right_point=Vector3D(W-1,0)
        self.bottom_left_point=Vector3D(0,H-1)
        self.bottom_right_point=Vector3D(W-1,H-1)
    def get_neighbors_obstacles_ignored(self,nd:T_Vector)->list:
        #获取所有的可用的相邻节点 忽略obstacles的限制：认为obstacle也可以通行
        assert isinstance(nd, Vector3D)
        #先判断是不是有效点
        if self.judge_point_postion(nd) is not self.PointPosition.ValidPoint:
            return []#不是有效点时返回空列表
        # 先判断是不是角点
        if nd == self.top_left_point:
            return [Vector3D(1, 0), Vector3D(0, 1)]
        elif nd == self.top_right_point:
            return [Vector3D(self.Width - 1, 1), Vector3D(self.Width - 2, 0)]
        elif nd == self.bottom_left_point:
            return [Vector3D(1, self.Height - 1), Vector3D(0, self.Height - 2)]
        elif nd == self.bottom_right_point:
            return [Vector3D(self.Width - 2, self.Height - 1), Vector3D(self.Width - 1, self.Height - 2)]

        # 在判断是不是边线点
        if nd in self.topline:
            return [nd + Vector3D(1, 0),
                    nd + Vector3D(-1, 0),
                    nd + Vector3D(0, 1)]
        elif nd in self.bottomline:
            return [nd + Vector3D(1, 0),
                    nd + Vector3D(-1, 0),
                    nd + Vector3D(0, -1)]
        elif nd in self.leftline:
            return [nd + Vector3D(1, 0),
                    nd + Vector3D(0, -1),
                    nd + Vector3D(0, 1)]
        elif nd in self.rightline:
            return [nd + Vector3D(-1, 0),
                    nd + Vector3D(0, -1),
                    nd + Vector3D(0, 1)]
        # 在内部
        return [nd + Vector3D(-1, 0),
                nd + Vector3D(1, 0),
                nd + Vector3D(0, 1),
                nd + Vector3D(0, -1)]
    def get_neighbors(self,nd:T_Vector)->list:
        #获取所有的可用的相邻节点
        assert isinstance(nd,Vector3D)
        lst=self.get_neighbors_obstacles_ignored(nd)#忽略obstacle 选取可能的节点
        return [x for x in lst if x not in self.obstacles]#删除掉obstacle中的点

    def judge_point_postion(self,pt:T_Vector)->PointPosition:
        #判断点与map位置关系
        assert isinstance(pt,Vector3D)
        if pt.x<0 or pt.x>self.Width-1 or pt.y <0 or pt.y>self.Height-1:#是不是外部点
            return self.PointPosition.OutPoint
        if pt in self.obstacles:#判断是不是障碍点
            return self.PointPosition.Obstacle
        return self.PointPosition.ValidPoint

    # def __is_point_on_map(self,pt:T_Vector)->bool:
    #     #判断点是不是在地图上
    #     if self.judge_point_postion(pt) is in (self.PointPosition.InnerPoint,self.PointPosition.ob)

    def get_cost(self,pt:T_Vector)->float:
        #从相邻点走到这一点的花费
        assert isinstance(pt,Vector3D)
        assert self.judge_point_postion(pt) is self.PointPosition.ValidPoint#必须是有效点
        for x in self.special_points:
            if x.vector==pt:
                return x.cost
        return 1


def A_star_search_algorithm(map,start,goal):
    """
    a星寻路算法：https://en.wikipedia.org/wiki/A*_search_algorithm
    :param map:
    :param start:
    :param goal:
    :return: list,总路程 失败时返回[],-1
    """
    def estimate_distance(pt1,pt2):
        #估算距离 采用直线距离 这里可以改用其他方法 寻路的效率受这个函数的影响
        return (pt1-pt2).modulus
    class NodeData:#当结构体用 挂载到Node的data变量上
        def __init__(self,g,h,pt):
            self.h=h
            self.g=g
            self.pt=pt
            self.f=self.h+self.g

        def __str__(self):
            return "估计总耗费:%f,已耗费:%f,坐标点:%s"%(self.f,self.g,self.pt)


    assert isinstance(map,RectMap)
    assert isinstance(start,Vector3D)
    assert isinstance(goal,Vector3D)
    start_node=Node(rootNode,NodeData(g=0,
                                      h=0,
                                      pt=start))
    tree=Tree(start_node)
    active_node=start_node
    dead_leafs=[]#记录走不下去的叶
    while True:
        # print("活动节点—%s"%active_node.data)
        # os.system('pause')
        #检查是否到达目的地
        if active_node.data.pt==goal:#寻路成功
            #寻找路
            return tree.get_path(ancestor=start_node,descendent=active_node),active_node.data.f
        neighbors=map.get_neighbors(active_node.data.pt)
        tree_nodes=tree.get_all_nodes()
        tree_nodes_data=[x.data.pt for x in tree_nodes]
        neighbors=[x for x in neighbors if x not in tree_nodes_data]
        if len(neighbors)==0:
            dead_leafs.append(active_node)
            # return [], -1  # 寻路失败
        for nd in neighbors:
            node_data=NodeData(g=active_node.data.g+map.get_cost(nd),#默认每走一步 花费加1
                               h=estimate_distance(nd,goal),# 估算花费
                               pt=nd)
            # print(node_data)
            # os.system('pause')
            active_node.add_child(node_data)
        #在leaf中寻找最短的节点
        leafs=tree.get_all_leafs()
        leafs=[x for x in leafs if x not in dead_leafs]
        if len(leafs)==0:
            return [],-1
        # node_data_lst=[x.data for x in leafs]
        # cmpfun = operator.attrgetter('f')  # 参数为排序依据的属性，可以有多个，这里优先id，使用时按需求改换参数即可
        leafs.sort(key=lambda x:x.data.f)
        active_node=leafs[0]#更新active node








if __name__ == '__main__':
    #测试
    W=10
    H=10
    map=RectMap(W=W, H=H, obstacles=[])
    assert len(map.get_neighbors(Vector3D(0,0)))==2
    assert len(map.get_neighbors(Vector3D(W-1, 0))) == 2
    assert len(map.get_neighbors(Vector3D(W-1, H-1))) == 2
    assert len(map.get_neighbors(Vector3D(0, H-1))) == 2
    assert  len(map.get_neighbors(Vector3D(5,5)))==4
    assert len(map.get_neighbors(Vector3D(0,5)))==3
    assert len(map.get_neighbors(Vector3D(W-1, 5))) == 3
    assert len(map.get_neighbors(Vector3D(5, 0))) == 3
    assert len(map.get_neighbors(Vector3D(5, H-1))) == 3

    W = 10
    H = 10
    map = RectMap(W=W, H=H, obstacles=[Vector3D(1, 0)])
    assert len(map.get_neighbors_obstacles_ignored(Vector3D(0,0)))==2
    assert len(map.get_neighbors(Vector3D(0,0)))==1
    pt=Vector3D(1,0)
    assert len(map.get_neighbors(pt)) == 0
    pt = Vector3D(-1, 0)
    assert len(map.get_neighbors(pt)) == 0
    # for nd in map.get_neighbors_obstacles_ignored(Vector3D(0,0)):
    #     print(nd)
    # print('_________')
    # for nd in map.get_neighbors(Vector3D(0,0)):
    #     print(nd)

    map = RectMap(W=3, H=3, obstacles=[Vector3D(1, 1), Vector3D(2, 1), Vector3D(0, 1)])
    start = Vector3D(0, 0)
    goal = Vector3D(2, 2)
    path, f = A_star_search_algorithm(map=map,
                                      start=start,
                                      goal=goal)
    assert f==-1

    map = RectMap(W=3, H=3, obstacles=[])
    start = Vector3D(0, 0)
    goal = Vector3D(2, 2)
    path, f = A_star_search_algorithm(map=map,
                                      start=start,
                                      goal=goal)
    assert f == 4

    map = RectMap(W=10, H=10, obstacles=[Vector3D(1, 2),
                                              Vector3D(2,2),
                                              Vector3D(3,2),
                                              Vector3D(4,2),
                                              Vector3D(4,3),
                                              Vector3D(4,4),
                                              Vector3D(4,5),
                                              Vector3D(4,6),
                                              Vector3D(3,6),
                                              Vector3D(2,6),
                                              Vector3D(1,6)
                                              ])
    start = Vector3D(0, 4)
    goal = Vector3D(6, 3)
    path, f = A_star_search_algorithm(map=map,
                                      start=start,
                                      goal=goal)
    for nd in path:
        print(nd.data.pt)
    assert f==11

    map = RectMap(W=10, H=10, special_points=[SpecialPoint(Vector3D(1, 2), 100),
                                              SpecialPoint(Vector3D(2, 2), 100),
                                              SpecialPoint(Vector3D(3, 2), 100),
                                              SpecialPoint(Vector3D(4, 2), 100),
                                              SpecialPoint(Vector3D(4, 3), 100),
                                              SpecialPoint(Vector3D(4, 4), 100),
                                              SpecialPoint(Vector3D(4, 5), 100),
                                              SpecialPoint(Vector3D(4, 6), 100),
                                              SpecialPoint(Vector3D(3, 6), 100),
                                              SpecialPoint(Vector3D(2, 6), 100),
                                              SpecialPoint(Vector3D(1, 6), 100)
                                              ])
    start = Vector3D(0, 4)
    goal = Vector3D(6, 3)
    path, f = A_star_search_algorithm(map=map,
                                      start=start,
                                      goal=goal)
    for nd in path:
        print(nd.data.pt)
    assert f == 11

    map = RectMap(W=10, H=10, special_points=[SpecialPoint(Vector3D(1, 2), 100),
                                              SpecialPoint(Vector3D(2, 2), 100),
                                              SpecialPoint(Vector3D(3, 2), 100),
                                              SpecialPoint(Vector3D(4, 2), 100),
                                              SpecialPoint(Vector3D(4, 3), 2),
                                              SpecialPoint(Vector3D(4, 4), 100),
                                              SpecialPoint(Vector3D(4, 5), 100),
                                              SpecialPoint(Vector3D(4, 6), 100),
                                              SpecialPoint(Vector3D(3, 6), 100),
                                              SpecialPoint(Vector3D(2, 6), 100),
                                              SpecialPoint(Vector3D(1, 6), 100)
                                              ])
    start = Vector3D(0, 4)
    goal = Vector3D(6, 3)
    path, f = A_star_search_algorithm(map=map,
                                      start=start,
                                      goal=goal)
    print('__________________')
    for nd in path:
        print(nd.data.pt)
    assert f == 8
    #测试结束


