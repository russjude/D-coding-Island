import pygame
import os
import time
import cv2
import numpy as np
import math
from datetime import datetime, timedelta
import subprocess
import sys

# Initialize Pygame and mixer
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

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Game constants
TILE_SIZE = SCREEN_HEIGHT // 36
GRAVITY = 0.40
JUMP_SPEED = -11
MOVE_SPEED = 6
game_over = 0
current_level = 0
keys_collected = 0
game_start_time = None
level_times = []
dialogue_states = {}

# Pause state
paused = False
pause_start_time = None
total_pause_time = timedelta(0)
fade_alpha = 0
fade_target = 180
fade_speed = 15

# Colors
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
target_size = (25, 25)

# Load and scale key animation frames
for i in range(1, 13):
    image = pygame.image.load(f'img/AnimatedKey_{i}.png')
    scaled_image = pygame.transform.scale(image, target_size)
    key_frames.append(scaled_image)

# Scale other images
closeddoor_img = pygame.transform.scale(closeddoor_img, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
key_img = pygame.transform.scale(key_img, (10, 25))
npc_img = pygame.transform.scale(npc_img, (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2)))

# Load sounds
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

# Update scale factors
def update_scale_factors():
    global SCALE_X, SCALE_Y
    current_size = pygame.display.get_surface().get_size()
    SCALE_X = current_size[0] / BASE_WIDTH
    SCALE_Y = current_size[1] / BASE_HEIGHT

# Toggle fullscreen mode
def toggle_fullscreen():
    global FULLSCREEN, screen, SCREEN_WIDTH, SCREEN_HEIGHT
    FULLSCREEN = not FULLSCREEN
    
    if FULLSCREEN:
        info = pygame.display.Info()
        target_ratio = BASE_WIDTH / BASE_HEIGHT
        monitor_ratio = info.current_w / info.current_h
        
        if monitor_ratio > target_ratio:
            SCREEN_HEIGHT = info.current_h
            SCREEN_WIDTH = int(SCREEN_HEIGHT * target_ratio)
        else:
            SCREEN_WIDTH = info.current_w
            SCREEN_HEIGHT = int(SCREEN_WIDTH / target_ratio)
            
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        SCREEN_WIDTH = BASE_WIDTH
        SCREEN_HEIGHT = BASE_HEIGHT
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    update_scale_factors()

# Level platform data
LEVEL_PLATFORM_DATA = {...}

# Level deadly data
LEVEL_DEADLY_DATA = {...}

# Level blue data
LEVEL_BLUE_DATA = {...}

# Initialize video capture and load images
background_surfaces = {}
video_captures = {}

for level, bg_data in level_backgrounds.items():
    if bg_data['type'] == 'video':
        try:
            video_captures[level] = cv2.VideoCapture(bg_data['path'])
        except Exception as e:
            print(f"Error loading video for level {level}: {e}")
            background_surfaces[level] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_surfaces[level].fill((0, 0, 0))
    else:
        try:
            img = pygame.image.load(bg_data['path']).convert()
            background_surfaces[level] = pygame.transform.scale(img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading image for level {level}: {e}")
            background_surfaces[level] = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            background_surfaces[level].fill((0, 0, 0))

# Update collision tile creation
class World:
    def __init__(self, level_data, deadly_data):
        self.collision_tiles = []
        self.deadly_tiles = []
        self.blue_tiles = []

        for plat in level_data:
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            height = int(plat[3] * TILE_SIZE)
            
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
            
            margin = 2
            self.deadly_tiles.append(CollisionTile(
                x + margin, 
                y + margin, 
                width - margin * 2, 
                height - margin * 2
            ))

# Update LEVEL_DIALOGUES
LEVEL_DIALOGUES = {...}

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
        self.scores.sort(key=lambda x: x['time'])
        self.scores = self.scores[:10]
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
        leaderboard_surface = pygame.Surface((300, 400), pygame.SRCALPHA)
        pygame.draw.rect(leaderboard_surface, (0, 0, 0, 180), (0, 0, 300, 400))
        
        title = self.title_font.render("LEADERBOARD", True, (255, 215, 0))
        leaderboard_surface.blit(title, (150 - title.get_width()//2, 10))
        
        y = 60
        for i, score in enumerate(self.scores):
            minutes = int(score['time'] // 60)
            seconds = int(score['time'] % 60)
            text = self.font.render(f"{i+1}. {score['name']}: {minutes:02d}:{seconds:02d}", True, (255, 255, 255))
            leaderboard_surface.blit(text, (20, y))
            y += 30
        
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
        self.scenes = [...]  # Scene data

    def update_scenes_with_name(self):
        for i in range(1, len(self.scenes)):
            if 'text' in self.scenes[i]:
                self.scenes[i]['text'] = self.scenes[i]['text'].format(
                    player_name=self.player_name)
        
        if self.scene_index > 0:
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index], self.player_name)

    def next_scene(self):
        self.scene_index += 1
        if self.scene_index < len(self.scenes):
            self.current_scene = Scene(self.screen, self.scenes[self.scene_index], self.player_name)
        else:
            self.scene_index = len(self.scenes) - 1

    def handle_level_completion(self, level):
        self.level_completed = True
        self.current_level = level + 1
        level_to_scene = {
            0: 7,  # After tutorial, go to Scene 8
            1: 8,  # After Level 1, go to Scene 9
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

    def draw(self):
        if self.current_scene:
            self.current_scene.draw()
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
        self.cursor_blink_speed = 500
        self.max_length = 20
        
        self.box_width = 300
        self.box_height = 50
        self.text_color = (255, 255, 255)
        self.box_color = (0, 0, 0, 180)
        self.border_color = (100, 100, 100)
        self.active_border_color = (200, 200, 200)
        self.prompt_text = "Enter your name:"
        
        self.prompt_surface = self.font.render(self.prompt_text, True, self.text_color)

    def handle_event(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_text.strip():
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

        box_x = x - self.box_width // 2
        box_y = y

        prompt_x = x - self.prompt_surface.get_width() // 2
        prompt_y = box_y - 40
        self.screen.blit(self.prompt_surface, (prompt_x, prompt_y))

        s = pygame.Surface((self.box_width, self.box_height), pygame.SRCALPHA)
        pygame.draw.rect(s, self.box_color, (0, 0, self.box_width, self.box_height))
        self.screen.blit(s, (box_x, box_y))

        border_color = self.active_border_color if self.active else self.border_color
        pygame.draw.rect(self.screen, border_color, 
                        (box_x, box_y, self.box_width, self.box_height), 2)

        if self.input_text:
            text_surface = self.font.render(self.input_text, True, self.text_color)
            text_x = box_x + 10
            text_y = box_y + (self.box_height - text_surface.get_height()) // 2
            self.screen.blit(text_surface, (text_x, text_y))

        current_time = pygame.time.get_ticks()
        if current_time - self.cursor_timer > self.cursor_blink_speed:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = current_time

        if self.cursor_visible:
            cursor_x = box_x + 10 + (self.font.size(self.input_text)[0] if self.input_text else 0)
            cursor_y = box_y + 10
            pygame.draw.line(self.screen, self.text_