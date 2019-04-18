from typing import TypeVar, Generic
T_Node=TypeVar('T_Node')
rootNode='root'#parent=rootnode的节点时根节点 这个值不重要
# tbdNode='tbd'#父节点待定
class Node(Generic[T_Node]):
    """
    树上的节点
    """
    def __init__(self,parent,data=None):
        if not( isinstance(parent,Node) or parent == rootNode):
            raise Exception("parent参数不合法")
        self.parent=parent
        self.data=data
        self.child_nodes=[]#子节点 初始化为空列表
        #处理节点的深度
        if parent==rootNode:
            self.depth=1
        else:
            self.depth=1+parent.depth

    @property
    def degree(self):#节点的度
        return len(self.child_nodes)

    def add_child(self,data)->T_Node:
        """
        添加子节点
        :param data: 是子节点的数据 不是node类
        :return: 生成的子节点
        """
        cd=Node(parent=self,data=data)
        self.child_nodes.append(cd)
        return cd



class Tree:
    """
    树 数据结构
    """
    def __init__(self,rootNode:T_Node):
        assert isinstance(rootNode,Node)
        self.root_node=rootNode



    def get_all_leafs(self) -> list:
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
        search_in_child_nodes(self.root_node.child_nodes,lst)
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
        search_in_child_nodes(self.root_node.child_nodes,lst)
        return lst



if __name__ == '__main__':
    rn=Node(parent=rootNode,
            data='0')
    tree=Tree(rn)
    n1=rn.add_child('01')
    n2=rn.add_child('02')

    n1.add_child('011')
    n1.add_child('012')
    n1.add_child('013')
    n2.add_child('021')
    n2.add_child('022')
    for nd in tree.get_all_leafs():
        print(nd.data)
    for nd in tree.get_all_nodes():
        print(nd.data)