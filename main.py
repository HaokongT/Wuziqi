import pygame
import sys
import numpy as np
from constants import *
from draw_utils import *
from game_logic import check_win, is_board_full
from ai import ai_move
from progress_bar import ProgressBar
import time

def main():
    pygame.init()
    screen_info = pygame.display.Info()
    SCREEN_WIDTH = min(screen_info.current_w, 1920)
    SCREEN_HEIGHT = min(screen_info.current_h, 1080)

    GRID_SIZE = min(SCREEN_HEIGHT * 0.8 // BOARD_SIZE, SCREEN_WIDTH * 0.8 // BOARD_SIZE)
    # 棋盘居中
    BOARD_PADDING = (SCREEN_WIDTH - (BOARD_SIZE - 1) * GRID_SIZE) // 2
    BOARD_TOP = (SCREEN_HEIGHT - (BOARD_SIZE - 1) * GRID_SIZE) // 2
    STONE_RADIUS = GRID_SIZE * 0.4

    # 创建窗口
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("五子棋 - 竹林幽境")

    # 游戏状态
    game_state = "home"  # home, difficulty_setting, time_setting, playing, game_over, instructions
    player_color = 1  # 1: 黑棋, 2: 白棋
    board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
    last_move = None
    game_over = False
    winner = 0
    move_history = []
    player_thinking = False
    player_timer_start = 0
    player_time_limit = 30
    ai_difficulty = 0  # 默认难度为困难

    debug_enabled = False
    last_debug_output = 0

    bar_width = 300
    bar_height = 20
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = SCREEN_HEIGHT - 50
    player_progress_bar = ProgressBar(bar_x, bar_y, bar_width, bar_height, player_time_limit)

    try:
        title_font = pygame.font.Font("simhei.ttf", 60)
        font = pygame.font.Font("simhei.ttf", 36)
        small_font = pygame.font.Font("simhei.ttf", 28)
    except:
        try:
            title_font = pygame.font.Font("msyh.ttc", 60)
            font = pygame.font.Font("msyh.ttc", 36)
            small_font = pygame.font.Font("msyh.ttc", 28)
        except:
            try:
                title_font = pygame.font.SysFont('Microsoft YaHei', 60)
                font = pygame.font.SysFont('Microsoft YaHei', 36)
                small_font = pygame.font.SysFont('Microsoft YaHei', 28)
            except:
                title_font = pygame.font.Font(None, 60)
                font = pygame.font.Font(None, 36)
                small_font = pygame.font.Font(None, 28)

    # 主游戏循环
    clock = pygame.time.Clock()

    # 用于窗口大小调整的变量
    current_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

    while True:
        # 处理窗口大小调整
        if current_size != screen.get_size():
            SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
            current_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

            # 重新计算尺寸 - 棋盘居中
            GRID_SIZE = min(SCREEN_HEIGHT * 0.8 // BOARD_SIZE, SCREEN_WIDTH * 0.8 // BOARD_SIZE)
            BOARD_PADDING = (SCREEN_WIDTH - (BOARD_SIZE - 1) * GRID_SIZE) // 2
            BOARD_TOP = (SCREEN_HEIGHT - (BOARD_SIZE - 1) * GRID_SIZE) // 2
            STONE_RADIUS = GRID_SIZE * 0.4

            # 更新进度条位置
            bar_width = 300
            bar_height = 20
            bar_x = (SCREEN_WIDTH - bar_width) // 2
            bar_y = SCREEN_HEIGHT - 50
            player_progress_bar.x = bar_x
            player_progress_bar.y = bar_y
            player_progress_bar.width = bar_width
            player_progress_bar.height = bar_height

        mouse_pos = pygame.mouse.get_pos()

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            if event.type == pygame.VIDEORESIZE:
                # 更新窗口尺寸
                SCREEN_WIDTH, SCREEN_HEIGHT = event.w, event.h
                screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
                current_size = (SCREEN_WIDTH, SCREEN_HEIGHT)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game_state == "home":
                    home_buttons = draw_home_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, STONE_RADIUS,
                                                    title_font, font, small_font)
                    for btn_type, rect in home_buttons:
                        if rect.collidepoint(mouse_pos):
                            if btn_type == "black":
                                player_color = 1
                                game_state = "difficulty_setting"
                            elif btn_type == "white":
                                player_color = 2
                                game_state = "difficulty_setting"
                            elif btn_type == "instructions":
                                game_state = "instructions"

                elif game_state == "instructions":
                    # 绘制游玩须知对话框
                    ok_btn_rect = draw_instructions_dialog(screen, SCREEN_WIDTH, SCREEN_HEIGHT, font, small_font)
                    if ok_btn_rect.collidepoint(mouse_pos):
                        game_state = "home"

                elif game_state == "difficulty_setting":
                    difficulty_buttons = draw_difficulty_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                                                                title_font, font, small_font)
                    for i, rect in enumerate(difficulty_buttons):
                        if rect.collidepoint(mouse_pos):
                            if i == 0:
                                ai_difficulty = 3  # 简单
                            elif i == 1:
                                ai_difficulty = 4  # 正常
                            elif i == 2:
                                ai_difficulty = 5  # 困难

                            game_state = "time_setting"

                elif game_state == "time_setting":
                    time_buttons = draw_time_setting_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                                                            title_font, font, small_font)
                    for i, rect in enumerate(time_buttons):
                        if rect.collidepoint(mouse_pos):
                            if i == 0:
                                player_time_limit = 30
                            elif i == 1:
                                player_time_limit = 60
                            elif i == 2:
                                player_time_limit = 120
                            else:
                                player_time_limit = 0

                            # 更新进度条总时间（无限时间设置为0）
                            player_progress_bar.total_time = player_time_limit

                            game_state = "playing"

                            # 重置进度条
                            player_progress_bar.reset()

                            # 如果玩家选择白棋，AI先下
                            if player_color == 2:
                                x, y = BOARD_SIZE // 2, BOARD_SIZE // 2
                                board[y][x] = 1
                                last_move = (x, y)
                                move_history.append((x, y))
                                # 玩家回合开始
                                player_thinking = True
                                player_timer_start = pygame.time.get_ticks()
                                if player_time_limit > 0:
                                    player_progress_bar.start()
                            else:
                                # 玩家选择黑棋，玩家先手
                                player_thinking = True
                                player_timer_start = pygame.time.get_ticks()
                                if player_time_limit > 0:
                                    player_progress_bar.start()

                elif game_state == "playing":
                    # 检查控制按钮
                    control_buttons = draw_control_panel(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_color,
                                                         game_over, winner, font, small_font)
                    for i, (text, rect) in enumerate(control_buttons):
                        if rect.collidepoint(mouse_pos):
                            if text == "退出":
                                pygame.quit()
                                sys.exit()
                            elif text == "和棋":
                                game_over = True
                                winner = 0
                                game_state = "game_over"
                                player_thinking = False
                            elif text == "悔棋":
                                # 只有在至少有两步棋的情况下才能悔棋
                                if len(move_history) >= 2:
                                    # 移除最后两步棋（玩家和AI各一步）
                                    for _ in range(2):
                                        if move_history:
                                            x, y = move_history.pop()
                                            board[y][x] = 0

                                    # 更新最后一步显示
                                    last_move = move_history[-1] if move_history else None

                                    player_thinking = True
                                    player_timer_start = pygame.time.get_ticks()
                                    player_progress_bar.reset()
                                    if player_time_limit > 0:
                                        player_progress_bar.start()

                            # 处理"重新开始"按钮
                            elif text == "重新开始":
                                # 重置游戏状态
                                board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
                                last_move = None
                                game_over = False
                                winner = 0
                                move_history = []
                                player_thinking = False
                                player_progress_bar.reset()

                                # 根据玩家颜色决定谁先手
                                if player_color == 2:  # 玩家选择白棋，AI先下
                                    x, y = BOARD_SIZE // 2, BOARD_SIZE // 2
                                    board[y][x] = 1
                                    last_move = (x, y)
                                    move_history.append((x, y))
                                    # 玩家回合开始
                                    player_thinking = True
                                    player_timer_start = pygame.time.get_ticks()
                                    if player_time_limit > 0:
                                        player_progress_bar.start()
                                else:  # 玩家选择黑棋，玩家先手
                                    player_thinking = True
                                    player_timer_start = pygame.time.get_ticks()
                                    if player_time_limit > 0:
                                        player_progress_bar.start()

                    # 玩家下棋
                    if not game_over and player_thinking:
                        # 计算当前玩家
                        current_player = 1 if len(move_history) % 2 == 0 else 2

                        # 只有当轮到玩家时才能下棋
                        if current_player == player_color:
                            # 计算点击的棋盘位置
                            if (BOARD_PADDING - GRID_SIZE // 2 <= mouse_pos[0] <= BOARD_PADDING +
                                    (BOARD_SIZE - 0.5) * GRID_SIZE and
                                    BOARD_TOP - GRID_SIZE // 2 <= mouse_pos[1] <= BOARD_TOP +
                                    (BOARD_SIZE - 0.5) * GRID_SIZE):

                                x = round((mouse_pos[0] - BOARD_PADDING) / GRID_SIZE)
                                y = round((mouse_pos[1] - BOARD_TOP) / GRID_SIZE)

                                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[y][x] == 0:
                                    board[y][x] = player_color
                                    last_move = (x, y)
                                    move_history.append((x, y))

                                    # 停止玩家计时
                                    player_thinking = False
                                    player_progress_bar.reset()

                                    # 检查胜利
                                    if check_win(board, player_color):
                                        game_over = True
                                        winner = player_color
                                        game_state = "game_over"
                                    elif is_board_full(board):
                                        game_over = True
                                        winner = 0
                                        game_state = "game_over"
                                    else:
                                        # AI下棋
                                        ai_player = 3 - player_color
                                        move = ai_move(board, ai_player, ai_difficulty)
                                        if move:
                                            x, y = move
                                            board[y][x] = ai_player
                                            last_move = (x, y)
                                            move_history.append((x, y))

                                            # 检查胜利
                                            if check_win(board, ai_player):
                                                game_over = True
                                                winner = ai_player
                                                game_state = "game_over"
                                            elif is_board_full(board):
                                                game_over = True
                                                winner = 0
                                                game_state = "game_over"
                                            else:
                                                # 玩家回合开始
                                                player_thinking = True
                                                player_timer_start = pygame.time.get_ticks()
                                                player_progress_bar.reset()
                                                if player_time_limit > 0:
                                                    player_progress_bar.start()

                elif game_state == "game_over":
                    control_buttons = draw_control_panel(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_color,
                                                         game_over, winner, font, small_font)
                    for text, rect in control_buttons:
                        if rect.collidepoint(mouse_pos):
                            if text == "退出":
                                pygame.quit()
                                sys.exit()
                            elif text == "重玩":
                                board = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
                                last_move = None
                                game_over = False
                                winner = 0
                                move_history = []
                                player_thinking = False
                                player_progress_bar.reset()
                                game_state = "home"

        current_time = time.time()
        if debug_enabled and current_time - last_debug_output > 1.0:  # 每秒输出一次
            last_debug_output = current_time
            # 输出游戏状态信息到控制台
            print("\n=== 游戏调试信息 ===")
            print(f"游戏状态: {game_state}")
            print(f"玩家颜色: {'黑棋' if player_color == 1 else '白棋'}")
            print(f"棋盘状态: {np.count_nonzero(board == 1)} 黑棋, {np.count_nonzero(board == 2)} 白棋")
            print(f"最后一步: {last_move}")
            print(f"步数历史: {len(move_history)} 步")
            print(f"游戏结束: {game_over}")
            print(f"胜利者: {winner}")
            print(f"时间限制: {player_time_limit} 秒")
            print(f"游戏难度:{ai_difficulty}")
            print("==================\n")

        if game_state == "playing" and player_thinking and not game_over and player_time_limit > 0:
            time_up = player_progress_bar.update()
            if time_up:
                # 玩家思考时间用完，判玩家失败
                game_over = True
                winner = 3 - player_color
                game_state = "game_over"
                player_thinking = False

        # 绘制游戏
        screen.fill(BACKGROUND)

        if game_state == "home":
            home_buttons = draw_home_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, STONE_RADIUS,
                                            title_font, font, small_font)
        elif game_state == "instructions":
            # 绘制主界面背景
            draw_home_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, STONE_RADIUS,
                             title_font, font, small_font)
            # 绘制游玩须知对话框
            draw_instructions_dialog(screen, SCREEN_WIDTH, SCREEN_HEIGHT, font, small_font)
        elif game_state == "difficulty_setting":
            difficulty_buttons = draw_difficulty_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                                                        title_font, font, small_font)
        elif game_state == "time_setting":
            time_buttons = draw_time_setting_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                                                    title_font, font, small_font)
        else:
            # 绘制棋盘和棋子
            draw_board(screen, SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_PADDING, BOARD_TOP, GRID_SIZE)
            draw_stone(screen, board, last_move, BOARD_PADDING, BOARD_TOP, GRID_SIZE, STONE_RADIUS)

            # 绘制左上角控制面板
            control_buttons = draw_control_panel(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_color,
                                                 game_over, winner, font, small_font)

            # 显示当前回合
            if not game_over:
                turn_player = "黑棋" if len(move_history) % 2 == 0 else "白棋"
                turn_text = font.render(f"当前回合: {turn_player}", True, WHITE)
                screen.blit(turn_text, (SCREEN_WIDTH - turn_text.get_width() - 20, 120))

            # 绘制进度条
            if player_thinking and player_time_limit > 0:
                player_progress_bar.draw(screen)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()