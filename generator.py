# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :      generator
   Author :         zmfy
   DateTime :       2023/5/18 22:27
   Description :    Sudoku-v1 generator
-------------------------------------------------
"""
import random
from copy import deepcopy
import numpy as np
from solver import SudokuSolver


class SudokuGenerator:
    def __init__(self, size=9):
        self.type = size
        self.sudoku = np.zeros(shape=(self.type, self.type), dtype=np.int32)
        self.answer = None

    def generate(self, level='easy'):
        """
        生成数独
        :param level:难度，表现在移除的数字数量，easy: 40-45, normal: 46-50,
        hard: 51-55, expert: 55-60, extreme: 60-64
        """
        solver = SudokuSolver(self.sudoku)
        solver.solve(shuffle=True)
        self.sudoku = deepcopy(solver.sudoku)
        self.answer = deepcopy(solver.sudoku)
        random_list = list(range(self.type ** 2))
        np.random.shuffle(random_list)

        def dig_holes(random_list, cnt, amount):
            if cnt == amount:
                return
            x, y = divmod(random_list[cnt], self.type)
            if self.sudoku[x, y] > 0:
                sudoku = deepcopy(self.sudoku)
                sudoku[x, y] = 0        # 尝试移除该位置的解
                count = SudokuSolver(sudoku).count_solution()
                if count == 1:      # 移除后如果可行解仍唯一，则可以移除
                    self.sudoku[x, y] = 0
            dig_holes(random_list, cnt+1, amount)

        if level == 'easy':
            hole_amount = np.random.choice(list(range(40, 45)))
        elif level == 'normal':
            hole_amount = np.random.choice(list(range(45, 50)))
        elif level == 'hard':
            hole_amount = np.random.choice(list(range(50, 55)))
        elif level == 'perfessional':
            hole_amount = np.random.choice(list(range(55, 60)))
        elif level == 'extreme':
            hole_amount = np.random.choice(list(range(60, 65)))
        else:
            raise ValueError('param "level" should be easy, normal, hard, perfessional or extreme.')
        dig_holes(random_list, 0, hole_amount)
        
        return self.sudoku

    def plot(self):
        for i in range(self.type):
            print(self.sudoku[i])

    def plot_answer(self):
        for i in range(self.type):
            print(self.answer[i])
            
            
if __name__ == '__main__':
    generator = SudokuGenerator()
    generator.generate(level='extreme')
    print("--------生成结果--------")
    generator.plot()
    print("--------可行解--------")
    generator.plot_answer()
    solver = SudokuSolver(generator.sudoku)
    solver.solve()
    print("--------求解结果--------")
    solver.plot()
    if np.array_equal(generator.answer, solver.sudoku) is True:
        print("求解结果一致")
    else:
        print("求解结果不一致")


