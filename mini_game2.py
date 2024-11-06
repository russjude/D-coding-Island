"""
mini-game2.py

Primary Author: Russel Rafanan
Secondary Author: Jessica Ng

A Python-based word guessing game inspired by Wordle, featuring a programming-themed
word list. Players have 6 attempts to guess a 5-letter word, with color-coded feedback
for correct letters and positions. The game includes a graphical interface using Pygame
with a mountain background and custom title image.
"""

import pygame
import random

# Initialize Pygame engine
pygame.init()

SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
GRID_SIZE = 6
WORD_LENGTH = 5
FONT_SIZE = 50  # Reduced font size
BOX_SIZE = 80   # Reduced box size
BOX_SPACING = 10  # Reduced spacing
BOX_BORDER_RADIUS = 5

# Color scheme definitions
BACKGROUND_COLOR = (18, 18, 19)  # Dark theme background
EMPTY_BOX_COLOR = (58, 58, 60)   # Unfilled box color
BORDER_COLOR = (58, 58, 60)      # Box outline color
FILLED_BOX_COLOR = (58, 58, 60)  # Box color for entered letters
GREEN = (83, 141, 78)   # Indicates correct letter in correct position
YELLOW = (181, 159, 59) # Indicates correct letter in wrong position
GRAY = (58, 58, 60)     # Indicates letter not in word
TEXT_COLOR = (255, 255, 255)  # Letter color

# Programming-themed word bank
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

