class ToDoException(Exception):
    """
    未实现异常， 当前代码并未实现 而非真实异常 暗示在此处需要添加代码
    """
    def __init__(self,description=''):
        assert isinstance(description,str)
        if len(description)!=0:
            description="未实现异常。描述："+description
        else:
            description="未实现异常。"
        super().__init__(description)

if __name__ == '__main__':
    raise ToDoException("sd")