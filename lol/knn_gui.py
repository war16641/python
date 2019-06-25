from GoodToolPython.lol.knn import MyKNN,OCR_FAIL
import wx,time
import threading
from PIL import Image


def ticking(mf):
    ct=1
    while True:
        time.sleep(1)
        while not mf.flag:
            time.sleep(1)
        ct+=1
        evt = MyTestEvent(myEVT_MY_TEST,-1)  # 5 创建自定义事件对象
        evt.SetEventArgs("test event"+str(ct))  # 6添加数据到事件
        mf.GetEventHandler().ProcessEvent(evt)  # 7 处理事件

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

        self.textbox=wx.TextCtrl(panel,-1,"D:/knn/unclassified/9274.bmp",size=(175,-1))
        self.button2 = wx.Button(panel, id=-1, pos=(40, 80), label="打开图片")
        self.Bind(wx.EVT_BUTTON, self.OnButton2Click, self.button2)

        self.button1 = wx.Button(panel, id=-1, pos=(40, 40), label="暂停")
        self.Bind(wx.EVT_BUTTON, self.OnButton1Click, self.button1)
        self.flag = True

        bmp = wx.Image('D:/knn/unclassified/6184.bmp', wx.BITMAP_TYPE_BMP).ConvertToBitmap()
        #显示正在识别的图片
        self.picture_box=wx.StaticBitmap(panel, -1, bmp, (10, 120), (bmp.GetWidth(), bmp.GetHeight()))
        #显示正在识别图片的结果
        self.result_box = wx.StaticText(panel, wx.ID_ANY, "待识别", (40, 120), (100, -1))
        #visualize的图框
        self.pic_boxes=[]
        self.smc_boxes=[]
        self.name_boxes=[]
        for i in range(10):
            pic_box = wx.StaticBitmap(panel, -1, bmp, (0, 140+i*40), (bmp.GetWidth(), bmp.GetHeight()))
            smc_box=wx.StaticText(panel,wx.ID_ANY,"0",(40,140+i*40),(100,-1))
            name_box = wx.StaticText(panel, wx.ID_ANY, "0", (150, 140+i*40), (100, -1))
            self.pic_boxes.append(pic_box)
            self.smc_boxes.append(smc_box)
            self.name_boxes.append(name_box)
        #初始化knn
        self.knn=MyKNN()

    def OnButton1Click(self,evt):
        if self.flag is False:
            self.flag=True
            self.button1.SetLabel("暂停")
        else:
            self.flag=False
            self.button1.SetLabel("继续")

    def get_wx_from_pil(self,pilImage):
        #把pil下的image转化为wx的image
        return wx.Image(pilImage.size[0], pilImage.size[1],pilImage.convert("RGB").tobytes())
    def OnButton2Click(self, event):
        pilImage=Image.open(self.textbox.GetValue())
        self.result_box.SetLabel("待识别")
        self.predict_and_visualize(pilImage)


    def predict_and_visualize(self,im):
        """
        核心函数 knn的predict可视化
        :param im:
        :return:
        """
        bmp = wx.Bitmap(self.get_wx_from_pil(im))
        self.picture_box.SetBitmap(bmp)
        try:
            result,valid_distance_lst=self.knn.predict(im,inspection=True)
            self.result_box.SetLabel(result)
            for i in range(len(valid_distance_lst)):
                if i>9:
                    continue#最多支持10个
                self.smc_boxes[i].SetLabel("%6.4f"%valid_distance_lst[i].similarity)
                self.name_boxes[i].SetLabel(valid_distance_lst[i].point.filename)
                im_tmp=valid_distance_lst[i].point.image
                bmp = wx.Bitmap(self.get_wx_from_pil(im_tmp))
                self.pic_boxes[i].SetBitmap(bmp)
        except OCR_FAIL:
            self.result_box.SetLabel("识别失败")





    def HandleEvt(self,evt):
        # self.SetLabel(evt.GetEventArgs())
        self.predict_and_visualize(evt.GetEventArgs())



gui_pointer=None
def create_gui():
    global gui_pointer
    app = wx.App()
    gui_pointer = MyFrame()
    gui_pointer.Show(True)
    app.MainLoop()



if __name__ == '__main__':
    print(gui_pointer)
    t=threading.Thread(target=create_gui)
    t.start()
    time.sleep(3)
    im=Image.open("D:/knn/unclassified/9274.bmp")
    evt = MyTestEvent(myEVT_MY_TEST, -1)  # 5 创建自定义事件对象
    evt.SetEventArgs(im)  # 6添加数据到事件
    gui_pointer.GetEventHandler().ProcessEvent(evt)  # 7 处理事件
    while True:
        time.sleep(2)
        print(gui_pointer)


