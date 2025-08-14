import math
import random
import numpy as np
from game_logic import check_win

# 棋型分数
SCORE_FIVE = 10000000  # 连五
SCORE_FOUR = 100000  # 活四
SCORE_BLOCKED_FOUR = 10000  # 冲四
SCORE_THREE = 1000  # 活三
SCORE_BLOCKED_THREE = 100  # 眠三
SCORE_TWO = 100  # 活二
SCORE_BLOCKED_TWO = 10  # 眠二


def evaluate_position(board, player, x, y):
    BOARD_SIZE = len(board)
    if board[y][x] != 0:
        return 0

    directions = [
        (1, 0),  # 水平
        (0, 1),  # 垂直
        (1, 1),  # 对角线
        (1, -1)  # 反对角线
    ]

    score = 0

    for dx, dy in directions:
        # 检查两个方向
        line = []

        # 收集9个点的信息（当前点+两边各4个点）
        for i in range(-4, 5):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                line.append(board[ny][nx])
            else:
                line.append(-1)  # 边界

        # 评估当前方向
        center_index = 4  # 中心点（当前空位）
        player_score = evaluate_line(line, center_index, player)
        opponent = 3 - player
        opponent_score = evaluate_line(line, center_index, opponent)

        # 优先防守对手的进攻
        if opponent_score >= SCORE_FOUR:
            score += opponent_score * 2  # 紧急防守
        else:
            score += player_score + opponent_score * 0.7

    # 中心位置加分
    center_x, center_y = BOARD_SIZE // 2, BOARD_SIZE // 2
    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    score += max(0, 100 - distance * 5)

    return score


def evaluate_line(line, center_index, player):
    """评估一条线上的棋型"""
    score = 0

    # 计算连续棋子
    count = 0
    block_left = 0
    block_right = 0

    # 向左检查
    for i in range(center_index - 1, -1, -1):
        if line[i] == player:
            count += 1
        else:
            if line[i] == -1 or line[i] != 0:  # 边界或对手棋子
                block_left = 1
            break

    # 向右检查
    for i in range(center_index + 1, len(line)):
        if line[i] == player:
            count += 1
        else:
            if line[i] == -1 or line[i] != 0:  # 边界或对手棋子
                block_right = 1
            break

    # 计算棋型
    total_block = block_left + block_right

    # 连五
    if count >= 4:
        return SCORE_FIVE

    # 活四
    if count == 3 and total_block == 0:
        return SCORE_FOUR

    # 冲四
    if count == 3 and total_block == 1:
        return SCORE_BLOCKED_FOUR

    # 活三
    if count == 2 and total_block == 0:
        return SCORE_THREE

    # 眠三
    if count == 2 and total_block == 1:
        return SCORE_BLOCKED_THREE

    # 活二
    if count == 1 and total_block == 0:
        return SCORE_TWO

    # 眠二
    if count == 1 and total_block == 1:
        return SCORE_BLOCKED_TWO

    return score


def get_candidate_moves(board, player, n=8):
    """获取候选移动位置（只考虑已有棋子周围的点）"""
    BOARD_SIZE = len(board)
    candidate_moves = []
    opponent = 3 - player

    # 优先检查对手的潜在连五位置
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == 0:
                # 检查周围是否有棋子
                has_neighbor = False
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        if dy == 0 and dx == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                            if board[ny][nx] != 0:
                                has_neighbor = True
                                break
                    if has_neighbor:
                        break

                if has_neighbor:
                    # 评估对手在这个位置落子的威胁
                    score = evaluate_position(board, opponent, x, y)
                    candidate_moves.append((x, y, score))

    # 如果没有候选点，返回中心点
    if not candidate_moves:
        center = BOARD_SIZE // 2
        candidate_moves.append((center, center, 100))
        return candidate_moves

    # 按分数排序
    candidate_moves.sort(key=lambda move: move[2], reverse=True)

    # 只返回前n个候选点
    return candidate_moves[:n]


def minmax(board, player, depth, alpha, beta):
    """Minimax算法，带alpha-beta剪枝"""
    if depth == 0:
        return 0, None

    opponent = 3 - player
    candidate_moves = get_candidate_moves(board, player)

    # 检查游戏是否结束
    if check_win(board, player):
        return SCORE_FIVE, None
    if check_win(board, opponent):
        return -SCORE_FIVE, None

    best_score = -float('inf')
    best_move = None

    for x, y, _ in candidate_moves:
        if board[y][x] != 0:
            continue

        # 尝试落子
        board[y][x] = player

        # 递归评估
        score, _ = minmax(board, opponent, depth - 1, -beta, -alpha)
        score = -score

        # 撤销落子
        board[y][x] = 0

        if score > best_score:
            best_score = score
            best_move = (x, y)

        # Alpha-beta剪枝
        if best_score > alpha:
            alpha = best_score
        if alpha >= beta:
            break

    return best_score, best_move


def ai_move(board, player):
    BOARD_SIZE = len(board)

    # 第一步下在中心
    center = BOARD_SIZE // 2
    if board[center][center] == 0 and sum(sum(row) for row in board) == 0:
        return (center, center)

    # 使用Minimax算法（深度3）
    _, move = minmax(board, player, 3, -float('inf'), float('inf'))
    if move:
        return move

    # 如果Minimax失败，使用启发式方法
    candidate_moves = get_candidate_moves(board, player)
    if candidate_moves:
        return candidate_moves[0][:2]  # 返回分数最高的候选点

    # 如果没有找到好的移动，随机选择
    empty_cells = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if board[y][x] == 0]
    if empty_cells:
        return random.choice(empty_cells)
    return None