import matplotlib.pyplot as plt
import numpy as np





class SnaptoCursor:
    """
    自动捕捉到最近的数据点
    可以支持axes有多条线
    但是要求：这些线的x数据是递增的 不然判断最近会出差错
    在figure上按下f1，会开启或者关闭自动捕捉
    使用方法：SnaptoCursor(axes)即可
    """

    def __init__(self, ax):
        self.ax = ax #axes
        self.lx = ax.axhline(color='k',linewidth=1)  # the horiz line
        self.ly = ax.axvline(color='k',linewidth=1)  # the vert line
        # text location in axes coords
        self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)
        self.snap_active=True#是否捕捉
        #绑定事件
        ax.figure.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        ax.figure.canvas.mpl_connect('key_press_event', self.onpress)

    def mouse_move(self, event):
        # print(event.inaxes)
        if not event.inaxes or not self.snap_active:
            #不再画图区域内的 和 未打开active的 返回
            return

        xui, yui = event.xdata, event.ydata
        #寻找最近的点
        neareast_points=[]#每条线上最近的点
        for ln in self.ax.lines:
            if ln is self.lx or ln is self.ly:
                continue#跳过十字线
            x1=ln.get_xdata()
            y1=ln.get_ydata()
            indx = min(np.searchsorted(x1, xui), len(x1) - 1)#假设x数据是递增的
            neareast_points.append((x1[indx],y1[indx]))
        #在neareast_points中再找最近的
        neareast_points.sort(key=lambda x:(x[0]-xui)**2+(x[1]-yui)**2)#按距离的平方排序
        x = neareast_points[0][0]
        y = neareast_points[0][1]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%.4f, y=%.4f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()


    def onpress(self,evt=None):
        if evt.key =='f1':
            self.snap_active=False if self.snap_active else True #切换真假值
            ax=self.ax
            if self.snap_active is False:#清除线
                ax.lines.remove(self.lx)
                ax.lines.remove(self.ly)
                ax.texts.remove(self.txt)
            else:#添加线
                self.lx = ax.axhline(color='k', linewidth=1)  # the horiz line
                self.ly = ax.axvline(color='k', linewidth=1)  # the vert line
                self.txt = ax.text(0.7, 0.9, '', transform=ax.transAxes)
                # del self.lx
                # del self.ly
            self.ax.figure.canvas.draw()

        print(evt.key)

if __name__ == '__main__':

    t = np.arange(0.0, 1.0, 0.01)
    s = np.sin(2 * 2 * np.pi * t)*100
    s1=np.cos(2 * 2 * np.pi * t)*100



    fig, ax = plt.subplots()
    ln1=ax.plot(t, s, 'o')
    ax.plot(t,s1,'+')
    snap_cursor = SnaptoCursor(ax)
    plt.show()