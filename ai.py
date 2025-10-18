import math
import random
from game_logic import check_win  # 依赖外部胜负判断函数
import first  # 导入精简后的开局库

# 评分常量（定义棋型价值）
SCORE_FIVE = 10000000
SCORE_FOUR = 100000
SCORE_BLOCKED_FOUR = 10000
SCORE_THREE = 1000  
SCORE_BLOCKED_THREE = 100
SCORE_TWO = 100
SCORE_BLOCKED_TWO = 10

def evaluate_line(line, center_index, player_str):
    """评估单条线上的棋型分数（辅助评估函数）"""
    count = 0  # 连续同色棋子数（不含中心位置）
    block_left = 0  # 左侧阻挡（1=阻挡，0=空）
    block_right = 0  # 右侧阻挡

    # 向左统计连续棋子
    for i in range(center_index - 1, -1, -1):
        if line[i] == player_str:
            count += 1
        else:
            # 边界（#）或对方棋子视为阻挡
            if line[i] == '#' or line[i] not in ('0', player_str):
                block_left = 1
            break

    # 向右统计连续棋子
    for i in range(center_index + 1, len(line)):
        if line[i] == player_str:
            count += 1
        else:
            if line[i] == '#' or line[i] not in ('0', player_str):
                block_right = 1
            break

    total_block = block_left + block_right

    # 根据棋型返回分数
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
    return 0


def is_double_two_threat(board, opponent, x, y):
    """检测(x,y)是否被对方的两个活二同时指向（高风险点）"""
    if board[y][x] != 0:
        return False  # 非空位不考虑

    size = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 四个方向
    two_count = 0  # 活二指向该点的数量

    # 模拟对方在(x,y)落子，检查是否形成活二（可发展为活三）
    board[y][x] = opponent  # 临时落子

    for dx, dy in directions:
        # 提取当前方向的9个位置（-4到+4）
        line = []
        for i in range(-4, 5):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < size and 0 <= ny < size:
                line.append(board[ny][nx])
            else:
                line.append(-1)  # 边界标记
        center_idx = 4  # (x,y)在line中的位置

        # 统计当前方向的连续子数（不含中心）和阻挡情况
        left_count = 0
        left_block = 0
        for i in range(center_idx - 1, -1, -1):
            if line[i] == opponent:
                left_count += 1
            else:
                left_block = 1 if line[i] != 0 else 0  # 非空即阻挡
                break

        right_count = 0
        right_block = 0
        for i in range(center_idx + 1, len(line)):
            if line[i] == opponent:
                right_count += 1
            else:
                right_block = 1 if line[i] != 0 else 0
                break

        total_count = left_count + right_count  # 连续子数（不含中心）
        total_block = left_block + right_block

        # 若形成“活二”（连续1子+中心=2子，两端无挡，可发展为活三）
        if total_count == 1 and total_block == 0:
            two_count += 1

    # 回溯（清除临时落子）
    board[y][x] = 0

    # 两个及以上方向的活二指向该点 → 高风险
    return two_count >= 2


def evaluate_position(board, player, x, y):
    """评估落子(x,y)后的全局分数（平衡攻防，区分普通/关键威胁）"""
    size = len(board)
    if board[y][x] != 0:
        return 0  # 非空位置分数为0

    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 四个方向
    score = 0
    opponent = 3 - player

    # 检测当前点是否是对方的“双活二威胁点”（高风险需优先防御）
    is_high_risk = is_double_two_threat(board, opponent, x, y)

    for dx, dy in directions:
        # 提取当前方向的9个位置（-4到+4）
        line = []
        for i in range(-4, 5):
            nx, ny = x + dx * i, y + dy * i
            if 0 <= nx < size and 0 <= ny < size:
                line.append(str(board[ny][nx]))
            else:
                line.append('#')  # 边界标记
        center_index = 4  # 当前落子在line中的位置

        # 计算玩家和对手的分数
        player_score = evaluate_line(line, center_index, str(player))
        opponent_score = evaluate_line(line, center_index, str(opponent))

        # 攻防权重调整（核心优化）：
        if opponent_score >= SCORE_FOUR:
            # 对方高威胁（冲四、活四）：最高优先级防御
            score += opponent_score * 3
        elif is_high_risk and (opponent_score >= SCORE_TWO):
            # 双活二威胁点：次高优先级防御（人类易遗漏）
            score += opponent_score * 2
        else:
            # 普通情况：自身进攻权重 > 对方低威胁防御
            if opponent_score >= SCORE_TWO:
                # 对方单活二/冲二：降低防御权重（0.3倍），优先自身进攻
                score += player_score * 1.2 + opponent_score * 0.3
            else:
                # 无明显威胁：优先自身发展（进攻权重1.5倍）
                score += player_score * 1.5 + opponent_score * 0.5

    # 中心区域加成（鼓励早期抢占中心）
    center_x, center_y = size // 2, size // 2
    distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    score += max(0, 100 - distance * 5)

    return score


