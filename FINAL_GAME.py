import pygame
from pygame.locals import *
from pygame import mixer
import os
import time

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Get the screen resolution
infoObject = pygame.display.Info()
monitor_width = infoObject.current_w
monitor_height = infoObject.current_h

# Calculate the game window size (90% of screen size while maintaining aspect ratio)
SCREEN_SCALE = 0.9
target_width = int(monitor_width * SCREEN_SCALE)
target_height = int(monitor_height * SCREEN_SCALE)

# Load and get aspect ratio from first level background (as reference)
original_bg = pygame.image.load('Level1.png')
bg_aspect_ratio = original_bg.get_width() / original_bg.get_height()

# Adjust window size to maintain aspect ratio
if target_width / target_height > bg_aspect_ratio:
    SCREEN_WIDTH = int(target_height * bg_aspect_ratio)
    SCREEN_HEIGHT = target_height
else:
    SCREEN_WIDTH = target_width
    SCREEN_HEIGHT = int(target_width / bg_aspect_ratio)

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Define tile size based on background height
TILE_SIZE = SCREEN_HEIGHT // 36  # 36 is the number of tiles vertically
GRAVITY = 0.79
JUMP_SPEED = -15
MOVE_SPEED = 7
game_over = 0
current_level = 0  # 0 for start screen, 1-5 for levels
keys_collected = 0
game_start_time = None
level_times = []
dialogue_states = {}

# Define colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Load images
start_bg = pygame.image.load('img/background.png')
start_bg = pygame.transform.scale(start_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
start_btn = pygame.image.load('img/start_btn.png')
restart_img = pygame.image.load('img/restart_btn.png')
door_img = pygame.image.load('img/exit.png')
key_img = pygame.image.load('img/key.png')
npc_img = pygame.image.load('img/skeleton.png')

# Scale images
door_img = pygame.transform.scale(door_img, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))
key_img = pygame.transform.scale(key_img, (TILE_SIZE, TILE_SIZE))
npc_img = pygame.transform.scale(npc_img, (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2)))

# Load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

# Level platform data (you'll need to adjust these coordinates based on your level designs)
LEVEL_PLATFORM_DATA = {
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
            (23.2, 3.6, 3, 1),
            (13.5, 2, 7.6, 4),
            (10.1, 3.7, 3, 1),
            (0.3, 3.7, 4.6, 1),
            (5.2, 5.3, 1.3, 1),

            # 6th layer
            (51.3, 10.2, 7.5, 5.7),
            (26.4, 10.2, 4.8, 1.3),
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
            (13.4, 21.7, 6.2, 1),
            (9.9, 20.1, 1.7, 1),

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
            (19.9, 1.9, 3, 1.4),
            

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
            (47.7, 13.5, 3.2, 1.3),
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
            (0.3, 35, 58.8, 6)
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

            (51, 20, 10, 1),
            (38.1, 0, 1.3, 8),
            (39.3, 6.8, 6.3, 1.2),
            (38, 3.5, 3, 1),



            # 3rd layer
            (8.5, 21.8, 1.5, 1),
            (21.2, 21.8, 1.5, 1),
            (16.9, 29.5, 1.6, 1.5),
            (19.4, 29.5, 1.6, 1.5),
            (10, 23.4, 11.3, 1.3),
            (18.5, 23.4, 1, 7.6),
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
            (26.3, 26.7, 8.2, 1.5),
            (19.6, 26.7, 5.3, 1.5),
            (36.1, 26.7, 3.7, 1.5),
            (41, 26.7, 5, 1.5),

            (15, 13.5, 3, 1), 
            (18, 8.5, 5, 1),
            (49.3, 30, 3.3, 1.1), 
            (46, 23.3, 6.5, 1),
            (44.4, 18.5, 4.8, 1),

            (16.5, 20, 5, 1.3),
            (23, 20, 1.7, 1.3),
            (26.4, 20, 4.8, 1.3),
            (33, 20, 3.3, 1.3),
            (38, 20, 4.7, 1.3),
            (41.2, 13.5, 3.2, 1),
            (29.7, 7, 6.5, 1.1),
            (22.9, 7, 5, 1.2),

            (19.8, 13.5, 5, 1.3),
            (26.2, 13.5, 1.7, 1.3),
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
            (16.5, 31.5, 3, 1),



            (9.9, 33.2, 5, 1.3),
            (19.4, 33.2, 19, 1.3),
            (36, 33.2, 7, 1.3),
            (44, 33.2, 5.3, 1.3)
    ]
}

