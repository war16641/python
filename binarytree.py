import GoodToolPython.tree as otree
from GoodToolPython.tree import rootNode
from nose.tools import assert_raises
from enum import Enum, unique

@unique
class BinaryNodePosition(Enum):
    LEFT=0
    RIGHT=1#左右子节点
    ROOT=2#根节点
class BinaryNode(otree.Node):
    """
    child_nodes最多两个node 第一个是左节点 第二个是右节点
    和父类一样：BinaryNode的对象只会在make_root_node和add_child中产生
    """
    def __init__(self, parent, data=None, tree: 'BinaryTree' = None,ndpos=None):
        """

        :param parent:
        :param data:
        :param tree:
        :param ndpos: 指定自己在父节点中的位置 为None时，自动判断
        """
        #如果新建的节点覆盖了其他节点
        if ndpos is not None:
            if parent[ndpos] is not None:
                tree.delete_node(parent[ndpos])

        super().__init__(parent=parent,
                         data=data,
                         tree=tree)

        #初始化节点的左右子节点
        self._left_node = None #type:BinaryNode
        self._right_node = None  # type:BinaryNode

        #处理节点位置
        self.position=None#type:BinaryNodePosition #标记自身在父节点下的位置
        #判断自身位置
        if ndpos is None:#自动
            if self.parent is rootNode:#根节点
                self.position=BinaryNodePosition.ROOT
            else:#一般情况
                if self.parent.left_node is None:
                    self.position=BinaryNodePosition.LEFT
                elif self.parent.right_node is None:
                    self.position=BinaryNodePosition.RIGHT
                else:
                    raise Exception("父节点已存在左右子节点")
        else:#指定位置
            assert isinstance(ndpos,BinaryNodePosition),'必须为BinaryNodePosition对象'
            #检查该位置是否已经存在节点
            if self[ndpos] is not None:
                self.tree.delete_node(self[ndpos])#删除已存在节点
            self.position=ndpos
        #更新父节点的左右子节点
        if self.position is BinaryNodePosition.LEFT:
            self.parent._left_node=self
        elif self.position is BinaryNodePosition.RIGHT:
            self.parent._right_node=self

        #最后检查是否父节点的子节点个数超过了2
        if self.parent != rootNode:
            assert self.parent.degree <= 2, '节点最多只能有两个子节点'





    def add_child(self, data,ndpos:BinaryNodePosition=None) -> 'BinaryNode':
        """
        二叉树要求最多两个节点
        :param data:
        :return:
        """

        cd = BinaryNode(parent=self,
                          data=data,
                          tree=self.tree,
                        ndpos=ndpos)
        self.child_nodes.append(cd)
        return cd

    @property
    def left_node(self)->'BinaryNode':
        """没有时返回NOne"""
        return self._left_node
        # if len(self.child_nodes)>=1:
        #     return self.child_nodes[0]
        # else:
        #     return None
    @property
    def right_node(self)->'BinaryNode':
        return self._right_node
        # if len(self.child_nodes)==2:
        #     return self.child_nodes[1]
        # else:
        #     return None
    @left_node.setter
    def left_node(self,v):
        assert isinstance(v,BinaryNode)
        self._left_node=v
    @right_node.setter
    def right_node(self,v):
        assert isinstance(v,BinaryNode)
        self._right_node=v
    def __str__(self):
        return self.data.__str__()


    def __getitem__(self, item):
        """
        BinaryNode支持BinaryNode[BinaryNodePosition]的索引和赋值
        :param item:
        :return:
        """
        if isinstance(item,BinaryNodePosition):
            if item is BinaryNodePosition.LEFT:
                return self.left_node
            elif item is BinaryNodePosition.RIGHT:
                return self.right_node
            else:
                raise Exception("参数错误")
        else:
            raise Exception("参数错误")

    def __setitem__(self, item, value):
        if isinstance(item,BinaryNodePosition):
            if item is BinaryNodePosition.LEFT:
                self.left_node=value
            elif item is BinaryNodePosition.RIGHT:
                self.right_node=value
            else:
                raise Exception("参数错误")
        else:
            raise Exception("参数错误")


class BinaryTree(otree.Tree):
    def make_root_node(self, data) -> 'BinaryNode':
        """
        使用BinaryNode代替Node
        :param data:
        :return:
        """
        self.root_node=BinaryNode(parent=otree.rootNode,
                                  data=data,
                                  tree=self)
        return self.root_node

    # def delete_node(self, nd: BinaryNode) -> None:
    #     assert nd in self
    #     # 处理node_list\leaf_list
    #     tmp = self.get_nodes_below(nd)  # 获取nd及以下的节点
    #     # 其父节点在删除后可能成为叶
    #     if isinstance(nd.parent, otree.Node) and nd.parent.degree == 0:
    #         self._leaf_list.append(nd.parent)
    #     # 删除父节点中子节点列表中的自身
    #     nd.parent.child_nodes.remove(nd)
    #     for x in tmp:
    #         self._node_list.remove(x)  # 一一删除
    #         if x.degree == 0:  # 为叶
    #             self._leaf_list.remove(x)
    #
    #         # 强制删除
    #         x.delete()

if __name__ == '__main__':
    tree=BinaryTree()
    rn=tree.make_root_node(data='起始')
    assert isinstance(rn,BinaryNode)
    assert rn.left_node is None and rn.right_node is None
    rn.add_child('01')
    assert rn.right_node is None
    rn.add_child('02')
    assert tree.height==1
    assert_raises(Exception,rn.add_child,'0')
    assert rn.left_node.data=='01'
    assert rn.right_node.data=='02'
    n1=rn.add_child(data='01a',ndpos=BinaryNodePosition.LEFT)
    left=BinaryNodePosition.LEFT
    print(rn[left])
    assert rn[BinaryNodePosition.LEFT].data=='01a'
    assert rn.degree==2
    n1.add_child(data='01b',ndpos=BinaryNodePosition.RIGHT)
    n1.add_child(data='012', ndpos=BinaryNodePosition.RIGHT)
    n1.add_child(data='011', ndpos=BinaryNodePosition.LEFT)
    assert n1.right_node.data=='012'
    assert len(tree.get_nodes_below())==5
    assert len(tree.get_leafs_below())==3
    tree.delete_node(n1)
    assert rn.degree==1
    tree.show_in_gui()
