import pygame

class Platform:
    def __init__(self, x, y, move_x, move_y):
        self.rect = pygame.Rect(x, y, 50, 10)
        self.move_x = move_x
        self.move_y = move_y

    def update(self):
        self.rect.x += self.move_x
        self.rect.y += self.move_y