# Level requirements (keys needed per level)
LEVEL_REQUIREMENTS = {
    1: 4,
    2: 5,
    3: 6,
    4: 8,
    5: 10
}

# Level backgrounds
level_backgrounds = {
    1: pygame.image.load('Level1.png'),
    2: pygame.image.load('Level2game!.png'),
    3: pygame.image.load('Level3game!!.png'),
    4: pygame.image.load('Level4.png'),
    5: pygame.image.load('Level5.png')
}

# Update the background scaling code:
for level in level_backgrounds:
    orig_bg = level_backgrounds[level]
    level_backgrounds[level] = pygame.transform.scale(orig_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

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

    
STORYLINE = {
    "intro": [
        "img/Background.png",
        "img/Background.png",
        "You've just won the international decoding competition and decided to celebrate by going fishing.",
        "Suddenly, you were ambushed by mysterious spirits and knocked unconscious.",
        "You wake up and find yourself washed up on an unknown island.",
        "A note lies next to you, and it reads:",
        '"We are the spirits of the past decoding masters. To prove your worth, you must complete a set of challenges."',
        "Determined to face the challenges head-on, you set out to meet the first spirit guarding the island."
    ],
    "level1": [
        "You encounter Palak the Assassin, the spirit guarding the first level.",
        '"Greetings, young decoder. Your first challenge awaits. Prove your skills and proceed."',
        "Palak explains the rules of the challenge and the dangers that lie ahead.",
        '"Collect the keys scattered throughout the level to unlock the door and advance."',
        '"But beware, the path is treacherous, and one misstep could lead to your demise."',
        "Press SPACE to begin the challenge..."
    ],
    "level2": [
        "As you progress, you come face to face with Russ the Wizard.",
        '"Ah, the rising star. Your journey has just begun. Show me your coding prowess!"',
        "Russ conjures magical obstacles and riddles to test your problem-solving abilities.",
        '"Decipher the clues and overcome the challenges to prove your worth."',
        '"Remember, in the realm of coding, logic and creativity are your greatest allies."',
        "Press SPACE to continue your quest..."
    ],
    "level3": [
        "Halfway through your quest, you meet Geoff the Autocrat.",
        '"Impressive, but can you handle the trials that lie ahead? Let us see!"',
        "Geoff presents you with complex algorithms and data structures to navigate.",
        '"Efficiency and optimization are key to conquering this level."',
        '"Show me your mastery of code, and you shall pass this threshold."',
        "Press SPACE to tackle the challenges head-on..."
    ],
    "level4": [
        "Near the end of your journey, Jessica the Wraith appears before you.",
        '"You have come far, but the true test of your abilities awaits. Brace yourself!"',
        "Jessica challenges you with intricate puzzles and mind-bending riddles.",
        '"Your coding skills and logical thinking will be pushed to their limits."',
        '"Prove that you have what it takes to be a true decoding master!"',
        "Press SPACE to face the final trials..."
    ],
    "level5": [
        "At the final level, you stand before Jacobo the Undead King.",
        '"Decoding master, your final challenge is here. Prove your worth and claim your rightful title!"',
        "Jacobo presents you with the ultimate coding challenge, a combination of all previous trials.",
        '"Utilize all the skills and knowledge you have acquired throughout your journey."',
        '"Emerge victorious, and the title of \'Decoding Master\' shall be yours!"',
        "Press SPACE to begin the final showdown..."
    ],
    "ending": [
        "Victorious, you stand before the spirits, holding your well-earned trophy.",
        '"Congratulations, young one. You have proven yourself worthy of the title \'Decoding Master\'!"',
        "The spirits acknowledge your skills and bestow their blessings upon you.",
        "With a sense of pride and accomplishment, you set sail back home, ready for your next coding adventure!"
    ]
}

# Level dialogues
LEVEL_DIALOGUES = {
    1: [
        "Welcome to Decoding Island!",
        "You've woken up on a mysterious island...",
        "To proceed to the next level, collect 4 keys scattered around.",
        "Press SPACE to continue..."
    ],
    2: [
        "Level 2: The challenge increases!",
        "Find 5 keys to unlock the next area.",
        "Press SPACE to continue..."
    ],
    3: [
        "Level 3: Halfway there!",
        "Collect 6 keys to proceed.",
        "Press SPACE to continue..."
    ],
    4: [
        "Level 4: The difficulty rises!",
        "8 keys are required for the next level.",
        "Press SPACE to continue..."
    ],
    5: [
        "Final Level!",
        "Collect 10 keys to complete your journey.",
        "Press SPACE to continue..."
    ]
}

LEVEL_DEADLY_DATA = {
    1: [
        (0, 2, 2, 2)
    ],
    2: [
        (0, 2, 2, 2)
    ],
    3: [
        (0, 2, 2, 2)
    ],
    4: [
        (0, 2, 2, 2)
    ],
    5: [
        (0, 2, 2, 2)
    ]
}

# Update LEVEL_ENEMY_DATA to include boundary information:
LEVEL_ENEMY_DATA = {
    1: [
        (12, 32, "horizontal", 12, 20)  # x, y, direction, boundary_start, boundary_end
    ],
    2: [
        (5, 10, "horizontal", 3, 8),
        (8, 15, "vertical", 13, 18)
    ],
    3: [
        (5, 10, "horizontal", 3, 8),
        (8, 15, "vertical", 13, 18)
    ],
    4: [
        (5, 10, "horizontal", 3, 8),
        (8, 15, "vertical", 13, 18)
    ],
    5: [
        (5, 10, "horizontal", 3, 8),
        (8, 15, "vertical", 13, 18)
    ]
}

class DialogueBox:
    def __init__(self, screen):
        self.screen = screen
        self.animation_complete = False
        self.current_alpha = 0
        self.target_alpha = 230
        self.fade_speed = 10
        self.current_line = 0
        self.current_word = 0
        self.current_char = 0
        self.text_delay = 2  # Controls typing speed
        self.frame_counter = 0
        self.words_revealed = []  # List to store revealed words for each line
        
    def animate(self, dialogue_lines):
        # Create semi-transparent background
        dialogue_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        dialogue_surface.fill(BLACK)
        
        # Animate fade in
        if self.current_alpha < self.target_alpha:
            self.current_alpha = min(self.current_alpha + self.fade_speed, self.target_alpha)
        dialogue_surface.set_alpha(self.current_alpha)
        self.screen.blit(dialogue_surface, (0, 0))
        
        # Initialize words_revealed list if needed
        if not self.words_revealed:
            self.words_revealed = [[] for _ in dialogue_lines]
        
        # Calculate text position for centering
        total_height = len(dialogue_lines) * 60
        start_y = (SCREEN_HEIGHT - total_height) // 2
        
        # Update text animation
        self.frame_counter += 1
        if self.frame_counter >= self.text_delay:
            self.frame_counter = 0
            self.update_text(dialogue_lines)
        
        # Draw text
        for i, line in enumerate(dialogue_lines):
            # Split line into words
            words = line.split()
            revealed_text = ' '.join(self.words_revealed[i])
            
            text_surface = pygame.font.SysFont('Bauhaus 93', 40).render(
                revealed_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * 60))
            self.screen.blit(text_surface, text_rect)
        
        # Add "Press SPACE to continue" prompt when animation is complete
        if self.animation_complete:
            prompt = pygame.font.SysFont('Bauhaus 93', 30).render(
                "Press SPACE to continue...", True, (200, 200, 200))
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(prompt, prompt_rect)
        
        return self.animation_complete
    
    def update_text(self, dialogue_lines):
        if self.current_line < len(dialogue_lines):
            words = dialogue_lines[self.current_line].split()
            
            if self.current_word < len(words):
                # Add next word
                self.words_revealed[self.current_line].append(words[self.current_word])
                self.current_word += 1
            else:
                # Move to next line
                self.current_line += 1
                self.current_word = 0
        else:
            self.animation_complete = True

