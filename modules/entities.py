import pygame

class key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('img/key.png')
        self.rect = self.image.get_rect(center=(x, y))

# Define other entities similarly (Enemy, Lava, Exit, etc.)
