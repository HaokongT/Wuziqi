# 游戏逻辑

import numpy as np
import math


def check_win(board, player):
    directions = [
        [(0, 1), (0, -1)],  # 垂直
        [(1, 0), (-1, 0)],  # 水平
        [(1, 1), (-1, -1)],  # 对角线
        [(1, -1), (-1, 1)]  # 反对角线
    ]

    for y in range(len(board)):
        for x in range(len(board[0])):
            if board[y][x] != player:
                continue

            for dir_pair in directions:
                count = 1  # 当前位置已经有一个棋子

                # 检查两个相反的方向
                for dx, dy in dir_pair:
                    nx, ny = x, y

                    # 沿着一个方向检查
                    for _ in range(4):
                        nx += dx
                        ny += dy

                        if 0 <= nx < len(board[0]) and 0 <= ny < len(board) and board[ny][nx] == player:
                            count += 1
                        else:
                            break

                if count >= 5:
                    return True
    return False


def is_board_full(board):
    for row in board:
        for cell in row:
            if cell == 0:
                return False
    return True