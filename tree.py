from typing import TypeVar, Generic,List
T_Node=TypeVar('T_Node')
T_Tree=TypeVar('T_Tree')
rootNode='root'#根节点标志 这个值不重要


class Node(Generic[T_Node]):
    """
    树上的节点
    节点实例化通过：调用tree中make_root_node方法生成根节点 或 内部addchild方法
    """
    def __init__(self,parent,data=None,tree:T_Tree=None):
        if not( isinstance(parent,Node) or parent == rootNode):
            raise Exception("parent参数不合法")
        assert isinstance(tree,Tree)
        self.parent=parent
        self.data=data
        self.child_nodes=[]#子节点 初始化为空列表
        self.tree=tree
        #处理节点的深度
        if parent==rootNode:
            self.depth=0
        else:
            self.depth=1+parent.depth
        #新增节点的深度可能会影响树的高度
        self.tree.updata_height(self.depth)


    @property
    def degree(self):#节点的度
        return len(self.child_nodes)

    def add_child(self,data)->T_Node:
        """
        添加子节点
        :param data: 是子节点的数据 不是node类
        :return: 生成的子节点
        """
        cd=Node(parent=self,
                data=data,
                tree=self.tree)
        self.child_nodes.append(cd)
        return cd

    def get_siblings(self,)->List[T_Node]:
        """
        返回siblings
        :return: 没有就返回[]
        """
        if self.parent==rootNode:
            return []
        siblings=self.parent.child_nodes
        siblings=[x for x in siblings if x!=self]
        return siblings



class Tree(Generic[T_Tree]):
    """
    树 数据结构
    来源：https://en.wikipedia.org/wiki/Tree_(data_structure)
    使用方法：
    tree=Tree()#实例化树
    rn=tree.make_root_node(数据1)#生成根节点
    rn.add_child(数据2)#生成其他节点
    """
    def __init__(self):
        self.root_node=None
        self._height=-1#在没有节点时高度为-1
        pass

    def make_root_node(self,data)->T_Node:
        """
        生成根节点
        #返回生成的节点
        :param data: 节点数据
        :return:
        """
        self.root_node=Node(parent=rootNode,
                            data=data,
                            tree=self)
        return self.root_node



    def get_all_leafs(self) -> List[Node]:
        """
        获取所有的叶
        :return:
        """
        def search_in_child_nodes(nds,lst):
            # 在子节点列表中搜索
            for nd in nds:
                if nd.degree == 0:  # 为叶
                    lst.append(nd)
                else:  # 为枝
                    search_in_child_nodes(nd.child_nodes,lst)


        lst = []
        # search_in_child_nodes(self.root_node.child_nodes,lst)
        search_in_child_nodes([self.root_node], lst)
        return lst

    def get_all_nodes(self)->list:
        #返回所有的节点
        def search_in_child_nodes(nds,lst):
            # 在子节点列表中搜索
            for nd in nds:
                if nd.degree == 0:  # 为叶
                    lst.append(nd)
                else:  # 为枝
                    lst.append(nd)
                    search_in_child_nodes(nd.child_nodes,lst)
        lst = []
        search_in_child_nodes([self.root_node],lst)
        return lst



    def get_path(self,ancestor:T_Node,descendent:T_Node)->list:
        """
        寻找从一个节点到另一个节点的路
        :param ancestor:
        :param descendent:
        :return: 如果没找到 返回空列表
        """
        assert isinstance(ancestor,Node)
        assert isinstance(descendent,Node)
        up=descendent.parent
        path=[descendent]
        while True:
            if up==ancestor:
                path.append(up)
                path.reverse()
                return path
            elif up==rootNode:
                return []
            else:
                path.append(up)
                up=up.parent

    @property
    def height(self):
        return self._height

    def updata_height(self,a_depth:int)->Node:
        """
        更新树的高度 =节点的最大深度
        :param a_depth:
        :return:
        """
        self._height=a_depth if a_depth>self._height else self._height




if __name__ == '__main__':
    tree=Tree()
    assert tree.height == -1
    rn=tree.make_root_node(data='0')
    assert tree.height == 0
    n1=rn.add_child('01')
    assert tree.height == 1
    n2=rn.add_child('02')
    assert tree.height == 1
    t1=n1.add_child('011')
    n1.add_child('012')
    n1.add_child('013')
    n2.add_child('021')
    n2.add_child('022')
    assert len(tree.get_all_leafs())==5
    assert len(tree.get_all_nodes())==8
    assert len(t1.get_siblings())==2
    assert len(rn.get_siblings())==0
    assert tree.height==2

