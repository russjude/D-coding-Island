import pygame
from Archive.settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.reset(x, y)

    def update(self, game_over, world):
        dx, dy = 0, 0
        if game_over == 0:
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                JUMP_FX.play()
                self.vel_y = -15
                self.jumped = True

            if key[pygame.K_LEFT]:
                dx = -5
            if key[pygame.K_RIGHT]:
                dx = 5

            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            for tile in world.tile_list:
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    dy = tile[1].top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

            self.rect.x += dx
            self.rect.y += dy

        screen.blit(self.image, self.rect)
        return game_over

    def reset(self, x, y):
        self.image = pygame.image.load('img/dino1.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.jumped = False
        self.in_air = True