# Update the show_dialogue function to properly handle space key:
def show_dialogue(dialogue_lines):
    dialogue_box = DialogueBox(screen)
    
    waiting = True
    space_pressed = False
    
    while waiting:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dialogue_box.animation_complete:
                    waiting = False
                    return True  # Always return True when space is pressed
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        dialogue_box.animate(dialogue_lines)
        pygame.display.update()
    
    return True

class CollisionTile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

class Key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = key_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = door_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = npc_img
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.animations_right = []
        self.animations_left = []
        player_size = (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2))
        
        for i in range(1, 5):
            img = pygame.image.load(f'img/dino{i}.png')
            img = pygame.transform.scale(img, player_size)
            self.animations_right.append(img)
            self.animations_left.append(pygame.transform.flip(img, True, False))
        
        self.dead_image = pygame.image.load('img/Skeleton.png')
        self.dead_image = pygame.transform.scale(self.dead_image, player_size)
        
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

    def update(self, game_over, world, keys_group):
        global keys_collected
        
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
            key = pygame.key.get_pressed()
            
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.vel_y = JUMP_SPEED
                self.jumped = True
                self.in_air = True
            
            if not key[pygame.K_SPACE]:
                self.jumped = False

            if key[pygame.K_LEFT]:
                dx -= MOVE_SPEED
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += MOVE_SPEED
                self.counter += 1
                self.direction = 1
            if not key[pygame.K_LEFT] and not key[pygame.K_RIGHT]:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.animations_right[self.index]
                else:
                    self.image = self.animations_left[self.index]

            # Handle animation
            if self.counter > walk_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.animations_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.animations_right[self.index]
                else:
                    self.image = self.animations_left[self.index]

            # Add gravity
            self.vel_y += GRAVITY
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Check for collision with keys
            key_hits = pygame.sprite.spritecollide(self, keys_group, True)
            keys_collected += len(key_hits)

            # Assume we're in the air unless collision detection proves otherwise
            self.in_air = True

            # Check for collision
            dx, dy = world.check_collision(self, dx, dy)

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
                game_over = -1
                game_over_fx.play()

        elif game_over == -1:
            self.image = self.dead_image
            if self.rect.y > 200:
                self.rect.y -= 5

        return game_over

