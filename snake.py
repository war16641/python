import random
import pygame
import sys
from pygame.locals import *
import warnings
from GoodToolPython.vector3d import Vector3D

fps = 2#fps
Window_Width = 200
Window_Height = 200
Cell_Size = 20  # Width and height of the cells
assert Window_Width % Cell_Size == 0, "Window width must be a multiple of cell size."
# Ensuring that only whole integer number of cells fit perfectly in the window.
assert Window_Height % Cell_Size == 0, "Window height must be a multiple of cell size."
Cell_W = int(Window_Width / Cell_Size)  #  Width
Cell_H = int(Window_Height / Cell_Size)  #  Height  in cells

White = (255, 255, 255)# Defining element colors for the program.
Black = (0, 0, 0)
Red = (255, 0, 0)
Green = (0, 255, 0)
DARKGreen = (0, 155, 0)
DARKGRAY = (40, 40, 40)
YELLOW = (255, 255, 0)
Red_DARK = (150, 0, 0)
BLUE = (0, 0, 255)
BLUE_DARK = (0, 0, 150)

BGCOLOR = Black  # Background color

UP = 'up'# Defining keyboard keys.
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

segment_color1=(DARKGreen,Green)#蛇节段的配色方案
segment_color2=(BLUE_DARK,BLUE)



def spawn_food():
    while True:
        # 刷新食物
        food = Vector3D(x=random.randint(0, Cell_W - 1),
                        y=random.randint(0, Cell_H - 1))
        if food not in snake:
            return food
def draw_food(food):
    x = food.x
    y = food.y
    x *= Cell_Size
    y *= Cell_Size
    sg_Rect = pygame.Rect(x, y, Cell_Size, Cell_Size)
    pygame.draw.rect(DISPLAYSURF, Red, sg_Rect)

def terminate():#关闭程序
    pygame.quit()
    sys.exit()

def drawGrid():
    DISPLAYSURF.fill(BGCOLOR)
    for x in range(0, Window_Width, Cell_Size):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, Window_Height))
    for y in range(0, Window_Height, Cell_Size):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (Window_Width, y))
def checkForKeyPress():
    #检查是否有按键按下
    if len(pygame.event.get(QUIT)) > 0:
        terminate()
    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key

def show_gameover_screen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 100)
    gameSurf = gameOverFont.render('Game', True, White)
    overSurf = gameOverFont.render('Over', True, White)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (Window_Width / 2, 10)
    overRect.midtop = (Window_Width / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    pygame.display.update()
    pygame.time.wait(500)

    while True:
        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            terminate()
            return

class Snake:
    def __init__(self,xy0=Vector3D(5,5),length0=3,direction=RIGHT):
        self.length,self._direction=length0,direction#长度 方向
        self.segments=[xy0]#蛇的所有节段
        #根据方向 计算其余节段
        dxy=self.direction_interpreter(direction)
        for it in range(1,length0):
            self.segments.append(xy0-it*dxy)
        self.food=None


    def direction_interpreter(self,d):
        if d==RIGHT:
            return Vector3D(1,0)
        elif d==LEFT:
            return Vector3D(-1,0)
        elif d==DOWN:
            return Vector3D(0,1)
        elif d==UP:
            return Vector3D(0,-1)
        else:
            raise Exception("无效方向")
    def update(self):
        #更新蛇
        newhead=self.segments[0]+self.direction_interpreter(self.direction)
        self.segments.insert(0,newhead)#更换新头部
        self.segments.pop()#弹出最后一个

    def check_gameover(self)->bool:
        """检查游戏结束的条件
        当游戏结束时返回1"""
        #头部是否在边境以外
        x=self.segments[0].x
        y=self.segments[0].y
        if x < 0 or x > Cell_W - 1 or y < 0 or y > Cell_H - 1:
            return True
        #头碰到身体
        if self.segments[0] in self.segments[1:]:
            return True
        return False

    @property
    def direction(self):
        return self._direction
    @direction.setter
    def direction(self,v):
        if v==RIGHT and self._direction!=LEFT:
            self._direction=v
        elif v==LEFT and self._direction!=RIGHT:
            self._direction = v
        elif v==UP and self._direction!=DOWN:
            self._direction = v
        elif v==DOWN and self._direction!=UP:
            self._direction = v
        else:
            pass
            # raise Exception("方向错误设置")
    def draw(self):
        """
        画出蛇
        :return:
        """
        def draw_segment(sg:Vector3D,color_plan=segment_color1)->None:
            #画出一个节段
            x=sg.x
            y=sg.y
            #检查坐标是否超出屏幕范围
            if x<0 or x>Cell_W-1 or y<0 or y>Cell_H-1:
                warnings.warn("警告:蛇节段超出屏幕:%d,%d"%(x,y))
            x*=Cell_Size
            y*=Cell_Size
            sg_Rect = pygame.Rect(x, y, Cell_Size, Cell_Size)
            pygame.draw.rect(DISPLAYSURF, color_plan[0], sg_Rect)
            sg_Inner_Rect = pygame.Rect(
                x + 4, y + 4, Cell_Size - 8, Cell_Size - 8)
            pygame.draw.rect(DISPLAYSURF, color_plan[1], sg_Inner_Rect)
        for id,sg in enumerate(self.segments):
            draw_segment(sg,
                         (segment_color1 if id!=0 else segment_color2))

    def __contains__(self, item):
        """
        判断点是否在内部
        :param item:
        :return:
        """
        assert isinstance(item,Vector3D)
        return item in self.segments

    def add_segment(self):
        #添加节段
        assert len(self.segments)>1#小于1无法添加
        sg=2*self.segments[-1]-self.segments[-2]
        self.segments.append(sg)




if __name__ == '__main__':
    global DISPLAYSURF,snake

    pygame.init()
    SnakespeedCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((Window_Width, Window_Height))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Snake')

    #初始化蛇
    snake=Snake(direction=UP)
    #刷新食物
    food=spawn_food()


    while True:
        #检查是否游戏结束
        if snake.check_gameover()==True:
            show_gameover_screen()
        #画网格
        drawGrid()

        #处理用户事件
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_LEFT :
                    snake.direction = LEFT
                elif event.key == K_RIGHT:
                    snake.direction = RIGHT
                elif event.key == K_UP:
                    snake.direction = UP
                elif event.key == K_DOWN:
                    snake.direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        #更新蛇
        snake.update()
        #检查是否吃到food
        if snake.segments[0]==food:#吃到
            snake.add_segment()#添加节段
            food=spawn_food()#更新食物
        # 画蛇
        snake.draw()
        # 画食物
        draw_food(food)

        #收尾工作
        pygame.display.update()
        SnakespeedCLOCK.tick(fps)

