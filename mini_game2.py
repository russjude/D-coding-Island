"""
mini-game2.py

Primary Author: Russel Rafanan
Editor: Jessica Ng
Enhanced by: Claude

A Python-based word guessing game inspired by Wordle, featuring a programming-themed
word list, timer, and GIF feedback system with improved transitions.
"""

import pygame
import random
from PIL import Image
import os
import sys
import time

pygame.init()

# Screen and game constants
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
GRID_SIZE = 6
WORD_LENGTH = 5
FONT_SIZE = 50
ANSWER_FONT_SIZE = 40
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

# Programming-themed word bank plus master word
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
    "PROTO", "RESET", "ROUND", "SCALE", "THROW",
    "RUSSS"  # Master word for instant win
]

class GifPlayer:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.frame_duration = 30
        self.is_complete = False
        
        try:
            gif = Image.open(gif_path)
            try:
                while True:
                    frame = gif.copy()
                    frame = frame.resize((400, 400), Image.Resampling.LANCZOS)
                    frame = pygame.image.fromstring(
                        frame.convert('RGBA').tobytes(), frame.size, 'RGBA'
                    ).convert_alpha()
                    self.frames.append(frame)
                    gif.seek(gif.tell() + 1)
            except EOFError:
                pass
        except Exception as e:
            print(f"Error loading GIF {gif_path}: {e}", file=sys.stderr)
            surface = pygame.Surface((400, 400))
            surface.fill((255, 0, 0))
            self.frames = [surface]

    def update(self):
        current_time = pygame.time.get_ticks()
        if not self.is_complete and current_time - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
            if self.current_frame == 0:
                self.is_complete = True

    def get_current_frame(self):
        return self.frames[self.current_frame]

    def reset(self):
        self.current_frame = 0
        self.last_update = 0
        self.is_complete = False

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
        self.gif_queue = []
        self.showing_answer = False
        self.answer_start_time = 0
        self.lost_gif_complete = False
        self.won_gif_complete = False
        self.answer_display_duration = 2000
        try:
            self.answer_font = pygame.font.Font('Minigame2/PRESSSTART2P.ttf', ANSWER_FONT_SIZE)
        except:
            print("Error loading font, using system font")
            self.answer_font = pygame.font.SysFont(None, ANSWER_FONT_SIZE)

    def show_gif(self, gif_name):
        if gif_name not in [g[0] for g in self.gif_queue]:
            self.gifs[gif_name].reset()
            self.gif_queue.append((gif_name, None))

    def update(self, screen, secret_word=None, game_font=None):
        current_time = pygame.time.get_ticks()
        
        if self.won_gif_complete:
            pygame.time.wait(1000)
            return True

        if self.showing_answer and secret_word:
            start_y = 175
            grid_height = GRID_SIZE * (BOX_SIZE + BOX_SPACING)
            answer_y = start_y + grid_height + 30
            
            answer_text = f"The word was: {secret_word}"
            text_surface = self.answer_font.render(answer_text, True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, answer_y))
            screen.blit(text_surface, text_rect)
            
            if self.lost_gif_complete and current_time - self.answer_start_time > self.answer_display_duration:
                return 'restart'
        
        if self.gif_queue:
            gif_name, _ = self.gif_queue[0]
            current_gif = self.gifs[gif_name]
            current_gif.update()
            frame = current_gif.get_current_frame()
            screen.blit(frame, (FEEDBACK_X, FEEDBACK_Y))
            
            if current_gif.is_complete:
                self.gif_queue.pop(0)
                
                if gif_name == 'lost':
                    self.showing_answer = True
                    self.answer_start_time = current_time
                    self.lost_gif_complete = True
                elif gif_name == 'won':
                    self.won_gif_complete = True
        
        return False

    def reset(self):
        self.showing_answer = False
        self.lost_gif_complete = False
        self.won_gif_complete = False
        self.gif_queue = []
        for gif in self.gifs.values():
            gif.reset()

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

