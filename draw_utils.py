import pygame
import random
import numpy as np
from constants import *


def draw_background(screen, SCREEN_WIDTH, SCREEN_HEIGHT):
    # 绘制纯色背景
    screen.fill(BACKGROUND)


def draw_board(screen, SCREEN_WIDTH, SCREEN_HEIGHT, BOARD_PADDING, BOARD_TOP, GRID_SIZE):
    # 绘制木质棋盘背景
    board_width = GRID_SIZE * (BOARD_SIZE - 1)
    board_rect = pygame.Rect(
        BOARD_PADDING - GRID_SIZE * 0.5,
        BOARD_TOP - GRID_SIZE * 0.5,
        board_width + GRID_SIZE,
        board_width + GRID_SIZE
    )
    pygame.draw.rect(screen, BOARD_COLOR, board_rect)

    # 绘制棋盘纹理
    for i in range(50):
        x = random.randint(board_rect.left, board_rect.right)
        y = random.randint(board_rect.top, board_rect.bottom)
        w = random.randint(5, 30)
        h = random.randint(1, 3)
        pygame.draw.rect(screen, (200, 170, 130), (x, y, w, h))

    # 绘制网格线
    for i in range(BOARD_SIZE):
        # 横线
        pygame.draw.line(
            screen, LINE_COLOR,
            (BOARD_PADDING, BOARD_TOP + i * GRID_SIZE),
            (BOARD_PADDING + (BOARD_SIZE - 1) * GRID_SIZE, BOARD_TOP + i * GRID_SIZE),
            2
        )
        # 竖线
        pygame.draw.line(
            screen, LINE_COLOR,
            (BOARD_PADDING + i * GRID_SIZE, BOARD_TOP),
            (BOARD_PADDING + i * GRID_SIZE, BOARD_TOP + (BOARD_SIZE - 1) * GRID_SIZE),
            2
        )

    # 绘制天元和星位
    star_points = [3, BOARD_SIZE // 2, BOARD_SIZE - 4]
    for x in star_points:
        for y in star_points:
            pygame.draw.circle(
                screen, LINE_COLOR,
                (BOARD_PADDING + x * GRID_SIZE, BOARD_TOP + y * GRID_SIZE),
                5
            )


def draw_stone(screen, board, last_move, BOARD_PADDING, BOARD_TOP, GRID_SIZE, STONE_RADIUS):
    for y in range(BOARD_SIZE):
        for x in range(BOARD_SIZE):
            pos_x = BOARD_PADDING + x * GRID_SIZE
            pos_y = BOARD_TOP + y * GRID_SIZE

            if board[y][x] == 1:  # 黑棋
                pygame.draw.circle(screen, BLACK, (pos_x, pos_y), STONE_RADIUS)
                pygame.draw.circle(screen, (50, 50, 50), (pos_x, pos_y), STONE_RADIUS - 2)
            elif board[y][x] == 2:  # 白棋
                pygame.draw.circle(screen, WHITE, (pos_x, pos_y), STONE_RADIUS)
                pygame.draw.circle(screen, (230, 230, 230), (pos_x, pos_y), STONE_RADIUS - 2)

    # 高亮显示最后一步
    if last_move:
        x, y = last_move
        pos_x = BOARD_PADDING + x * GRID_SIZE
        pos_y = BOARD_TOP + y * GRID_SIZE
        pygame.draw.circle(screen, RED, (pos_x, pos_y), 5)


def draw_control_panel(screen, SCREEN_WIDTH, SCREEN_HEIGHT, player_color, game_over=False, winner=0,
                       font=None, small_font=None):
    if font is None:
        font = pygame.font.Font(None, 36)
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    # 缩小控制面板尺寸并移到左上角
    panel_width = min(SCREEN_WIDTH * 0.15, 200)  # 更小宽度
    # 增加面板高度以容纳更多按钮
    panel_height = min(SCREEN_HEIGHT * 0.25, 220)  # 增加高度
    panel_x = 10  # 左上角
    panel_y = 10  # 左上角

    # 绘制半透明面板
    s = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
    s.fill(PANEL_COLOR)
    screen.blit(s, (panel_x, panel_y))

    # 绘制面板边框
    pygame.draw.rect(screen, GOLD, (panel_x, panel_y, panel_width, panel_height), 2, border_radius=5)

    # 绘制标题
    title = small_font.render("控制台", True, GOLD)
    screen.blit(title, (panel_x + panel_width / 2 - title.get_width() / 2, panel_y + 5))

    # 显示玩家信息
    player_text = small_font.render(f"玩家: {'黑' if player_color == 1 else '白'}", True, TEXT_COLOR)
    screen.blit(player_text, (panel_x + 5, panel_y + 30))

    # 显示游戏状态
    if game_over:
        if winner == 0:
            status_text = small_font.render("平局!", True, RED)
        else:
            winner_text = "黑胜!" if winner == 1 else "白胜!"
            status_text = small_font.render(winner_text, True, RED)
    else:
        status_text = small_font.render("游戏中", True, TEXT_COLOR)
    screen.blit(status_text, (panel_x + 5, panel_y + 55))

    # 绘制按钮
    buttons = []
    button_y = panel_y + 80
    button_height = 25  # 更小按钮高度

    # 根据游戏状态显示不同的按钮
    if game_over:
        button_texts = ["退出", "重玩"]
    else:
        # 添加"重新开始"按钮
        button_texts = ["退出", "和棋", "悔棋", "重新开始"]  # 新增"重新开始"按钮

    for text in button_texts:
        button_rect = pygame.Rect(panel_x + 5, button_y, panel_width - 10, button_height)
        buttons.append((text, button_rect))

        # 按钮颜色（根据鼠标悬停状态）
        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(screen, color, button_rect, border_radius=3)
        pygame.draw.rect(screen, GOLD, button_rect, 1, border_radius=3)

        text_surf = small_font.render(text, True, TEXT_COLOR)
        screen.blit(text_surf, (button_rect.centerx - text_surf.get_width() // 2,
                                button_rect.centery - text_surf.get_height() // 2))

        button_y += button_height + 5  # 更小按钮间距

    return buttons

def draw_home_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT, STONE_RADIUS,
                     title_font=None, font=None, small_font=None):
    if title_font is None:
        title_font = pygame.font.Font(None, 60)
    if font is None:
        font = pygame.font.Font(None, 36)
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    # 绘制天空蓝背景
    screen.fill(SKY_BLUE)

    # 绘制标题
    title = title_font.render("五子棋", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() // 2, SCREEN_HEIGHT * 0.15))

    subtitle = font.render("选择棋子颜色", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH / 2 - subtitle.get_width() // 2, SCREEN_HEIGHT * 0.25))

    # 绘制棋子选择按钮
    buttons = []
    button_width = min(200, SCREEN_WIDTH * 0.3)
    button_height = min(60, SCREEN_HEIGHT * 0.1)
    button_y = SCREEN_HEIGHT * 0.4

    # 黑棋按钮
    black_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width - 20, button_y, button_width, button_height)
    buttons.append(('black', black_rect))
    pygame.draw.rect(screen, (50, 50, 50), black_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, black_rect, 3, border_radius=10)
    black_text = font.render("黑棋", True, WHITE)
    screen.blit(black_text, (black_rect.centerx - black_text.get_width() // 2,
                             black_rect.centery - black_text.get_height() // 2))

    # 白棋按钮
    white_rect = pygame.Rect(SCREEN_WIDTH / 2 + 20, button_y, button_width, button_height)
    buttons.append(('white', white_rect))
    pygame.draw.rect(screen, (220, 220, 220), white_rect, border_radius=10)
    pygame.draw.rect(screen, GOLD, white_rect, 3, border_radius=10)
    white_text = font.render("白棋", True, BLACK)
    screen.blit(white_text, (white_rect.centerx - white_text.get_width() // 2,
                             white_rect.centery - white_text.get_height() // 2))

    # 绘制装饰性棋子
    for i in range(5):
        pygame.draw.circle(screen, BLACK,
                           (SCREEN_WIDTH * 0.3 + i * 40, SCREEN_HEIGHT * 0.7),
                           STONE_RADIUS * 0.8)
        pygame.draw.circle(screen, WHITE,
                           (SCREEN_WIDTH * 0.7 - i * 40, SCREEN_HEIGHT * 0.75),
                           STONE_RADIUS * 0.8)

    copyright = small_font.render("© 2025 五子棋", True, (50, 50, 50))
    screen.blit(copyright, (SCREEN_WIDTH / 2 - copyright.get_width() // 2, SCREEN_HEIGHT * 0.88))

    creator = small_font.render("制作人：聆听风的声音", True, (50, 50, 50))
    screen.blit(creator, (SCREEN_WIDTH / 2 - creator.get_width() // 2, SCREEN_HEIGHT * 0.91))

    instructions_btn_width = 120
    instructions_btn_height = 30
    instructions_btn_rect = pygame.Rect(
        SCREEN_WIDTH / 2 - instructions_btn_width // 2,
        SCREEN_HEIGHT * 0.96,
        instructions_btn_width,
        instructions_btn_height
    )
    buttons.append(('instructions', instructions_btn_rect))

    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if instructions_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR

    pygame.draw.rect(screen, color, instructions_btn_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD, instructions_btn_rect, 1, border_radius=5)

    instructions_text = small_font.render("游玩须知", True, TEXT_COLOR)
    screen.blit(instructions_text, (instructions_btn_rect.centerx - instructions_text.get_width() // 2,
                                    instructions_btn_rect.centery - instructions_text.get_height() // 2))

    return buttons

def draw_instructions_dialog(screen, SCREEN_WIDTH, SCREEN_HEIGHT, font=None, small_font=None):
    if font is None:
        font = pygame.font.Font(None, 36)
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    s.fill((0, 0, 0, 128))  # 黑色半透明
    screen.blit(s, (0, 0))

    dialog_width = min(SCREEN_WIDTH * 0.8, 600)
    dialog_height = min(SCREEN_HEIGHT * 0.6, 400)
    dialog_x = (SCREEN_WIDTH - dialog_width) // 2
    dialog_y = (SCREEN_HEIGHT - dialog_height) // 2

    pygame.draw.rect(screen, (240, 240, 240), (dialog_x, dialog_y, dialog_width, dialog_height), border_radius=10)
    pygame.draw.rect(screen, GOLD, (dialog_x, dialog_y, dialog_width, dialog_height), 3, border_radius=10)

    title = font.render("游玩须知", True, (25, 25, 112))
    screen.blit(title, (dialog_x + dialog_width // 2 - title.get_width() // 2, dialog_y + 20))

    # 内容
    content = [
        "游戏为免费软件，禁止任何形式的商业使用",
        "未经作者允许，不得用于商业用途",
        "可以进行学习参考或二次开发",
        "但请保留原始版权信息和作者信息",
        "",
        "作者保留对软件的最终解释权",
        "感谢您的支持与理解！"
    ]

    content_y = dialog_y + 60
    for line in content:
        text = small_font.render(line, True, (50, 50, 50))
        screen.blit(text, (dialog_x + dialog_width // 2 - text.get_width() // 2, content_y))
        content_y += 30

    ok_btn_width = 100
    ok_btn_height = 40
    ok_btn_rect = pygame.Rect(
        dialog_x + dialog_width // 2 - ok_btn_width // 2,
        dialog_y + dialog_height - 60,
        ok_btn_width,
        ok_btn_height
    )

    mouse_pos = pygame.mouse.get_pos()
    color = BUTTON_HOVER if ok_btn_rect.collidepoint(mouse_pos) else BUTTON_COLOR

    pygame.draw.rect(screen, color, ok_btn_rect, border_radius=5)
    pygame.draw.rect(screen, GOLD, ok_btn_rect, 2, border_radius=5)

    ok_text = small_font.render("确定", True, TEXT_COLOR)
    screen.blit(ok_text, (ok_btn_rect.centerx - ok_text.get_width() // 2,
                          ok_btn_rect.centery - ok_text.get_height() // 2))

    return ok_btn_rect


def draw_time_setting_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                             title_font=None, font=None, small_font=None):
    if title_font is None:
        title_font = pygame.font.Font(None, 60)
    if font is None:
        font = pygame.font.Font(None, 36)
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    screen.fill(SKY_BLUE)

    title = title_font.render("选择您的思考时间", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() // 2, SCREEN_HEIGHT * 0.15))

    subtitle = font.render("选择时间限制", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH / 2 - subtitle.get_width() // 2, SCREEN_HEIGHT * 0.25))

    buttons = []
    button_width = min(300, SCREEN_WIDTH * 0.6)
    button_height = min(60, SCREEN_HEIGHT * 0.1)
    button_y = SCREEN_HEIGHT * 0.35
    time_options = ["30秒", "1分钟", "2分钟", "无限时间"]

    for i, option in enumerate(time_options):
        button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, button_y, button_width, button_height)
        buttons.append(button_rect)

        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, button_rect, 3, border_radius=10)

        text = font.render(option, True, TEXT_COLOR)
        screen.blit(text, (button_rect.centerx - text.get_width() // 2,
                           button_rect.centery - text.get_height() // 2))

        button_y += button_height + 15

    return buttons

def draw_difficulty_screen(screen, SCREEN_WIDTH, SCREEN_HEIGHT,
                           title_font=None, font=None, small_font=None):
    if title_font is None:
        title_font = pygame.font.Font(None, 60)
    if font is None:
        font = pygame.font.Font(None, 36)
    if small_font is None:
        small_font = pygame.font.Font(None, 28)

    screen.fill(SKY_BLUE)

    title = title_font.render("选择AI难度", True, GOLD)
    screen.blit(title, (SCREEN_WIDTH / 2 - title.get_width() // 2, SCREEN_HEIGHT * 0.15))

    subtitle = font.render("难度越高，AI思考越深", True, WHITE)
    screen.blit(subtitle, (SCREEN_WIDTH / 2 - subtitle.get_width() // 2, SCREEN_HEIGHT * 0.25))

    buttons = []
    button_width = min(300, SCREEN_WIDTH * 0.6)
    button_height = min(60, SCREEN_HEIGHT * 0.1)
    button_y = SCREEN_HEIGHT * 0.35
    difficulty_options = ["简单", "正常", "困难"]

    for i, option in enumerate(difficulty_options):
        button_rect = pygame.Rect(SCREEN_WIDTH / 2 - button_width / 2, button_y, button_width, button_height)
        buttons.append(button_rect)

        mouse_pos = pygame.mouse.get_pos()
        color = BUTTON_HOVER if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR

        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        pygame.draw.rect(screen, GOLD, button_rect, 3, border_radius=10)

        text = font.render(option, True, TEXT_COLOR)
        screen.blit(text, (button_rect.centerx - text.get_width() // 2,
                           button_rect.centery - text.get_height() // 2))

        button_y += button_height + 15

    return buttons