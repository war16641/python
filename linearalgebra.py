import numpy.linalg
import numpy
from enum import Enum, unique


class MyLinearAlgebraEquations:
    """
    线性方程组的求解
    """

    @unique
    class NumOfSolution(Enum):
        no = 0
        one = 1
        many = 2  # 依次是 无解 唯一 无穷

    def __init__(self, A: numpy.matrix, b: numpy.matrix):
        """

        :param a: 系数矩阵
        :param b: 左端值向量
        """
        self.rank_A = numpy.linalg.matrix_rank(A)  # A的秩
        self.rank_Ab = numpy.linalg.matrix_rank(numpy.hstack((A, b)))  # 增广矩阵的秩
        self.num_of_x = A.shape[1]  # 未知数个数
        self.x = None  # 方程的解（当无解时给出最小二乘解）

        # 先判断解的数量
        if self.rank_A == self.rank_Ab:
            if self.num_of_x == self.rank_A:
                self.num_of_solutions = self.NumOfSolution.one  # 正定 有唯一解
            elif self.num_of_x > self.rank_A:
                self.num_of_solutions = self.NumOfSolution.many  # 无穷解
        else:
            self.num_of_solutions = self.NumOfSolution.no

        # 求解

        if self.NumOfSolution.one is self.num_of_solutions:
            self.x = numpy.linalg.solve(a=A, b=b)
        elif self.NumOfSolution.many is self.num_of_solutions:
            (x, res, rank, s) = numpy.linalg.lstsq(a=A, b=b, rcond=None)
            self.x = x  # 给出一个解即可
        else:  # 无解给出最小二乘解
            (x, res, rank, s) = numpy.linalg.lstsq(a=A, b=b, rcond=None)
            self.x = x


if __name__ == '__main__':
    # 测试
    # 唯一解
    A = numpy.matrix([[1, 1, 1],
                      [2, 3, 1],
                      [-1, -1, 3]])
    b = numpy.matrix([[2],
                      [7],
                      [-6]])
    x = numpy.matrix([1, 2, -1])
    sol = MyLinearAlgebraEquations(A=A, b=b)
    assert MyLinearAlgebraEquations.NumOfSolution.one == sol.num_of_solutions
    assert (x.T == sol.x).all()
    t = sol.x

    # print(t)
    # print(type(t))

    # 无穷解
    A = numpy.matrix([[1, 1, 1],
                      [2, 3, 1]])
    b = numpy.matrix([[2],
                      [7]])
    sol = MyLinearAlgebraEquations(A=A, b=b)
    assert MyLinearAlgebraEquations.NumOfSolution.many == sol.num_of_solutions
    assert numpy.linalg.norm(A * sol.x - b) < 1e-10

    # 无解
    A = numpy.matrix([[1, 1, 1],
                      [2, 3, 1],
                      [3, 4, 2]])
    b = numpy.matrix([[2],
                      [7],
                      [-6]])
    sol = MyLinearAlgebraEquations(A=A, b=b)
    assert MyLinearAlgebraEquations.NumOfSolution.no == sol.num_of_solutions
    # assert sol.x is None
    # 测试结束