class Game:
    def __init__(self):
        # Don't reinitialize pygame, just verify/restore display if needed
        if not pygame.get_init() or not pygame.display.get_surface():
            pygame.init()
            
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, 2, 512)
            except pygame.error:
                print("Warning: Could not initialize sound mixer")
        
        # Store original display settings
        self.original_resolution = None
        self.was_fullscreen = False
        if pygame.display.get_surface():
            self.original_resolution = pygame.display.get_surface().get_size()
            self.was_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
        
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Decoding Island - Word Puzzle")

        # Load resources
        try:
            self.game_font = pygame.font.Font('Minigame2/PRESSSTART2P.ttf', FONT_SIZE)
            self.background_image = pygame.image.load("Minigame2/Palak Minigame (7).png")
            self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading resources: {e}")
            self.game_font = pygame.font.SysFont('Arial', FONT_SIZE)
            self.background_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background_image.fill(BACKGROUND_COLOR)

        # Initialize game components
        self.feedback = FeedbackSystem()
        self.reset_game_state()

    def reset_game_state(self):
        """Reset all game-specific state variables"""
        self.secret_word = random.choice(word_list)
        self.timer = Timer(90)
        self.guesses = []
        self.current_guess = ""
        self.game_over = False
        self.won = False
        self.feedback.reset()
        self.feedback.show_gif('welcome')
        self.feedback.show_gif('instructions')

    def cleanup(self):
        """Safe cleanup that preserves pygame instance"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.stop()
            
            # Restore original display mode if needed
            if self.original_resolution:
                try:
                    if self.was_fullscreen:
                        pygame.display.set_mode(self.original_resolution, pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode(self.original_resolution)
                except pygame.error:
                    print("Warning: Could not restore original display mode")
            
            # Reset game state
            self.reset_game_state()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def handle_win(self):
        """Handle win condition"""
        if not pygame.display.get_surface():
            return False
            
        self.game_over = True
        self.won = True
        self.timer.stop()
        self.feedback.show_gif('won')
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            if not pygame.display.get_surface():
                return False
                
            self.screen.blit(self.background_image, (0, 0))
            draw_grid(self.screen, self.game_font, self.guesses, self.current_guess, self.secret_word)
            self.feedback.update(self.screen, self.secret_word, self.game_font)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
        return True

    def handle_lose(self):
        """Handle loss condition"""
        if not pygame.display.get_surface():
            return False
            
        self.game_over = True
        self.timer.stop()
        self.feedback.show_gif('lost')
        
        start_time = time.time()
        while time.time() - start_time < 2.0:
            if not pygame.display.get_surface():
                return False
                
            self.screen.blit(self.background_image, (0, 0))
            draw_grid(self.screen, self.game_font, self.guesses, self.current_guess, self.secret_word)
            self.feedback.update(self.screen, self.secret_word, self.game_font)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
        return 'restart'

    def run(self):
            """Main game loop with proper error handling"""
            if not pygame.display.get_surface():
                return False
                
            clock = pygame.time.Clock()
            running = True

            try:
                while running:
                    if not pygame.display.get_surface():
                        self.cleanup()
                        return False
                    
                    self.screen.blit(self.background_image, (0, 0))
                    draw_grid(self.screen, self.game_font, self.guesses, self.current_guess, self.secret_word)
                    self.timer.draw(self.screen, self.game_font)
                    
                    should_restart = self.feedback.update(self.screen, self.secret_word, self.game_font)
                    if should_restart == 'restart':
                        self.reset_game_state()
                        continue
                    elif should_restart:  # True means win condition
                        return True
                    
                    if self.timer.should_show_warning():
                        self.feedback.show_gif('time')
                    
                    if self.timer.is_finished() and not self.game_over:
                        if self.handle_lose() == 'restart':
                            self.reset_game_state()
                            continue

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            break
                            
                        if event.type == pygame.KEYDOWN and not self.game_over:
                            if event.key == pygame.K_RETURN:
                                if len(self.current_guess) < WORD_LENGTH:
                                    self.feedback.show_gif('short')
                                elif len(self.current_guess) == WORD_LENGTH:
                                    current_word = self.current_guess.upper()
                                    
                                    # Check for win condition before appending
                                    if current_word == self.secret_word or current_word == "RUSSS":
                                        self.guesses.append(current_word)
                                        self.current_guess = ""  # Clear immediately
                                        if self.handle_win():
                                            return True
                                        return False
                                    
                                    # Handle normal guesses
                                    self.guesses.append(current_word)
                                    if len(self.guesses) >= GRID_SIZE:
                                        if self.handle_lose() == 'restart':
                                            self.reset_game_state()
                                    self.current_guess = ""
                                            
                            elif event.key == pygame.K_BACKSPACE:
                                self.current_guess = self.current_guess[:-1]
                            elif len(self.current_guess) < WORD_LENGTH and event.unicode.isalpha():
                                self.current_guess += event.unicode.upper()

                    pygame.display.flip()
                    clock.tick(60)

            except Exception as e:
                print(f"Error in game loop: {e}")
                return False
            finally:
                self.cleanup()
            
            return self.won

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
    # Special case for RUSSS - all green
    if guess == "RUSSS":
        return [GREEN] * WORD_LENGTH
        
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
    """Main function with proper error handling"""
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, 2, 512)
            except pygame.error:
                print("Warning: Could not initialize sound mixer")
        
        game = Game()
        result = game.run()
        game.cleanup()
        return result
        
    except Exception as e:
        print(f"Error in main: {e}")
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        return False

if __name__ == "__main__":
    main()