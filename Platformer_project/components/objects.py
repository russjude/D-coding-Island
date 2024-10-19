import pygame

class Lava:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 10)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 100, 0), self.rect)

class Coin:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 215, 0), self.rect.center, 10)

class Exit:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), self.rect)
