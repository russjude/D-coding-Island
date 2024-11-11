import pygame
from pygame.locals import *
from pygame import mixer
import os
import time
import cv2
import numpy as np
import math
from datetime import datetime, timedelta
import subprocess
import sys


def load_minigame(level):
    """Load and run a minigame module when needed"""
    try:
        # Stop any ongoing sounds and music
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        
        # Store current display settings
        current_display = pygame.display.get_surface().copy()
        
        result = False
        
        # Map levels to their corresponding minigame modules
        minigame_modules = {
            1: 'mini_game1',
            2: 'mini_game2',
            3: 'mini_game3',
            4: 'mini_game4',
            5: 'mini_game5'
        }
        
        if level in minigame_modules:
            try:
                # Import the corresponding minigame module
                minigame = __import__(minigame_modules[level])
                result = minigame.main()  # Run the minigame
            except ImportError as e:
                print(f"Could not load minigame module for level {level}: {e}")
                return False
            except Exception as e:
                print(f"Error running minigame {level}: {e}")
                return False
                
        # Reset display mode and caption
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Decoding Island')
        
        # Show message if minigame wasn't completed
        if not result:
            screen = pygame.display.get_surface()
            screen.blit(current_display, (0, 0))
            
            # Create semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Show message
            font = pygame.font.SysFont('Bauhaus 93', 32)
            text1 = font.render("You must complete the minigame to proceed!", True, (255, 255, 255))
            text2 = font.render("Press any key to try again...", True, (255, 255, 255))
            
            text1_rect = text1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
            text2_rect = text2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20))
            
            screen.blit(text1, text1_rect)
            screen.blit(text2, text2_rect)
            pygame.display.flip()
            
            # Wait for keypress
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return False
                    if event.type == pygame.KEYDOWN:
                        waiting = False
                pygame.time.wait(100)
            
            # Try the minigame again
            return load_minigame(level)
            
        return result
        
    except Exception as e:
        print(f"Error in load_minigame: {e}")
        return False



# Initialize Pygame and mixer first
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Set up display and constants
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
BASE_WIDTH = 1539
BASE_HEIGHT = 940
SCALE_X = 1.0
SCALE_Y = 1.0
FULLSCREEN = False

# Set up the display
# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'
# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Update these constants at the top of your file
TILE_SIZE = SCREEN_HEIGHT // 36
GRAVITY = 0.45  # Reduced from 0.45
JUMP_SPEED = -12  # Reduced from -13
MOVE_SPEED = 6  # Reduced from 5
game_over = 0
current_level = 0  # 0 for start screen, 1-5 for levels
keys_collected = 0
game_start_time = None
level_times = []
dialogue_states = {}
walk_cooldown = 12

# Add these with other global variables
paused = False
pause_start_time = None
total_pause_time = timedelta(0)
fade_alpha = 0
fade_target = 180
fade_speed = 15


