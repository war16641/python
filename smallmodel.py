import math
import random

def one_dimensional_collision_problem(m1,m2,v10=0,v20=0,e=1):
    """
    一维碰撞问题
    :param m1: 质量  在前面的球 与速度同向
    :param m2:质量 在后面的球
    :param v10: 初速度
    :param v20:
    :param e: 弹性系数 介于0到1       当等于1时，满足能量守恒
    :return: 碰撞后的两个速度
    """
    assert m1!=0 and m2!=0
    assert v20>v10
    # v1=(m1*v10 + m2*v20 + e*m2*v10 - e*m2*v20)/(m1 + m2)
    # v2=(m1*v10 + m2*v20 - e*m1*v10 + e*m1*v20)/(m1 + m2)
    v1=(m1*v10 + m2*v20 - e*m2*v10 + e*m2*v20)/(m1 + m2)
    v2=(m1*v10 + m2*v20 + e*m1*v10 - e*m1*v20)/(m1 + m2)
    return v1,v2


class NoCollisionError(Exception):
    """不会发生碰撞"""
    pass

def two_dimensional_collision_problem(m1,m2,from_m2_to_m1,v10,v20,e):
    """
    二维碰撞问题
    原理：将M1m2的速度分解到两者连线方向和垂直连线方向 连线方向上的速度满足一维碰撞 垂直连线的速度不变
    :param m1:
    :param m2:
    :param from_m2_to_m1: Vector 向量从一质心指向令一个质心
    :param v10: Vector速度
    :param v20:
    :param e: 弹性恢复系数
    :return: Vector 碰撞后的两个速度
    """
    assert m1 != 0 and m2 != 0
    from_m2_to_m1.modulus=1
    v10e=from_m2_to_m1*v10
    v20e=from_m2_to_m1*v20 # 将速度投影到质心连线上
    v10_idle=v10-from_m2_to_m1*v10e
    v20_idle = v20 - from_m2_to_m1 * v20e # 速度垂直于连线的分量

    # 判断谁在前面
    if v20e>v10e:
        v1e,v2e=one_dimensional_collision_problem(m1=m1,
                                                  m2=m2,
                                                  v10=v10e,
                                                  v20=v20e,
                                                  e=e)
        v1=from_m2_to_m1*v1e+v10_idle
        v2 = from_m2_to_m1 * v2e + v20_idle
        return v1,v2
    else:
        raise NoCollisionError("没法相撞")




if __name__ == '__main__':
    # m1=1
    # m2=2
    # v10=random.uniform(-2,2)
    # v20=random.uniform(-2,2)
    # v1,v2=one_dimensional_collision_problem(m1,m2,v10,v20,1)
    # print("动量：%f > %f,%f"%(m1*v10+m2*v20,m1*v1+m2*v2,m1*v1+m2*v2-m1*v10-m2*v20))
    # print("能量：%f > %f,%f"%(m1*v10**2+m2*v20**2,m1*v1**2+m2*v2**2,m1*v1**2+m2*v2**2-m1*v10**2-m2*v20**2))


    m1=1
    m2=1
    v10=-5
    v20=0
    v1, v2 = one_dimensional_collision_problem(m1, m2, v10, v20, 1)
    print("速度: m1=%f>%f, m2=%f>%f"%(v10,v1,v20,v2))
    # assert (m1*v10+m2*v20) == (m1*v1+m2*v2) and (m1*v10**2+m2*v20**2 == m1*v1**2+m2*v2**2)