class World:
    def __init__(self, level_data, deadly_data):
        self.collision_tiles = []
        self.deadly_tiles = []

        for plat in level_data:
            # Adjust coordinates to align with background
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            height = int(plat[3] * TILE_SIZE)
            
            # Add a small offset for better visual alignment if needed
            offset_x = 0  # Adjust these values if needed
            offset_y = 0
            
            collision_rect = pygame.Rect(
                x + offset_x,
                y + offset_y,
                width,
                height
            )
            self.collision_tiles.append(CollisionTile(x + offset_x, y + offset_y, width, height))

        for deadly in deadly_data:
            x = deadly[0] * TILE_SIZE
            y = deadly[1] * TILE_SIZE
            width = deadly[2] * TILE_SIZE
            height = int(deadly[3] * TILE_SIZE)
            
            self.deadly_tiles.append(CollisionTile(x, y, width, height))
            
    def check_collision(self, player, dx, dy):
        for tile in self.collision_tiles:
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
        for tile in self.deadly_tiles:
            if tile.rect.colliderect(player.rect):
                return "deadly"
        return dx, dy

    def draw(self, screen):
        for tile in self.collision_tiles:
            pygame.draw.rect(screen, (255, 0, 0), tile.rect, 1)
        for tile in self.deadly_tiles:
            pygame.draw.rect(screen, (0, 255, 0), tile.rect, 2)  # Changed to outline

