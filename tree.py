import copy
import time
from typing import TypeVar, Generic, List

import wx
from nose.tools import *

T_Node = TypeVar('T_Node')
T_Tree = TypeVar('T_Tree')
rootNode = 'root'  # 根节点标志 这个值不重要


class Node(Generic[T_Node]):
    """
    树上的节点
    节点实例化通过：调用tree中make_root_node方法生成根节点 或 内部addchild方法
    """

    def __init__(self, parent, data=None, tree: T_Tree = None):
        if not (isinstance(parent, Node) or parent == rootNode):
            raise Exception("parent参数不合法")
        assert isinstance(tree, Tree)
        self.parent = parent
        self.data = data
        self.child_nodes = []  # 子节点 初始化为空列表
        self.tree = tree
        # 处理节点的深度
        if parent == rootNode:
            self.depth = 0
        else:
            self.depth = 1 + parent.depth
        # 新增节点的深度可能会影响树的高度
        self.tree.updata_height(self.depth)
        # 新增节点增加树的节点列表
        tree._node_list.append(self)
        # 新增节点增加树的叶列表
        tree._leaf_list.append(self)
        # 新增节点删除树的叶列表中自身的父节点
        try:
            tree._leaf_list.remove(self.parent)
        except ValueError:
            pass  # 有可能已经被删除 这是正常情况
        except Exception:
            raise

    @property
    def degree(self):  # 节点的度
        return len(self.child_nodes)

    def add_child(self, data) -> T_Node:
        """
        添加子节点
        :param data: 是子节点的数据 不是node类
        :return: 生成的子节点
        """
        cd = Node(parent=self,
                  data=data,
                  tree=self.tree)
        self.child_nodes.append(cd)
        return cd

    def get_siblings(self, ) -> List[T_Node]:
        """
        返回siblings
        :return: 没有就返回[]
        """
        if self.parent == rootNode:
            return []
        siblings = self.parent.child_nodes
        siblings = [x for x in siblings if x != self]
        return siblings

    def delete(self, ):
        # 强制删除所有成员变量
        # python内部采用gc机制 当引用为0时才真正删除对象 有时候需要在还有其他引用时仍删除对象
        tmp = copy.deepcopy(list(vars(self).keys()))
        for name in tmp:
            delattr(self, name)
        pass


class Tree(Generic[T_Tree]):
    """
    树 数据结构
    来源：https://en.wikipedia.org/wiki/Tree_(data_structure)
    使用方法：
    tree=Tree()#实例化树
    rn=tree.make_root_node(数据1)#生成根节点
    rn.add_child(数据2)#生成其他节点
    """

    class MyFrame(wx.Frame):
        def __init__(self, parent=None, tree=None, valexp=None, app=None):
            super().__init__(parent, -1, "请关闭gui", size=(450, 250))
            # 检查树
            assert isinstance(tree, Tree)
            assert tree.root_node is not None
            # 设置valexp的默认参数
            if valexp is None:
                valexp = lambda x: x.__str__()  # 默认字符串方法
            self.tree = wx.TreeCtrl(self)  # 创建树形控件
            root = self.tree.AddRoot(valexp(tree.root_node.data))  # 设置根
            self.show_nodes_below(parent=root,
                                  nds=tree.root_node.child_nodes,
                                  valexp=valexp)
            self.tree.Expand(root)  # 展开根节点
            self.app = app

        def run_to_mainloop(self):
            self.app.MainLoop()

        def show_nodes_below(self, parent, nds, valexp):
            for nd in nds:
                cur = self.tree.AppendItem(parent, valexp(nd.data))
                if nd.degree != 0:  # 有子节点
                    self.show_nodes_below(cur, nd.child_nodes, valexp)

    def __init__(self):
        self.root_node = None
        self._node_list = []  # 保存所有的节点
        self._leaf_list = []  # 保存所有的叶
        self._height = -1  # 在没有节点时高度为-1
        self.wx_frame = None
        self.wx_app = wx.App()
        pass

    def make_root_node(self, data) -> T_Node:
        """
        生成根节点
        #返回生成的节点
        :param data: 节点数据
        :return:
        """
        self.root_node = Node(parent=rootNode,
                              data=data,
                              tree=self)
        return self.root_node

    def get_leafs_below(self, nd: Node = None) -> List[Node]:
        """
        获取nd及之下所有的叶
        :param nd: 为None时 使用根节点
        :return:
        """

        def search_in_child_nodes(nds, lst):
            # 在子节点列表中搜索
            for nd in nds:
                if nd.degree == 0:  # 为叶
                    lst.append(nd)
                else:  # 为枝
                    search_in_child_nodes(nd.child_nodes, lst)

        if nd is None:
            nd = self.root_node
        assert isinstance(nd, Node)
        lst = []
        # search_in_child_nodes(self.root_node.child_nodes,lst)
        search_in_child_nodes([nd], lst)
        return lst

    def get_nodes_below(self, nd: Node = None) -> List[Node]:
        # 返回所有的节点
        # return self._node_list
        def search_in_child_nodes(nds, lst):
            # 在子节点列表中搜索
            for nd in nds:
                if nd.degree == 0:  # 为叶
                    lst.append(nd)
                else:  # 为枝
                    lst.append(nd)
                    search_in_child_nodes(nd.child_nodes, lst)

        if nd is None:
            nd = self.root_node
        lst = []
        search_in_child_nodes([nd], lst)
        return lst

    def __contains__(self, item: Node):
        # item是否是树上的节点
        return isinstance(item, Node) and item.tree is self

    def delete_node(self, nd: Node) -> None:
        """
        删除节点
        :param nd:
        :return:
        """
        assert nd in self
        # 处理node_list\leaf_list
        tmp = self.get_nodes_below(nd)  # 获取nd及以下的节点
        # 其父节点在删除后可能成为叶
        if isinstance(nd.parent, Node) and nd.parent.degree == 0:
            self._leaf_list.append(nd.parent)
        # 删除父节点中子节点列表中的自身
        nd.parent.child_nodes.remove(nd)
        for x in tmp:
            self._node_list.remove(x)  # 一一删除
            if x.degree == 0:  # 为叶
                self._leaf_list.remove(x)
            # 强制删除
            x.delete()

        # #先处理node_list
        # self._node_list.remove(nd)#删除本身
        # for x in nd.child_nodes:#删除所有子节点
        #     self._node_list.remove(x)
        # #删除父节点中子节点列表中的自身
        # nd.parent.child_nodes.remove(nd)

    def get_path(self, ancestor: T_Node, descendent: T_Node) -> list:
        """
        寻找从一个节点到另一个节点的路
        :param ancestor:
        :param descendent:
        :return: 如果没找到 返回空列表
        """
        assert isinstance(ancestor, Node)
        assert isinstance(descendent, Node)
        up = descendent.parent
        path = [descendent]
        while True:
            if up == ancestor:
                path.append(up)
                path.reverse()
                return path
            elif up == rootNode:
                return []
            else:
                path.append(up)
                up = up.parent

    @property
    def height(self):
        return self._height

    def updata_height(self, a_depth: int) -> Node:
        """
        更新树的高度 =节点的最大深度
        :param a_depth:
        :return:
        """
        self._height = a_depth if a_depth > self._height else self._height

    def find_by_data(self, data) -> Node:
        """
        通过node上挂载的data寻找node
        此算法要求data定义了==操作符
        :param data:
        :return: 只返回一个符合条件的Node 没找到返回None
        """
        for x in self._node_list:
            if x.data == data:
                return x
        return None

    def show_in_gui(self, valueexp=None) -> None:
        """
        此函数为阻塞 需要用户手动关闭
        :param valueexp: 匿名函数 表示节点的text数据取data的什么值
        :return:
        """
        print('请手动关闭gui')
        self.frame = self.MyFrame(tree=self, app=self.wx_app, valexp=valueexp)
        self.frame.Show()
        self.frame.run_to_mainloop()


