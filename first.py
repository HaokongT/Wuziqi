OPENING_BOOK = {
    "0" * 225: (7, 7),
    "0" * 112 + "1" + "0" * 112: (7, 6),
    "0" * 112 + "1" + "0" * 55 + "2" + "0" * 56: (8, 7),
    "0" * 48 + "1" + "0" * (112 - 49) + "1" + "0" * (224 - 112): (3, 11)
}

def board_to_string(board):
    return ''.join(str(cell) for row in board for cell in row)

def get_symmetric_boards(board_str):
    size = 15
    symmetries = [board_str]
    # 旋转90度
    rotated90 = []
    for x in range(size):
        for y in range(size-1, -1, -1):
            rotated90.append(board_str[y * size + x])
    symmetries.append(''.join(rotated90))
    # 旋转180度
    symmetries.append(board_str[::-1])
    # 旋转270度
    rotated270 = []
    for x in range(size-1, -1, -1):
        for y in range(size):
            rotated270.append(board_str[y * size + x])
    symmetries.append(''.join(rotated270))
    # 水平翻转
    flipped_h = []
    for y in range(size):
        flipped_h.append(board_str[y*size : (y+1)*size][::-1])
    symmetries.append(''.join(flipped_h))
    return symmetries

def transform_move_for_symmetry(move, original_board_str, current_board_str):
    size = 15
    x, y = move
    current_symmetries = get_symmetric_boards(current_board_str)
    if original_board_str not in current_symmetries:
        return (x, y)
    idx = current_symmetries.index(original_board_str)
    if idx == 1:
        return (y, size - 1 - x)
    elif idx == 2:
        return (size - 1 - x, size - 1 - y)
    elif idx == 3:
        return (size - 1 - y, x)
    elif idx == 4:
        return (size - 1 - x, y)
    return (x, y)

def get_opening_move(board, player):
    board_str = board_to_string(board)
    current_symmetries = get_symmetric_boards(board_str)
    for original_str, move in OPENING_BOOK.items():
        if original_str in current_symmetries:
            transformed_move = transform_move_for_symmetry(move, original_str, board_str)
            tx, ty = transformed_move
            if 0 <= tx < 15 and 0 <= ty < 15 and board[ty][tx] == 0:
                return transformed_move
    return None

def is_very_early_game(board):
    return sum(sum(1 for cell in row if cell != 0) for row in board) < 4