import matplotlib.pyplot as plt
import numpy as np


class SnaptoCursor:
    """
    自动捕捉到最近的数据点
    可以支持axes有多条线
    但是要求：这些线的x数据是递增的 不然判断最近会出差错
    在figure上按下f1，会开启或者关闭自动捕捉
    使用方法：SnaptoCursor(axes)即可
    支持双y轴
    """

    def __init__(self, ax, txt_pos=(0.7, 0.9), txt_format="%.2f,%.2f"):
        """

        @param ax:
        @param txt_pos: txt位置 介于0,1
        @param txt_format: txt格式
        """
        self.ax = ax  # axes
        self.lx = ax.axhline(color='k', linewidth=1)  # the horiz line
        self.ly = ax.axvline(color='k', linewidth=1)  # the vert line
        self.axes_refline = ax  # lx ly所在的axes

        # text location in axes coords
        self.txt_pos = txt_pos
        self.txt_format = txt_format
        self.txt = ax.text(self.txt_pos[0], self.txt_pos[1], '', transform=ax.transAxes)
        self.snap_active = True  # 是否捕捉
        # 绑定事件
        ax.figure.canvas.mpl_connect('motion_notify_event', self.mouse_move)
        ax.figure.canvas.mpl_connect('key_press_event', self.onpress)

    def mouse_move(self, event):
        # print(event.inaxes)
        if not event.inaxes or not self.snap_active:
            # 不再画图区域内的 和 未打开active的 返回
            return

        # 收集鼠标在各个axes中的坐标
        xy_in_axes = []  # 在各个axes中的坐标 最多两个
        for ax1 in self.ax.figure.axes:
            inv = ax1.transData.inverted()
            t1, t2 = inv.transform((event.x, event.y))  # 得到在ax中的坐标
            xy_in_axes.append((t1, t2))

        # 生成x y距离的缩放比例：axes中距离对应到像素距离
        scales = {}
        for ax1 in self.ax.figure.axes:
            t1 = ax1.bbox.width / ax1.viewLim.width
            t2 = ax1.bbox.height / ax1.viewLim.height
            scales[id(ax1)] = (t1, t2,)

        # 在各个axes上 axes各个线上寻找最近的点
        neareast_points = []  # 每条线上最近的点
        for i1, ax1 in enumerate(self.ax.figure.axes):
            xui, yui = xy_in_axes[i1]  # 当前axes下的鼠标坐标
            for ln in ax1.lines:
                if ln is self.lx or ln is self.ly:
                    continue  # 跳过十字线
                x1 = ln.get_xdata()
                y1 = ln.get_ydata()
                indx = min(np.searchsorted(x1, xui), len(x1) - 1)  # 假设x数据是递增的
                neareast_points.append((x1[indx], y1[indx], ax1, xui, yui))  # x y 点 和这个点对应的axes,和鼠标在这个axes上的坐标
                # 缩放到fig的像素尺寸上

        # 在neareast_points中再找最近的
        neareast_points.sort(
            key=lambda x: (x[0] - x[3]) ** 2 * scales[id(x[2])][0] ** 2 + (x[1] - x[4]) ** 2 * scales[id(x[2])][
                1] ** 2)  # 按距离的平方排序 计算距离时，用当前点坐标减去鼠标在当前axes中的坐标 乘以axes坐标缩放到图素的系数
        x = neareast_points[0][0]
        y = neareast_points[0][1]
        # update the line positions
        # 先删除之前的线
        self.axes_refline.lines.remove(self.lx)
        self.axes_refline.lines.remove(self.ly)
        # 在建立新的线
        self.axes_refline = neareast_points[0][2]
        self.lx = self.axes_refline.axhline(color='k', linewidth=1)  # the horiz line
        self.ly = self.axes_refline.axvline(color='k', linewidth=1)  # the vert line
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)
        # st=['x=%.2f, y=%.2f' % (x, y) for x,y in xy_in_axes]
        # st1=",".join(st)
        self.txt.set_text(self.txt_format % (x, y))
        # print('x=%1.2f, y=%1.2f' % (x, y))
        self.ax.figure.canvas.draw()

    def onpress(self, evt=None):
        if evt.key == 'f1':
            self.snap_active = False if self.snap_active else True  # 切换真假值
            ax = self.ax
            if self.snap_active is False:  # 清除线
                self.axes_refline.lines.remove(self.lx)
                self.axes_refline.lines.remove(self.ly)
                ax.texts.remove(self.txt)
            else:  # 添加线
                self.lx = self.axes_refline.axhline(color='k', linewidth=1)  # the horiz line
                self.ly = self.axes_refline.axvline(color='k', linewidth=1)  # the vert line
                self.txt = ax.text(self.txt_pos[0], self.txt_pos[1], '', transform=ax.transAxes)
                # del self.lx
                # del self.ly
            self.ax.figure.canvas.draw()

        # print(evt.key)


if __name__ == '__main__':
    t = np.arange(0.0, 1.0, 0.01)
    s = np.sin(2 * 2 * np.pi * t) * 100
    s1 = np.cos(2 * 2 * np.pi * t) * 1
    # t = np.arange(0.0, 1.0, 0.1)
    # s = t*100
    # s1=t*-1

    fig1, ax = plt.subplots()
    ln1 = ax.plot(t, s, 'o')
    ax1 = ax.twinx()
    ax1.plot(t, s1, '+')
    snap_cursor1 = SnaptoCursor(ax)

    fig, ax = plt.subplots()
    ln1 = ax.plot(t, s, 'o')
    ax.plot(t, s1, '+')
    snap_cursor = SnaptoCursor(ax)
    plt.show()