def init_level(level_num):
    global keys_collected, game_start_time
    keys_collected = 0
    
    if game_start_time is None:
        game_start_time = time.time()
    
    # Create key positions for the level
    keys_group = pygame.sprite.Group()
    key_positions = generate_key_positions(level_num)
    for pos in key_positions:
        keys_group.add(Key(pos[0], pos[1]))
    
    # Position door and NPC based on level layout
    platforms = LEVEL_PLATFORM_DATA[level_num]
    
    # Find suitable platform for door placement
    suitable_platform = find_suitable_platform(platforms)
    
    # Calculate door position on the suitable platform
    platform_x = suitable_platform[0]
    platform_y = suitable_platform[1]
    platform_width = suitable_platform[2]
    
    # Place door near the right edge of the platform
    door_x = (platform_x + platform_width - 2) * TILE_SIZE  # Leave some space from the edge
    door_y = (platform_y - 2) * TILE_SIZE  # Place door above platform
    
    # Ensure door isn't too close to screen edge
    if door_x > SCREEN_WIDTH - 3 * TILE_SIZE:
        door_x = SCREEN_WIDTH - 3 * TILE_SIZE
    
    door = Door(door_x, door_y)
    npc = NPC(door_x - TILE_SIZE * 2, door_y)
    
    deadly_tiles = LEVEL_DEADLY_DATA[level_num]
    world = World(platforms, deadly_tiles)
    
    moving_enemies.empty()
    for enemy_data in LEVEL_ENEMY_DATA[level_num]:
        x, y, direction, boundary_start, boundary_end = enemy_data
        enemy = MovingEnemy(x, y, direction, boundary_start, boundary_end)
        moving_enemies.add(enemy)
    
    return keys_group, door, npc, world, moving_enemies

class MovingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, boundary_start, boundary_end):
        super().__init__()
        self.image = pygame.transform.scale(npc_img, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.direction = direction
        self.speed = 2
        self.boundary_start = boundary_start * TILE_SIZE
        self.boundary_end = boundary_end * TILE_SIZE
        self.initial_pos = self.rect.x if direction == "horizontal" else self.rect.y
    
    def draw_boundaries(self, screen):
        if self.direction == "horizontal":
            # Draw horizontal boundary line
            pygame.draw.line(screen, (255, 0, 0), 
                           (self.boundary_start, self.rect.centery),
                           (self.boundary_end, self.rect.centery), 2)
        else:
            # Draw vertical boundary line
            pygame.draw.line(screen, (255, 0, 0), 
                           (self.rect.centerx, self.boundary_start),
                           (self.rect.centerx, self.boundary_end), 2)

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

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

# Update the show_dialogue function:
def show_dialogue(dialogue_lines):
    dialogue_box = DialogueBox(screen)
    
    waiting = True
    while waiting:
        clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and dialogue_box.animation_complete:
                    waiting = False
                elif event.key == pygame.K_ESCAPE:
                    return False
        
        dialogue_box.animate(dialogue_lines)
        pygame.display.update()
    
    return True

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
        
        # Skip platforms that are too low or too high
        if y < SCREEN_HEIGHT * 0.8 and y > SCREEN_HEIGHT * 0.1 and x > 0 and x < SCREEN_WIDTH:
            viable_platforms.append((x, y, width))
    
    # Ensure we have enough platforms
    if len(viable_platforms) < required_keys:
        # Add some lower platforms if needed
        for plat in platforms:
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            if (x, y, width) not in viable_platforms:
                viable_platforms.append((x, y, width))
    
    # Randomly select platforms and place keys on them
    import random
    random.shuffle(viable_platforms)
    
    for i in range(min(required_keys, len(viable_platforms))):
        plat = viable_platforms[i]
        # Place key somewhere along the platform
        key_x = plat[0] + random.uniform(TILE_SIZE, plat[2] - TILE_SIZE * 2)  # Leave space at edges
        key_y = plat[1] - TILE_SIZE * 1.5  # Place key above platform
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

# Initialize game state
current_state = "start_screen"
start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, start_btn)
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)

# Create initial player and world objects
player = Player(100, SCREEN_HEIGHT - 130)
world = World(LEVEL_PLATFORM_DATA[1], LEVEL_DEADLY_DATA[1])  # Initialize with level 1 data

# Game loop
clock = pygame.time.Clock()
fps = 60
running = True
moving_enemies = pygame.sprite.Group()
game_over = 0  # Make sure game_over is initialized

