"""一些常用的命令"""
import numpy as np
from GoodToolPython.vector3d import Vector3D

def eigenvalue_problem(A:np.ndarray)->(np.ndarray,np.ndarray):
    """
    求方阵的特征向量 特征值
    :param A:
    :return: eigenvalue按从大到小排列 形状为1*多列
             eigenvector与eigenvalue一一对应 每一列为一个特征向量
    """
    assert isinstance(A,np.ndarray)
    (m,n)=A.shape
    assert m==n,'必须要求是方阵'
    eigenvalue,eigenvector=np.linalg.eig(A)
    tmp=eigenvalue.argsort()
    eigenvalue=eigenvalue[tmp[::-1]]
    eigenvector=eigenvector[:,tmp[::-1]]
    return eigenvalue,eigenvector

def stress_solver(stress:np.ndarray)->():
    """
    对一个应力张量进行分析
    :param stress:
    :return: pricipal_stress,mean_normal_stress,stress_deviator,invariant_of_deviator
            pricipal_stress 三个主应力
            mean_normal_stress 平均正应力
            stress_deviator 应力偏量
            invariant_of_deviator 应力偏量的三个不变量
    """
    assert isinstance(stress, np.ndarray)
    pricipal_stress, _=eigenvalue_problem(stress)
    mean_normal_stress=1/3*pricipal_stress.sum()#平均正应力
    stress_deviator=stress-mean_normal_stress*np.eye(3)#应力偏量
    eigenvalue,_=eigenvalue_problem(stress_deviator)
    invariant_of_deviator=[0,0,0]
    invariant_of_deviator[0]=eigenvalue.sum()
    invariant_of_deviator[1] = -1*(eigenvalue[0]*eigenvalue[1]+eigenvalue[0]*eigenvalue[2]+eigenvalue[1]*eigenvalue[2])
    invariant_of_deviator[2]=eigenvalue[0]*eigenvalue[1]*eigenvalue[2]
    return pricipal_stress,mean_normal_stress,stress_deviator,invariant_of_deviator


if __name__ == '__main__':
    # A = np.array([[3/2,-1/2/2**0.5,-1/2/2**0.5],
    #               [-1/2/2**0.5, 11/4, -5/4],
    #               [-1/2/2**0.5,-5/4,11/4]])
    # stress_solver(A)


    A = np.array([[-10,9,5],
                  [9,0,0],
                  [5,0,8]])
    eigenvalue, eigenvector=eigenvalue_problem(A)
    print(eigenvalue)
    print(eigenvector)
    d1=eigenvector[:,0]
    d2=eigenvector[:,1]
    d3=eigenvector[:,2]
    print(np.mat(d1.reshape(1,3)*np.mat(A)*np.mat(d1.reshape(3,1))))
    d1=Vector3D(d1[0],d1[1],d1[2])
    d2 = Vector3D(d2[0], d2[1], d2[2])
    d3 = Vector3D(d3[0], d3[1], d3[2])
    pass


    # pricipal_stress,mean_normal_stress,stress_deviator,invariant_of_deviator=stress_solver(A)
    # pass
    # A = np.array([[-2,0,0],
    #               [0,-1,0],
    #               [0,0,-1]])
    # pricipal_stress,mean_normal_stress,stress_deviator,invariant_of_deviator=stress_solver(A)
    # print(invariant_of_deviator)
    # A = 2*A
    # pricipal_stress, mean_normal_stress, stress_deviator, invariant_of_deviator = stress_solver(A)
    # print(invariant_of_deviator)

    # A = np.array([[-80,16,26],
    #               [16,26,-28],
    #               [26,-28,-36]])
    # d=np.array([0.25,0.5,11**0.5/4])
    # d=d.reshape(3,1)
    # print(np.mat(d.reshape(1,3))*np.mat(A)*np.mat(d.reshape(3,1)))
    # pass