# You may need to adjust other elements (buttons, player size, etc.) to fit the new resolution
# For example:
# start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, start_btn)
# restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Load images
start_bg = pygame.image.load('img/background.png')
start_bg = pygame.transform.scale(start_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
start_btn = pygame.image.load('img/start_btn.png')
restart_img = pygame.image.load('img/restart_btn.png')
closeddoor_img = pygame.image.load('img/closeddoor.PNG')
opendoor_img = pygame.image.load('img/opendoor_img.PNG')
key_img = pygame.image.load('img/key.png')
npc_img = pygame.image.load('img/Wghost.png')
key_frames = []
target_size = (25, 25)  # Your desired size

# Append Keys
for i in range(1, 13):
    image = pygame.image.load(f'img/AnimatedKey_{i}.png')
    scaled_image = pygame.transform.scale(image, target_size)
    key_frames.append(scaled_image)

# Scale images
closeddoor_img = pygame.transform.scale(closeddoor_img, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
key_img = pygame.transform.scale(key_img, (10, 25 ))
npc_img = pygame.transform.scale(npc_img, (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2)))

# Load sounds
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

FULLSCREEN = False  # Track fullscreen state

def update_scale_factors():
    """Update scale factors based on current screen size"""
    global SCALE_X, SCALE_Y
    current_size = pygame.display.get_surface().get_size()
    SCALE_X = current_size[0] / BASE_WIDTH
    SCALE_Y = current_size[1] / BASE_HEIGHT

def toggle_fullscreen():
    """Toggle between fullscreen and windowed mode"""
    global FULLSCREEN, screen, SCREEN_WIDTH, SCREEN_HEIGHT
    FULLSCREEN = not FULLSCREEN
    
    if FULLSCREEN:
        # Get monitor resolution
        info = pygame.display.Info()
        # Calculate aspect ratio preserved resolution
        target_ratio = BASE_WIDTH / BASE_HEIGHT
        monitor_ratio = info.current_w / info.current_h
        
        if monitor_ratio > target_ratio:
            # Monitor is wider than our target ratio
            SCREEN_HEIGHT = info.current_h
            SCREEN_WIDTH = int(SCREEN_HEIGHT * target_ratio)
        else:
            # Monitor is taller than our target ratio
            SCREEN_WIDTH = info.current_w
            SCREEN_HEIGHT = int(SCREEN_WIDTH / target_ratio)
            
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        SCREEN_WIDTH = BASE_WIDTH
        SCREEN_HEIGHT = BASE_HEIGHT
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Update scale factors after changing resolution
    update_scale_factors()

# Level platform data (you'll need to adjust these coordinates based on your level designs)
LEVEL_PLATFORM_DATA = {
    0: [
            # Top platforms
            (5.2, 13.4, 6, 2.5),    
            (48, 13.4, 6, 2.5),   

            # small-top platform
            (13.3, 15.5, 1.4, 1.0), 
            (44.4, 15.5, 1.6, 1.0), 
            
            # semi-top platform
            (16.7, 16.6, 4.5, 1.0), 
            (38, 16.6, 4.5, 1.0), 

            # Middle platform
            (26.5, 18.3, 6.2, 2.5),  
            
            # Lower platforms
            (34.6, 23.2, 4.8, 2.5),
            (19.9, 23.2, 4.7, 2.5),
            
            # Bottom platforms
            (11.8, 28, 6.2, 2.5),
            (26.6, 28, 6.2, 2.5),
            (41.3, 28, 8, 1.),
            
            # Ground level
            (0, 33, 8, 3.0),
            (51, 33, 8.2, 3.0),
    ],
    1: [
            # 5th layer
            (23.1, 8.4, 4.8, 1.4),
            (44.5, 8.4, 4.8, 1.4),
            (15, 5.1, 6.2, 3),
            (0, 6.8, 9.8, 1.3),

            # 4th layer
            (28.1, 11.7, 6.4, 3),
            (51.2, 11.7, 6.3, 3),

            # 3rd layer
            (24.8, 15.5, 1.4, 1.7),
            (36.3, 16.6, 4.8, 1.3),
            (44.5, 16.6, 4.8, 1.3),

            # 2nd layer
            (51.1, 21.5, 6.4, 3),
            (36.3, 23.2, 6.4, 1),
            (18.3, 19.9, 9.6, 3),
            (31.3, 19.9, 3.3, 1.4),

            # Ground level
            (44.6, 26.4, 6.4, 3),
            (33, 29.7, 9.7, 3),
            (16.6, 28.1, 4.8, 1.4),
            (16.6, 34.7, 16, 12),

            # Ground Pillars
            (11.7, 23.2, 3.1, 12),
            (6.7, 26.4, 3.1, 9),
            (1.7, 29.8, 3.1, 6)
    ],
    2: [
            # 7th layer
            (13.5, 2, 7.6, 4),
            (10.1, 3.7, 3, 1),
            (0.3, 3.7, 4.6, 1),
            (5.2, 5.3, 1.3, 1),

            # 6th layer
            (51.3, 10.2, 7.5, 5.7),
            (5.2, 8.6, 4.6, 1),

            # 5th layer
            (43, 11.9, 6.3, 1),
            (11.8, 13.5, 4.6, 1),
            (0.2, 13.5, 4.6, 1),

            # 4th layer
            (31.7, 18.1, 1.8, 1.3),
            (42.3, 18.1, 1.8, 1.3),
            (33.3, 15.2, 9.2, 4),
            (0, 18.4, 9.5, 2.5),

            # 3rd layer
            (47.9, 20, 4.7, 1),
            (29.85, 20, 1.3, 1),
            (13.6, 21.7, 6, 1),
            (9.9, 20.1, 1.4, 1),

            # 2nd layer
            (48, 26.7, 6.2, 1),
            (41.4, 23.4, 4.6, 1),
            (26.7, 23.4, 7.6, 2.5),
            (7, 25, 14, 5),

            # Ground level
            (0.5, 28.4, 6.6, 8.0),
            (21, 28.4, 6.7, 8.0),
            (43.2, 31.7, 27, 5.0),

            # Ground Pillars
            (39.8, 31.7, 1.2, 3),
            (34.8, 31.7, 1.2, 3),
            (29.9, 31.7, 1.2, 3)
    ],
    3: [
            # 6th layer
            (3.5, 7, 6.2, 1),
            (0.3, 2, 4.3, 2.5),
            (20, 8.5, 3, 1),
            (46.4, 8.5, 11.4, 1),
            (57.8, 0.4, 1.3, 9),
            (29.9, 3.7, 9.5, 1),
            (48, 3.7, 4.6, 1),
            

            # 5th layer
            (26.4, 11.5, 2.8, 1.3),
            (25, 8.6, 1.4, 4.3),
            (11.5, 10.2, 5, 1),


            # 4th layer
            (18.1, 10.3, 1.7, 5.8),
            (7.1, 14.8, 10.9, 1.3),
            (31.5, 13.6, 3, 0.8),
            (36.5, 16.8, 7.8, 0.8),

            # 3rd layer
            (51.3, 20.1, 2.8, 5.7),
            (44.8, 20.1, 2.8, 5.7),
            (47.6, 24.8, 3.8, 1),
            (33.2, 23.4, 7.8, 1),
            (9.9, 25, 11.3, 1),
            (1.4, 20.1, 6.5, 5.8),
            (23.4, 18.5, 7.5, 4.2),
            (11.8, 21.8, 3, 0.8),
            (1.7, 13.6, 1.6, 1),
            (37.9, 11.9, 1.6, 1),
            (43, 10.3, 1.2, 2.7),
            (16.7, 13.5, 1.3, 1.3),
            

            # 2nd layer
            (34.8, 30, 2.9, 1),
            (26.7, 26.7, 5.9, 1),
            (31.3, 26.7, 1.4, 5.8),
            (23.6, 31.3, 7.7, 1.2),
            (10, 28.4, 4.8, 1),
            (21.6, 21.9, 1.4, 2.3),
            (19.8, 18.5, 1.6, 1),
            (8.3, 20, 1.6, 1),
            (0.1, 18.4, 1.6, 1),


            # Ground level
            (0.3, 35, 19, 6),
            (23.4, 35, 20.6, 6),
            (46.6, 35, 12.6, 6)
    ],
    4: [
            # 4th layer
            (33.2, 15.2, 7.8, 5.8),
            (31.3, 16.8, 2, 1),

            (6.8, 11.9, 5, 1),
            (10.2, 5.3, 3, 2.4),
            (15, 21.9, 1.2, 2),
            (13, 7, 1.8, 2.3),

            (19.9, 7, 1.2, 2.3),
            (21.4, 5.2, 1.3, 11),
            (22.6, 7, 1.8, 1),
            (11.9, 5.3, 1.1, 10.9),
            (13, 14.9, 8.4, 1.3),
            (16.4, 8.5, 1.7, 1),
            (14.9, 11.9, 5, 1),

            (24.8, 11.9, 3, 1),
            (46, 11.9, 5, 1),
            (44.4, 16.8, 6.6, 1),

            (51, 20, 8, 1),
            (38.1, 0, 1.3, 8),
            (39.3, 6.8, 6.3, 1.2),
            (39.3, 3.5, 1.7, 1),



            # 3rd layer
            (8.5, 21.8, 1.5, 1),
            (21.2, 21.8, 1.5, 1),
            (16.9, 29.5, 1.6, 1.5),
            (19.4, 29.5, 1.6, 1.5),
            (26.4, 20, 1.8, 1),
            (29.4, 20, 1.8, 1),
            (28.2, 15.2, 1.2, 9.3),
            (26.4, 23.4, 1.8, 1),
            (29.4, 23.4, 3.3, 1),
            

            # 2nd layer
            (6.9, 28.3, 4.3, 1),
            (1.7, 25, 6.3, 1),
            (0, 20, 8, 1),
            (0, 15.1, 5, 1),
            (11.9, 26.7, 1.3, 6),
            (13, 31.2, 1.3, 1.4),
            (11.9, 26.6, 6.7, 1),
            (23, 26.7, 5, 1),
            (33, 26.7, 3, 1),
            (39, 38.2, 5, 1),
            (29.8, 30, 3, 1),
            (56, 30, 3, 1),
            (41, 23.4, 5, 1),
            (52.9, 33.1, 2.9, 4),
            (38, 28.2, 5, 1),
            (46, 26.7, 6.7, 5.8),
            (44.7, 31.2, 1.5, 1.3),


            # Ground level
            (0, 33.3, 6.3, 6),
            (6.7, 34.9, 3, 6),
            (11.6, 34.9, 8.1, 6),
            (21.6, 34.9, 1.3, 6),
            (23, 33.2, 6.5, 0.9),
            (34.7, 33.3, 9.5, 6)
    ],
    5: [

            (0, 5.2, 9.5, 1),
            (0, 13.5, 11.4, 1),
            (0.2, 23.4, 1.1, 14),
            (3.5, 26.7, 1.4, 11),

            (6.8, 30, 3, 1),
            (6.7, 23.4, 3, 1),
            (10, 18.5, 4.6, 1),
            (10, 26.7, 8.2, 1.5),
            (26.3, 26.7, 5.3, 1.5),
            (36.1, 26.7, 3.7, 1.5), 

            (15, 13.5, 3, 1), 
            (18, 8.5, 5, 1),
            (49.3, 30, 3.3, 1.1), 
            (46, 23.3, 6.5, 1),
            (44.4, 18.5, 4.8, 1),

            (16.5, 20, 5, 1.3),
            (23, 20, 1.7, 1.3),
            (33, 20, 3.3, 1.3),
            (38, 20, 4.7, 1.3),
            (41.2, 13.5, 3.2, 1),
            (29.7, 7, 6.5, 1.1),
            (22.9, 7, 5, 1.2),

            (19.8, 13.5, 5, 1.3),
            (29.6, 13.5, 1.7, 1.3),
            (34.4, 13.5, 5.2, 1.3),
            (36.4, 8.5, 4.5, 1.2),
            (42.9, 5.3, 6.5, 1),
            (51, 15, 8, 1),

            (15.1, 26.8, 1, 8),
            (43.1, 26.8, 1, 8),
            (21.7, 13.6, 1.2, 7.7),
            (36.5, 13.6, 1.2, 7.7),
            (18.4, 20, 1, 8.1), 
            (39.9, 20, 1, 8.1),
            (25, 7, 1, 7.8),
            (33.3, 7, 1, 7.8),

            (54.5, 26.8, 1.2, 11),
            (57.9, 23.4, 1.2, 14),
            (51.3, 3.2, 1.5, 6.3),
            (53, 8.3, 4.4, 1.3),
            (57.6, 3.3, 1.5, 6),
            (54.3, 5, 1.7, 1.3),

            (28.2, 12, 1.2, 2.5), 
            (31.5, 18.5, 1.3, 2.5),
            (25, 25, 1, 3),
            (34.9, 31.7, 1, 3),
            (17.7, 31.5, 1.8, 1),

            (9.9, 33.2, 5, 1.3),
            (19.4, 33.2, 7.3, 1.3),
            (29.4, 33.2, 5.4, 1.3),
            (36, 33.2, 5.5, 1.3),
            (44, 33.2, 5.3, 1.3)
    ]
}

# 1. Fix the level_backgrounds initialization
level_backgrounds = {
    0: {'type': 'video', 'path': 'Level Data/Level Image/Level0_Background.mp4'},
    1: {'type': 'video', 'path': 'Level Data/Level Image/Level1_Background.mp4'},
    2: {'type': 'video', 'path': 'Level Data/Level Image/Level2_Background.mp4'},
    3: {'type': 'video', 'path': 'Level Data/Level Image/Level3_Background.mp4'},
    4: {'type': 'video', 'path': 'Level Data/Level Image/Level4_Background.mp4'},
    5: {'type': 'image', 'path': 'Level Data/Level Image/Level5.png'}
}

# Dictionary mapping dialogue scenes to background images
DIALOGUE_BACKGROUNDS = {
    "intro": "Level Data/Dialouge/bg.png",
    "level0": "Level Data/Dialouge/Forest3.png",
    "level1": "Level Data/Dialouge/origbig.png",
    "level2": "Level Data/Dialouge/mountainbg.png",
    "level3": "Level Data/Dialouge/Geoffrey.png",
    "level4": "Level Data/Dialouge/Jessi.png",
    "level5": "Level Data/Dialouge/Jacobo.png",
    "ending": "Level Data/Dialouge/Jacobo.png"
}

# Update LEVEL_REQUIREMENTS dictionary
LEVEL_REQUIREMENTS = {
    0: 3,  # Tutorial level 
    1: 4,  # Level 1: Assassin's Trial
    2: 5,  # Level 2: Wizard's Tower
    3: 6,  # Level 3: Autocrat's Domain
    4: 8,  # Level 4: Wraith's Nightmare
    5: 10  # Level 5: Undead King's Castle
}

# Update LEVEL_NAMES dictionary
LEVEL_NAMES = {
    0: "The Awakening Path",
    1: "Shadows of Deception",
    2: "Mystic Tower Ascent", 
    3: "Cryptic Dominion",
    4: "Phantom's Labyrinth",
    5: "Undead King's Sanctum"
}

# Update LEVEL_TIME_LIMITS dictionary
LEVEL_TIME_LIMITS = {
    0: 60,  # Tutorial: 1 minute
    1: 60,  # Level 1: 1 minute 
    2: 60,  # Level 2: 1 minute
    3: 60,  # Level 3: 1 minute
    4: 60,  # Level 4: 1 minute
    5: 60   # Level 5: 1 minute
}

# Update LEVEL_ENEMY_DATA to match old version
LEVEL_ENEMY_DATA = {
    0: [],  # No enemies in tutorial
    1: [
        (17, 33.4, "horizontal", 17, 32),
        (0.2, 5.5, "horizontal", 0.2, 8.5),
        (36.2, 22, "horizontal", 36.2, 41.2),
        (50.5, 10.6, "horizontal", 50.5, 56),
        (18.5, 19, "horizontal", 18.5, 27.2)
    ],
    2: [
        (8.5, 24, "horizontal", 8.5, 20),
        (0.2, 17.2, "horizontal", 0.2, 8.7),
        (44.5, 30.5, "horizontal", 44, 58.5),
        (35, 14, "horizontal", 35, 41),
        (52.3, 9.1, "horizontal", 52.3, 58.5)
    ],
    3: [
        (10.5, 24, "horizontal", 10.5, 20.5),
        (24, 34, "horizontal", 24, 43),
        (8, 13.6, "horizontal", 8, 16.5),
        (30, 2.6, "horizontal", 30, 38.5),
        (48, 6.4, "horizontal", 48, 57),
        (37.5, 13.8, "horizontal", 37.5, 43.5)
    ],
    4: [],  # No enemies in level 4
    5: [
        (0, 4.2, "horizontal", 0, 9.5),
        (0, 12.5, "horizontal", 0, 11.4),
        (10, 25.7, "horizontal", 10, 18.2),
        (41, 25.7, "horizontal", 41, 45),
        (16.5, 19, "horizontal", 16.5, 22.3),
        (38, 19, "horizontal", 38, 42),
        (19.8, 12.5, "horizontal", 19.8, 24),
        (34.4, 12.5, "horizontal", 34.4, 39.7),
        (42.9, 4.3, "horizontal", 42.9, 48.9),
        (51, 14, "horizontal", 51, 59),
        (44, 32.2, "horizontal", 44, 49),
        (10, 32.2, "horizontal", 10, 14)
    ]
}

# Update LEVEL_DEADLY_DATA for hazardous tiles
LEVEL_DEADLY_DATA = {
    0: [],  # No deadly tiles in tutorial
    1: [],  # No deadly tiles in level 1
    2: [
        (23.2, 3.6, 3, 1),
        (26.4, 10.2, 4.8, 1.3),
        (28, 34, 15, 1)
    ],
    3: [
        (19.9, 1.9, 3, 1.4),
        (47.7, 13.5, 3.2, 1.3),
        (19.5, 35, 3.7, 6),
        (44.2, 35, 2.2, 6)
    ],
    4: [
        (10, 22.4, 11.3, 1.3)
    ],
    5: [
        (0.2, 34, 59, 4),
        (15.4, 28, 2.2, 3),
        (22, 25.4, 2, 2),
        (25, 12, 2.4, 2.7),
        (28.4, 18.7, 2.4, 2.3),
        (31.8, 25.2, 2.3, 2),
        (26.9, 32, 2, 2),
        (40.2, 25.3, 2, 2),
        (41.7, 30.3, 2, 2)
    ]
}

# Update LEVEL_BLUE_DATA for special tiles
LEVEL_BLUE_DATA = {
    0: [],  # No blue tiles in tutorial
    1: [],  # No blue tiles in level 1
    2: [
        (23.2, 3.6, 3, 1.1),
        (26.4, 10.2, 4.8, 1.4)
    ],
    3: [
        (19.9, 1.9, 3, 1.4),
        (47.7, 13.5, 3.2, 1.3),
        (19.5, 35, 3.7, 6),
        (44.2, 35, 2.2, 6)
    ],
    4: [
        (10, 23.4, 11.3, 1.3),
        (18.5, 23.4, 1, 7.6)
    ],
    5: [
        (26.2, 13.5, 1.7, 1.3),
        (26.4, 20, 4.8, 1.3),
        (19.6, 26.7, 5.3, 1.5),
        (41, 26.7, 5, 1.5),
        (31.1, 26.7, 3.3, 1.5)
    ]
}

# Initialize video capture and load images
background_surfaces = {}
video_captures = {}

for level, bg_data in level_backgrounds.items():
    if bg_data['type'] == 'video':
        try:
            video_captures[level] = cv2.VideoCapture(bg_data['path'])
        except Exception as e:
            print(f"Error loading video for level {level}: {e}")
            # Fallback to a solid color or default image
            background_surfaces[level] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_surfaces[level].fill((0, 0, 0))
    else:
        try:
            img = pygame.image.load(bg_data['path']).convert()
            background_surfaces[level] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading image for level {level}: {e}")
            # Fallback to a solid color
            background_surfaces[level] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_surfaces[level].fill((0, 0, 0))

# Update collision tile creation (in World class):
def __init__(self, level_data, deadly_data):
    self.collision_tiles = []
    self.deadly_tiles = []

    for plat in level_data:
        # Adjust coordinates to align with background
        x = plat[0] * TILE_SIZE
        y = plat[1] * TILE_SIZE
        width = plat[2] * TILE_SIZE
        height = int(plat[3] * TILE_SIZE)
        
        # Add small margin for better collision
        margin = 2
        collision_rect = pygame.Rect(
            x + margin,
            y + margin,
            width - margin * 2,
            height - margin * 2
        )
        self.collision_tiles.append(CollisionTile(x, y, width, height))

    for deadly in deadly_data:
        x = deadly[0] * TILE_SIZE
        y = deadly[1] * TILE_SIZE
        width = deadly[2] * TILE_SIZE
        height = int(deadly[3] * TILE_SIZE)
        
        # Add similar margin for deadly tiles
        margin = 2
        self.deadly_tiles.append(CollisionTile(
            x + margin, 
            y + margin, 
            width - margin * 2, 
            height - margin * 2
        ))

    
# Update LEVEL_DIALOGUES dictionary to add Level 0
LEVEL_DIALOGUES = {
    0: [
        "Tutorial Level: Learning the Basics",
        "Master the art of movement and key collection.",
        "Collect 3 keys to proceed to your first real challenge.",
        "Press SPACE to continue..."
    ],
    1: [
        "Level 1: The Assassin's Trial",
        "Find 4 keys while avoiding deadly traps.",
        "Press SPACE to continue..."
    ],
    2: [
        "Level 2: The Wizard's Tower",
        "Collect 5 keys hidden by magical illusions.",
        "Press SPACE to continue..."
    ],
    3: [
        "Level 3: The Autocrat's Domain",
        "Gather 6 keys from this sprawling fortress.",
        "Press SPACE to continue..."
    ],
    4: [
        "Level 4: The Wraith's Nightmare",
        "Find 8 keys in this realm of shadows.",
        "Press SPACE to continue..."
    ],
    5: [
        "Final Level: The Undead King's Castle",
        "Collect all 10 keys to complete your journey.",
        "Press SPACE to continue..."
    ]
}

class Leaderboard:
    def __init__(self, screen):
        self.screen = screen
        self.scores = []
        self.font = pygame.font.SysFont('Bauhaus 93', 24)
        self.title_font = pygame.font.SysFont('Bauhaus 93', 32)
        self.load_scores()

    def add_score(self, player_name, time_seconds):
        self.scores.append({
            'name': player_name,
            'time': time_seconds
        })
        self.scores.sort(key=lambda x: x['time'])  # Sort by time (ascending)
        self.scores = self.scores[:10]  # Keep only top 10
        self.save_scores()

    def load_scores(self):
        try:
            with open('leaderboard.txt', 'r') as f:
                lines = f.readlines()
                self.scores = []
                for line in lines:
                    name, time = line.strip().split(',')
                    self.scores.append({'name': name, 'time': float(time)})
        except FileNotFoundError:
            self.scores = []

    def save_scores(self):
        with open('leaderboard.txt', 'w') as f:
            for score in self.scores:
                f.write(f"{score['name']},{score['time']}\n")

    def draw(self):
        # Create semi-transparent background
        leaderboard_surface = pygame.Surface((300, 400), pygame.SRCALPHA)
        pygame.draw.rect(leaderboard_surface, (0, 0, 0, 180), (0, 0, 300, 400))
        
        # Draw title
        title = self.title_font.render("LEADERBOARD", True, (255, 215, 0))
        leaderboard_surface.blit(title, (150 - title.get_width()//2, 10))
        
        # Draw scores
        y = 60
        for i, score in enumerate(self.scores):
            minutes = int(score['time'] // 60)
            seconds = int(score['time'] % 60)
            text = self.font.render(f"{i+1}. {score['name']}: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            leaderboard_surface.blit(text, (20, y))
            y += 30
        
        # Position leaderboard on right side of screen
        self.screen.blit(leaderboard_surface, (self.screen.get_width() - 320, 60))


class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None
        self.scenes = []
        self.scene_index = 0
        self.player_name = ""
        self.text_input = TextInput(screen)
        self.text_input.active = True
        self.current_state = "scene"
        self.level_completed = False
        self.current_level = 0
        self.load_scenes()

    def load_scenes(self):
        self.scenes = [
            # Scene 1 - Name Input
            {
                'image': 'DCI_Scenes/Scene1.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene1.mp3',
                'text': 'Enter Your Name:',
                'input': True,
                'next': 'scene'
            },
            # Scene 2
            {
                'image': 'DCI_Scenes/Scene2.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene2.mp3',
                'text': f'Dear {self.player_name}, you stumbled upon the ancient artifact, half-buried in a cave. It was a stone box, covered in intricate, interlocking symbols that seemed to shift if you stared too long.',
                'next': 'scene'
            },
            # Scene 3
            {
                'image': 'DCI_Scenes/Scene3.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene3.mp3',
                'text': f'{self.player_name} worked carefully, pressing and turning parts of the stone, the symbols clicked into alignment. Inside was a letter that wrote: "Whoever unlocks these secrets is bound to us. Your presence is now required. The island awaits, {self.player_name}."',
                'next': 'scene'
            },
            # Scene 4
            {
                'image': 'DCI_Scenes/Scene4.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene4.mp3',
                'text': f'{self.player_name} feels something watching. A mysterious voice echoes through the darkness.',
                'next': 'scene'
            },
            # Scene 5
            {
                'image': 'DCI_Scenes/Scene5.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene5.mp3',
                'text': f'{self.player_name} follows the voice as it gets closer and closer.',
                'next': 'scene'
            },
            # Scene 6
            {
                'image': 'DCI_Scenes/Scene6.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene6.mp3',
                'text': f'Before {self.player_name} realizes, the path leads to a forest with an eerie feel.',
                'next': 'scene'
            },
            # Scene 7 - Lead to Tutorial Level
            {
                'image': 'DCI_Scenes/Scene7.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene7.mp3',
                'text': f'The ghostly voice of Eralt lingers in the air.\n\nEralt the Ghost: "Welcome, {self.player_name}. Beware, young master. The island knows your fears, your weaknesses. Solve the code, and move closer to your destiny. Fail, and join the lost souls who could not decode the island\'s secrets."',
                'next': 'level_0'
            },
            # Scene 8 - After Tutorial, before Level 1
            {
                'image': 'DCI_Scenes/Scene8.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene8.mp3',
                'text': f'A figure emerges from the shadows.\n\nPalak the Assassin: "I am Palak, the Assassin, Guardian of the First Level. Ah, so you are {self.player_name}. To pass my challenge, you must prove you can see through deception and lies. Codes are more than words—theyre veils of truth and deceit. Decipher mine, or face the consequences."',
                'next': 'level_1'
            },
            # Scene 9 - After Level 1 completion
            {
                'image': 'DCI_Scenes/Scene9.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene9.mp3',
                'text': f'{self.player_name} completes the code with determination.\n\nPalak the Assassin: "Impressive, {self.player_name}. You may pass… for now. Your journey has only begun."',
                'next': 'scene'
            },
            # Scene 10 - Lead to Level 2
            {
                'image': 'DCI_Scenes/Scene10.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene10.mp3',
                'text': f'Russ the Wizard: "Ah, so the prophecy speaks true. {self.player_name}, the new champion, has arrived." He gestures to a puzzle box floating in mid-air, surrounded by a shimmering aura.',
                'next': 'level_2'
            },
            # Scene 11 - After Level 2 completion
            {
                'image': 'DCI_Scenes/Scene11.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene11.mp3',
                'text': f'The Wizard smiles approvingly, nodding.\n\nRuss the Wizard: "Well done, {self.player_name}. You\'ve earned the right to advance. Your wisdom grows stronger with each challenge."',
                'next': 'scene'
            },
            # Scene 12 - Lead to Level 3
            {
                'image': 'DCI_Scenes/Scene12.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene12.mp3',
                'text': f'Geoff the Autocrat: "So, {self.player_name}, you\'ve passed the others. But codes are not just puzzles; they\'re tools of control, of power. I rule through secrets, and now you shall learn their true weight."',
                'next': 'level_3'
            },
            # Scene 13 - After Level 3 completion
            {
                'image': 'DCI_Scenes/Scene13.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene13.mp3',
                'text': f'Autocrat inclines his head, a dark smile on his lips.\n\nGeoff the Autocrat: "Impressive, {self.player_name}. Remember, only those who understand power can control it. Your mastery grows. Proceed."',
                'next': 'scene'
            },
            # Scene 14 - Lead to Level 4
            {
                'image': 'DCI_Scenes/Scene14.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene14.mp3',
                'text': f'Jessica the Wraith materializes from the mist.\n\nJessica: "Ah, {self.player_name}, you are brave, but bravery means nothing in the face of fear. This trial is not of logic, but of your darkest nightmares. Let us see what lies in the depths of your soul."',
                'next': 'level_4'
            },
            # Scene 15 - After Level 4 completion
            {
                'image': 'DCI_Scenes/Scene15.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene15.mp3',
                'text': f'Jessica the Wraith: "You surprise me, {self.player_name}. Few have faced their fears with such resolve. You may go on, though many are lost here… Remember this strength in the trials ahead."',
                'next': 'scene'
            },
            # Scene 16 - Lead to Final Level
            {
                'image': 'DCI_Scenes/Scene16.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene16.mp3',
                'text': f'The Undead King\'s voice resonates through the chamber.\n\nJacobo: "At last, {self.player_name}, you stand before the final trial. I am Jacobo, the Undead King, master of the lost and forgotten. To claim victory, you must decipher the oldest code of all, the language of life and death itself."',
                'next': 'level_5'
            },
            # Scene 17 - After Final Level completion
            {
                'image': 'DCI_Scenes/Scene17.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene17.mp3',
                'text': f'Jacobo the Undead King: "Remarkable, {self.player_name}. You have proven yourself beyond all expectations. But know that this accomplishment is not a prize, but a burden. The codes you now possess contain secrets that even the spirits dare not speak. Guard them well, for they will change everything."',
                'next': 'scene'
            },
            # Scene 18 - Exit scene
            {
                'image': 'DCI_Scenes/Scene18.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene18.mp3',
                'text': f'{self.player_name} emerges from the cave, forever changed by the journey.',
                'next': 'scene'
            },
            # Scene 19 - Final scene and credits
            {
                'image': 'DCI_Scenes/Scene19.png',
                'audio': 'DCI_Scenes/Sound_Effects/Scene19.mp3',
                'text': f'Congratulations, {self.player_name}. You are free, but the knowledge you carry will be your eternal companion.',
                'next': 'game_complete',
                'show_credits': True
            }
        ]
        
        # Initialize first scene
        self.current_scene = Scene(self.screen, self.scenes[0])

    def update_scenes_with_name(self):
        """Update all scenes with the player's name"""
        for i in range(1, len(self.scenes)):
            if 'text' in self.scenes[i]:
                self.scenes[i]['text'] = self.scenes[i]['text'].format(
                    player_name=self.player_name)
        
        # Update current scene if not on first scene
        if self.scene_index > 0:
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index], self.player_name)

    def next_scene(self):
        self.scene_index += 1
        if self.scene_index < len(self.scenes):
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index], self.player_name)
        else:
            self.scene_index = len(self.scenes) - 1  # Stay on last scene

    def handle_level_completion(self, level):
        self.level_completed = True
        self.current_level = level + 1
        level_to_scene = {
            0: 6,  # After tutorial, go to Scene 7
            1: 7,  # After Level 1, go to Scene 8
            2: 10, # After Level 2, go to Scene 11
            3: 12, # After Level 3, go to Scene 13
            4: 14, # After Level 4, go to Scene 15
            5: 16  # After Level 5, go to Scene 17
        }
        if level in level_to_scene:
            self.scene_index = level_to_scene[level]
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index], self.player_name)
            return 'scene'
        return 'playing'

    def update(self, dt):
        # Handle current scene update
        if self.current_scene:
            scene_complete = self.current_scene.update(dt)
            if scene_complete:
                next_state = self.scenes[self.scene_index].get('next', 'scene')
                if next_state.startswith('level_'):
                    level_num = int(next_state.split('_')[1])
                    self.current_level = level_num
                    return 'playing'
                elif next_state == 'scene':
                    self.next_scene()
        return self.current_state

    def next_scene(self):
        self.scene_index += 1
        if self.scene_index < len(self.scenes):
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index])
        else:
            self.scene_index = len(self.scenes) - 1  # Stay on last scene

    def draw(self):
        """Draw the current scene"""
        if self.current_scene:
            self.current_scene.draw()
            
            # Draw text input if active and in name input state
            if self.text_input.active:
                self.text_input.draw(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        

class TextInput:
    def __init__(self, screen, font_size=32):
        self.screen = screen
        self.font = pygame.font.SysFont('Bauhaus 93', font_size)
        self.input_text = ""
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = pygame.time.get_ticks()
        self.cursor_blink_speed = 500  # Blink every 500ms
        self.max_length = 20
        
        # Visual styling
        self.box_width = 300
        self.box_height = 50
        self.text_color = (255, 255, 255)
        self.box_color = (0, 0, 0, 180)
        self.border_color = (100, 100, 100)
        self.active_border_color = (200, 200, 200)
        self.prompt_text = "Enter your name:"
        
        # Create prompt surface once
        self.prompt_surface = self.font.render(self.prompt_text, True, self.text_color)

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():  # Only accept if there's actual text
                    result = self.input_text.strip()
                    self.active = False
                    return result
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < self.max_length and event.unicode.isprintable():
                    self.input_text += event.unicode
        return None

    def draw(self, x, y):
        if not self.active:
            return

        # Center the input box
        box_x = x - self.box_width // 2
        box_y = y

        # Draw the prompt text centered above the input box
        prompt_x = x - self.prompt_surface.get_width() // 2
        prompt_y = box_y - 40
        self.screen.blit(self.prompt_surface, (prompt_x, prompt_y))

        # Draw input box background
        s = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(s, self.box_color, (0, 0, self.box_width, self.box_height))
        self.screen.blit(s, (box_x, box_y))

        # Draw border
        border_color = self.active_border_color if self.active else self.border_color
        pygame.draw.rect(self.screen, border_color, 
                        (box_x, box_y, self.box_width, self.box_height), 2)

        # Draw input text
        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.text_color)
            text_x = box_x + 10
            text_y = box_y + (self.box_height - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))

        # Draw blinking cursor
        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time

        if self.cursor_visible:
            cursor_x = box_x + 10 + (self.font.size(self.input_text)[0] if self.input_text else 0)
            cursor_y = box_y + 10
            pygame.draw.line(self.screen, self.text_color,
                           (cursor_x, cursor_y),
                           (cursor_x, cursor_y + self.box_height - 20),
                           2)

        # Draw instruction text
        instruction_text = "Press ENTER to confirm"
        instruction_surface = pygame.font.SysFont('Bauhaus 93', 20).render(
            instruction_text, True, (200, 200, 200))
        instruction_x = x - instruction_surface.get_width() // 2
        instruction_y = box_y + self.box_height + 10
        self.screen.blit(instruction_surface, (instruction_x, instruction_y))

