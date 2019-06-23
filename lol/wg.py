import sys
sys.path.append("F:\我的文档\python_file")
sys.path.append("F:\我的文档\python_file\GoodToolPython")
from GoodToolPython.lol.knn import *
from GoodToolPython.lol.script import get_xxg
import time
import winsound
class Detect_Failed(Exception):
    pass
def detect_information(knn):
    """
    探测所有的相关信息
    :param knn:
    :return:
    """
    hp, level, ad, ap = detect_my_hero(knn)
    hp_emy, armor_ad, armor_ap = detect_enemy(knn)
    winsound.Beep(500,440)
    if hp is None:
        hp_max = 0
    else:
        try:
            tmp = hp.split('f')
            hp_max = float(tmp[1])
        except:
            print("hp值异常:%s" % hp)
            hp_max = 0

    if level is None:
        raise Detect_Failed("等级未探测")
    else:
        level = int(level)

    if ad is None:
        ad = 0
    else:
        try:
            ad = float(ad)
        except Exception:
            print("ad值异常:%s"%ad)
            ad=60

    if ap is None:
        raise Detect_Failed("ap未探测")
    else:
        try:
            ap = float(ap)
        except Exception:
            print("ap值异常:%s" % ap)
            ap = 0

    if hp_emy is None:
        hp_emy_max = 10000  # 不知道 按1w算
    else:
        try:
            tmp = hp_emy.split('f')
            hp_emy_max = float(tmp[1])
        except Exception:
            hp_emy_max = 10000

    if armor_ap is None:
        armor_ap = 40.  # 不知道 默认100
    else:
        try:
            armor_ap = float(armor_ap)
        except Exception:
            print("魔抗探测值异常%s"%armor_ap)
            armor_ap=40

    if armor_ad is None:
        armor_ad = 50.
    else:
        try:
            armor_ad = float(armor_ad)
        except Exception:
            print("物抗探测值异常%s" % armor_ad)
            armor_ad=50

    print('探测信息为:')
    print((hp_max,level,ad,ap,))
    print((armor_ad,armor_ap,))
    return hp_max,level,ad,ap,hp_emy_max,armor_ad,armor_ap

if __name__ == '__main__':
    knn=MyKNN()
    time.sleep(2)
    # hp, level, ad, ap = detect_my_hero(knn)
    sleep_inteval=2
    xxg=get_xxg()

    while True:
        try:
            hp_max, level, ad, ap, hp_emy_max, armor_ad, armor_ap=detect_information(knn)
            xxg.level=level
            xxg.hp=hp_max
            xxg.ad=ad
            xxg.ap=ap
            os.system("cls")
            print("法强：%f"%ap)
            print("敌方魔抗:%f"%armor_ap)
            tmp=xxg.combo0(armor_ap=armor_ap)
            print("q技能:%s"%tmp[0])
            print("w技能:%s" % tmp[1])
            print("e技能:%s" % tmp[2])
            print("r技能:%s" % tmp[3])
            print("qe伤害：%s"%xxg.combo1(magic_armor=armor_ap))
            print("qer伤害：%s" % xxg.combo2(magic_armor=armor_ap))
            print("qerq伤害：%s" % xxg.combo3(magic_armor=armor_ap))
        except Detect_Failed:
            print("本次探测失败")
        except Exception as e:
            raise e

        time.sleep(sleep_inteval)
