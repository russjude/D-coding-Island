import pygame
from components.player import Player
from components.world import World
from components.enemy import Enemy
from components.platform import Platform
from components.objects import Lava, Coin, Exit
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
world = reset_level(1)

# Main game loop
run = True
while run:
    screen.blit(bg_img, (0, 0))
    screen.blit(sun_img, (100, 100))

    # Draw the world and player
    world.draw(screen)
    player.update(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