def instance1():  # 实例化一个tree 用于调试
    tree = Tree()
    rn = tree.make_root_node(data='0')
    n1 = rn.add_child('01')
    n2 = rn.add_child('02')
    t1 = n1.add_child('011')
    n1.add_child('012')
    n1.add_child('013')
    n2.add_child('021')
    n2.add_child('022')
    t1.add_child('0111')
    t1 = t1.add_child('0112')
    t1.add_child('01121')
    return tree


if __name__ == '__main__':
    # 测试开始
    tree = Tree()
    assert tree.height == -1
    rn = tree.make_root_node(data='起始')
    assert rn.degree == 0
    assert tree.height == 0
    n1 = rn.add_child('01')
    assert tree.height == 1
    n2 = rn.add_child('02')
    assert tree.height == 1
    t1 = n1.add_child('011')
    n1.add_child('012')
    n1.add_child('013')
    n2.add_child('021')
    n2.add_child('022')
    tree.show_in_gui()
    rn.data = '0'
    tree.show_in_gui()
    assert len(tree.get_leafs_below()) == 5
    assert len(tree.get_leafs_below(n1)) == 3
    assert len(tree.get_nodes_below()) == 8
    assert len(t1.get_siblings()) == 2
    assert len(rn.get_siblings()) == 0
    assert tree.height == 2
    tree.delete_node(t1)
    assert len(tree.get_leafs_below(n1)) == 2
    assert len(tree.get_nodes_below()) == 7
    tree.delete_node(n2)
    assert len(tree.get_nodes_below()) == 4
    assert rn.degree == 1

    tree = instance1()
    n1 = tree.find_by_data('01')
    n2 = tree.find_by_data('0111')
    tree.delete_node(n1)
    assert len(tree.get_nodes_below()) == 4
    assert len(tree.get_leafs_below()) == 2
    assert_raises(AttributeError, n1.__getattribute__, 'data')  # 删除后 应无法访问节点的数据
    assert_raises(AttributeError, n2.__getattribute__, 'data')

    tree = instance1()
    tree.show_in_gui()
    n1 = tree.find_by_data('01121')
    n2 = n1.parent
    assert n2.degree == 1
    assert len(tree.get_leafs_below()) == 6
    tree.delete_node(n1)
    assert len(tree.get_leafs_below()) == 6
    assert n2.degree == 0
    assert n2 in tree.get_leafs_below()
    time.sleep(10)
    # 测试结束
