"""双向列表 闭环的 有一个名为header的头部节点  定义上:第一个节点为header的next 最后一个节点为header的previous"""
from GoodToolPython.mybaseclasses.selfdelete import SelfDelete


class Node(SelfDelete):
    """
    双向列表使用的节点
    为了防止节点不知道自己被删除 继承了selfdelete类
    使用时 不可在双向列表外实例化
    """
    def __init__(self, data=None, previous=None, next=None, list=None):
        self.previous = previous  # type:Node
        self.next = next  # type:Node
        self.data = data  # 数据
        self.list = list  # type:DoublyLinkedList #所属双向链表


class DoublyLinkedList:
    def __init__(self):
        self.header = Node(data='header')  # type:Node #双向列表的头结点
        self.header.previous = self.header
        self.header.next = self.header
        self.header.list = self
        self._length = 0  # type:int #长度

    @property
    def length(self):
        return self._length

    def insert(self, data, mode='after', ref_node=None) -> Node:
        """
        插入节点
        默认插入到最后一个
        可以选择在参考结点之前或者之后插入 算法在实现上都是转化为之后插入
        :param data: 节点上挂载的数据
        :param mode: 'after' 'before'
        :param ref_node: 参考结点
        :return: 生成的节点
        """
        if ref_node is None:
            ref_node = self.header.previous  # 默认参考结点是最后一个节点
        assert mode in ('after', 'before'), 'mode只能是after或者before'
        assert ref_node in self, '参考结点必须在结点内部'
        func = self.__insert_after if mode == 'after' else self.__insert_before
        return func(data, ref_node)

    def __insert_after(self, data, ref_node):
        replaced = ref_node.next
        tmp = Node(data=data, previous=ref_node, next=replaced, list=self)
        ref_node.next = tmp
        replaced.previous = tmp
        self._length += 1
        return tmp

    def __insert_before(self, data, ref_node):
        return self.__insert_after(data=data, ref_node=ref_node.previous)

    def __contains__(self, item):
        assert isinstance(item, Node), '必须为节点'
        return item.list == self

    def __str__(self):
        return '长度:%d' % self._length

    def print(self, expr=None) -> None:
        #详细打印列表信息 默认直接输出data
        if expr is None:
            expr = lambda x: x.data
        assert callable(expr)
        print(self)
        for n in self:
            print(expr(n))

    def __iter__(self):
        #迭代器 从第一个节点开始迭代 不含头部
        self.__next_node = self.header.next  # 迭代用的变量
        return self

    def __next__(self) -> Node:
        if self.__next_node == self.header:
            raise StopIteration
        self.__next_node = self.__next_node.next
        return self.__next_node.previous

    def delete_node(self, node: Node):
        assert isinstance(node, Node), '必须为节点对象'
        assert node in self, '必须为链表内部节点'
        assert node != self.header, '头部节点不能删除'
        node.previous.next = node.next
        node.next.previous = node.previous
        node.delete()
        self._length -= 1

    def find_by_data(self, data) -> Node:
        #通过数据 查找节点 返回第一个满足data相等的节点 没找到返回none
        for n in self:
            if n.data == data:
                return n
        return None

    def __len__(self):
        return self._length


    @property
    def last_node(self)->Node:
        #最后节点
        if self._length==0:
            return None
        return self.header.previous
    @property
    def first_node(self)->Node:
        #第一个节点 不是头部
        if self._length==0:
            return None
        return self.header.next
    def __getitem__(self, item)->Node:
        #通过索引获取节点 支持负数索引
        assert isinstance(item,int),'只支持数字索引'
        if item>=0:#自然数时 正向索引
            if item>self._length-1:
                raise Exception("索引超出范围")
            it=self.header
            for i in range(0,item+1):
                it=it.next
            return it
        else:#负数
            if -1*item>self._length:
                raise Exception("索引超出范围")
            it = self.header
            for i in range(-1,item-1,-1):
                it=it.previous
            return it

if __name__ == '__main__':
    lst = DoublyLinkedList()
    lst.print()
    lst.insert('1')
    lst.print(expr=lambda x: x.data)
    assert len(lst) == 1
    assert lst[0].data=='1'
    assert lst[-1].data == '1'
    t1 = lst.insert('2')
    lst.insert('3')
    lst.print()
    assert len(lst) == 3
    lst.insert(data='2.5', ref_node=t1)
    assert len(lst) == 4
    lst.print()
    lst.insert(data='1.5', ref_node=t1, mode='before')
    assert lst.last_node.data == '3'
    assert lst[2].data == '2'
    assert len(lst) == 5
    lst.print()
    lst.delete_node(t1)
    assert lst.last_node.previous.data == '2.5'
    assert len(lst) == 4
    lst.print()
    lst.delete_node(lst.find_by_data('2.5'))
    lst.print()
    assert len(lst) == 3
    assert lst.last_node.data == '3'
    assert lst[-1].data == '3'
    assert lst[-2].data == '1.5'
