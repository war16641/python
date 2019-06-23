"""
自定义事件 多线程
开启线程后 标题每一秒都会变化
按下暂停 继续 会中断 恢复线程的执行
"""
import wx,time
import threading
from GoodToolPython.lol.knn import *
from GoodToolPython.lol.script import get_xxg,Hero
from GoodToolPython.lol.wg import *

def ticking(mf):
    mf.SetLabel('线程已启动')
    # return
    knn=MyKNN()    #初始化knn
    xxg=get_xxg()#吸血鬼对象
    while True:
        time.sleep(5)
        #探测
        try:
            s=mf.SetLabel("开始探测")
            hp_max, level, ad, ap, hp_emy_max, armor_ad, armor_ap = detect_information(knn)
            xxg.level = level
            xxg.hp = hp_max
            xxg.ad = ad
            xxg.ap = ap
            os.system("cls")
            print("法强：%f" % ap)
            print("敌方魔抗:%f" % armor_ap)
            evt = MyTestEvent(myEVT_MY_TEST, -1)  # 5 创建自定义事件对象
            evt.SetEventArgs((xxg, hp_emy_max, armor_ad, armor_ap,))  # 6添加数据到事件
            mf.GetEventHandler().ProcessEvent(evt)  # 7 处理事件
        except Detect_Failed:
            print("本次探测失败")
        finally:
            print('结束探测')





class MyTestEvent(wx.PyCommandEvent):  # 1 定义事件
    def __init__(self, evtType, id):
        wx.PyCommandEvent.__init__(self, evtType, id)
        self.eventArgs = ""

    def GetEventArgs(self):
        return self.eventArgs

    def SetEventArgs(self, args):
        self.eventArgs = args


myEVT_MY_TEST = wx.NewEventType()  # 2 创建一个事件类型
EVT_MY_TEST = wx.PyEventBinder(myEVT_MY_TEST)  # 3 创建一个绑定器对象


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "My Frame", size=(600, 600), pos=(300, 300))
        panel = wx.Panel(self, -1)
        self.Bind(EVT_MY_TEST, self.HandleEvt)  # 4绑定事件处理函数


        #布局
        font=wx.Font(14,wx.DEFAULT,wx.NORMAL,wx.NORMAL)

        self.attribute=wx.StaticText(panel,id=-1,pos=(0,0),label="未探测")
        self.attribute.SetFont(font)

        self.ability_a_hint=wx.StaticText(panel,id=-1,pos=(0,40),label="平a")
        self.ability_a = wx.StaticText(panel, id=-1, pos=(100, 40), label="未探测")
        self.ability_a_hint.SetFont(font)
        self.ability_a.SetFont(font)

        self.ability_q_hint=wx.StaticText(panel,id=-1,pos=(0,80),label="技能q")
        self.ability_q = wx.StaticText(panel, id=-1, pos=(100, 80), label="未探测")
        self.ability_q_hint.SetFont(font)
        self.ability_q.SetFont(font)

        self.ability_w_hint=wx.StaticText(panel,id=-1,pos=(0,120),label="技能w")
        self.ability_w = wx.StaticText(panel, id=-1, pos=(100, 120), label="未探测")
        self.ability_w_hint.SetFont(font)
        self.ability_w.SetFont(font)

        self.ability_e_hint=wx.StaticText(panel,id=-1,pos=(0,160),label="技能e")
        self.ability_e = wx.StaticText(panel, id=-1, pos=(100, 160), label="未探测")
        self.ability_e_hint.SetFont(font)
        self.ability_e.SetFont(font)

        self.ability_r_hint=wx.StaticText(panel,id=-1,pos=(0,200),label="技能r")
        self.ability_r = wx.StaticText(panel, id=-1, pos=(100, 200), label="未探测")
        self.ability_r_hint.SetFont(font)
        self.ability_r.SetFont(font)

        self.combo_1_hint=wx.StaticText(panel,id=-1,pos=(0,240),label="连招qe")
        self.combo_1 = wx.StaticText(panel, id=-1, pos=(100, 240), label="未探测")
        self.combo_1_hint.SetFont(font)
        self.combo_1.SetFont(font)

        self.combo_2_hint = wx.StaticText(panel, id=-1, pos=(0, 280), label="连招qer")
        self.combo_2 = wx.StaticText(panel, id=-1, pos=(100, 280), label="未探测")
        self.combo_2_hint.SetFont(font)
        self.combo_2.SetFont(font)

        self.combo_3_hint = wx.StaticText(panel, id=-1, pos=(0,320), label="连招qerq")
        self.combo_3 = wx.StaticText(panel, id=-1, pos=(100, 320), label="未探测")
        self.combo_3_hint.SetFont(font)
        self.combo_3.SetFont(font)

        self.t=threading.Thread(target=ticking,args=(self,))
        self.t.start()

        # self.button2 = wx.Button(panel, id=-1, pos=(40, 80), label="开启线程")
        # self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)
        #
        # self.button1 = wx.Button(panel, id=-1, pos=(40, 40), label="暂停")
        # self.Bind(wx.EVT_BUTTON, self.OnButton1Click, self.button1)
        # self.flag = True

    # def OnButton1Click(self,evt):
    #     if self.flag is False:
    #         self.flag=True
    #         self.button1.SetLabel("暂停")
    #     else:
    #         self.flag=False
    #         self.button1.SetLabel("继续")
    #
    # def OnButton2Click(self, event):
    #     self.SetLabel('2')
    #     self.t=threading.Thread(target=ticking,args=(self,))
    #     self.t.start()



    def quzheng(self,lst):
        lst[0]=int(lst[0])
        lst[1]=int(lst[1])

    def HandleEvt(self,evt):
        self.SetLabel('收到消息，更新界面中...')
        xxg, hp_emy_max, armor_ad, armor_ap=evt.GetEventArgs()
        assert isinstance(xxg,Hero)

        self.attribute.SetLabel("等级%d,法伤%d,魔抗%d,敌方血量%d"%(xxg.level,xxg.ap,armor_ap,hp_emy_max))

        damage0_after, damage1_after, damage2_after, damage3_after, damage4_after=xxg.combo0(armor_ad=armor_ad,
                                                                                             armor_ap=armor_ap)
        self.quzheng(damage0_after)
        self.quzheng(damage1_after)
        self.quzheng(damage2_after)
        self.quzheng(damage3_after)
        self.quzheng(damage4_after)
        self.ability_a.SetLabel(damage0_after.__str__())
        self.ability_q.SetLabel(damage1_after.__str__())
        self.ability_w.SetLabel(damage2_after.__str__())
        self.ability_e.SetLabel(damage3_after.__str__())
        self.ability_r.SetLabel(damage4_after.__str__())

        c1=xxg.combo1(magic_armor=armor_ap)
        c2 = xxg.combo2(magic_armor=armor_ap)
        c3 = xxg.combo3(magic_armor=armor_ap)
        self.quzheng(c1)
        self.quzheng(c2)
        self.quzheng(c3)
        self.combo_1.SetLabel(c1.__str__())
        self.combo_2.SetLabel(c2.__str__())
        self.combo_3.SetLabel(c3.__str__())
        self.SetLabel('等待新的消息...')
def run():
    app = wx.PySimpleApp()
    frame = MyFrame()
    frame.Show(True)
    app.MainLoop()

if __name__ == '__main__':
    run()

