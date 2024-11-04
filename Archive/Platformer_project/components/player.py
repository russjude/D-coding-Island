import pygame

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 80)
        self.vel_y = 0

    def update(self, screen):
        self.vel_y += 1  # Gravity
        self.rect.y += self.vel_y

        pygame.draw.rect(screen, (0, 0, 255), self.rect)  # Temporary visual