def get_candidate_moves(board, player, n=15):
    """获取候选落子（减少搜索范围，优先有邻棋的位置）"""
    size = len(board)
    candidate_moves = []
    opponent = 3 - player

    for y in range(size):
        for x in range(size):
            if board[y][x] == 0:
                # 只保留有邻棋的位置（减少无效计算）
                has_neighbor = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < size and 0 <= ny < size and board[ny][nx] != 0:
                            has_neighbor = True
                            break
                    if has_neighbor:
                        break
                if has_neighbor:
                    # 用评估函数打分，筛选高价值候选
                    score = evaluate_position(board, player, x, y)
                    candidate_moves.append((x, y, score))

    # 若无候选，默认中心
    if not candidate_moves:
        center = size // 2
        return [(center, center, 100)]

    # 按分数排序，取前n个
    candidate_moves.sort(key=lambda m: m[2], reverse=True)
    return candidate_moves[:n]


def check_winning_move(board, player):
    """检查是否有一步必胜的走法（最高优先级）"""
    size = len(board)
    for y in range(size):
        for x in range(size):
            if board[y][x] == 0:
                board[y][x] = player  # 模拟落子
                if check_win(board, player):
                    board[y][x] = 0  # 回溯
                    return (x, y)
                board[y][x] = 0  # 回溯
    return None


def minmax(board, player, depth, alpha, beta):
    """minimax算法（带alpha-beta剪枝，强化进攻倾向）"""
    if depth == 0:
        return 0, None  # 深度为0时返回基础分

    opponent = 3 - player
    candidate_moves = get_candidate_moves(board, player)

    # 检查当前是否已获胜
    if check_win(board, player):
        return SCORE_FIVE, None
    if check_win(board, opponent):
        return -SCORE_FIVE, None

    best_score = -float('inf')
    best_move = None

    for x, y, _ in candidate_moves:
        if board[y][x] != 0:
            continue  # 跳过非空位置

        # 模拟落子
        board[y][x] = player
        # 递归搜索对手的最优解（分数取反）
        score, _ = minmax(board, opponent, depth - 1, -beta, -alpha)
        score = -score

        # 对进攻性走法额外加分（鼓励主动建威胁）
        current_score = evaluate_position(board, player, x, y)
        if current_score >= SCORE_TWO:  # 形成活二及以上进攻型棋型
            score *= 1.1

        # 回溯
        board[y][x] = 0

        # 更新最优解
        if score > best_score:
            best_score = score
            best_move = (x, y)

        # alpha-beta剪枝（加速搜索）
        if best_score > alpha:
            alpha = best_score
        if alpha >= beta:
            break

    return best_score, best_move


def ai_move(board, player, difficulty=5):
    """AI决策入口（平衡攻防优先级，符合人类下棋逻辑）"""
    size = len(board)
    move_count = sum(sum(1 for cell in row if cell != 0) for row in board)

    # 1. 必胜/必防步（不允许失误）
    winning_move = check_winning_move(board, player)
    if winning_move:
        return winning_move
    blocking_move = check_winning_move(board, 3 - player)
    if blocking_move:
        return blocking_move

    # 2. 开局库
    if first.is_very_early_game(board):
        opening_move = first.get_opening_move(board, player)
        if opening_move and board[opening_move[1]][opening_move[0]] == 0:
            # 验证：预设走法需接近AI最优候选（80%评分）
            tx, ty = opening_move
            opening_score = evaluate_position(board, player, tx, ty)
            candidate_moves = get_candidate_moves(board, player, n=3)
            best_candidate_score = max([m[2] for m in candidate_moves]) if candidate_moves else 0
            if opening_score >= best_candidate_score * 0.8:
                return opening_move

    # 3. 核心逻辑
    _, move = minmax(board, player, difficulty, -float('inf'), float('inf'))
    if move:
        return move

    # 4. 兜底方案
    candidate_moves = get_candidate_moves(board, player)
    if candidate_moves:
        return candidate_moves[0][:2]
    empty_cells = [(x, y) for y in range(size) for x in range(size) if board[y][x] == 0]
    return random.choice(empty_cells) if empty_cells else None