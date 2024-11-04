import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1000
GRID_SIZE = 6  # Number of guesses
WORD_LENGTH = 5  # Length of the word
FONT_SIZE = 60
BOX_SIZE = 85  # Size of each letter box
BOX_SPACING = 15  # Space between boxes
BOX_BORDER_RADIUS = 5  # Rounded corners for boxes

# Colors
BACKGROUND_COLOR = (18, 18, 19)  # Dark background like original Wordle
EMPTY_BOX_COLOR = (58, 58, 60)   # Dark gray for empty boxes
BORDER_COLOR = (58, 58, 60)      # Border color for empty boxes
FILLED_BOX_COLOR = (58, 58, 60)  # Color for filled but unsubmitted boxes
GREEN = (83, 141, 78)   # Correct letter, correct position
YELLOW = (181, 159, 59) # Correct letter, wrong position
GRAY = (58, 58, 60)     # Wrong letter
TEXT_COLOR = (255, 255, 255)  # White text
TITLE_COLOR = (255, 255, 255) # White title

# Load a list of words
word_list = [
    "ARRAY", "CLASS", "DEBUG", "ERROR", "FLOAT", 
    "INPUT", "LOGIC", "LOOPS", "QUEUE", "STACK",
    "PARSE", "PRINT", "PROXY", "QUERY", "RANGE",
    "SCOPE", "SHELL", "SLICE", "SWING", "TUPLE",
    "TYPES", "VALUE", "WHILE", "YIELD", "BREAK",
    "CATCH", "CONST", "EVENT", "FALSE", "FINAL",
    "FRAME", "INDEX", "LABEL", "MACRO", "MATCH",
    "MERGE", "NODES", "PIXEL", "POINT", "POWER",
    "REACT", "ROUTE", "SCALA", "SETUP", "SPLIT",
    "STATE", "SUPER", "TABLE", "TRACE", "VALID",
    "BLOCK", "CACHE", "CHAIN", "CHECK", "COUNT",
    "DELAY", "DRAFT", "EMPTY", "FETCH", "FLAGS",
    "FLASH", "GROUP", "GUARD", "HTTPS", "LEVEL",
    "LINKS", "MODEL", "NUMPY", "PATCH", "PAUSE",
    "PROTO", "RESET", "ROUND", "SCALE", "THROW"
]

def draw_title():
    """Draw the game title at the top of the screen."""
    title_surface = title_font.render("DeCoding Island", True, TITLE_COLOR)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
    screen.blit(title_surface, title_rect)
    
    pygame.draw.line(screen, BORDER_COLOR, 
                    (SCREEN_WIDTH // 4, 130), 
                    (3 * SCREEN_WIDTH // 4, 130), 
                    2)

def draw_box(x, y, color, letter='', border_color=None):
    """Draw a single letter box with optional border and letter."""
    box_rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)
    pygame.draw.rect(screen, color, box_rect, border_radius=BOX_BORDER_RADIUS)
    
    if border_color:
        pygame.draw.rect(screen, border_color, box_rect, 3, border_radius=BOX_BORDER_RADIUS)
    
    if letter:
        text_surface = game_font.render(letter, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(x + BOX_SIZE // 2, y + BOX_SIZE // 2))
        screen.blit(text_surface, text_rect)

def draw_grid(guesses, current_guess):
    """Draw the grid of guesses and the current guess."""
    start_x = (SCREEN_WIDTH - (WORD_LENGTH * (BOX_SIZE + BOX_SPACING))) // 2
    start_y = 180
    
    for i in range(GRID_SIZE):
        for j in range(WORD_LENGTH):
            x = start_x + j * (BOX_SIZE + BOX_SPACING)
            y = start_y + i * (BOX_SIZE + BOX_SPACING)
            
            if i < len(guesses):
                letter = guesses[i][j]
                color = GRAY
                if letter in secret_word:
                    if letter == secret_word[j]:
                        color = GREEN
                    else:
                        color = YELLOW
                draw_box(x, y, color, letter)
            else:
                draw_box(x, y, BACKGROUND_COLOR, border_color=BORDER_COLOR)

    # Draw current guess
    current_row = len(guesses)
    if current_row < GRID_SIZE:
        for j in range(WORD_LENGTH):
            x = start_x + j * (BOX_SIZE + BOX_SPACING)
            y = start_y + current_row * (BOX_SIZE + BOX_SPACING)
            if j < len(current_guess):
                draw_box(x, y, FILLED_BOX_COLOR, current_guess[j])
            else:
                draw_box(x, y, BACKGROUND_COLOR, border_color=BORDER_COLOR)

def show_game_over_message(won):
    """Display game over message."""
    message = "You Won!" if won else f"Game Over! Word was: {secret_word}"
    text_surface = game_font.render(message, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))
    screen.blit(text_surface, text_rect)

def main():
    global secret_word, screen, game_font, title_font
    
    # Set up the screen
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Wordle")
    
    # Fonts
    game_font = pygame.font.SysFont('Arial Bold', FONT_SIZE)
    title_font = pygame.font.SysFont('Arial Bold', 70)
    
    # Select a random word
    secret_word = random.choice(word_list)
    
    running = True
    guesses = []
    current_guess = ""
    game_over = False
    won = False
    
    while running:
        screen.fill(BACKGROUND_COLOR)
        draw_title()
        draw_grid(guesses, current_guess)
        
        if game_over:
            show_game_over_message(won)
            pygame.display.flip()
            pygame.time.wait(2000)  # Show result for 2 seconds
            return won

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                return False

            if event.type == pygame.KEYDOWN and not game_over:
                if event.key == pygame.K_RETURN and len(current_guess) == WORD_LENGTH:
                    guesses.append(current_guess)
                    if current_guess == secret_word:
                        game_over = True
                        won = True
                    elif len(guesses) >= GRID_SIZE:
                        game_over = True
                    current_guess = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                elif len(current_guess) < WORD_LENGTH and event.unicode.isalpha():
                    current_guess += event.unicode.upper()

        pygame.display.flip()

    return won

if __name__ == "__main__":
    main()