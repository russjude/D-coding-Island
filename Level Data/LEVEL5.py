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
original_bg = pygame.image.load('Level Data/Level Image/LEVEL5.png')
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

# Define colors
white = (255, 255, 255)
blue = (0, 0, 255)

# Load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
restart_img = pygame.image.load('img/restart_btn.png')

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

    def update(self, game_over):
        dx = 0
        dy = 0
        walk_cooldown = 5

        if game_over == 0:
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

def draw_grid(screen):
    # Create a new surface for the grid
    grid_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # Set the alpha value for translucency
    grid_surface.set_alpha(128)  # Adjust this value for more or less transparency

    # Draw vertical lines
    for x in range(0, SCREEN_WIDTH, TILE_SIZE):
        color = (255, 0, 0) if (x // TILE_SIZE) % 5 == 0 else (200, 200, 200)  # Red for every 5 tiles
        pygame.draw.line(grid_surface, color, (x, 0), (x, SCREEN_HEIGHT), 1)

    # Draw horizontal lines
    for y in range(0, SCREEN_HEIGHT, TILE_SIZE):
        color = (255, 0, 0) if (y // TILE_SIZE) % 5 == 0 else (200, 200, 200)  # Red for every 5 tiles
        pygame.draw.line(grid_surface, color, (0, y), (SCREEN_WIDTH, y), 1)

    # Blit the grid surface onto the main screen
    screen.blit(grid_surface, (0, 0))

class World:
    def __init__(self):
        self.collision_tiles = []
        
        # Platform data for level 1
        platform_data = [

            (15.4, 28, 2.2, 3),
            (22, 25.4, 2, 2),
            (25, 12, 2.4, 2.7),
            (28.4, 18.7, 2.4, 2.3),
            (31.8, 25.2,  2.3, 2),
            (26.9, 32, 2, 2),
            (40.2, 25.3, 2, 2),
            (41.7, 30, 2, 2),
            


            (0, 5.2, 9.5, 1),
            (0, 13.5, 11.4, 1),
            (0.2, 23.4, 1.1, 14),
            (3.5, 26.7, 1.4, 11),

            (6.8, 30, 3, 1),
            (6.7, 23.4, 3, 1),
            (10, 18.5, 4.6, 1),
            (10, 26.7, 8.2, 1.5),
            (26.3, 26.7, 5.3, 1.5),
            (31.1, 26.7, 3.3, 1.5),
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
            (17.7, 31.5, 1.8, 1),



            (9.9, 33.2, 5, 1.3),
            (19.4, 33.2, 7.3, 1.3),
            (29.4, 33.2, 5.4, 1.3),
            (36, 33.2, 5.5, 1.3),
            (44, 33.2, 5.3, 1.3)
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

# Add this with other game data at the top
ENEMY_DATA = [
            


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

class MovingEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, boundary_start, boundary_end):
        super().__init__()
        self.image = pygame.transform.scale(
            pygame.image.load('img/skeleton.png'),
            (int(TILE_SIZE * 0.8), int(TILE_SIZE * 0.8))
        )
        self.rect = self.image.get_rect()
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE
        self.direction = direction
        self.speed = 2
        self.moving_right = True
        self.boundary_start = boundary_start * TILE_SIZE
        self.boundary_end = boundary_end * TILE_SIZE

    def update(self):
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
    
    def check_collision(self, player):
        collision_margin = 4
        collision_rect = pygame.Rect(
            self.rect.x + collision_margin,
            self.rect.y + collision_margin,
            self.rect.width - (collision_margin * 2),
            self.rect.height - (collision_margin * 2)
        )
        return collision_rect.colliderect(player.rect)

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
restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)

# Add this line to create enemy group
moving_enemies = pygame.sprite.Group()
for enemy_data in ENEMY_DATA:
    x, y, direction, boundary_start, boundary_end = enemy_data
    enemy = MovingEnemy(x, y, direction, boundary_start, boundary_end)
    moving_enemies.add(enemy)

# Game loop
clock = pygame.time.Clock()
fps = 60
run = True

while run:
    clock.tick(fps)

    screen.blit(bg_img, (0, 0))

    if game_over == 0:
        game_over = player.update(game_over)
        
        # Add these lines for enemy updates and collision checks
        moving_enemies.update()
        for enemy in moving_enemies:
            if enemy.check_collision(player):
                game_over = -1
                game_over_fx.play()
                
    elif game_over == -1:
        draw_text('GAME OVER!', pygame.font.SysFont('Bauhaus 93', 70), blue, 
                 (SCREEN_WIDTH // 2) - 200, SCREEN_HEIGHT // 2)
        if restart_button.draw():
            player.rect.x = 100
            player.rect.y = SCREEN_HEIGHT - 130
            game_over = 0

    # Draw the world (collision boxes)
    world.draw(screen)
    draw_grid(screen)
    
    # Draw the player
    screen.blit(player.image, player.rect)
    
    # Add this line to draw enemies
    moving_enemies.draw(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()