class FeedbackMessage:
    """Handles the display of game messages with visual effects"""
    def __init__(self, text, duration, color=TEXT_COLOR):
        self.text = text
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.color = color
        self.active = True
        self.outline_thickness = 2

    def should_display(self):
        """Check if message should still be shown based on duration"""
        if not self.active:
            return False
        elapsed = pygame.time.get_ticks() - self.start_time
        return elapsed < self.duration

    def get_darker_shade(self, color, factor=0.6):
        """Create outline color by darkening the main color"""
        return tuple(int(c * factor) for c in color)

    def draw_outlined_text(self, screen, font, pos):
        """Draw text with outline effect for better visibility"""
        outline_color = self.get_darker_shade(self.color if self.color != TEXT_COLOR else (128, 128, 128))
        text_surface = font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=pos)

        # Apply outline effect using multiple offset positions
        outline_positions = [
            (-self.outline_thickness, -self.outline_thickness),
            (-self.outline_thickness, self.outline_thickness),
            (self.outline_thickness, -self.outline_thickness),
            (self.outline_thickness, self.outline_thickness),
            (-self.outline_thickness, 0),
            (self.outline_thickness, 0),
            (0, -self.outline_thickness),
            (0, self.outline_thickness),
        ]

        for dx, dy in outline_positions:
            outline_rect = text_rect.copy()
            outline_rect.x += dx
            outline_rect.y += dy
            outline_surface = font.render(self.text, True, outline_color)
            screen.blit(outline_surface, outline_rect)

        screen.blit(text_surface, text_rect)

    def draw(self, screen, font, y_position):
        """Draw the message if it's still within its display duration"""
        if self.should_display():
            self.draw_outlined_text(screen, font, (SCREEN_WIDTH // 2, y_position))

def draw_title():
    """Display game title image centered at the top"""
    title_rect = title_image.get_rect(center=(SCREEN_WIDTH // 2, 100))  # Moved up
    screen.blit(title_image, title_rect)

def draw_box(x, y, color, letter='', border_color=None):
    """Draw a letter box with specified styling and content"""
    box_rect = pygame.Rect(x, y, BOX_SIZE, BOX_SIZE)
    pygame.draw.rect(screen, color, box_rect, border_radius=BOX_BORDER_RADIUS)
    
    if border_color:
        pygame.draw.rect(screen, border_color, box_rect, 3, border_radius=BOX_BORDER_RADIUS)
    
    if letter:
        text_surface = game_font.render(letter, True, TEXT_COLOR)
        text_rect = text_surface.get_rect(center=(x + BOX_SIZE // 2, y + BOX_SIZE // 2))
        screen.blit(text_surface, text_rect)

def get_letter_colors(guess, secret):
    """Determine feedback colors for each letter in the guess"""
    colors = [GRAY] * WORD_LENGTH
    remaining_letters = {}

    # Count remaining letters after marking exact matches
    for i in range(WORD_LENGTH):
        if guess[i] != secret[i]:
            remaining_letters[secret[i]] = remaining_letters.get(secret[i], 0) + 1

    # Mark correct letters in correct positions
    for i in range(WORD_LENGTH):
        if guess[i] == secret[i]:
            colors[i] = GREEN
            if guess[i] in remaining_letters:
                remaining_letters[guess[i]] -= 1

    # Mark correct letters in wrong positions
    for i in range(WORD_LENGTH):
        if colors[i] != GREEN and guess[i] in remaining_letters and remaining_letters[guess[i]] > 0:
            colors[i] = YELLOW
            remaining_letters[guess[i]] -= 1

    return colors

def draw_grid(guesses, current_guess):
    """Render the game grid with all guesses and current input"""
    start_x = (SCREEN_WIDTH - (WORD_LENGTH * (BOX_SIZE + BOX_SPACING))) // 2
    start_y = 250  # Moved up

    # Draw previous guesses
    for i in range(GRID_SIZE):
        for j in range(WORD_LENGTH):
            x = start_x + j * (BOX_SIZE + BOX_SPACING)
            y = start_y + i * (BOX_SIZE + BOX_SPACING)

            if i < len(guesses):
                letter = guesses[i][j]
                colors = get_letter_colors(guesses[i], secret_word)
                draw_box(x, y, colors[j], letter)
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

def main():
    """Main game loop and initialization"""
    global secret_word, screen, game_font, title_image
    
    # Initialize display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Wordle")

    # Load and scale background and title images
    background_image = pygame.image.load("Minigame2/mountainbg.png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    title_image = pygame.image.load("Minigame2/spelltodecode.png")
    title_image = pygame.transform.scale(title_image, (600, 150))

    # Set up game font
    game_font = pygame.font.SysFont('Arial Bold', FONT_SIZE)

    # Initialize game state
    secret_word = "RUSSS"
    print(f"Secret word: {secret_word}")  # Development testing only
    
    running = True
    guesses = []
    current_guess = ""
    game_over = False
    won = False
    feedback_messages = []
    play_again_message = None

    # Main game loop
    while running:
        screen.blit(background_image, (0,0))
        draw_title()
        draw_grid(guesses, current_guess)

        # Update and display feedback messages
        y_position = SCREEN_HEIGHT - 150
        for message in feedback_messages[:]:
            message.draw(screen, game_font, y_position)
            if not message.should_display():
                feedback_messages.remove(message)
            y_position -= 60

        if play_again_message:
            play_again_message.draw(screen, game_font, SCREEN_HEIGHT - 100)

        # Handle game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Reset game state for new round
                        secret_word = random.choice(word_list)
                        guesses = []
                        current_guess = ""
                        game_over = False
                        won = False
                        feedback_messages = []
                        play_again_message = None
                        print(f"New secret word: {secret_word}")  # Development testing only
                elif event.key == pygame.K_RETURN and len(current_guess) == WORD_LENGTH:
                    # Process completed guess
                    guesses.append(current_guess)
                    if current_guess == secret_word:
                        won = True
                        game_over = True
                        feedback_messages.append(FeedbackMessage("Congratulations! You won!", 5000, GREEN))
                        return True  # Return True when player wins
                    elif len(guesses) >= GRID_SIZE:
                        game_over = True
                        feedback_messages.append(FeedbackMessage(f"Game Over! The word was {secret_word}", 5000))
                        play_again_message = FeedbackMessage("Press SPACE to play again", float('inf'))
                    current_guess = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                elif len(current_guess) < WORD_LENGTH and event.unicode.isalpha():
                    current_guess += event.unicode.upper()
                elif event.key == pygame.K_RETURN and len(current_guess) < WORD_LENGTH:
                    feedback_messages.append(FeedbackMessage("Word is too short!", 2000))

        pygame.display.flip()
if __name__ == "__main__":
    main()