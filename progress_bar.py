import pygame


class ProgressBar:
    def __init__(self, x, y, width, height, total_time):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.total_time = total_time
        self.remaining_time = total_time
        self.active = False
        self.last_update = pygame.time.get_ticks()

    def start(self):
        self.active = True
        self.remaining_time = self.total_time
        self.last_update = pygame.time.get_ticks()

    def pause(self):
        self.active = False

    def reset(self):
        self.active = False
        self.remaining_time = self.total_time

    def update(self):
        if not self.active:
            return False

        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.last_update) / 1000.0

        if elapsed >= 1.0:
            self.remaining_time -= 1
            self.last_update = current_time

            if self.remaining_time <= 0:
                self.active = False
                return True

        return False

    def draw(self, screen):
        if not self.active:
            return

        ratio = self.remaining_time / self.total_time
        bar_width = int(self.width * ratio)

        if self.remaining_time <= 10:
            color = (255, 0, 0)
        elif self.remaining_time <= 20:
            color = (255, 255, 0)
        else:
            color = (0, 255, 0)

        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, color, (self.x, self.y, bar_width, self.height))
        pygame.draw.rect(screen, (200, 200, 200), (self.x, self.y, self.width, self.height), 2)

        font = pygame.font.Font(None, 24)
        text = font.render(f"{self.remaining_time}s", True, (255, 255, 255))
        screen.blit(text, (self.x + self.width // 2 - text.get_width() // 2, self.y - 25))