class Scene:
    def __init__(self, screen: pygame.Surface, scene_data: dict, player_name=""):  # Add player_name parameter
        self.screen = screen
        self.scene_data = scene_data.copy()
        self.bg_image = None
        self.audio = None
        self.text_box = None
        self.text_font = pygame.font.SysFont('Bauhaus 93', 32)
        self.fade_alpha = 0
        self.fade_speed = 5
        self.fading_in = True
        self.fading_out = False
        self.completed = False
        self.is_name_input = scene_data.get('input', False)
        
        # Format the text with the player's name if available
        if 'text' in self.scene_data and player_name:
            self.scene_data['text'] = self.scene_data['text'].replace('{self.player_name}', player_name)
            self.scene_data['text'] = self.scene_data['text'].replace('{player_name}', player_name)
                
        self.load_assets()
                
    def load_assets(self):
        # Load background image
        if 'image' in self.scene_data:
            try:
                self.bg_image = pygame.image.load(self.scene_data['image'])
                self.bg_image = pygame.transform.scale(self.bg_image, self.screen.get_size())
            except pygame.error:
                print(f"Could not load image: {self.scene_data['image']}")
                self.bg_image = pygame.Surface(self.screen.get_size())
                self.bg_image.fill((0, 0, 0))
        
        # Load audio
        if 'audio' in self.scene_data:
            try:
                self.audio = pygame.mixer.Sound(self.scene_data['audio'])
                self.audio.play()
            except pygame.error:
                print(f"Could not load audio: {self.scene_data['audio']}")
    
    def update(self, dt: float) -> bool:
        if self.fading_in:
            self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            if self.fade_alpha >= 255:
                self.fading_in = False
        elif self.fading_out:
            self.fade_alpha = max(0, self.fade_alpha - self.fade_speed)
            if self.fade_alpha <= 0:
                self.cleanup()  # Stop audio when fade out completes
                self.completed = True
        
        # Only return completed if we're not in the middle of a fade effect
        return self.completed
    
    def draw(self):
        # Always draw background image first
        if self.bg_image:
            self.screen.blit(self.bg_image, (0, 0))
        
        # Draw text box if there's text and not a name input scene
        if not self.is_name_input and 'text' in self.scene_data:
            self.draw_text_box(self.scene_data['text'])
        
        # Show prompt when ready for input
        if not self.fading_in and not self.fading_out and not self.is_name_input:
            prompt_font = pygame.font.SysFont('Bauhaus 93', 24)
            prompt = prompt_font.render("Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(
                right=self.screen.get_width() - 20,
                bottom=self.screen.get_height() - 20
            )
            self.screen.blit(prompt, prompt_rect)
        
        # Apply fade effect last
        fade_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        fade_surface.fill((0, 0, 0, 255 - self.fade_alpha))
        self.screen.blit(fade_surface, (0, 0))
    
    def draw_text_box(self, text: str):
        # Create semi-transparent text box
        box_height = 150
        box_surface = pygame.Surface((self.screen.get_width(), box_height), pygame.SRCALPHA)
        box_surface.fill((0, 0, 0, 180))
        
        # Draw text
        lines = self.wrap_text(text, self.screen.get_width() - 40)
        y_offset = 20
        for line in lines:
            text_surface = self.text_font.render(line, True, (255, 255, 255))
            box_surface.blit(text_surface, (20, y_offset))
            y_offset += 40
        
        # Draw box at bottom of screen
        self.screen.blit(box_surface, (0, self.screen.get_height() - box_height))
    
    def wrap_text(self, text: str, max_width: int):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.text_font.render(word + " ", True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def cleanup(self):
        """Stop audio playback and cleanup resources"""
        if hasattr(self, 'audio') and self.audio:
            try:
                self.audio.stop()
            except (pygame.error, AttributeError):
                pass  # Ignore errors during cleanup
        self.audio = None

    def __del__(self):
        """Ensure audio is stopped when the scene is destroyed"""
        self.cleanup()

    def handle_input(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not self.fading_in and not self.fading_out:
                self.fading_out = True

def load_minigame(level):
    """Load and run a minigame module when needed"""
    try:
        # Stop any ongoing sounds and music
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        
        # Store current display settings
        current_display = pygame.display.get_surface().copy()
        
        result = False
        
        if level == 1:
            from mini_game1 import main
            result = main()
        elif level == 2:
            from mini_game2 import main
            result = main()
        elif level == 3:
            from mini_game3 import main
            result = main()
        elif level == 4:
            from mini_game4 import main
            result = main()
        elif level == 5:
            from mini_game5 import main
            result = main()
        else:
            print(f"No minigame defined for level {level}")
            return False
            
        # Reset display mode and caption
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Decoding Island')
        
        # Restore previous display if minigame wasn't completed
        if not result:
            screen.blit(current_display, (0, 0))
            pygame.display.flip()
            
            # Show message to player
            font = pygame.font.SysFont('Bauhaus 93', 32)
            text = font.render("You must complete the minigame to proceed!", True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            
            # Wait a moment so player can read the message
            pygame.time.wait(2000)
            
        # Re-initialize game sounds
        init_game()
        
        return result
        
    except ImportError as e:
        print(f"Warning: Could not load minigame {level}: {e}")
        return False
    except Exception as e:
        print(f"Error running minigame {level}: {e}")
        return False

class PauseButton:
    def __init__(self, screen):
        self.screen = screen
        # Create button in top right corner with padding
        self.rect = pygame.Rect(SCREEN_WIDTH - 120, 10, 100, 30)
        self.color = (0, 0, 0, 180)  # Semi-transparent black
        self.hover_color = (50, 50, 50, 180)
        self.font = pygame.font.SysFont('Bauhaus 93', 24)
        self.text = self.font.render('PAUSE', True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.is_hovered = False

    def draw(self):
        # Create surface with alpha for transparency
        button_surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        # Draw button with hover effect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=5)
        
        # Draw button on screen
        self.screen.blit(button_surface, self.rect)
        self.screen.blit(self.text, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

class EnhancedGameStats:
    def __init__(self, screen):
        self.screen = screen
        
        # Load and scale icons with more reasonable size
        try:
            icon_size = (32, 32)  # Reduced from 40
            self.trophy_icon = pygame.transform.scale(pygame.image.load('img/trophy.png'), icon_size)
            self.key_icon = pygame.transform.scale(pygame.image.load('img/key_icon.png'), icon_size)
            self.clock_icon = pygame.transform.scale(pygame.image.load('img/clock.png'), icon_size)
        except Exception as e:
            print(f"Error loading game stats icons: {e}")
            self.trophy_icon = pygame.Surface(icon_size)
            self.trophy_icon.fill((255, 215, 0))
            self.key_icon = pygame.Surface(icon_size)
            self.key_icon.fill((255, 255, 255))
            self.clock_icon = pygame.Surface(icon_size)
            self.clock_icon.fill((100, 200, 255))
        
        # Fonts with better sizes
        self.title_font = pygame.font.SysFont('Bauhaus 93', 28)
        self.stats_font = pygame.font.SysFont('Bauhaus 93', 24)
        self.small_font = pygame.font.SysFont('Bauhaus 93', 20)

    def draw_stats_panel(self, level, keys_collected, required_keys, elapsed_time, time_limit):
        # Main panel dimensions
        panel_width = 600  # Fixed width
        panel_height = 40  # Reduced height
        panel_x = (SCREEN_WIDTH - panel_width) // 2  # Center horizontally
        panel_y = 10  # Top padding
        
        # Create semi-transparent panel
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (0, 0, 0, 150), (0, 0, panel_width, panel_height), border_radius=10)
        
        # Section widths
        section_width = panel_width // 3
        
        # Level name (left section)
        level_text = f"{LEVEL_NAMES[level]}"
        name_surface = self.stats_font.render(level_text, True, (255, 215, 0))
        name_x = 20  # Left padding
        name_y = (panel_height - name_surface.get_height()) // 2
        panel_surface.blit(name_surface, (name_x, name_y))
        
        # Time remaining (middle section)
        remaining_time = time_limit - elapsed_time
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        timer_text = self.stats_font.render(f"{minutes:02}:{seconds:02}", True, (255, 255, 255))
        timer_x = section_width + (section_width - timer_text.get_width()) // 2
        timer_y = (panel_height - timer_text.get_height()) // 2
        panel_surface.blit(timer_text, (timer_x, timer_y))
        
        # Keys collected (right section)
        key_text = self.stats_font.render(f"{keys_collected}/{required_keys}", True, (255, 255, 255))
        key_x = section_width * 2 + (section_width - key_text.get_width() - self.key_icon.get_width() - 5) // 2
        key_y = (panel_height - key_text.get_height()) // 2
        panel_surface.blit(self.key_icon, (key_x, key_y))
        panel_surface.blit(key_text, (key_x + self.key_icon.get_width() + 5, key_y))
        
        # Draw the panel on screen
        self.screen.blit(panel_surface, (panel_x, panel_y))

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.options = ['RESUME', 'RESTART LEVEL', 'QUIT TO MENU']
        
        # Button dimensions and styling
        self.button_width = 250
        self.button_height = 40
        self.button_spacing = 20
        
        # Create button rects centered on screen
        self.button_rects = []
        start_y = SCREEN_HEIGHT // 2
        for i in range(len(self.options)):
            rect = pygame.Rect(
                (SCREEN_WIDTH - self.button_width) // 2,
                start_y + (self.button_height + self.button_spacing) * i,
                self.button_width,
                self.button_height
            )
            self.button_rects.append(rect)
            
        # Fonts
        self.title_font = pygame.font.SysFont('Bauhaus 93', 50)
        self.option_font = pygame.font.SysFont('Bauhaus 93', 35)
        
        # Colors
        self.text_color = (255, 255, 255)
        self.button_color = (50, 50, 50, 180)
        self.hover_color = (70, 70, 70, 180)
        self.selected_color = (255, 215, 0)
        
        self.hovered = None

    def draw(self):
        # Draw dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw PAUSED text
        pause_text = self.title_font.render('PAUSED', True, self.text_color)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//4))
        self.screen.blit(pause_text, text_rect)
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons with hover effect
        for i, (option, rect) in enumerate(zip(self.options, self.button_rects)):
            # Check if mouse is hovering over button
            is_hovered = rect.collidepoint(mouse_pos)
            if is_hovered:
                self.hovered = i
                color = self.hover_color
            else:
                color = self.button_color
            
            # Create button surface with alpha
            button_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            pygame.draw.rect(button_surface, color, button_surface.get_rect(), border_radius=5)
            self.screen.blit(button_surface, rect)
            
            # Draw button text
            text = self.option_font.render(option, True, self.selected_color if is_hovered else self.text_color)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    return self.options[i]
        return None

def handle_level_completion(current_level, door, player):
    """Handle level completion and transitions"""
    if not door.entered and keys_collected >= LEVEL_REQUIREMENTS[current_level]:
        # Start door zoom if we have enough keys
        if not door.is_open:
            camera.start_door_zoom(door)
        elif pygame.sprite.collide_rect(player, door):
            door.entered = True
            camera.stop_sounds()
            return True
    return False

def transition_to_next_level():
    """Handle transition to the next level"""
    global current_level, movement_enabled
    
    # Store completion time
    if game_start_time:
        elapsed_time = int(time.time() - game_start_time)
        level_times.append(elapsed_time)
    
    # Determine next level
    next_level = current_level + 1 if current_level < 5 else None
    
    if next_level is not None:
        # Initialize next level
        result = init_level(next_level)
        if result is not None:
            keys_group, door, world, moving_enemies, player, ghost = result
            camera.start_transition()
            movement_enabled = False
            return "playing"
        else:
            print(f"Failed to initialize level {next_level}")
            return "error"
    else:
        # Game completed
        return "game_complete"

def handle_pause():
    """Handle pause menu state and actions"""
    global paused, running, current_state, keys_collected, game_over, total_pause_time, pause_start_time
    
    pause_menu.draw()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
            
        if current_state in ["intro_scenes", "level_transition"]:
            scene_manager.handle_input(event)
        
        # Handle pause button click
        if current_state == "playing" and not paused and pause_button.handle_event(event):
            paused = True
            pause_start_time = datetime.now()
            fade_alpha = 0
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                paused = False
                total_pause_time += datetime.now() - pause_start_time
                return True
                
        action = pause_menu.handle_input(event)
        if action:
            if action == 'RESUME':
                paused = False
                total_pause_time += datetime.now() - pause_start_time
            elif action == 'RESTART LEVEL':
                paused = False
                game_over = 0
                keys_collected = 0
                if hasattr(player, 'stop_sounds'):
                    player.stop_sounds()
                if hasattr(camera, 'stop_sounds'):
                    camera.stop_sounds()
                camera.cleanup()
                camera.reset_zoom()
                keys_group, door, world, moving_enemies, player, ghost = init_level(current_level)
                camera.start_transition()
            elif action == 'QUIT TO MENU':
                # Cleanup current game resources
                if hasattr(player, 'stop_sounds'):
                    player.stop_sounds()
                if hasattr(camera, 'stop_sounds'):
                    camera.stop_sounds()
                cleanup_backgrounds()
                pygame.mixer.stop()  # Stop all sound channels
                pygame.mixer.music.stop()  # Stop background music
                pygame.quit()

                # Import and run main menu
                try:
                    import MAINMENU
                    MAINMENU.main()
                    sys.exit()
                except ImportError as e:
                    print(f"Error returning to main menu: {e}")
                    return False
    
    pygame.display.update()
    return True

def cleanup_game():
    """Cleanup all game resources"""
    if hasattr(player, 'stop_sounds'):
        player.stop_sounds()
    if hasattr(camera, 'stop_sounds'):
        camera.stop_sounds()
    if hasattr(scene_manager, 'cleanup'):
        scene_manager.cleanup()
    cleanup_backgrounds()
    pygame.mixer.stop()
    pygame.mixer.music.stop()
    pygame.quit()

class DialogueBox:
    def __init__(self, screen):
        self.screen = screen
        self.animation_complete = False
        self.current_alpha = 0
        self.target_alpha = 180
        self.fade_speed = 10
        self.current_line = 0
        self.current_word = 0
        self.text_delay = 2
        self.frame_counter = 0
        self.words_revealed = []
        
        # Dialogue box dimensions and position
        self.box_height = 200
        self.box_padding = 20
        self.box_y = SCREEN_HEIGHT - self.box_height - 30
        
        # Text formatting
        self.line_height = 40
        self.max_width = SCREEN_WIDTH - (self.box_padding * 2)
        self.font = pygame.font.SysFont('Bauhaus 93', 32)
        
    def wrap_text(self, text):
        """Split text into lines that fit within the dialogue box"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = self.font.render(word + ' ', True, (255, 255, 255))
            word_width = word_surface.get_width()
            
            if current_width + word_width <= self.max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def animate(self, dialogue_lines, background_image=None):
        # Draw background image if provided
        if background_image:
            try:
                bg_img = pygame.image.load(background_image).convert()
                bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
                self.screen.blit(bg_img, (0, 0))
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading background image: {e}")
                self.screen.fill((0, 0, 0))
        
        # Create semi-transparent dialogue box
        dialogue_surface = pygame.Surface((SCREEN_WIDTH, self.box_height), pygame.SRCALPHA)
        box_color = (0, 0, 0, self.current_alpha)
        pygame.draw.rect(dialogue_surface, box_color, (0, 0, SCREEN_WIDTH, self.box_height))
        
        # Animate fade in
        if self.current_alpha < self.target_alpha:
            self.current_alpha = min(self.current_alpha + self.fade_speed, self.target_alpha)
        
        self.screen.blit(dialogue_surface, (0, self.box_y))
        
        # Initialize words_revealed if needed
        if not self.words_revealed:
            # Wrap each dialogue line
            wrapped_lines = []
            for line in dialogue_lines:
                wrapped_lines.extend(self.wrap_text(line))
            self.words_revealed = [[] for _ in wrapped_lines]
        
        # Update text animation
        self.frame_counter += 1
        if self.frame_counter >= self.text_delay:
            self.frame_counter = 0
            self.update_text(dialogue_lines)
        
        # Draw text
        y_offset = self.box_y + self.box_padding
        line_spacing = 40
        
        for i, revealed_words in enumerate(self.words_revealed):
            if revealed_words:  # Only draw lines that have revealed words
                text = ' '.join(revealed_words)
                text_surface = self.font.render(text, True, (255, 255, 255))
                text_rect = text_surface.get_rect(
                    left=self.box_padding,
                    top=y_offset + i * line_spacing
                )
                self.screen.blit(text_surface, text_rect)
        
        # Add "Press SPACE to continue" prompt when animation is complete
        if self.animation_complete:
            prompt = pygame.font.SysFont('Bauhaus 93', 24).render(
                "Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(
                right=SCREEN_WIDTH - self.box_padding,
                bottom=SCREEN_HEIGHT - self.box_padding
            )
            self.screen.blit(prompt, prompt_rect)
        
        return self.animation_complete
    
    def update_text(self, dialogue_lines):
        if self.current_line < len(dialogue_lines):
            wrapped_lines = []
            for line in dialogue_lines:
                wrapped_lines.extend(self.wrap_text(line))
            
            if self.current_line < len(wrapped_lines):
                words = wrapped_lines[self.current_line].split()
                if self.current_word < len(words):
                    self.words_revealed[self.current_line].append(words[self.current_word])
                    self.current_word += 1
                else:
                    self.current_line += 1
                    self.current_word = 0
            else:
                self.animation_complete = True
        else:
            self.animation_complete = True

def show_dialogue(dialogue_lines, background_key=None):
    """
    Show dialogue with background image based on the dialogue section.
    
    Args:
        dialogue_lines (list): List of strings containing dialogue text
        background_key (str): Key for background image from DIALOGUE_BACKGROUNDS
    """
    dialogue_box = DialogueBox(screen)
    background_path = None
    
    if background_key and background_key in DIALOGUE_BACKGROUNDS:
        background_path = DIALOGUE_BACKGROUNDS[background_key]
        try:
            background = pygame.image.load(background_path).convert()
            background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading background image {background_path}: {e}")
            background = None
    else:
        background = None

    waiting = True
    while waiting:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dialogue_box.animation_complete:
                    waiting = False
                    return True
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw background if available
        if background:
            screen.blit(background, (0, 0))
            
        dialogue_box.animate(dialogue_lines)
        pygame.display.update()
    
    return True

class Ghost(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, player, level):
        super().__init__()
        # Load and scale ghost image
        self.image = pygame.image.load('img/sghost.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (60, 60))
        self.rect = self.image.get_rect()
        
        # Ghost properties - Make ghost slower in higher levels
        self.base_speed = 2.0
        # Decrease speed for each level instead of increasing
        self.level_speed_multiplier = -0.25  # Changed from 0.4 to -0.25
        # Set minimum speed to prevent ghost from becoming too slow
        self.speed = max(0.8, self.base_speed + (level * self.level_speed_multiplier))
        self.player = player
        
        # Decrease visibility range in higher levels
        self.visibility_range = max(400, 600 - (level * 50))  # Starts at 600, decreases by 50 each level
        
        # Set initial position
        self.spawn_position(screen_width, screen_height)
        
        # Floating movement properties
        self.float_offset = 0
        self.float_speed = 0.05
        self.float_amplitude = 8
        self.true_x = float(self.rect.x)
        self.true_y = float(self.rect.y)
        
        # Transparency properties - Make ghost more transparent in higher levels
        self.min_alpha = max(80, 120 - (level * 10))  # Starts at 120, decreases by 10 each level
        
        # Pulsing effect
        self.pulse_counter = 0
        self.pulse_speed = 0.05
        self.pulse_range = max(20, 40 - (level * 5))  # Reduced pulsing range in higher levels

    def spawn_position(self, screen_width, screen_height):
        """Spawn ghost at the farthest point from player"""
        corners = [
            (0, 0),
            (screen_width - self.rect.width, 0),
            (0, screen_height - self.rect.height),
            (screen_width - self.rect.width, screen_height - self.rect.height)
        ]
        
        max_distance = 0
        spawn_pos = corners[0]
        
        for corner in corners:
            distance = math.sqrt(
                (corner[0] - self.player.rect.x) ** 2 + 
                (corner[1] - self.player.rect.y) ** 2
            )
            if distance > max_distance:
                max_distance = distance
                spawn_pos = corner
        
        self.rect.x = spawn_pos[0]
        self.rect.y = spawn_pos[1]
        self.true_x = float(self.rect.x)
        self.true_y = float(self.rect.y)

    def update(self):
        if not movement_enabled or camera.door_zoom:
            return
            
        # Calculate direction to player
        dx = self.player.rect.centerx - self.rect.centerx
        dy = self.player.rect.centery - self.rect.centery
        
        # Normalize the direction
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance > 0:
            dx = dx / distance
            dy = dy / distance
        
        # Update position with adjusted tracking
        distance_factor = min(1.0, distance / self.visibility_range)  # Reduced from 1.5 to 1.0
        actual_speed = self.speed * distance_factor
        
        self.true_x += dx * actual_speed
        self.true_y += dy * actual_speed
        
        # Add floating movement
        self.float_offset += self.float_speed
        float_y = math.sin(self.float_offset) * self.float_amplitude
        
        # Update rect position
        self.rect.x = int(self.true_x)
        self.rect.y = int(self.true_y + float_y)
        
        # Update pulsing effect
        self.pulse_counter += self.pulse_speed
        pulse_alpha = math.sin(self.pulse_counter) * self.pulse_range
        
        # Calculate alpha with reduced visibility range
        current_distance = math.sqrt(
            (self.player.rect.centerx - self.rect.centerx) ** 2 + 
            (self.player.rect.centery - self.rect.centery) ** 2
        )
        
        # Calculate alpha with pulsing effect
        base_alpha = max(self.min_alpha, min(255, (1 - current_distance / self.visibility_range) * 255))
        final_alpha = min(255, max(self.min_alpha, base_alpha + pulse_alpha))
        
        # Apply alpha
        self.image.set_alpha(int(final_alpha))

    def check_collision(self, player):
        """Check for collision with player using a larger collision margin in higher levels"""
        # Increase collision margin for higher levels to make it more forgiving
        collision_margin = 8 + (current_level * 2)  # Increases by 2 pixels per level
        collision_rect = pygame.Rect(
            self.rect.x + collision_margin,
            self.rect.y + collision_margin,
            self.rect.width - (collision_margin * 2),
            self.rect.height - (collision_margin * 2)
        )
        return collision_rect.colliderect(player.rect)
    
def check_level_timer(elapsed_time, time_limit):
    """Check if the level time limit has been exceeded"""
    return elapsed_time >= time_limit

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scroll_x = 0
        self.scroll_y = 0
        self.zoom = 1
        self.target_zoom = 1
        self.base_zoom = 2.5
        self.zoom_out_level = 1.3
        self.zoom_speed = 0.04
        self.transitioning = False
        self.transition_start_time = 0
        self.transition_delay = 2000
        self.transition_duration = 2000
        self.transition_total_time = self.transition_delay + self.transition_duration
        self.transition_complete = False
        self.manual_zoom_active = False
        self.initial_zoom_done = False
        
        # Door zoom properties
        self.door_zoom = False
        self.door_zoom_target = None
        self.door_zoom_speed = 0.02
        self.door_target_zoom = 3.5
        self.door_transition_start = 0
        self.door_transition_duration = 1500
        self.post_open_delay = 1000
        self.door_opened_time = 0
        self.reset_on_death = False
        self.death_reset_time = 0
        self.death_reset_duration = 1000  # 1 second for reset animation
        
        # Sound properties
        self.wind_sound = pygame.mixer.Sound('img/Gust of Wind.mp3')
        self.jungle_music = pygame.mixer.Sound('img/Background Music.MP3')
        self.zoom_out_sound = pygame.mixer.Sound('img/zoom_out.mp3')  # Add this line
        self.wind_sound.set_volume(0.8)
        self.jungle_music.set_volume(0.4)
        self.zoom_out_sound.set_volume(0.5)  # Add this line
        self.wind_sound_playing = False
        self.jungle_music_playing = False
        self.wind_sound_start_time = 0
        self.wind_sound_duration = int(self.wind_sound.get_length() * 1000)
        
        self.visible_width = width
        self.visible_height = height

    def apply(self, surface, entity):
        scaled_rect = scale_rect(entity.rect)
        return pygame.Rect(
            scaled_rect.x - self.scroll_x,
            scaled_rect.y - self.scroll_y,
            scaled_rect.width,
            scaled_rect.height
        )

    def apply_sprite(self, surface, sprite):
        scaled_pos = scale_position(
            sprite.rect.x - self.scroll_x,
            sprite.rect.y - self.scroll_y
        )
        return scaled_pos

    def reset_zoom(self):
        """Reset camera zoom when player dies"""
        self.reset_on_death = True
        self.death_reset_time = pygame.time.get_ticks()
        self.zoom = self.base_zoom
        self.target_zoom = self.base_zoom
        self.manual_zoom_active = False
        self.door_zoom = False
        self.door_zoom_target = None
        self.transitioning = False
        self.initial_zoom_done = True

    def start_door_zoom(self, door):
        if not self.door_zoom and not self.manual_zoom_active:
            self.door_zoom = True
            self.door_zoom_target = door
            self.door_transition_start = pygame.time.get_ticks()
            self.door_target_zoom = 3.5
            # All entities will freeze due to the door_zoom check in their update methods
        
    def start_transition(self):
        # Stop any existing sounds before starting new ones
        self.stop_sounds()
        self.transitioning = True
        self.transition_complete = False
        self.zoom = 1
        self.transition_start_time = pygame.time.get_ticks()
        
        # Start wind sound and track its start time
        self.wind_sound.play()
        self.wind_sound_playing = True
        self.wind_sound_start_time = pygame.time.get_ticks()
        self.jungle_music_playing = False
    
    def update(self, target, keys_collected, door, required_keys):
        current_time = pygame.time.get_ticks()
        
        # Handle manual zoom control with Enter key
        keys = pygame.key.get_pressed()
        if keys[pygame.K_RETURN]:
            self.manual_zoom_active = True
            self.target_zoom = self.zoom_out_level
            self.zoom_out_sound.play()
        elif self.manual_zoom_active:
            self.manual_zoom_active = False
            self.target_zoom = self.base_zoom if self.transition_complete else 1
        
        # Handle initial transition
        if self.transitioning and not self.initial_zoom_done:
            elapsed = current_time - self.transition_start_time
            
            if elapsed >= self.transition_delay:
                zoom_elapsed = elapsed - self.transition_delay
                progress = min(zoom_elapsed / self.transition_duration, 1.0)
                progress = self.ease_out_cubic(progress)
                
                if not self.manual_zoom_active:
                    self.zoom = 1 + (self.base_zoom - 1) * progress
                
                if progress >= 1:
                    self.transitioning = False
                    self.transition_complete = True
                    self.initial_zoom_done = True
                    global movement_enabled, game_start_time
                    movement_enabled = True
                    
                    # Only start the timer when the initial zoom is complete
                    if game_start_time is None:
                        game_start_time = time.time()
                    
                    if not self.manual_zoom_active:
                        self.zoom = self.base_zoom
                        self.target_zoom = self.base_zoom
        
        # Handle smooth zoom transition
        elif not self.door_zoom:
            if self.zoom != self.target_zoom:
                diff = self.target_zoom - self.zoom
                self.zoom += diff * self.zoom_speed
        
        # Handle door zoom if active
        if self.door_zoom and self.door_zoom_target:
            elapsed = current_time - self.door_transition_start
            
            if not self.door_zoom_target.is_open:
                progress = min(elapsed / self.door_transition_duration, 1.0)
                progress = self.ease_out_cubic(progress)
                
                self.zoom = 1 + (self.door_target_zoom - 1) * progress
                
                # Calculate center position for the door
                target_x = self.door_zoom_target.rect.centerx - (SCREEN_WIDTH // (2 * self.zoom))
                target_y = self.door_zoom_target.rect.centery - (SCREEN_HEIGHT // (2 * self.zoom))
                
                # Smoothly move camera to center the door
                self.scroll_x += (target_x - self.scroll_x) * 0.1
                self.scroll_y += (target_y - self.scroll_y) * 0.1
                
                if progress >= 1.0:
                    self.door_zoom_target.open_door()
                    self.door_opened_time = current_time
            else:
                hold_time = current_time - self.door_opened_time
                if hold_time >= self.post_open_delay:
                    zoom_out_progress = min((hold_time - self.post_open_delay) / 1000, 1.0)
                    zoom_out_progress = self.ease_out_cubic(zoom_out_progress)
                    
                    target_zoom = self.target_zoom
                    self.zoom = self.door_target_zoom - (self.door_target_zoom - target_zoom) * zoom_out_progress
                    
                    if zoom_out_progress >= 1.0:
                        self.door_zoom = False
                        self.zoom = target_zoom
        
        # Handle death reset
        if self.reset_on_death:
            elapsed = current_time - self.death_reset_time
            if elapsed <= self.death_reset_duration:
                # Smoothly transition zoom back to base level
                progress = elapsed / self.death_reset_duration
                progress = self.ease_out_cubic(progress)
                self.zoom = 1 + (self.base_zoom - 1) * progress
            else:
                self.reset_on_death = False
                self.zoom = self.base_zoom
                self.target_zoom = self.base_zoom
        
        # Update sound behavior
        if (self.wind_sound_playing and 
            current_time - self.wind_sound_start_time >= self.wind_sound_duration and 
            not self.jungle_music_playing):
            self.wind_sound_playing = False
            self.jungle_music.play()
            self.jungle_music_playing = True
        
        # Update visible area and camera position
        self.visible_width = self.width // self.zoom
        self.visible_height = self.height // self.zoom
        
        # Normal camera follow behavior when not zooming to door
        if not self.door_zoom:
            target_x = target.rect.centerx - self.visible_width // 2
            target_y = target.rect.centery - self.visible_height // 2
            
            self.scroll_x += (target_x - self.scroll_x) * 0.1
            self.scroll_y += (target_y - self.scroll_y) * 0.1
        
        # Keep the camera within bounds
        self.scroll_x = max(0, min(self.scroll_x, SCREEN_WIDTH - self.visible_width))
        self.scroll_y = max(0, min(self.scroll_y, SCREEN_HEIGHT - self.visible_height))
    
    def stop_sounds(self):
        """Stop all sounds and reset sound states"""
        try:
            if pygame.mixer.get_init():  # Check if mixer is initialized
                self.wind_sound.stop()
                self.jungle_music.stop()
                self.zoom_out_sound.stop()  # Add this line
        except (AttributeError, pygame.error):
            pass
        self.wind_sound_playing = False
        self.jungle_music_playing = False

        
    # Update the Camera class cleanup method:
    def cleanup(self):
        """Clean up all audio resources and reset camera state"""
        self.stop_sounds()
        self.transitioning = False
        self.transition_complete = False
        self.zoom = 1
        self.wind_sound_start_time = 0
        self.door_zoom = False
        self.door_zoom_target = None
        
    def __del__(self):
        """Destructor to ensure sounds are stopped when the camera object is destroyed"""
        try:
            self.stop_sounds()
        except:
            pass  # Ignore any errors during cleanup

    def ease_out_cubic(self, x):
        return 1 - pow(1 - x, 3)

    def apply(self, surface, entity):
        return pygame.Rect(
            entity.rect.x - self.scroll_x,
            entity.rect.y - self.scroll_y,
            entity.rect.width,
            entity.rect.height
        )

    def apply_sprite(self, surface, sprite):
        # Return the position where the sprite should be drawn
        return (sprite.rect.x - self.scroll_x,
                sprite.rect.y - self.scroll_y)
                
    def apply_rect(self, rect):
        # Apply camera offset to a rect
        return pygame.Rect(
            rect.x - self.scroll_x,
            rect.y - self.scroll_y,
            rect.width,
            rect.height
        )

def reset_level():
    """Properly reset the level state and reinitialize all game components"""
    global game_over, keys_collected, movement_enabled, game_start_time
    global player, world, moving_enemies, keys_group, door, ghost, camera
    global total_pause_time, current_level

    # Reset game state
    game_over = 0
    keys_collected = 0
    movement_enabled = False
    game_start_time = None
    total_pause_time = timedelta(0)

    # Stop all sounds
    if hasattr(player, 'stop_sounds'):
        player.stop_sounds()
    if hasattr(camera, 'stop_sounds'):
        camera.stop_sounds()

    # Cleanup camera
    camera.cleanup()
    camera.reset_zoom()

    try:
        # Get fresh level data
        platforms = LEVEL_PLATFORM_DATA[current_level]
        deadly_tiles = LEVEL_DEADLY_DATA[current_level]
        enemy_data = LEVEL_ENEMY_DATA[current_level]

        # Create new world instance
        world = World(platforms, deadly_tiles)

        # Get spawn position
        spawn_pos = find_spawn_position(platforms)

        # Create new player at spawn position
        player = Player(spawn_pos[0], spawn_pos[1])
        player.dead = False  # Ensure player is not dead

        # Create fresh ghost
        ghost = Ghost(SCREEN_WIDTH, SCREEN_HEIGHT, player, current_level)

        # Get door position and create new door
        door_pos = find_door_position(platforms)
        door = Door(door_pos[0], door_pos[1])
        door.entered = False
        door.is_open = False

        # Create fresh key group with new key positions
        keys_group = pygame.sprite.Group()
        key_positions = generate_key_positions(current_level)
        for pos in key_positions:
            keys_group.add(Key(pos[0], pos[1]))

        # Create fresh enemies
        moving_enemies = pygame.sprite.Group()
        for enemy_info in enemy_data:
            x, y, direction, boundary_start, boundary_end = enemy_info
            enemy = MovingEnemy(x * TILE_SIZE, y * TILE_SIZE, direction, boundary_start, boundary_end)
            moving_enemies.add(enemy)

        # Reset camera and start transition
        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        camera.start_transition()

        return True

    except Exception as e:
        print(f"Error resetting level: {e}")
        return False


def generate_key_positions(level):
    """Improved key position generation with better boundary checking"""
    positions = []
    required_keys = LEVEL_REQUIREMENTS[level]
    platforms = LEVEL_PLATFORM_DATA[level]
    
    # Screen boundaries with margin
    MARGIN = TILE_SIZE * 2
    screen_bounds = {
        'left': MARGIN,
        'right': SCREEN_WIDTH - MARGIN,
        'top': MARGIN,
        'bottom': SCREEN_HEIGHT - MARGIN
    }
    
    def is_within_bounds(x, y):
        """Check if position is within screen bounds"""
        return (screen_bounds['left'] <= x <= screen_bounds['right'] and
                screen_bounds['top'] <= y <= screen_bounds['bottom'])
    
    # Get viable platform positions
    viable_platforms = []
    for plat in platforms:
        x = plat[0] * TILE_SIZE
        y = plat[1] * TILE_SIZE
        width = plat[2] * TILE_SIZE
        
        # Skip ground level platforms
        if y < SCREEN_HEIGHT * 0.8:
            # Adjust platform boundaries to ensure keys stay within screen
            plat_left = max(x + MARGIN, screen_bounds['left'])
            plat_right = min(x + width - MARGIN, screen_bounds['right'])
            
            if plat_right > plat_left:  # Only add if there's valid space
                viable_platforms.append((plat_left, y, plat_right - plat_left))
    
    import random
    random.shuffle(viable_platforms)
    
    # Keep trying until we have all required keys
    attempts = 0
    max_attempts = required_keys * 10  # Generous attempt limit
    
    while len(positions) < required_keys and attempts < max_attempts:
        if not viable_platforms:
            break
            
        plat = random.choice(viable_platforms)
        
        # Generate position on platform
        key_x = random.uniform(plat[0], plat[0] + plat[2])
        key_y = plat[1] - TILE_SIZE * 1.5  # Place above platform
        
        # Verify position is within bounds
        if is_within_bounds(key_x, key_y):
            positions.append((key_x, key_y))
        
        attempts += 1
    
    # If we still need more keys, place them on the most suitable platforms
    while len(positions) < required_keys:
        if not viable_platforms:
            break
            
        # Use the widest platform available
        plat = max(viable_platforms, key=lambda p: p[2])
        
        # Calculate safe position
        key_x = plat[0] + (plat[2] / 2)  # Center of platform
        key_y = plat[1] - TILE_SIZE * 1.5
        
        if is_within_bounds(key_x, key_y):
            positions.append((key_x, key_y))
        viable_platforms.remove(plat)
    
    return positions

# Update the video background handling code
def update_video_background(level):
    """Update video frame for video backgrounds"""
    if level in video_captures and video_captures[level] is not None:
        ret, frame = video_captures[level].read()
        if not ret:
            # Reset video to beginning if we've reached the end
            video_captures[level].set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = video_captures[level].read()
        
        if ret:
            # Convert frame from BGR to RGB and flip to match Pygame's format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
            frame = np.rot90(frame)
            frame = np.flipud(frame)
            frame = pygame.surfarray.make_surface(frame)
            return frame
    return None

# Update the initialization of video captures
# Initialize game assets
def init_game():
    """Initialize video captures and background surfaces"""
    global video_captures, background_surfaces, game_stats, pause_menu
    update_scale_factors()  # Update scaling factors
    video_captures = {}
    background_surfaces = {}
    # Update this line to use EnhancedGameStats instead of GameStats
    game_stats = EnhancedGameStats(screen)
    pause_menu = PauseMenu(screen)
    
    for level, bg_data in level_backgrounds.items():
        if bg_data['type'] == 'video':
            try:
                cap = cv2.VideoCapture(bg_data['path'])
                if not cap.isOpened():
                    print(f"Failed to open video file for level {level}")
                    cap = None
                video_captures[level] = cap
            except Exception as e:
                print(f"Error loading video for level {level}: {e}")
                video_captures[level] = None
        else:
            try:
                img = pygame.image.load(bg_data['path']).convert()
                background_surfaces[level] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
            except Exception as e:
                print(f"Error loading image for level {level}: {e}")
                fallback = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                fallback.fill((0, 0, 0))
                background_surfaces[level] = fallback

def get_background(level):
    """Get the current background surface for the given level"""
    if level_backgrounds[level]['type'] == 'video':
        return update_video_background(level)
    else:
        return background_surfaces[level]

# Update the cleanup function
def cleanup_backgrounds():
    """Release all video captures properly"""
    global video_captures
    if 'video_captures' in globals():
        for cap in video_captures.values():
            if cap is not None:
                cap.release()
        video_captures.clear()


def create_zoomed_view(screen, camera, player, world, keys_group, door, moving_enemies, ghost):
    current_visible_width = int(SCREEN_WIDTH // camera.zoom)
    current_visible_height = int(SCREEN_HEIGHT // camera.zoom)
    
    view_surface = pygame.Surface((current_visible_width, current_visible_height))
    
    # Get and draw the current background
    current_background = get_background(current_level)
    if current_background:
        view_surface.blit(current_background, (-camera.scroll_x, -camera.scroll_y))
    
    # Draw platforms (if you want them visible)
    # for tile in world.collision_tiles:
    #     pygame.draw.rect(view_surface, (255, 0, 0), camera.apply_rect(tile.rect), 1)
    
    # Draw keys
    for key in keys_group:
        pos = camera.apply_sprite(view_surface, key)
        if (0 <= pos[0] < current_visible_width and 
            0 <= pos[1] < current_visible_height):
            view_surface.blit(key.image, pos)
    
    # Draw door
    door_pos = camera.apply_sprite(view_surface, door)
    if (0 <= door_pos[0] < current_visible_width and 
        0 <= door_pos[1] < current_visible_height):
        view_surface.blit(door.image, door_pos)
    
    # Draw moving enemies
    for enemy in moving_enemies:
        enemy_pos = camera.apply_sprite(view_surface, enemy)
        if (0 <= enemy_pos[0] < current_visible_width and 
            0 <= enemy_pos[1] < current_visible_height):
            view_surface.blit(enemy.image, enemy_pos)
    
    # Draw ghost
    ghost_pos = camera.apply_sprite(view_surface, ghost)
    if (0 <= ghost_pos[0] < current_visible_width and 
        0 <= ghost_pos[1] < current_visible_height):
        view_surface.blit(ghost.image, ghost_pos)
    
    # Draw player last
    player_pos = camera.apply_sprite(view_surface, player)
    if (0 <= player_pos[0] < current_visible_width and 
        0 <= player_pos[1] < current_visible_height):
        view_surface.blit(player.image, player_pos)
    
    # Scale and draw the final view
    scaled_surface = pygame.transform.scale(view_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled_surface, (0, 0))
    
    """"
    # Draw HUD elements
    draw_text(f"Level {current_level}", 40, WHITE, 10, 10)
    draw_text(f"Keys: {keys_collected}/{LEVEL_REQUIREMENTS[current_level]}", 40, WHITE, 10, 60)
    """
    
class CollisionTile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = key_frames  # Use the key_frames list we created earlier
        
        # Animation variables
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_delay = 100  # Milliseconds between frame changes
        
        # Set initial image
        self.image = self.frames[self.current_frame] if self.frames else key_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Floating movement variables
        self.original_y = float(y)
        self.float_offset = 0
        self.float_speed = 0.03  # Slightly slower float speed
        
    def update(self):
        if self.frames:  # Only animate if we have frames
            # Update animation frame
            current_time = pygame.time.get_ticks()
            if current_time - self.animation_timer > self.animation_delay:
                self.animation_timer = current_time
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
        
        # Update floating movement with reduced amplitude (changed from 15 to 5)
        self.float_offset += self.float_speed
        self.rect.y = self.original_y + math.sin(self.float_offset) * 5  # Reduced from 15 to 5

# In the Door class, update the open_door method to handle the image transition properly:
class Door:
    def __init__(self, x, y):
        super().__init__()
        try:
            # Load closed portal image (using underscore instead of space)
            self.closed_image = pygame.image.load('img/closed_portal.png')
            self.closed_image = pygame.transform.scale(self.closed_image, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
            
            # Load portal animation frames
            self.portal_frames = []
            for i in range(1, 6):
                frame = pygame.image.load(f'img/portal_frame_{i}.png')
                frame = pygame.transform.scale(frame, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
                self.portal_frames.append(frame)
                
        except FileNotFoundError as e:
            print(f"Error loading portal images: {e}")
            print("Falling back to default door images...")
            # Fallback to original door images if portal images aren't found
            self.closed_image = pygame.image.load('img/closeddoor.PNG')
            self.closed_image = pygame.transform.scale(self.closed_image, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
            # Create a simple animation using the open door image
            self.portal_frames = []
            open_image = pygame.image.load('img/opendoor_img.PNG')
            open_image = pygame.transform.scale(open_image, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
            self.portal_frames = [open_image] * 5  # Create 5 copies of the open door image
        
        # Animation properties
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_delay = 50  # Milliseconds between frame changes
        self.is_animating = False
        
        # Initial setup
        self.image = self.closed_image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_open = False
        self.door_sound = pygame.mixer.Sound('img/electric_zap.MP3')
        self.door_sound.set_volume(0.5)
        self.sound_played = False
        self.collision_enabled = True
        self.entered = False

    def update(self):
        if self.is_animating:
            current_time = pygame.time.get_ticks()
            
            # Update animation frame
            if current_time - self.animation_timer > self.animation_delay:
                self.animation_timer = current_time
                self.current_frame = (self.current_frame + 1) % len(self.portal_frames)
                self.image = self.portal_frames[self.current_frame]

    def open_door(self):
        if not self.is_open:
            self.is_open = True
            self.is_animating = True
            self.collision_enabled = False
            self.animation_timer = pygame.time.get_ticks()
            if not self.sound_played:
                self.door_sound.play()
                self.sound_played = True

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations_right = []
        self.animations_left = []
        player_size = (int(TILE_SIZE * 1.6), int(TILE_SIZE * 1.6))  # Doubled the size from TILE_SIZE * 1
        
        # Load animations
        for i in range(1, 5):
            img = pygame.image.load(f'img/MainC{i}.png')
            img = pygame.transform.scale(img, player_size)
            self.animations_right.append(img)
            self.animations_left.append(pygame.transform.flip(img, True, False))
        
        # Load sound effects
        self.walking_sound = pygame.mixer.Sound('img/Character Walking.MP3')
        self.walking_sound.set_volume(0.5)
        self.is_walking_sound_playing = False
        
        self.key_collect_sound = pygame.mixer.Sound('img/key_collect.mp3')
        self.key_collect_sound.set_volume(0.4)
        
        self.falling_sound = pygame.mixer.Sound('img/falling_character.mp3')
        self.falling_sound.set_volume(2)
        self.is_falling_sound_playing = False
        self.falling_threshold = 10
        self.falling_counter = 0
        
        self.dead = False  # Add this flag
        self.dead_image = pygame.image.load('img/Skeleton.png')
        self.dead_image = pygame.transform.scale(self.dead_image, (int(TILE_SIZE * 1.6), int(TILE_SIZE * 1.6)))
        
        self.index = 0
        self.counter = 0
        self.image = self.animations_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.rect.width
        self.height = self.rect.height
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True

        self.image = self.animations_right[0]
        self.stop_sounds()
        spawn_pos = find_spawn_position(LEVEL_PLATFORM_DATA[current_level])
        self.rect.x = spawn_pos[0]
        self.rect.y = spawn_pos[1]


    def stop_sounds(self):
        """Stop all player sounds"""
        if self.is_walking_sound_playing:
            self.walking_sound.stop()
            self.is_walking_sound_playing = False
        if self.is_falling_sound_playing:
            self.falling_sound.stop()
            self.is_falling_sound_playing = False

    def cleanup(self):
        """Clean up player resources"""
        self.stop_sounds()
        self.is_walking_sound_playing = False
        self.is_falling_sound_playing = False
        self.falling_counter = 0

    def __del__(self):
        """Ensure sounds are stopped when player object is destroyed"""
        self.stop_sounds()

    def update(self, game_over, world, keys_group, camera):
        dx = 0  # Initialize dx
        dy = 0  # Initialize dy
        
        if game_over == -1:
            if not self.dead:
                self.dead = True
                self.image = self.dead_image
                game_over_fx.play()
                self.stop_sounds()

            # Draw game over text
            draw_text('GAME OVER!', 70, BLUE, (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2)
            
            # Check for restart button press
            if restart_button.draw(screen):
                self.dead = False
                self.image = self.animations_right[self.index]  # Reset to normal image
                
                # Call reset_level instead of manually resetting values
                if reset_level():
                    return 0  # Return 0 to indicate successful restart
                
            return -1  # Keep game over state if restart wasn't successful

        if not movement_enabled or camera.door_zoom:
            self.stop_sounds()  # Stop sounds when movement is disabled
            self.vel_y = 0  # Reset vertical velocity
            return game_over

        if self.dead:
            return game_over  
        
        # Normal movement code here
        if camera.transition_complete:
            key = pygame.key.get_pressed()
            
            # Handle walking sound
            is_moving = False
            
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.vel_y = JUMP_SPEED
                self.jumped = True
                self.in_air = True
                # Reset falling counter when jumping
                self.falling_counter = 0
                if self.is_falling_sound_playing:
                    self.falling_sound.stop()
                    self.is_falling_sound_playing = False
            
            if not key[pygame.K_SPACE]:
                self.jumped = False

            # Check for movement keys and play sound
            if key[pygame.K_LEFT] or key[pygame.K_a]:
                dx -= MOVE_SPEED
                self.counter += 1
                self.direction = -1
                is_moving = True
            if key[pygame.K_RIGHT] or key[pygame.K_d]:
                dx += MOVE_SPEED
                self.counter += 1
                self.direction = 1
                is_moving = True
            
            # Handle walking sound
            if is_moving and not self.in_air and not self.is_walking_sound_playing:
                self.walking_sound.play(-1)
                self.is_walking_sound_playing = True
            elif (not is_moving or self.in_air) and self.is_walking_sound_playing:
                self.walking_sound.stop()
                self.is_walking_sound_playing = False

            if not (key[pygame.K_LEFT] or key[pygame.K_RIGHT] or key[pygame.K_a] or key[pygame.K_d]):
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.animations_right[self.index]
                else:
                    self.image = self.animations_left[self.index]

            # Handle animation
            if self.counter > walk_cooldown:  # walk_cooldown needs to be defined
                self.counter = 0
                self.index += 1
                if self.index >= len(self.animations_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.animations_right[self.index]
                else:
                    self.image = self.animations_left[self.index]

        # Always apply gravity regardless of camera state
        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        
        # Handle falling sound
        if self.in_air and self.vel_y > 0:  # If falling
            self.falling_counter += 1
            if self.falling_counter >= self.falling_threshold and not self.is_falling_sound_playing:
                self.falling_sound.play()
                self.is_falling_sound_playing = True
        elif not self.in_air:  # When landing
            self.falling_counter = 0
            if self.is_falling_sound_playing:
                self.falling_sound.stop()
                self.is_falling_sound_playing = False

        # Check for collision with keys
        key_hits = pygame.sprite.spritecollide(self, keys_group, True)
        if key_hits:
            self.key_collect_sound.play()
            global keys_collected
            keys_collected += len(key_hits)

        # Assume we're in the air unless collision detection proves otherwise
        self.in_air = True

        # Check for collision
        result = world.check_collision(self, dx, dy)
        if result == "deadly":
            return -1  # Return game over state
        else:
            dx, dy = result

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Check if player has fallen off the map
        if self.rect.top > SCREEN_HEIGHT:
            return -1  # Return game over state
            
        return game_over

class World:
    def __init__(self, level_data, deadly_data):
        self.collision_tiles = []
        self.deadly_tiles = []
        self.blue_tiles = []  # Initialize blue_tiles list

        # Create collision tiles
        for plat in level_data:
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            height = int(plat[3] * TILE_SIZE)
            
            offset_x = 0
            offset_y = 0
            
            collision_rect = pygame.Rect(
                x + offset_x,
                y + offset_y,
                width,
                height
            )
            self.collision_tiles.append(CollisionTile(x + offset_x, y + offset_y, width, height))

        # Create deadly tiles
        for deadly in deadly_data:
            x = deadly[0] * TILE_SIZE
            y = deadly[1] * TILE_SIZE
            width = deadly[2] * TILE_SIZE
            height = int(deadly[3] * TILE_SIZE)
            
            self.deadly_tiles.append(CollisionTile(x, y, width, height))

        # Create blue tiles
        if current_level in LEVEL_BLUE_DATA:
            for blue in LEVEL_BLUE_DATA[current_level]:
                x = blue[0] * TILE_SIZE
                y = blue[1] * TILE_SIZE
                width = blue[2] * TILE_SIZE
                height = int(blue[3] * TILE_SIZE)
                
                self.blue_tiles.append(CollisionTile(x, y, width, height))

                '''    def draw(self, screen):
                        # Draw regular collision tiles in red
                        for tile in self.collision_tiles:
                            pygame.draw.rect(screen, (255, 0, 0), tile.rect, 1)
                        
                        # Draw deadly tiles in green
                        for tile in self.deadly_tiles:
                            pygame.draw.rect(screen, (0, 255, 0), tile.rect, 2)
                        
                        # Draw blue tiles in blue
                        for tile in self.blue_tiles:
                            pygame.draw.rect(screen, (0, 0, 255), tile.rect, 1)'''

    def check_collision(self, player, dx, dy):
        # Check collision with both regular and blue tiles
        for tile in self.collision_tiles + self.blue_tiles:
            if tile.rect.colliderect(player.rect.x + dx, player.rect.y, player.width, player.height):
                dx = 0
            if tile.rect.colliderect(player.rect.x, player.rect.y + dy, player.width, player.height):
                if player.vel_y < 0:
                    dy = tile.rect.bottom - player.rect.top
                    player.vel_y = 0
                elif player.vel_y >= 0:
                    dy = tile.rect.top - player.rect.bottom
                    player.vel_y = 0
                    player.in_air = False
                    
        # Check deadly collisions
        for tile in self.deadly_tiles:
            if tile.rect.colliderect(player.rect):
                return "deadly"
                
        return dx, dy

def init_level(level_num):
    """Initialize a new level with all required components"""
    global keys_collected, game_start_time, current_level, player, camera
    global ghost, movement_enabled, total_pause_time
    
    try:
        # Reset level state
        keys_collected = 0
        current_level = level_num
        game_start_time = None  # Reset timer - will be started after transition
        total_pause_time = timedelta(0)
        movement_enabled = False
        
        # Stop all existing sounds
        if 'player' in globals() and player is not None:
            player.stop_sounds()
        if 'camera' in globals() and camera is not None:
            camera.stop_sounds()
        
        # Clean up existing camera if it exists
        if 'camera' in globals() and camera is not None:
            camera.cleanup()
        
        # Load level data
        platforms = LEVEL_PLATFORM_DATA.get(level_num, [])
        if not platforms:
            raise ValueError(f"No platform data found for level {level_num}")
            
        deadly_tiles = LEVEL_DEADLY_DATA.get(level_num, [])
        enemy_data = LEVEL_ENEMY_DATA.get(level_num, [])
        
        # Create world
        world = World(platforms, deadly_tiles)
        
        # Calculate spawn position
        spawn_pos = find_spawn_position(platforms)
        
        # Create player
        player = Player(spawn_pos[0], spawn_pos[1])
        
        # Create ghost with appropriate level difficulty
        ghost = Ghost(SCREEN_WIDTH, SCREEN_HEIGHT, player, level_num)
        
        # Set up door
        door_pos = find_door_position(platforms)
        door = Door(door_pos[0], door_pos[1])
        
        # Generate and place keys
        keys_group = pygame.sprite.Group()
        key_positions = generate_key_positions(level_num)
        for pos in key_positions:
            adjusted_y = pos[1] + TILE_SIZE - 20
            keys_group.add(Key(pos[0], adjusted_y))
            
        # Create enemies
        moving_enemies = pygame.sprite.Group()
        for enemy_info in enemy_data:
            x, y, direction, boundary_start, boundary_end = enemy_info
            enemy = MovingEnemy(x * TILE_SIZE, y * TILE_SIZE, direction, boundary_start, boundary_end)
            moving_enemies.add(enemy)
            
        # Reset camera
        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        camera.transitioning = False
        camera.transition_complete = False
        camera.manual_zoom_active = False
        camera.door_zoom = False
        camera.door_zoom_target = None
        camera.reset_on_death = False
        
        print(f"Level {level_num} initialized successfully")
        return keys_group, door, world, moving_enemies, player, ghost
        
    except Exception as e:
        import traceback
        print(f"\nError initializing level {level_num}:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Traceback:")
        traceback.print_exc()
        return None, None, None, None, None, None


class MovingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, boundary_start, boundary_end):
        super().__init__()
        self.image = pygame.transform.scale(npc_img, (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = direction
        self.speed = 1.2
        self.moving_right = True
        self.moving_down = True
        self.boundary_start = boundary_start * TILE_SIZE
        self.boundary_end = boundary_end * TILE_SIZE
        self.initial_pos = self.rect.x if direction == "horizontal" else self.rect.y


    def update(self):
        if not movement_enabled or camera.door_zoom:
            return
            
        if self.direction == "horizontal":
            if self.moving_right:
                self.rect.x += self.speed
                if self.rect.x >= self.boundary_end:
                    self.moving_right = False
                    self.image = pygame.transform.flip(self.image, True, False)
            else:
                self.rect.x -= self.speed
                if self.rect.x <= self.boundary_start:
                    self.moving_right = True
                    self.image = pygame.transform.flip(self.image, True, False)

    def draw_boundaries(self, screen):
        # Draw movement boundaries (for debugging)
        if self.direction == "horizontal":
            pygame.draw.line(screen, (255, 0, 0),
                           (self.boundary_start, self.rect.centery),
                           (self.boundary_end, self.rect.centery), 2)
        else:
            pygame.draw.line(screen, (255, 0, 0),
                           (self.rect.centerx, self.boundary_start),
                           (self.rect.centerx, self.boundary_end), 2)

    def check_collision(self, player):
        # Create a slightly smaller collision rect for more forgiving collisions
        collision_margin = 4
        collision_rect = pygame.Rect(
            self.rect.x + collision_margin,
            self.rect.y + collision_margin,
            self.rect.width - (collision_margin * 2),
            self.rect.height - (collision_margin * 2)
        )
        return collision_rect.colliderect(player.rect)

class Button:
    def __init__(self, x, y, image):
        self.original_image = image
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = int(x * SCALE_X)
        self.rect.y = int(y * SCALE_Y)
        self.clicked = False
        
        # Scale image if needed
        if SCALE_X != 1.0 or SCALE_Y != 1.0:
            new_size = (int(self.rect.width * SCALE_X), int(self.rect.height * SCALE_Y))
            self.image = pygame.transform.scale(self.original_image, new_size)
            self.rect = self.image.get_rect(x=self.rect.x, y=self.rect.y)

    def draw(self, screen):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()  # This gets the (x, y) position of the mouse

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

def draw_text(text, font_size, color, x, y):
    font = pygame.font.SysFont('Bauhaus 93', font_size)
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def find_suitable_platform(platforms):
    """
    Find a suitable platform for door placement using better criteria:
    1. Platform must be wide enough for door and NPC
    2. Platform should be reasonably high up but not necessarily the highest
    3. Platform should have enough space above it
    """
    # Sort platforms by height (y-coordinate), from top to bottom
    sorted_platforms = sorted(platforms, key=lambda p: p[1])
    
    # Required width for door and NPC (in tile units)
    required_width = 4  # Space for door and NPC
    
    # Check top 1/3 of platforms for a suitable spot
    top_third = len(sorted_platforms) // 3
    if top_third < 1:
        top_third = 1
    
    for platform in sorted_platforms[:top_third]:
        # Get platform dimensions
        x, y, width, height = platform
        
        # Check if platform is wide enough
        if width >= required_width:
            # Check if there's another platform directly above
            has_obstruction = False
            platform_top = y
            platform_left = x
            platform_right = x + width
            
            # Check for obstructions above
            for other_platform in platforms:
                other_x, other_y, other_width, other_height = other_platform
                other_left = other_x
                other_right = other_x + other_width
                other_bottom = other_y + other_height
                
                # Check if there's a platform directly above
                if (other_bottom > platform_top - 4 and  # Leave space for door height
                    other_y < platform_top and
                    other_right > platform_left and
                    other_left < platform_right):
                    has_obstruction = True
                    break
            
            if not has_obstruction:
                return platform
                
    # Fallback to the widest platform in the top half if no perfect match
    top_half = sorted_platforms[:len(sorted_platforms)//2]
    widest_platform = max(top_half, key=lambda p: p[2])
    return widest_platform

def find_spawn_position(platforms):
    """Find a safe spawn position on the leftmost ground platform"""
    # Filter for ground-level platforms (in the bottom third of the screen)
    ground_platforms = []
    screen_bottom_third = (SCREEN_HEIGHT / TILE_SIZE) * 2/3
    
    for platform in platforms:
        if platform[1] > screen_bottom_third:
            ground_platforms.append(platform)
    
    if not ground_platforms:
        # Fallback to the lowest platform if no ground platforms found
        lowest_platform = max(platforms, key=lambda p: p[1])
        spawn_x = (lowest_platform[0] + 1) * TILE_SIZE
        spawn_y = lowest_platform[1] * TILE_SIZE - TILE_SIZE * 1.6  # Adjust to be exactly on platform
        return (spawn_x, spawn_y)
    
    # Find leftmost ground platform
    leftmost = min(ground_platforms, key=lambda p: p[0])
    
    # Position player exactly on top of the platform
    spawn_x = (leftmost[0] + 1) * TILE_SIZE
    spawn_y = leftmost[1] * TILE_SIZE - TILE_SIZE * 1.6  # Adjust for player height
    
    return (spawn_x, spawn_y)

def find_door_position(platforms):
    """Find an appropriate position for the door"""
    # Find a suitable platform (high up but accessible)
    suitable_platform = find_suitable_platform(platforms)
    
    # Position door near the right edge of the platform
    door_x = (suitable_platform[0] + suitable_platform[2] - 2) * TILE_SIZE
    door_y = (suitable_platform[1] - 2) * TILE_SIZE
    
    # Ensure door doesn't go off screen
    if door_x > SCREEN_WIDTH - 3 * TILE_SIZE:
        door_x = SCREEN_WIDTH - 3 * TILE_SIZE
    
    return (door_x, door_y)

def generate_key_positions(level):
    positions = []
    required_keys = LEVEL_REQUIREMENTS[level]
    platforms = LEVEL_PLATFORM_DATA[level]
    deadly_tiles = LEVEL_DEADLY_DATA[level]
    
    # Get viable platform positions (excluding ground platforms)
    viable_platforms = []
    for plat in platforms:
        # Convert platform coordinates to screen coordinates
        x = plat[0] * TILE_SIZE
        y = plat[1] * TILE_SIZE
        width = plat[2] * TILE_SIZE
        
        # Skip very low platforms (ground level)
        if y < SCREEN_HEIGHT * 0.8:  # Only use platforms in upper 80% of screen
            viable_platforms.append((x, y, width))
    
    # Function to check if position is safe from deadly tiles
    def is_safe_position(x, y):
        SAFE_DISTANCE = TILE_SIZE * 3  # Minimum distance from deadly tiles
        
        for deadly in deadly_tiles:
            deadly_x = deadly[0] * TILE_SIZE
            deadly_y = deadly[1] * TILE_SIZE
            deadly_width = deadly[2] * TILE_SIZE
            deadly_height = deadly[3] * TILE_SIZE
            
            # Calculate boundaries of the deadly area with safety margin
            deadly_left = deadly_x - SAFE_DISTANCE
            deadly_right = deadly_x + deadly_width + SAFE_DISTANCE
            deadly_top = deadly_y - SAFE_DISTANCE
            deadly_bottom = deadly_y + deadly_height + SAFE_DISTANCE
            
            # Check if key position is within the danger zone
            if (deadly_left < x < deadly_right and 
                deadly_top < y < deadly_bottom):
                return False
        return True
    
    # Randomly select platforms and place keys on them
    import random
    random.shuffle(viable_platforms)
    attempts = 0
    max_attempts = 100  # Prevent infinite loop
    
    while len(positions) < required_keys and attempts < max_attempts:
        for plat in viable_platforms:
            if len(positions) >= required_keys:
                break
                
            # Try multiple positions on each platform
            for _ in range(5):  # Try 5 times per platform
                # Place key somewhere along the platform
                key_x = plat[0] + random.uniform(TILE_SIZE, plat[2] - TILE_SIZE * 2)
                key_y = plat[1] - TILE_SIZE * 1.5
                
                # Only add position if it's safe
                if is_safe_position(key_x, key_y):
                    positions.append((key_x, key_y))
                    break
            
            attempts += 1
    
    # If we couldn't find enough safe positions, fill remaining with positions farther from platforms
    while len(positions) < required_keys:
        plat = random.choice(viable_platforms)
        key_x = plat[0] + random.uniform(TILE_SIZE * 2, plat[2] - TILE_SIZE * 2)
        key_y = plat[1] - TILE_SIZE * 2  # Place keys higher above platform
        if is_safe_position(key_x, key_y):
            positions.append((key_x, key_y))
    
    return positions

def generate_key_positions(level):
    positions = []
    required_keys = LEVEL_REQUIREMENTS[level]
    platforms = LEVEL_PLATFORM_DATA[level]
    
    # Get viable platform positions (excluding ground platforms)
    viable_platforms = []
    for plat in platforms:
        # Convert platform coordinates to screen coordinates
        x = plat[0] * TILE_SIZE
        y = plat[1] * TILE_SIZE
        width = plat[2] * TILE_SIZE
        
        # Skip very low platforms (ground level)
        if y < SCREEN_HEIGHT * 0.8:  # Only use platforms in upper 80% of screen
            viable_platforms.append((x, y, width))
    
    # Randomly select platforms and place keys on them
    import random
    random.shuffle(viable_platforms)
    
    for i in range(min(required_keys, len(viable_platforms))):
        plat = viable_platforms[i]
        # Place key somewhere along the platform
        key_x = plat[0] + random.uniform(0, plat[2] - TILE_SIZE)
        key_y = plat[1] - TILE_SIZE * 1.5  # Place key above platform
        positions.append((key_x, key_y))
    
    return positions

# Modify the initialize_game_objects function to include the leaderboard
def initialize_game_objects():
    global start_button, restart_button, camera, player, world, moving_enemies
    global keys_group, door, ghost, game_over, current_state, movement_enabled
    global pause_button, scene_manager, game_stats, leaderboard

    # Create scene manager first
    scene_manager = SceneManager(screen)
    
    # Initialize other objects
    start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, start_btn)
    restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    # Initialize level components
    level_objects = init_level(0)  # Start with tutorial level
    if level_objects is not None:
        keys_group, door, world, moving_enemies, player, ghost = level_objects
    else:
        print("Failed to initialize level objects")
        return None
    
    game_over = 0
    current_state = "name_input"
    movement_enabled = False 
    pause_button = PauseButton(screen)
    game_stats = EnhancedGameStats(screen)
    leaderboard = Leaderboard(screen)

    return scene_manager

# Initialize game state
scene_manager = initialize_game_objects()
init_game()
update_scale_factors()

# Game loop
clock = pygame.time.Clock()
fps = 60
running = True
fullscreen = False

# Main game loop
while running:
    clock.tick(fps)
    
    # Handle pause state first
    if current_state == "playing" and paused:
        if not handle_pause():
            running = False
        continue
    
    # Global event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            break
            
        # Handle fullscreen toggle and update scaling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RSHIFT:
                toggle_fullscreen()
                # Recreate UI elements with new scaling
                initialize_game_objects()
                
        # Global pause handling
        if current_state == "playing" and not paused:
            if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE) or \
               pause_button.handle_event(event):
                paused = True
                pause_start_time = datetime.now()
                fade_alpha = 0
                continue

        # Handle scene-specific input
        if current_state in ["scene", "intro_scenes", "level_transition", "ending_scenes"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if not scene_manager.current_scene.fading_in and not scene_manager.current_scene.fading_out:
                    scene_manager.current_scene.fading_out = True
        
        # Handle name input
        if current_state == "name_input" and scene_manager.text_input.active:
            result = scene_manager.text_input.handle_event(event)
            if result:
                scene_manager.player_name = result
                scene_manager.text_input.active = False
                scene_manager.update_scenes_with_name()
                current_state = "scene"
    
    if not running:
        break

    # Clear screen
    screen.fill(BLACK)
    
    # State-specific updates
    if current_state == "name_input":
        scene_manager.draw()
        
    elif current_state in ["scene", "intro_scenes", "level_transition", "ending_scenes"]:
        scene_manager.update(clock.get_time() / 1000.0)
        scene_manager.draw()
        
        if scene_manager.current_scene.completed:
            next_state = scene_manager.scenes[scene_manager.scene_index].get('next', 'scene')
            
            # Check if we're at a scene that requires minigame completion
            minigame_levels = {
                7: 1,   # Before Level 1
                9: 2,   # Before Level 2
                11: 3,  # Before Level 3
                13: 4,  # Before Level 4
                15: 5   # Before Level 5
            }
            
            if scene_manager.scene_index in minigame_levels:
                minigame_level = minigame_levels[scene_manager.scene_index]
                minigame_result = load_minigame(minigame_level)
                
                if not minigame_result:
                    # If minigame wasn't completed, don't advance
                    scene_manager.current_scene.completed = False
                    scene_manager.current_scene.fading_out = False
                    continue
            
            # If we get here, either no minigame was required or it was completed successfully
            if next_state == 'scene':
                scene_manager.next_scene()
            elif next_state.startswith('level_'):
                level_num = int(next_state.split('_')[1])
                game_start_time = None
                movement_enabled = False
                
                level_objects = init_level(level_num)
                if all(obj is not None for obj in level_objects):
                    keys_group, door, world, moving_enemies, player, ghost = level_objects
                    camera.start_transition()
                    current_state = "playing"
            elif next_state == 'game_complete':
                current_state = "game_complete"
                
    elif current_state == "playing":
        # Get and draw the current background
        current_background = get_background(current_level)
        if current_background:
            scaled_bg = pygame.transform.scale(current_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
            screen.blit(scaled_bg, (0, 0))
        
        # Determine if entities can move
        can_move = movement_enabled and not camera.door_zoom and not paused
        
        # Update game entities only when movement is allowed
        if can_move:
            # Update entities
            keys_group.update()
            moving_enemies.update()
            ghost.update()
            
            # Check collisions with enemies and ghost
            for enemy in moving_enemies:
                if enemy.check_collision(player):
                    game_over = -1
                    break
            
            if ghost.check_collision(player):
                game_over = -1
            
            # Update player and check for game over
            game_over = player.update(game_over, world, keys_group, camera)
            
            # Update timer only when game started and movement allowed
            if game_start_time is None:
                if camera.transition_complete and camera.initial_zoom_done:
                    game_start_time = time.time()
            elif not game_over:
                current_time = time.time()
                elapsed_time = current_time - game_start_time
                if total_pause_time:
                    elapsed_time -= total_pause_time.total_seconds()
                
                # Check level timer
                if check_level_timer(elapsed_time, LEVEL_TIME_LIMITS[current_level]):
                    game_over = -1
                    game_over_fx.play()
        
        # Always update door animation
        door.update()
        
        # Check level completion
        if keys_collected >= LEVEL_REQUIREMENTS[current_level]:
            if not door.is_open:
                camera.start_door_zoom(door)
            elif pygame.sprite.collide_rect(player, door) and not door.entered:
                door.entered = True
                camera.stop_sounds()
                
                level_complete_mapping = {
                    0: (1, 7),    # Tutorial -> Level 1, Scene 8
                    1: (2, 9),    # Level 1 -> Level 2, Scene 10
                    2: (3, 11),   # Level 2 -> Level 3, Scene 12
                    3: (4, 13),   # Level 3 -> Level 4, Scene 14
                    4: (5, 15),   # Level 4 -> Level 5, Scene 16
                    5: (None, 17) # Level 5 -> Ending (Scene 18)
                }
                
                if current_level in level_complete_mapping:
                    next_level, next_scene = level_complete_mapping[current_level]
                    if next_level is None:
                        current_state = "ending_scenes"
                    else:
                        current_level = next_level
                        current_state = "level_transition"
                    scene_manager.scene_index = next_scene
                    scene_manager.current_scene = Scene(screen, scene_manager.scenes[next_scene])
        
        # Update camera and create zoomed view with scaling
        camera.update(player, keys_collected, door, LEVEL_REQUIREMENTS[current_level])
        create_zoomed_view(screen, camera, player, world, keys_group, door, moving_enemies, ghost)
        
        # Draw HUD if not in door zoom
        if not camera.door_zoom and camera.transition_complete:
            game_stats.draw_stats_panel(
                current_level,
                keys_collected,
                LEVEL_REQUIREMENTS[current_level],
                time.time() - game_start_time if game_start_time else 0,
                LEVEL_TIME_LIMITS[current_level]
            )
            if not paused:
                pause_button.draw()
                leaderboard.draw()  # Draw leaderboard during gameplay
                
        if game_over == -1:
            text_x = (SCREEN_WIDTH // 2) - int(200 * SCALE_X)
            text_y = SCREEN_HEIGHT // 2
            draw_text('GAME OVER!', int(70 * SCALE_Y), BLUE, text_x, text_y)
            
            if restart_button.draw(screen):
                success = reset_level()
                if not success:
                    print("Failed to reset level")
                    running = False
                else:
                    # Ensure the game state is properly reset
                    game_over = 0
                    player.dead = False
                    movement_enabled = False
                    camera.start_transition()
        
    elif current_state == "game_complete":
        screen.fill(BLACK)
        
        # Calculate final stats
        if game_start_time:
            total_time = datetime.now() - datetime.fromtimestamp(game_start_time) - total_pause_time
            total_seconds = total_time.total_seconds()
            
            # Add score to leaderboard
            leaderboard.add_score(scene_manager.player_name, total_seconds)
            
            minutes = int(total_time.total_seconds() // 60)
            seconds = int(total_time.total_seconds() % 60)
            
            # Draw completion card
            card_width = int(600 * SCALE_X)
            card_height = int(400 * SCALE_Y)
            completion_card = pygame.Surface((card_width, card_height))
            completion_card.fill((40, 40, 40))
            
            title_font = pygame.font.SysFont('Bauhaus 93', int(70 * SCALE_Y))
            title = title_font.render("GAME COMPLETE!", True, (255, 215, 0))
            completion_card.blit(title, (card_width//2 - title.get_width()//2, int(40 * SCALE_Y)))
            
            stats = [
                f"Player: {scene_manager.player_name}",
                f"Total Time: {minutes:02d}:{seconds:02d}",
                f"Keys Collected: {sum(LEVEL_REQUIREMENTS.values())}",
                f"Levels Completed: 5"
            ]
            
            stats_font = pygame.font.SysFont('Bauhaus 93', int(40 * SCALE_Y))
            for i, stat in enumerate(stats):
                text = stats_font.render(stat, True, WHITE)
                completion_card.blit(text, (card_width//2 - text.get_width()//2, 
                                         int((160 + i * 60) * SCALE_Y)))
            
            screen.blit(completion_card, 
                      (SCREEN_WIDTH//2 - card_width//2,
                       SCREEN_HEIGHT//2 - card_height//2))
            
            # Draw leaderboard next to completion card
            leaderboard.draw()
            
            if restart_button.draw(screen):
                current_state = "name_input"
                game_start_time = None
                current_level = 0
                keys_collected = 0
                level_times = []
                scene_manager = SceneManager(screen)
    
    pygame.display.update()

# Cleanup
cleanup_game()
pygame.quit()