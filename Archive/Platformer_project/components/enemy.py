import pygame

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 30, 30)

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)  # Temporary visual
