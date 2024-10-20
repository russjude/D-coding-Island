# main.py
import pygame
from components.player import Player
from components.world import World
from components.button import Button
from utils.helpers import draw_text, reset_level

pygame.init()

# Game setup
screen_width = 1000
screen_height = 1000
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

# Load assets
bg_img = pygame.image.load('assets/img/sky.png')
sun_img = pygame.image.load('assets/img/sun.png')

# Initialize player and world
player = Player(100, screen_height - 130)
world_data = reset_level(1)
world = World(world_data)

clock = pygame.time.Clock()

# Main game loop
run = True
while run:
    clock.tick(60)  # Limit frame rate to 60 FPS
    
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    # Draw the world and player
    world.draw(screen)
    player.update(screen, world.tile_list)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

# components/player.py
import pygame

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 80)
        self.vel_y = 0
        self.jump = False
        self.in_air = True

    def update(self, screen, tile_list):
        dx = 0
        dy = 0
        
        # Get key presses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jump and not self.in_air:
            self.vel_y = -15
            self.jump = True
        if not key[pygame.K_SPACE]:
            self.jump = False
        if key[pygame.K_LEFT]:
            dx -= 5
        if key[pygame.K_RIGHT]:
            dx += 5

        # Apply gravity
        self.vel_y += 1
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y

        # Check for collision with tiles
        self.in_air = True
        for tile in tile_list:
            # Check for collision in x direction
            if tile.colliderect(self.rect.x + dx, self.rect.y, self.rect.width, self.rect.height):
                dx = 0
            # Check for collision in y direction
            if tile.colliderect(self.rect.x, self.rect.y + dy, self.rect.width, self.rect.height):
                # Check if below the ground (i.e. jumping)
                if self.vel_y < 0:
                    dy = tile.bottom - self.rect.top
                    self.vel_y = 0
                # Check if above the ground (i.e. falling)
                elif self.vel_y >= 0:
                    dy = tile.top - self.rect.bottom
                    self.vel_y = 0
                    self.in_air = False

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

        # Draw player
        pygame.draw.rect(screen, (0, 0, 255), self.rect)

# components/world.py
import pygame

class World:
    def __init__(self, data):
        self.tile_list = []
        dirt_img = pygame.image.load('assets/img/dirt.png')
        grass_img = pygame.image.load('assets/img/grass.png')
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (50, 50))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * 50
                    img_rect.y = row_count * 50
                    tile = (img, img_rect)
                    self.tile_list.append(img_rect)
                if tile == 2:
                    img = pygame.transform.scale(grass_img, (50, 50))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * 50
                    img_rect.y = row_count * 50
                    tile = (img, img_rect)
                    self.tile_list.append(img_rect)
                col_count += 1
            row_count += 1

    def draw(self, screen):
        for tile in self.tile_list:
            pygame.draw.rect(screen, (200, 200, 200), tile)

# utils/helpers.py
import pickle
from os import path

def draw_text(text, font, color, x, y, screen):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_level(level):
    world_data = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 1],
        [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 7, 0, 5, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 1],
        [1, 7, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 7, 0, 0, 0, 0, 1],
        [1, 0, 2, 0, 0, 7, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 2, 0, 0, 4, 0, 0, 0, 0, 3, 0, 0, 3, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 2, 2, 2, 2, 2, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 7, 0, 0, 0, 0, 2, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 2, 0, 2, 2, 2, 2, 2, 1],
        [1, 0, 0, 0, 0, 0, 2, 2, 2, 6, 6, 6, 6, 6, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
    return world_data
