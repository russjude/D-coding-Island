import pygame
from pygame.locals import *
from pygame import mixer
import os

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

# Load and scale the background
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
pygame.display.set_caption('Platformer')

# Define game variables
TILE_SIZE = SCREEN_HEIGHT // 36
GRAVITY = 0.8
JUMP_SPEED = -15
MOVE_SPEED = 8
game_over = 0
score = 0
win = False

# Define colors
white = (255, 255, 255)
blue = (0, 0, 255)

# Load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
restart_img = pygame.image.load('img/restart_btn.png')
door_img = pygame.image.load('img/exit.png')
door_img = pygame.transform.scale(door_img, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 2)))

# Load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)

class CollisionTile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = door_img
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

    def update(self, game_over, win, door):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0 and not win:
            key = pygame.key.get_pressed()
            
            # Jump only if we're on the ground (not in_air) and haven't jumped yet
            if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
                jump_fx.play()
                self.vel_y = JUMP_SPEED
                self.jumped = True
                self.in_air = True
            
            # Reset jumped state when space is released
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

            # Assume we're in the air unless collision detection proves otherwise
            self.in_air = True

            # Check for collision
            dx, dy = world.check_collision(self, dx, dy)

            # Check for collision with the door
            if self.rect.colliderect(door.rect):
                win = True

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

        return game_over, win

class World:
    def __init__(self):
        self.collision_tiles = []
        
        # Platform data for level 1
        platform_data = [
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
        ]
        
        for plat in platform_data:
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            height = int(plat[3] * TILE_SIZE)
            collision_rect = pygame.Rect(
                x + 2,
                y + 2,
                width - 4,
                height - 4
            )
            self.collision_tiles.append(CollisionTile(x, y, width, height))

    def check_collision(self, player, dx, dy):
        for tile in self.collision_tiles:
            # Check x collision
            if tile.rect.colliderect(player.rect.x + dx, player.rect.y, player.width, player.height):
                dx = 0
            
            # Check y collision
            if tile.rect.colliderect(player.rect.x, player.rect.y + dy, player.width, player.height):
                # Check if below the ground i.e. jumping
                if player.vel_y < 0:
                    dy = tile.rect.bottom - player.rect.top
                    player.vel_y = 0
                # Check if above the ground i.e. falling
                elif player.vel_y >= 0:
                    dy = tile.rect.top - player.rect.bottom
                    player.vel_y = 0
                    player.in_air = False  # We've hit a platform, so we're not in the air
                
        return dx, dy

    def draw(self, screen):
        for tile in self.collision_tiles:
            pygame.draw.rect(screen, (255, 0, 0), tile.rect, 1)

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, self.rect)
        return action

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Initialize game objects
world = World()
player = Player(100, SCREEN_HEIGHT - 130)
door = Door(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200)
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)

# Game loop
clock = pygame.time.Clock()
fps = 60
run = True

while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))

    if game_over == 0 and not win:
        game_over, win = player.update(game_over, win, door)
    elif game_over == -1:
        draw_text('GAME OVER!', pygame.font.SysFont('Bauhaus 93', 70), blue, 
                 (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2)
        if restart_button.draw():
            player.rect.x = 100
            player.rect.y = SCREEN_HEIGHT - 130
            game_over = 0
            win = False
    elif win:
        draw_text('You Win!', pygame.font.SysFont('Bauhaus 93', 70), blue, 
                 (SCREEN_WIDTH // 2) - 150, SCREEN_HEIGHT // 2)
        if restart_button.draw():
            player.rect.x = 100
            player.rect.y = SCREEN_HEIGHT - 130
            game_over = 0
            win = False

    # Draw the world (collision boxes)
    world.draw(screen)
    
    # Draw the player
    screen.blit(player.image, player.rect)
    
    # Draw the door
    screen.blit(door.image, door.rect)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()

pygame.quit()