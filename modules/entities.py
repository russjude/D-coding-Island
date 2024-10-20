import pygame

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('img/coin.png')
        self.rect = self.image.get_rect(center=(x, y))

# Define other entities similarly (Enemy, Lava, Exit, etc.)
