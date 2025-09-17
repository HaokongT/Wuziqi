import math
import random
import numpy as np
from game_logic import check_win

SCORE_FIVE = 10000000
SCORE_FOUR = 100000
SCORE_BLOCKED_FOUR = 10000
SCORE_THREE = 1000
SCORE_BLOCKED_THREE = 100
SCORE_TWO = 100
SCORE_BLOCKED_TWO = 10

def evaluate_position(board, player, x, y):
    BOARD_SIZE = len(board)
    if board[y][x] != 0:
        return 0

    directions = [
        (1, 0),
        (0, 1),
        (1, 1),
        (1, -1)
    ]

    score = 0

    for dx, dy in directions:
        line = []

        for i in range(-4, 5):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                line.append(board[ny][nx])
            else:
                line.append(-1)

        center_index = 4
        player_score = evaluate_line(line, center_index, player)
        opponent = 3 - player
        opponent_score = evaluate_line(line, center_index, opponent)

        if opponent_score >= SCORE_FOUR:
            score += opponent_score * 2
        else:
            score += player_score + opponent_score * 0.7

    center_x, center_y = BOARD_SIZE // 2, BOARD_SIZE // 2
    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    score += max(0, 100 - distance * 5)

    return score

def evaluate_line(line, center_index, player):
    score = 0

    count = 0
    block_left = 0
    block_right = 0

    for i in range(center_index - 1, -1, -1):
        if line[i] == player:
            count += 1
        else:
            if line[i] == -1 or line[i] != 0:
                block_left = 1
            break

    for i in range(center_index + 1, len(line)):
        if line[i] == player:
            count += 1
        else:
            if line[i] == -1 or line[i] != 0:
                block_right = 1
            break

    total_block = block_left + block_right

    if count >= 4:
        return SCORE_FIVE

    if count == 3 and total_block == 0:
        return SCORE_FOUR

    if count == 3 and total_block == 1:
        return SCORE_BLOCKED_FOUR

    if count == 2 and total_block == 0:
        return SCORE_THREE

    if count == 2 and total_block == 1:
        return SCORE_BLOCKED_THREE

    if count == 1 and total_block == 0:
        return SCORE_TWO

    if count == 1 and total_block == 1:
        return SCORE_BLOCKED_TWO

    return score

def get_candidate_moves(board, player, n=15):
    BOARD_SIZE = len(board)
    candidate_moves = []
    opponent = 3 - player

    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            if board[y][x] == 0:
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
                    score = evaluate_position(board, opponent, x, y)
                    candidate_moves.append((x, y, score))

    if not candidate_moves:
        center = BOARD_SIZE // 2
        candidate_moves.append((center, center, 100))
        return candidate_moves

    candidate_moves.sort(key=lambda move: move[2], reverse=True)

    return candidate_moves[:n]

def minmax(board, player, depth, alpha, beta):
    if depth == 0:
        return 0, None

    opponent = 3 - player
    candidate_moves = get_candidate_moves(board, player)

    if check_win(board, player):
        return SCORE_FIVE, None
    if check_win(board, opponent):
        return -SCORE_FIVE, None

    best_score = -float('inf')
    best_move = None

    for x, y, _ in candidate_moves:
        if board[y][x] != 0:
            continue

        board[y][x] = player

        score, _ = minmax(board, opponent, depth - 1, -beta, -alpha)
        score = -score

        board[y][x] = 0

        if score > best_score:
            best_score = score
            best_move = (x, y)

        if best_score > alpha:
            alpha = best_score
        if alpha >= beta:
            break

    return best_score, best_move

def ai_move(board, player):
    BOARD_SIZE = len(board)

    center = BOARD_SIZE // 2
    if board[center][center] == 0 and sum(sum(row) for row in board) == 0:
        return (center, center)

    _, move = minmax(board, player, 5, -float('inf'), float('inf'))
    if move:
        return move

    candidate_moves = get_candidate_moves(board, player)
    if candidate_moves:
        return candidate_moves[0][:2]

    empty_cells = [(x, y) for y in range(BOARD_SIZE) for x in range(BOARD_SIZE) if board[y][x] == 0]
    if empty_cells:
        return random.choice(empty_cells)
    return None