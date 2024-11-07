import pygame
from pygame.locals import *
import pickle
from os import path
from Archive.settings import *
from Archive.player import Player
from world import World, key, Button

# Initialize Pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer')

# Create player and groups
player = Player(100, SCREEN_HEIGHT - 130)
blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
score_key = key(TILE_SIZE // 2, TILE_SIZE // 2)
key_group.add(score_key)

# Load level data
if path.exists(f'level{LEVEL}_data'):
    with open(f'level{LEVEL}_data', 'rb') as f:
        world_data = pickle.load(f)

world = World(world_data)

# Load button images
RESTART_IMG = pygame.image.load('img/restart_btn.png').convert_alpha()
START_IMG = pygame.image.load('img/start_btn.png').convert_alpha()
EXIT_IMG = pygame.image.load('img/exit_btn.png').convert_alpha()

# Create buttons
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, RESTART_IMG)
start_button = Button(SCREEN_WIDTH // 2 - 350, SCREEN_HEIGHT // 2, START_IMG)
exit_button = Button(SCREEN_WIDTH // 2 + 150, SCREEN_HEIGHT // 2, EXIT_IMG)

# Main game loop
run = True
while run:
    CLOCK.tick(FPS)
    screen.blit(BG_IMG, (0, 0))
    screen.blit(SUN_IMG, (100, 100))

    if MAIN_MENU:
        # Draw the buttons on the main menu
        if exit_button.draw(screen):
            run = False
        if start_button.draw(screen):
            MAIN_MENU = False
    else:
        world.draw(screen)

        if GAME_OVER == 0:
            blob_group.update()
            platform_group.update()
            if pygame.sprite.spritecollide(player, key_group, True):
                SCORE += 1
                key_FX.play()
            draw_text(f'X {SCORE}', FONT_SCORE, WHITE, TILE_SIZE - 10, 10, screen)

        blob_group.draw(screen)
        platform_group.draw(screen)
        lava_group.draw(screen)
        key_group.draw(screen)
        exit_group.draw(screen)

        GAME_OVER = player.update(GAME_OVER, world)

        if GAME_OVER == -1 and restart_button.draw(screen):
            world_data = []
            world = reset_level(LEVEL, player, world_data, blob_group, platform_group, lava_group, exit_group)
            GAME_OVER = 0
            SCORE = 0

        if GAME_OVER == 1:
            LEVEL += 1
            if LEVEL <= MAX_LEVELS:
                world_data = []
                world = reset_level(LEVEL, player, world_data, blob_group, platform_group, lava_group, exit_group)
                GAME_OVER = 0
            else:
                draw_text('YOU WIN!', FONT, BLUE, SCREEN_WIDTH // 2 - 140, SCREEN_HEIGHT // 2, screen)
                if restart_button.draw(screen):
                    LEVEL = 1
                    world_data = []
                    world = reset_level(LEVEL, player, world_data, blob_group, platform_group, lava_group, exit_group)
                    GAME_OVER = 0
                    SCORE = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()
