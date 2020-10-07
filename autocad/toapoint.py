"""
将vector3d变转换为apoint
"""
from pyautocad import APoint
from vector3d import Vector3D


def to_Apoint(p):
    return APoint(p.x,p.y,p.z)

def myaddarc(acad, center:Vector3D, sp:Vector3D, theta:float):
    """
    画圆弧
    这个方法不受坐标系变换的影响 而pyautocad自带的addarc则会受到坐标系旋转的影响
    @param acad:
    @param center: 圆心坐标
    @param sp: 第一个端点坐标
    @param theta: 弧线对应圆心角（逆时针为正）
    @return:

    """
    r_vec= sp - center
    radius=r_vec.modulus#半径
    theta1=Vector3D.calculate_angle_in_xoy(r_vec.x,r_vec.y)
    return acad.model.addarc(to_Apoint(center),radius,theta1,theta1+theta)
