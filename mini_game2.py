"""
mini-game2.py

Primary Author: Russel Rafanan
Editor: Jessica Ng
Enhanced by: Claude

A Python-based word guessing game inspired by Wordle, featuring a programming-themed
word list, timer, and GIF feedback system.
"""

import pygame
import random
from PIL import Image
import os

# Initialize Pygame engine
pygame.init()

# Screen and game constants
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
GRID_SIZE = 6
WORD_LENGTH = 5
FONT_SIZE = 50
BOX_SIZE = 100
BOX_SPACING = 15
BOX_BORDER_RADIUS = 5

# Feedback position constants
FEEDBACK_X = SCREEN_WIDTH - 420
FEEDBACK_Y = SCREEN_HEIGHT // 2 - 300

# Color scheme definitions
BACKGROUND_COLOR = (18, 18, 19)
EMPTY_BOX_COLOR = (58, 58, 60)
BORDER_COLOR = (58, 58, 60)
FILLED_BOX_COLOR = (58, 58, 60)
GREEN = (83, 141, 78)
YELLOW = (181, 159, 59)
GRAY = (58, 58, 60)
TEXT_COLOR = (255, 255, 255)

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

class GifPlayer:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.frame_duration = 100  # Default duration between frames in ms
        
        # Load GIF frames using Pillow
        gif = Image.open(gif_path)
        try:
            while True:
                frame = gif.copy()
                frame = pygame.image.fromstring(
                    frame.convert('RGBA').tobytes(), frame.size, 'RGBA')
                self.frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_current_frame(self):
        return self.frames[self.current_frame]

class FeedbackSystem:
    def __init__(self):
        self.gifs = {
            'welcome': GifPlayer('Minigame2/Russ Welcome.gif'),
            'instructions': GifPlayer('Minigame2/Russ Instructions.gif'),
            'time': GifPlayer('Minigame2/Russ Time.gif'),
            'short': GifPlayer('Minigame2/Russ Short.gif'),
            'won': GifPlayer('Minigame2/Russ Won.gif'),
            'lost': GifPlayer('Minigame2/Russ Lost.gif')
        }
        self.current_gif = None
        self.display_time = 0

    def show_gif(self, gif_name, duration=3000):
        self.current_gif = self.gifs[gif_name]
        self.display_time = pygame.time.get_ticks() + duration

    def update(self, screen):
        if self.current_gif and pygame.time.get_ticks() < self.display_time:
            self.current_gif.update()
            frame = self.current_gif.get_current_frame()
            screen.blit(frame, (FEEDBACK_X, FEEDBACK_Y))

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.is_running = True
        self.thirty_second_warning_shown = False

    def get_time_left(self):
        if not self.is_running:
            return 0
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        remaining = max(0, self.duration - elapsed)
        return remaining

    def is_finished(self):
        return self.get_time_left() <= 0

    def stop(self):
        self.is_running = False

    def draw(self, screen, font):
        if self.is_running:
            seconds_left = self.get_time_left()
            minutes = seconds_left // 60
            seconds = seconds_left % 60
            time_text = f"{minutes}:{seconds:02d}"
            text_surface = font.render(time_text, True, TEXT_COLOR)
            screen.blit(text_surface, (20, 20))

    def should_show_warning(self):
        seconds_left = self.get_time_left()
        if seconds_left <= 30 and not self.thirty_second_warning_shown:
            self.thirty_second_warning_shown = True
            return True
        return False

def draw_box(screen, game_font, x, y, color, letter='', border_color=None):
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

def draw_grid(screen, game_font, guesses, current_guess, secret_word):
    """Render the game grid with all guesses and current input"""
    start_x = (SCREEN_WIDTH - (WORD_LENGTH * (BOX_SIZE + BOX_SPACING))) // 2
    start_y = 175

    # Draw previous guesses
    for i in range(GRID_SIZE):
        for j in range(WORD_LENGTH):
            x = start_x + j * (BOX_SIZE + BOX_SPACING)
            y = start_y + i * (BOX_SIZE + BOX_SPACING)

            if i < len(guesses):
                letter = guesses[i][j]
                colors = get_letter_colors(guesses[i], secret_word)
                draw_box(screen, game_font, x, y, colors[j], letter)
            else:
                draw_box(screen, game_font, x, y, BACKGROUND_COLOR, border_color=BORDER_COLOR)

    # Draw current guess
    current_row = len(guesses)
    if current_row < GRID_SIZE:
        for j in range(WORD_LENGTH):
            x = start_x + j * (BOX_SIZE + BOX_SPACING)
            y = start_y + current_row * (BOX_SIZE + BOX_SPACING)
            if j < len(current_guess):
                draw_box(screen, game_font, x, y, FILLED_BOX_COLOR, current_guess[j])
            else:
                draw_box(screen, game_font, x, y, BACKGROUND_COLOR, border_color=BORDER_COLOR)

def main():
    # Initialize display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Wordle")

    # Load custom font and background
    game_font = pygame.font.Font('Minigame2/PRESSSTART2P.ttf', FONT_SIZE)
    background_image = pygame.image.load("Minigame2/Palak Minigame (7).png")
    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    # Initialize game components
    secret_word = random.choice(word_list)
    timer = Timer(90)  # 90 seconds = 1 minute and 30 seconds
    feedback = FeedbackSystem()
    
    running = True
    guesses = []
    current_guess = ""
    game_over = False
    won = False
    
    # Show welcome and instructions at start
    feedback.show_gif('welcome', 3000)
    feedback.show_gif('instructions', 3000)

    while running:
        screen.blit(background_image, (0, 0))
        draw_grid(screen, game_font, guesses, current_guess, secret_word)
        timer.draw(screen, game_font)
        feedback.update(screen)

        # Check timer warning
        if timer.should_show_warning():
            feedback.show_gif('time')

        # Check timer finished
        if timer.is_finished() and not game_over:
            game_over = True
            feedback.show_gif('lost')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_SPACE:
                        # Reset game state
                        secret_word = random.choice(word_list)
                        timer = Timer(90)
                        guesses = []
                        current_guess = ""
                        game_over = False
                        won = False
                        feedback.show_gif('welcome')
                elif event.key == pygame.K_RETURN:
                    if len(current_guess) < WORD_LENGTH:
                        feedback.show_gif('short')
                    elif len(current_guess) == WORD_LENGTH:
                        guesses.append(current_guess)
                        if current_guess == secret_word:
                            won = True
                            game_over = True
                            timer.stop()
                            feedback.show_gif('won')
                        elif len(guesses) >= GRID_SIZE:
                            game_over = True
                            timer.stop()
                            feedback.show_gif('lost')
                        current_guess = ""
                elif event.key == pygame.K_BACKSPACE:
                    current_guess = current_guess[:-1]
                elif len(current_guess) < WORD_LENGTH and event.unicode.isalpha():
                    current_guess += event.unicode.upper()

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()