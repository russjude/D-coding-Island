import pygame

# Initialize Pygame and Mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
TILE_SIZE = 50
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)

# Game Variables
LEVEL = 3
MAX_LEVELS = 7
SCORE = 0
GAME_OVER = 0
MAIN_MENU = True

# Load Fonts
FONT = pygame.font.SysFont('Bauhaus 93', 70)
FONT_SCORE = pygame.font.SysFont('Bauhaus 93', 30)

# Load Images
SUN_IMG = pygame.image.load('img/sun.png')
BG_IMG = pygame.image.load('img/sky.png')
RESTART_IMG = pygame.image.load('img/restart_btn.png')
START_IMG = pygame.image.load('img/start_btn.png')
EXIT_IMG = pygame.image.load('img/exit_btn.png')

# Load Sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
COIN_FX = pygame.mixer.Sound('img/coin.wav')
JUMP_FX = pygame.mixer.Sound('img/jump.wav')
GAME_OVER_FX = pygame.mixer.Sound('img/game_over.wav')

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer Game')

# Clock to control frame rate
CLOCK = pygame.time.Clock()

# Main Game Loop
run = True
while run:
    CLOCK.tick(FPS)
    
    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Draw Background
    screen.blit(BG_IMG, (0, 0))
    screen.blit(SUN_IMG, (100, 100))

    # Update the display
    pygame.display.update()

# Quit Pygame
pygame.quit()
