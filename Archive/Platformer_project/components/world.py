import pygame
from components.enemy import Enemy

class World:
    def __init__(self, data):
        self.tile_list = []
        for row in data:
            for tile in row:
                if tile == 3:  # Example: Add enemy
                    self.tile_list.append(Enemy())

    def draw(self, screen):
        for tile in self.tile_list:
            tile.draw(screen)
