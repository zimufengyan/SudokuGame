# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name :      solver
   Author :         zmfy
   DateTime :       2023/5/18 14:19
   Description :    solver to Sudoku-v1
-------------------------------------------------
"""
import random
from copy import deepcopy
from typing import Set, Tuple, List
import numpy as np


class SudokuSolver:
    def __init__(self, sudoku):
        if len(sudoku) == 0:
            raise ValueError("")
        elif len(sudoku[0]) != len(sudoku):
            raise ValueError("")

        self.type = 9  # 9x9
        self.sudoku = deepcopy(sudoku)
        self.iter = 0  # 迭代次数

    def solve(self, shuffle=False):
        state = self.update_state()

        def search(state) -> bool:
            if len(state) == 0 and self.is_valid():
                return True
            x, y, remaining = self.get_least_remaining(state, shuffle)
            for val in remaining:
                self.sudoku[x, y] = val
                new_state = self.update_state()
                self.iter += 1
                if search(new_state) is True:
                    return True
                self.sudoku[x, y] = 0

        search(state)
        return self.sudoku
    
    def count_solution(self) -> int:
        # 计算当前数独的可行解数量
        sudoku = deepcopy(self.sudoku)
        
        def search(cnt, count):
            if count > 1:
                return count
            if cnt >= self.type ** 2:
                count += 1
                return count
            r, c = divmod(cnt, self.type)
            if self.sudoku[r, c] > 0:
                count = search(cnt + 1, count)
            else:
                remaining = self.get_remaining(r, c)
                for val in remaining:
                    self.sudoku[r, c] = val
                    count = search(cnt + 1, count)
                    self.sudoku[r, c] = 0
            return count

        count = search(0, 0)
        self.sudoku = sudoku
        return count

    def update_state(self) -> dict:
        state = dict()
        for i in range(self.type):
            for j in range(self.type):
                if self.sudoku[i, j] == 0:  # 0 代表未填充
                    key = i * self.type + j
                    remaining = self.get_remaining(i, j)
                    state[key] = remaining
        return state
    
    def get_least_remaining(self, state : dict, shuffle=False) -> Tuple[int, int, List[int]]:
        items = list(state.items())
        if shuffle:
            np.random.shuffle(items)
        pos, remaining = sorted(items, key=lambda x: len(x[1]), reverse=False)[0]
        remaining = list(remaining)
        if shuffle:
            np.random.shuffle(remaining)
        row = pos // self.type
        col = pos % self.type
        return (row, col, remaining)

    def get_remaining(self, x, y) -> Set[int]:
        # 计算(x, y) 位置的候选解数量和候选解
        r = x // 3 * 3
        c = y // 3 * 3
        res = {1, 2, 3, 4, 5, 6, 7, 8, 9}
        return res.difference(set(self.sudoku[r:r + 3, c:c + 3].flat)). \
            difference(set(self.sudoku[x, :])).difference(set(self.sudoku[:, y]))

    def is_valid(self):
        # 检查数独是否合法，即其是否满足数独规则
        rows = [[0 for i in range(self.type)] for j in range(self.type)]
        cols = [[0 for i in range(self.type)] for j in range(self.type)]
        boxes = [[[0 for j in range(self.type)] for i in range(3)] for k in range(3)]
        for i in range(self.type):
            for j in range(self.type):
                index = self.sudoku[i, j] - 1
                if index == -1:
                    return False
                rows[i][index] += 1
                cols[j][index] += 1
                boxes[i // 3][j // 3][index] += 1
                if rows[i][index] > 1 or cols[j][index] > 1 or boxes[i // 3][j // 3][index] > 1:
                    return False
        return True

    def plot(self):
        for i in range(self.type):
            print(self.sudoku[i])


if __name__ == '__main__':
    sudoku = [[0, 0, 0, 0, 0, 0, 1, 7, 4],
              [0, 2, 0, 0, 0, 0, 8, 0, 0],
              [9, 8, 0, 0, 0, 0, 5, 0, 0],
              [0, 6, 3, 9, 0, 0, 2, 0, 8],
              [0, 0, 0, 5, 0, 0, 0, 4, 0],
              [0, 0, 0, 0, 0, 8, 0, 0, 3],
              [1, 0, 0, 0, 4, 0, 7, 0, 5],
              [7, 0, 0, 0, 0, 0, 0, 0, 0],
              [0, 0, 8, 0, 1, 7, 0, 0, 0]]
    sudoku = np.array(sudoku, dtype=np.int32)
    print("--------原始数独--------")
    for i in range(sudoku.shape[0]):
        print(sudoku[i])
    solver = SudokuSolver(sudoku=sudoku)
    print("可行解数量: ", solver.count_solution())
    solver.solve(shuffle=False)
    print("--------求解结果--------")
    solver.plot()
    print("迭代次数: ", solver.iter)