while running:
    clock.tick(fps)
        # Also add these variables at the start of the game loop section:
    if 'elapsed_time' not in locals():
        elapsed_time = 0
    if 'keys_group' not in locals():
        keys_group = pygame.sprite.Group()
    
    # Event handling at the start of the loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

    if current_state == "start_screen":
        screen.blit(start_bg, (0, 0))
        if start_button.draw(screen):
            current_state = "intro_dialogue"

    elif current_state == "intro_dialogue":
        if show_dialogue(STORYLINE["intro"]):
            current_state = "playing"
            current_level = 1
            keys_group, door, npc, world, moving_enemies = init_level(current_level)
            player = Player(100, SCREEN_HEIGHT - 130)
        else:
            current_state = "playing"
            current_level = 1
            keys_group, door, npc, world, moving_enemies = init_level(current_level)
            player = Player(100, SCREEN_HEIGHT - 130)
    
    elif current_state == "playing":
        screen.blit(level_backgrounds[current_level], (0, 0))
        
        # Create unique keys for tracking dialogue states
        storyline_key = f'storyline_{current_level}'
        level_key = f'level_{current_level}'
        
        # Initialize dialogue states if needed
        if storyline_key not in dialogue_states:
            dialogue_states[storyline_key] = False
        if level_key not in dialogue_states:
            dialogue_states[level_key] = False
        
        # Show storyline dialogue first
        if not dialogue_states[storyline_key]:
            if show_dialogue(STORYLINE[f"level{current_level}"]):
                dialogue_states[storyline_key] = True
            else:
                dialogue_states[storyline_key] = True
        
        # Then show level instructions
        elif not dialogue_states[level_key]:
            if show_dialogue(LEVEL_DIALOGUES[current_level]):
                dialogue_states[level_key] = True
            else:
                dialogue_states[level_key] = True
        
        draw_text(f"Level {current_level}", 40, WHITE, 10, 10)
        draw_text(f"Keys: {keys_collected}/{LEVEL_REQUIREMENTS[current_level]}", 40, WHITE, 10, 60)
        
        deadly_collision = world.check_collision(player, 0, 0)
        if deadly_collision == "deadly":
            game_over = -1
            game_over_fx.play()
        
        # Update and draw game objects
        game_over = player.update(game_over, world, keys_group)
        world.draw(screen)
        keys_group.draw(screen)
        
        # Draw enemies and their boundaries
        moving_enemies.update()
        for enemy in moving_enemies:
            enemy.draw_boundaries(screen)
        moving_enemies.draw(screen)
        
        screen.blit(player.image, player.rect)
        screen.blit(door.image, door.rect)
        screen.blit(npc.image, npc.rect)
        
        if game_over == -1:
            draw_text('GAME OVER!', 70, BLUE, (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2)
            if restart_button.draw(screen):
                game_over = 0
                player.rect.x = 100
                player.rect.y = SCREEN_HEIGHT - 130
                keys_collected = 0
                keys_group, door, npc, world, moving_enemies = init_level(current_level)
        
        elif keys_collected >= LEVEL_REQUIREMENTS[current_level] and pygame.sprite.collide_rect(player, door):
            # Show completion dialogue
            if show_dialogue([f"Level {current_level} Complete!", 
                            "You've found all the keys!", 
                            "Press SPACE to continue..."]):
                if current_level < 5:
                    # Advance to next level
                    current_level += 1
                    # Reset dialogue states for new level
                    storyline_key = f'storyline_{current_level}'
                    level_key = f'level_{current_level}'
                    dialogue_states[storyline_key] = False
                    dialogue_states[level_key] = False
                    if game_start_time:  # Only append time if game has started
                        elapsed_time = int(time.time() - game_start_time)
                        level_times.append(elapsed_time)
                    # Initialize next level
                    keys_group, door, npc, world, moving_enemies = init_level(current_level)
                    player.rect.x = 100
                    player.rect.y = SCREEN_HEIGHT - 130
                else:
                    # Game complete
                    if show_dialogue(["Congratulations!", 
                                    "You've completed all levels!", 
                                    "Press SPACE to see your results..."]):
                        current_state = "game_complete"

    elif current_state == "game_complete":
        screen.fill(BLACK)
        total_time = int(time.time() - game_start_time)
        minutes = total_time // 60
        seconds = total_time % 60
        
        draw_text("Congratulations!", 70, WHITE, SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT // 3)
        draw_text(f"You've completed Decoding Island!", 50, WHITE, SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2)
        draw_text(f"Total Time: {minutes:02d}:{seconds:02d}", 50, WHITE, SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2 + 100)
        
        if restart_button.draw(screen):
            current_state = "start_screen"
            game_start_time = None
            current_level = 0
            keys_collected = 0
            level_times = []
    
    pygame.display.update()

pygame.quit()