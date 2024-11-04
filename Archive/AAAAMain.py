import pygame
from pygame.locals import *
import os


# Initialize Pygame
pygame.init()

# Get the screen resolution
infoObject = pygame.display.Info()
monitor_width = infoObject.current_w
monitor_height = infoObject.current_h

# Calculate the game window size (90% of screen size while maintaining aspect ratio)
SCREEN_SCALE = 0.9  # This will make the window 90% of the screen size
target_width = int(monitor_width * SCREEN_SCALE)
target_height = int(monitor_height * SCREEN_SCALE)

# Load and scale the background
original_bg = pygame.image.load('Level0.png')
bg_aspect_ratio = original_bg.get_width() / original_bg.get_height()

# Adjust window size to maintain aspect ratio
if target_width / target_height > bg_aspect_ratio:
    SCREEN_WIDTH = int(target_height * bg_aspect_ratio)
    SCREEN_HEIGHT = target_height
else:
    SCREEN_WIDTH = target_width
    SCREEN_HEIGHT = int(target_width / bg_aspect_ratio)

# Scale background to fit the calculated screen size
bg = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer Game')

# Define colors and constants
TILE_SIZE = SCREEN_HEIGHT // 36  # Assuming the image is 36 tiles high
GRAVITY = 0.8
JUMP_SPEED = -15
MOVE_SPEED = 8

# Add this new class for collision tiles
class CollisionTile:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Load all dino animations and scale them
        self.animations_right = []
        self.animations_left = []
        # Adjust player size to match visual appearance
        player_size = (int(TILE_SIZE * 1.2), int(TILE_SIZE * 1.2))  # Slightly smaller than before
        
        for i in range(1, 5):
            img = pygame.image.load(f'img/dino{i}.png')
            img = pygame.transform.scale(img, player_size)
            self.animations_right.append(img)
            self.animations_left.append(pygame.transform.flip(img, True, False))
        
        self.index = 0
        self.counter = 0
        self.image = self.animations_right[self.index]
        self.rect = self.image.get_rect()
        # Create a smaller collision rect for more precise collisions
        self.collision_rect = pygame.Rect(0, 0, 
                                        int(player_size[0] * 0.7),  # 70% of image width
                                        int(player_size[1] * 0.9))  # 90% of image height
        self.rect.x = x
        self.rect.y = y
        # Center the collision rect within the sprite
        self.collision_rect.centerx = self.rect.centerx
        self.collision_rect.bottom = self.rect.bottom
        self.vel_y = 0
        self.jumped = False
        self.direction = 1
        self.in_air = True

    def update(self):
        dx = 0
        dy = 0
        walk_cooldown = 5

        # Get keypresses
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE] and not self.jumped and not self.in_air:
            self.vel_y = JUMP_SPEED
            self.jumped = True
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

        dx, dy = world.check_collision(self.rect, dx, dy)

        # Update player position
        self.rect.x += dx
        self.rect.y += dy

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Update in_air status
        self.in_air = dy != 0

class World:
    def __init__(self):
        self.collision_tiles = []
        
        # Create collision tiles based on LEVEL0GAME.tmx data
        # Adjusted platform coordinates and sizes for larger platforms
        platform_data = [
            # Top platforms
            (3, 8, 6, 1.0),    # Left platform (wider)
            (28, 8, 6, 1.0),   # Right platform (wider)
            
            # Middle platform
            (15, 13, 6, 1.0),  # Middle platform (wider)
            
            # Lower platforms
            (35, 23.2, 5, 1.0),  # Lower left (wider)
            (20, 23.2, 4, 1.0),  # Lower middle (wider)
            
            # Bottom platforms
            (11.8, 28, 6.2, 2.5),   # Bottom left (wider)
            (26.6, 28, 6.2, 2.5),  # Bottom middle (wider)
            (41.3, 28, 8, 1.),  # Bottom right (wider)
            
            # Ground level
            (0, 33, 8, 3.0),  # Ground (thicker)
            (51, 33, 8.2, 3.0),  # Ground (thicker)
        ]
        
        # Convert tile positions to screen coordinates with adjusted collision boxes
        for plat in platform_data:
            x = plat[0] * TILE_SIZE
            y = plat[1] * TILE_SIZE
            width = plat[2] * TILE_SIZE
            height = int(plat[3] * TILE_SIZE)
            # Add slight offset to collision boxes for better visual alignment
            collision_rect = pygame.Rect(
                x + 2,  # Small offset from left
                y + 2,  # Small offset from top
                width - 4,  # Slightly narrower
                height - 4  # Slightly shorter
            )
            self.collision_tiles.append(CollisionTile(x, y, width, height))

    def check_collision(self, player_rect, dx, dy):
        for tile in self.collision_tiles:
            # Update collision checks to use the player's collision rect
            if tile.rect.colliderect(player_rect.x + dx, player_rect.y, player_rect.width, player_rect.height):
                dx = 0
            
            if tile.rect.colliderect(player_rect.x, player_rect.y + dy, player_rect.width, player_rect.height):
                # Adjust collision response for better feel
                if player_rect.bottom + dy > tile.rect.top and dy > 0:
                    player_rect.bottom = tile.rect.top - 1  # Slight offset to prevent sticking
                    dy = 0
                elif player_rect.top + dy < tile.rect.bottom and dy < 0:
                    player_rect.top = tile.rect.bottom + 1  # Slight offset to prevent sticking
                    dy = 0
                
        return dx, dy

def find_lowest_platform(world):
    lowest_y = 0
    for tile in world.collision_tiles:
        if tile.rect.y > lowest_y:
            lowest_y = tile.rect.y
    return lowest_y

# Create world
world = World()

# Find the lowest platform
lowest_platform_y = find_lowest_platform(world)

# Create player and set initial position
player_start_x = 100  # You can adjust this value as needed
player_start_y = lowest_platform_y - TILE_SIZE * 2  # Position player two tiles above the lowest platform
player = Player(player_start_x, player_start_y)
player_group = pygame.sprite.Group()
player_group.add(player)

# Game loop
clock = pygame.time.Clock()
run = True

while run:
    clock.tick(60)

    # Draw background
    screen.blit(bg, (0, 0))

    # Update and draw player
    player_group.update()
    player_group.draw(screen)

    # Uncomment this section to see the collision boxes (for debugging)
    for tile in world.collision_tiles:
        pygame.draw.rect(screen, (255, 0, 0), tile.rect, 1)

    # Event handler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False

    pygame.display.update()

pygame.quit()