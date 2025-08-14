import pygame


class ProgressBar:
    def __init__(self, x, y, width, height, total_time):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.total_time = total_time  # 总时间（秒）
        self.remaining_time = total_time  # 剩余时间（秒）
        self.active = False
        self.last_update = pygame.time.get_ticks()

    def start(self):
        """开始计时"""
        self.active = True
        self.remaining_time = self.total_time
        self.last_update = pygame.time.get_ticks()

    def pause(self):
        """暂停计时"""
        self.active = False

    def reset(self):
        """重置计时器"""
        self.active = False
        self.remaining_time = self.total_time

    def update(self):
        """更新计时器状态"""
        if not self.active:
            return False

        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_update) / 1000.0  # 转换为秒

        if elapsed >= 1.0:  # 每秒钟更新一次
            self.remaining_time -= 1
            self.last_update = current_time

            if self.remaining_time <= 0:
                self.active = False
                return True  # 时间用完

        return False

    def draw(self, screen):
        """绘制进度条"""
        if not self.active:
            return

        # 计算进度比例
        ratio = self.remaining_time / self.total_time
        bar_width = int(self.width * ratio)

        # 根据剩余时间选择颜色
        if self.remaining_time <= 10:
            color = (255, 0, 0)  # 红色
        elif self.remaining_time <= 20:
            color = (255, 255, 0)  # 黄色
        else:
            color = (0, 255, 0)  # 绿色

        # 绘制背景
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))
        # 绘制进度条
        pygame.draw.rect(screen, color, (self.x, self.y, bar_width, self.height))
        # 绘制边框
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height), 2)

        # 绘制剩余时间文本
        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.remaining_time}s", True, (255, 255, 255))
        screen.blit(text, (self.x + self.width // 2 - text.get_width() // 2, self.y - 25))