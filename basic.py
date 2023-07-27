def find_subgrid_index(i, j):
    subgrid_i = (i - 1) // 3 + 1  # 计算行所在的子宫格索引
    subgrid_j = (j - 1) // 3 + 1  # 计算列所在的子宫格索引
    subgrid_index = (subgrid_i - 1) * 3 + subgrid_j  # 计算子宫格索引
    return subgrid_index

def get_subgrid_indices(i, j):
    subgrid_index = find_subgrid_index(i, j)
    # 根据子宫格索引计算子宫格内的所有索引
    subgrid_indices = []
    subgrid_i_start = (subgrid_index - 1) // 3 * 3 + 1
    subgrid_j_start = (subgrid_index - 1) % 3 * 3 + 1
    for row in range(subgrid_i_start, subgrid_i_start + 3):
        for col in range(subgrid_j_start, subgrid_j_start + 3):
            subgrid_indices.append((row, col))
    return subgrid_indices


def calculate_row_column(index: str):
    # index starts from 1, also with row and col.
    row = (index - 1) // 9 + 1
    column = (index - 1) % 9 + 1
    return row, column


def time_conversion(seconds: int) -> str:
    # tansfrom the format of time from second to min:sec.
    minutes = seconds // 60
    seconds = seconds % 60
    return "{:02d}:{:02d}".format(minutes, seconds)


if __name__ == '__main__':
    # 示例用法
    i = 1
    j = 9
    subgrid_indices = get_subgrid_indices(i, j)
    print("索引 ({}, {}) 在第 {} 个子宫格内".format(i, j, find_subgrid_index(i, j)))
    print("子宫格内所有索引：{}".format(subgrid_indices))
    i = 27
    row, column = calculate_row_column(i)
    print("索引{}在第{}行，第{}列".format(i, row, column))

