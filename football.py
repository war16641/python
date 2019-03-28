from GoodToolPython.vector import Vector
from tkinter import *
from line import Line
import itertools
import smallmodel

import random


class Court:
    """球场"""
    color = 'white'
    sideline_vector = {'top': Vector(0, 1),  # 四条边线的内侧向量 用于反射速度
                       'bot': Vector(0, -1),
                       'left': Vector(1, 0),
                       'right': Vector(-1, 0)}

    def __init__(self, x0=10, y0=10, width=400, height=400, canvas=None):
        self.x0, self.y0, self.width, self.height, self.canvas = x0, y0, width, height, canvas
        # 球场的四条边线
        self.top_line = Line(A=0, B=1, C=0, name='top')
        self.bot_line = Line(A=0, B=1, C=-height, name='bot')
        self.left_line = Line(A=1, B=0, C=0, name='left')
        self.right_line = Line(A=1, B=0, C=-width, name='right')
        self.line_lst = [self.top_line, self.bot_line, self.left_line, self.right_line, ]

    def draw(self):
        assert isinstance(self.canvas, Canvas)
        self.canvas.create_rectangle(self.x0, self.y0, self.x0 + self.width, self.y0 + self.height, fill=self.color)


class Ball:
    """球体"""
    radius = 5  # 球体半径
    color = 'red'  # 球体默认颜色
    distance_on_reflect = 5  # 反射时与边线最大的距离
    distance_on_collision = 5  # 碰撞发生的最大距离

    def __init__(self, name='', x0=0, y0=0, dx=0, dy=0, court=None, canvas=None, color='red'):
        self.name = name
        self.pos = Vector(x0, y0)
        self.speed = Vector(dx, dy)
        self.canvas = canvas
        self.court = court
        self.color = color
        self.pic = None

    def update(self, dt=0):
        """根据速度 时间 更新坐标"""
        if dt == 0:
            return

        self.pos += self.speed * dt

        # 检查是否到了边界
        dis = [ln.distance_to_point(self.pos.x, self.pos.y) for ln in self.court.line_lst]
        min_dis = min(dis)
        id = dis.index(min_dis)
        line = self.court.line_lst[id]
        if min_dis <= self.distance_on_reflect:  # 可能会反射速度
            drt = self.court.sideline_vector[line.name]
            if drt * self.speed < 0:
                self.speed = self.speed.reflect(drt)

        #

    def __str__(self):
        """打印当前状态"""
        return "球：%s 位置%s 速度%s" % (self.name, self.pos.__str__(), self.speed.__str__())

    def draw(self, color=None):
        assert isinstance(self.canvas, Canvas)
        if color is None:
            color = self.color
        if self.pic is None:
            self.pic = self.canvas.create_arc(self.court.x0 + self.pos.x - self.radius,
                                              self.court.x0 + self.pos.y - self.radius,
                                              self.court.x0 + self.pos.x + self.radius,
                                              self.court.x0 + self.pos.y + self.radius, style=CHORD, extent=359,
                                              outline=color, fill=color)

        else:
            # self.canvas.move(self.pic,10,10)
            self.canvas.coords(self.pic, self.court.x0 + self.pos.x - self.radius,
                               self.court.x0 + self.pos.y - self.radius, self.court.x0 + self.pos.x + self.radius,
                               self.court.x0 + self.pos.y + self.radius)

    def un_draw(self):
        self.draw('white')

    @staticmethod
    def distance(b1, b2):
        """返回两个球之间的距离"""
        assert isinstance(b1, Ball) and isinstance(b2, Ball)
        v = b1.pos - b2.pos
        return v.modulus


class Football:
    def __init__(self):
        # 窗口和标题
        window = Tk()
        window.title("鼠标键盘事件")

        # 打包一个白色画布到窗口
        self.canvas = Canvas(window, width=420, height=420, bg="white")
        self.canvas.focus_set()  # 让画布获得焦点
        self.canvas.pack()

        self.court = Court(10, 10, 400, 400, self.canvas)
        self.court.draw()

        # 产生球
        self.ball_list = []
        self.generate_balllist()

        for ball in self.ball_list:
            ball.draw()

        # 绑定鼠标左键事件，交由processMouseEvent函数去处理，事件对象会作为参数传递给该函数
        self.canvas.bind(sequence="<Button-1>", func=self.processMouseEvent)

        # 绑定鼠标键盘事件，交由processKeyboardEvent函数去处理，事件对象会作为参数传递给该函数
        self.canvas.bind(sequence="<Key>", func=self.processKeyboardEvent)
        self.canvas.after(1000, self.action)

        # 消息循环
        window.mainloop()

    # 处理鼠标事件，me为控件传递过来的鼠标事件对象
    def processMouseEvent(self, me):
        pass
        # print("me=", type(me))  # me= <class>
        #
        # print("位于屏幕", me.x_root, me.y_root)
        # print("位于窗口", me.x, me.y)
        # print("位于窗口", me.num)
        # self.canvas.create_rectangle(me.x-5,me.y-5,me.x+5,me.y+5,edge='red')

    # 处理鼠标事件，ke为控件传递过来的键盘事件对象
    def processKeyboardEvent(self, ke):
        pass
        # print("ke.keysym", ke.keysym)  # 按键别名
        # print("ke.char", ke.char)  # 按键对应的字符
        # print("ke.keycode", ke.keycode)

    def action(self):

        # 检查碰撞
        for b1, b2 in itertools.combinations(self.ball_list, 2):
            if Ball.distance(b1, b2) < Ball.distance_on_collision:
                try:
                    v1, v2 = smallmodel.two_dimensional_collision_problem(m1=1,
                                                                          m2=1,
                                                                          from_m2_to_m1=b1.pos - b2.pos,
                                                                          v10=b1.speed,
                                                                          v20=b2.speed,
                                                                          e=0
                                                                          )
                    b1.speed, b2.speed = v1, v2
                    print("碰撞")
                except smallmodel.NoCollisionError:
                    print('可惜没法说碰撞')
                    pass
                except Exception as e:
                    raise e

        for ball in self.ball_list:
            ball.update(dt=0.2)
            ball.draw()
        self.canvas.after(10, self.action)

    def generate_balllist(self):
        """负责生成所有的球"""

        for i in range(50):
            ball = self.generate_ball()
            self.ball_list.append(ball)

    def generate_balllist_script(self):
        """负责生产所有的球，生成两个对撞的球"""
        b1 = Ball(x0=100,
                  y0=200,
                  dx=5.1,
                  dy=0,
                  court=self.court,
                  canvas=self.canvas)
        b2 = Ball(x0=300,
                  y0=200,
                  dx=0,
                  dy=0,
                  court=self.court,
                  canvas=self.canvas,
                  color='green')
        self.ball_list.extend([b1, b2])

    def generate_ball(self):
        """产生一个球 这个函数主要设置如何产生"""
        drt = [-1, 1]
        return Ball(x0=random.randint(Ball.distance_on_reflect, self.court.width - Ball.distance_on_reflect),
                    y0=random.randint(Ball.distance_on_reflect, self.court.height - Ball.distance_on_reflect),
                    dx=random.choice(drt) * random.uniform(5, 10),
                    dy=random.choice(drt) * random.uniform(5, 10),
                    court=self.court,
                    canvas=self.canvas)


if __name__ == "__main__":
    Football()
