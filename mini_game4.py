"""
mini-game4.py

Primary Author: Jessica Ng
Enhanced by: Claude

An educational puzzle game that combines Python programming knowledge with visual
tile-based mechanics, featuring enhanced visuals and feedback systems.
"""

import pygame
import sys
import time
import random
import math
import os
from os.path import join
from PIL import Image

# Programming quiz questions
questions = [
    ("What keyword is used to define a function in Python?", "def"),
    ("What built-in Python function is used to get the length of a list?", "len"),
    ("What data type is used to store whole numbers?", "integer"),
    ("What method is used to add an item to the end of a list?", "append"),
    ("Which operator is used for exponentiation?", "**"),
    ("What function prints text to the screen?", "print"),
    ("What is the result of 10 // 3?", "3"),
    ("Which data type represents decimal numbers?", "float"),
    ("Which Python data type is an ordered, immutable sequence of characters?", "string"),
    ("What keyword is used to define a class in Python?", "class"),
    ("What method converts a string to lowercase?", "lower"),
    ("What is the boolean value for an empty list?", "false"),
    ("What function returns the absolute value of a number?", "abs"),
    ("What method removes whitespace from both ends of a string?", "strip"),
    ("What operator is used for string concatenation?", "+"),
    ("What keyword is used to exit a loop prematurely?", "break"),
    ("What method splits a string into a list?", "split"),
    ("What is the result of type([]) in Python?", "list"),
    ("What method returns a sorted version of a list?", "sorted"),
    ("What function converts a string to an integer?", "int"),
    ("What symbol starts a single-line comment in Python?", "#"),
    ("What method checks if a string contains only digits?", "isdigit"),
    ("What operator checks if two values are identical in memory?", "is"),
    ("What method converts all string characters to uppercase?", "upper"),
    ("What keyword is used to handle exceptions?", "try"),
    ("What method removes an item from a list by index?", "pop"),
    ("What function returns the maximum value in an iterable?", "max"),
    ("What method joins list elements into a string?", "join"),
    ("What keyword creates a function that yields values?", "yield"),
    ("What built-in function reverses an iterator?", "reversed"),
    ("What method checks if a string starts with a substring?", "startswith"),
    ("What function returns a random float between 0 and 1?", "random"),
    ("What keyword is used to import specific items from a module?", "from"),
    ("What method returns the index of an item in a list?", "index"),
    ("What function creates a range of numbers?", "range"),
    ("What method checks if a string ends with a substring?", "endswith"),
    ("What operator unpacks an iterable into individual elements?", "*"),
    ("What function returns the sum of an iterable?", "sum"),
    ("What method counts occurrences in a string or list?", "count"),
]

class GameConfig:
    # Display settings
    SCREEN_WIDTH = 1539
    SCREEN_HEIGHT = 940
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GOLD = (255, 215, 0)
    BLUE = (0, 0, 139)
    
    # Fonts
    FONT_SIZES = {
        'small': 18,
        'normal': 24,
        'medium': 28,
        'large': 36
    }
    
    # Feedback position
    FEEDBACK_X = SCREEN_WIDTH - 420
    FEEDBACK_Y = SCREEN_HEIGHT // 2 - 400
    
    # Game settings
    TILE_SIZE = 200
    TILE_SPACING = 220
    GAME_DURATION = 180
    WORD_LENGTH = 6
    CORRECT_WORD = "PYTHON"

class ResourceLoader:
    @staticmethod
    def load_image(path, size=None, fallback_color=(100, 100, 100)):
        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            return image
        except Exception as e:
            print(f"Failed to load image {path}: {e}")
            surface = pygame.Surface(size or (200, 200), pygame.SRCALPHA)
            pygame.draw.rect(surface, fallback_color, surface.get_rect())
            return surface

    @staticmethod
    def load_font(path, size, fallback_name=None):
        try:
            return pygame.font.Font(path, size)
        except Exception as e:
            print(f"Failed to load font {path}: {e}")
            return pygame.font.SysFont(fallback_name or None, size)

    @staticmethod
    def create_gradient_background(width, height):
        surface = pygame.Surface((width, height))
        for i in range(height):
            color = (
                min(255, 20 + i * 0.1),
                min(255, 30 + i * 0.1),
                min(255, 50 + i * 0.1)
            )
            pygame.draw.line(surface, color, (0, i), (width, i))
        return surface

class GifPlayer:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.frame_duration = 30
        
        try:
            gif = Image.open(gif_path)
            while True:
                frame = gif.copy()
                frame = pygame.image.fromstring(
                    frame.convert('RGBA').tobytes(), frame.size, 'RGBA'
                ).convert_alpha()
                self.frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"Error loading gif {gif_path}: {e}")
            fallback = pygame.Surface((200, 200), pygame.SRCALPHA)
            pygame.draw.rect(fallback, (100, 100, 100, 128), fallback.get_rect())
            self.frames = [fallback]

    def update(self):
        if not self.frames:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update > self.frame_duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time

    def get_current_frame(self):
        if not self.frames:
            return None
        return self.frames[self.current_frame]

class FeedbackSystem:
    def __init__(self):
        self.gifs = {
            'welcome': GifPlayer('Minigame4/Jess Welcome.gif'),
            'instructions': GifPlayer('Minigame4/Jess Instructions.gif'),
            'time': GifPlayer('Minigame4/Jess Time.gif'),
            '6initial': GifPlayer('Minigame4/Jess 6Initial.gif'),
            '3initial': GifPlayer('Minigame4/Jess 3Initial.gif'),
            'decode': GifPlayer('Minigame4/Jess Decode.gif'),
            'win': GifPlayer('Minigame4/Jess Win.gif'),
            'lost': GifPlayer('Minigame4/Jess Lost.gif')
        }
        self.current_gif = None
        self.display_time = 0
        self.last_gif = None

    def show_gif(self, gif_name, duration=5000):
        self.current_gif = self.gifs.get(gif_name)
        if self.current_gif:
            self.display_time = pygame.time.get_ticks() + duration
            self.last_gif = gif_name

    def is_playing(self):
        return pygame.time.get_ticks() < self.display_time

    def update(self, screen):
        if self.current_gif and pygame.time.get_ticks() < self.display_time:
            self.current_gif.update()
            frame = self.current_gif.get_current_frame()
            if frame:
                screen.blit(frame, (GameConfig.FEEDBACK_X, GameConfig.FEEDBACK_Y))

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.is_running = True
        self.one_minute_warning_shown = False
        self.paused_time = 0
        self.is_paused = False

    def pause(self):
        if not self.is_paused:
            self.is_paused = True
            self.paused_time = pygame.time.get_ticks()

    def unpause(self):
        if self.is_paused:
            self.is_paused = False
            pause_duration = pygame.time.get_ticks() - self.paused_time
            self.start_time += pause_duration

    def get_time_left(self):
        if not self.is_running:
            return 0
        if self.is_paused:
            elapsed = self.paused_time - self.start_time
        else:
            elapsed = pygame.time.get_ticks() - self.start_time
        remaining = max(0, self.duration * 1000 - elapsed) // 1000
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
            text_surface = font.render(time_text, True, GameConfig.WHITE)
            screen.blit(text_surface, (20, 20))

    def should_show_warning(self):
        seconds_left = self.get_time_left()
        if seconds_left <= 60 and not self.one_minute_warning_shown:
            self.one_minute_warning_shown = True
            return True
        return False

class Tile:
    def __init__(self, x, y, number, final_image, initial_image):
        self.original_rect = pygame.Rect(x, y, GameConfig.TILE_SIZE, GameConfig.TILE_SIZE)
        self.rect = self.original_rect.copy()
        self.number = number
        self.question = None
        self.answer = None
        self.solved = False
        
        # Animation properties
        self.pressing = False
        self.press_scale = 1.0
        self.press_duration = 300
        self.press_start_time = 0
        self.question_ready = False
        self.flash_alpha = 0
        self.flash_wrong = False
        self.flash_wrong_start = 0
        self.flash_duration = 500
        self.flash_color = GameConfig.RED
        
        # Visual effects
        self.victory_glow = False
        self.victory_glow_start = 0
        self.victory_glow_duration = 1000
        self.victory_glow_color = GameConfig.GOLD
        
        # Border properties
        self.border_thickness = 4
        self.border_color = GameConfig.GOLD
        self.border_radius = 10
        
        # Images
        self.final_image = final_image
        self.initial_image = initial_image
        self.show_in_question_phase = True
        
        # State
        self.moved_to_top = False
        self.final_position = None

    def start_press_animation(self):
        if not self.pressing:
            self.pressing = True
            self.press_start_time = pygame.time.get_ticks()
            self.press_scale = 1.0

    def start_wrong_flash(self):
        self.flash_wrong = True
        self.flash_wrong_start = pygame.time.get_ticks()

    def start_victory_glow(self):
        self.victory_glow = True
        self.victory_glow_start = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update press animation
        if self.pressing:
            elapsed = current_time - self.press_start_time
            if elapsed < self.press_duration / 2:
                self.press_scale = 1.0 + (elapsed / (self.press_duration / 2)) * 0.1
            elif elapsed < self.press_duration:
                progress = (elapsed - self.press_duration / 2) / (self.press_duration / 2)
                self.press_scale = 1.1 - progress * 0.1
            else:
                self.pressing = False
                self.press_scale = 1.0
                self.question_ready = True
                self.flash_alpha = 255

        # Update flash
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 10)

        if self.flash_wrong:
            elapsed = current_time - self.flash_wrong_start
            if elapsed >= self.flash_duration:
                self.flash_wrong = False

        # Update victory glow
        if self.victory_glow:
            elapsed = current_time - self.victory_glow_start
            if elapsed >= self.victory_glow_duration:
                self.victory_glow = False

    def draw_with_border(self, surface, image, rect):
        """Draw tile with border effect"""
        # Draw border
        border_rect = rect.inflate(self.border_thickness * 2, self.border_thickness * 2)
        pygame.draw.rect(surface, self.border_color, border_rect, border_radius=self.border_radius)
        # Draw tile image
        surface.blit(image, rect)

    def draw(self, surface, show_tiles=True):
        """Draw tile with all effects"""
        if not show_tiles or not self.show_in_question_phase:
            return
            
        if not self.question_ready or self.solved:
            if self.pressing:
                # Draw pressed state
                scaled_width = int(self.rect.width * self.press_scale)
                scaled_height = int(self.rect.height * self.press_scale)
                scaled_image = pygame.transform.scale(
                    self.initial_image if not self.solved else self.final_image,
                    (scaled_width, scaled_height)
                )
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                
                if self.solved:
                    self.draw_with_border(surface, scaled_image, scaled_rect)
                else:
                    surface.blit(scaled_image, scaled_rect)
            else:
                if self.solved:
                    # Draw solved state with effects
                    self.draw_with_border(surface, self.final_image, self.rect)
                    
                    if self.victory_glow:
                        self.draw_victory_glow(surface)
                else:
                    # Draw normal state
                    surface.blit(self.initial_image, self.rect)

    def draw_victory_glow(self, surface):
        """Draw victory glow effect"""
        elapsed = pygame.time.get_ticks() - self.victory_glow_start
        progress = elapsed / self.victory_glow_duration
        glow_alpha = int(255 * (1 - progress))
        
        glow_size = int(20 * (1 + progress))
        glow_surface = pygame.Surface(
            (self.rect.width + glow_size * 2, 
             self.rect.height + glow_size * 2), 
            pygame.SRCALPHA
        )
        
        for i in range(3):
            current_alpha = min(255, glow_alpha // (i + 1))
            pygame.draw.rect(
                glow_surface,
                (*self.victory_glow_color, current_alpha),
                (i * 5, i * 5, 
                 glow_surface.get_width() - i * 10,
                 glow_surface.get_height() - i * 10),
                border_radius=10
            )
        
        glow_rect = glow_surface.get_rect(center=self.rect.center)
        surface.blit(glow_surface, glow_rect)

class Game:
    def __init__(self):
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
        
        # Set up display
        self.screen = pygame.display.set_mode((GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        pygame.display.set_caption("D'Code and Build")

        # Load resources
        self.load_resources()
        
        # Initialize game state
        self.reset_game()
        self.clock = pygame.time.Clock()

    def load_resources(self):
        """Load all game resources"""
        # Load fonts
        self.fonts = {}
        for size_name, size in GameConfig.FONT_SIZES.items():
            try:
                self.fonts[size_name] = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', size)
            except:
                print(f"Failed to load font for size {size_name}")
                self.fonts[size_name] = pygame.font.SysFont(None, size)
        
        # Load background
        try:
            self.background = pygame.image.load(join('Minigame4', 'Jessica Background.png')).convert()
            self.background = pygame.transform.scale(self.background, 
                (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT))
        except:
            self.background = ResourceLoader.create_gradient_background(
                GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT)
        
        # Load tile images
        self.tile_images = []
        self.initial_tile_images = []
        for i in range(9):
            try:
                tile_img = pygame.image.load(join('Minigame4', f'Python_{i+1}.png')).convert_alpha()
                initial_img = pygame.image.load(join('Minigame4', f'initial_tile_{i+1}.png')).convert_alpha()
                
                tile_img = pygame.transform.scale(tile_img, (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
                initial_img = pygame.transform.scale(initial_img, (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
                
                self.tile_images.append(tile_img)
                self.initial_tile_images.append(initial_img)
            except:
                print(f"Failed to load tile images for tile {i+1}")
                fallback = pygame.Surface((GameConfig.TILE_SIZE, GameConfig.TILE_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(fallback, (100, 100, 100, 255), fallback.get_rect())
                self.tile_images.append(fallback)
                self.initial_tile_images.append(fallback)

        # Load complete Python image
        try:
            self.complete_python_img = pygame.image.load(join('Minigame4', 'complete_python.png')).convert_alpha()
            self.complete_python_img = pygame.transform.scale(self.complete_python_img, 
                (GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
        except:
            self.complete_python_img = pygame.Surface((GameConfig.TILE_SIZE, GameConfig.TILE_SIZE))
            pygame.draw.rect(self.complete_python_img, (100, 100, 100), self.complete_python_img.get_rect())

    def reset_game(self):
        """Reset game state"""
        self.questions_copy = questions.copy()
        random.shuffle(self.questions_copy)
        
        # Create tiles
        self.tiles = [
            Tile(GameConfig.SCREEN_WIDTH // 2 - 300 + (i % 3) * GameConfig.TILE_SPACING,
                 GameConfig.SCREEN_HEIGHT // 2 - 250 + (i // 3) * GameConfig.TILE_SPACING,
                 i + 1, 
                 self.tile_images[i],
                 self.initial_tile_images[i])
            for i in range(9)
        ]
        
        # Initialize game components
        self.timer = Timer(GameConfig.GAME_DURATION)
        self.feedback = FeedbackSystem()
        
        # Reset state variables
        self.user_input = ""
        self.selected_tile = None
        self.answer_input = ""
        self.end_game_started = False
        self.final_answer = ""
        self.final_answer_correct = False
        self.game_complete = False
        self.blank_spaces = ["_"] * GameConfig.WORD_LENGTH
        self.restart_pending = False
        self.restart_time = 0
        
        # Show initial feedback
        self.feedback.show_gif('welcome', 5000)
        self.feedback.show_gif('instructions', 5000)

    def cleanup(self):
        """Clean up game resources"""
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
                    
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # Handle game completion and restart
                if event.key == pygame.K_SPACE and self.game_complete:
                    return self.final_answer_correct

                # Handle normal gameplay
                if not self.end_game_started and not self.timer.is_finished():
                    if event.key == pygame.K_RETURN:
                        if not self.selected_tile:
                            if not self.handle_tile_selection():
                                return False
                        else:
                            if not self.handle_answer_submission():
                                return False
                    elif event.key == pygame.K_BACKSPACE:
                        if self.selected_tile and self.selected_tile.question_ready:
                            self.answer_input = self.answer_input[:-1]
                        else:
                            self.user_input = self.user_input[:-1]
                    elif event.unicode.isprintable():
                        if self.selected_tile and self.selected_tile.question_ready:
                            self.handle_answer_input(event.unicode)
                        else:
                            self.user_input += event.unicode
                # Handle final phase input
                elif not self.game_complete:
                    if not self.handle_final_input(event):
                        return False

        return None

    def handle_tile_selection(self):
        """Handle selecting a tile based on user input"""
        if self.user_input.isdigit() and 1 <= int(self.user_input) <= 9:
            tile_num = int(self.user_input)
            if self.questions_copy:
                for tile in self.tiles:
                    if tile.number == tile_num and not tile.solved:
                        self.selected_tile = tile
                        tile.start_press_animation()
                        tile.question, tile.answer = self.questions_copy.pop()
                        break
            self.user_input = ""
        return True

    def handle_answer_submission(self):
        """Handle submitting an answer for the current tile"""
        if self.answer_input.lower() == "jessica" or self.answer_input.lower() == self.selected_tile.answer.lower():
            self.selected_tile.solved = True
            self.selected_tile.start_victory_glow()
            self.selected_tile.question_ready = False
            
            unsolved_count = sum(1 for tile in self.tiles if not tile.solved)
            if unsolved_count == 6:
                self.feedback.show_gif('6initial', 5000)
            elif unsolved_count == 3:
                self.feedback.show_gif('3initial', 5000)
            elif unsolved_count == 0:
                self.feedback.show_gif('decode', 5000)
                self.end_game_started = True
                
            self.selected_tile = None
            self.answer_input = ""
        else:
            self.selected_tile.start_wrong_flash()
            self.selected_tile.question_ready = False
            self.selected_tile = None
            self.answer_input = ""
        return True

    def handle_answer_input(self, char):
        """Handle input for the answer textbox"""
        test_text = self.answer_input + char
        test_surface = self.fonts['small'].render(test_text, True, (0, 0, 0))
        if test_surface.get_width() <= 360:
            self.answer_input += char

    def handle_final_input(self, event):
        """Handle input during the final phase"""
        if event.key == pygame.K_RETURN:
            if self.final_answer.upper() == GameConfig.CORRECT_WORD:
                self.final_answer_correct = True
                self.game_complete = True
                self.feedback.show_gif('win', 5000)
            else:
                for tile in self.tiles:
                    tile.start_wrong_flash()
                self.final_answer = ""
                self.blank_spaces = ["_"] * GameConfig.WORD_LENGTH
        elif event.key == pygame.K_BACKSPACE:
            if self.final_answer:
                self.final_answer = self.final_answer[:-1]
                self.blank_spaces[len(self.final_answer)] = "_"
        elif event.unicode.isalpha() and len(self.final_answer) < GameConfig.WORD_LENGTH:
            self.final_answer += event.unicode.upper()
            self.blank_spaces[len(self.final_answer)-1] = event.unicode.upper()
        return True

    def draw_gameplay(self):
        """Draw the main gameplay state"""
        show_other_tiles = not (self.selected_tile and self.selected_tile.question_ready)
        
        # Draw tiles
        for tile in self.tiles:
            tile.update()
            if self.selected_tile and self.selected_tile.question_ready:
                tile.show_in_question_phase = (tile == self.selected_tile)
            else:
                tile.show_in_question_phase = True
            tile.draw(self.screen)

        if not self.selected_tile or not self.selected_tile.question_ready:
            self.draw_number_prompt()
        elif self.selected_tile and self.selected_tile.question_ready:
            self.draw_question()

    def draw_number_prompt(self):
        """Draw the number input prompt"""
        prompt_surface = self.fonts['normal'].render("Enter a number (1-9):", True, GameConfig.WHITE)
        prompt_rect = prompt_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 - 350))
        self.screen.blit(prompt_surface, prompt_rect)

        input_surface = self.fonts['normal'].render(self.user_input, True, GameConfig.WHITE)
        input_rect = input_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 - 300))
        self.screen.blit(input_surface, input_rect)

    def draw_question(self):
        """Draw the current question and answer input"""
        words = self.selected_tile.question.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 40:
                lines.append(' '.join(current_line[:-1]))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        y_offset = GameConfig.SCREEN_HEIGHT // 2 - 250
        for line in lines:
            question_surface = self.fonts['small'].render(line, True, GameConfig.WHITE)
            question_rect = question_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(question_surface, question_rect)
            y_offset += 40

        self.draw_answer_box()

    def draw_answer_box(self):
        """Draw the answer input box"""
        box_width = 400
        box_height = 50
        box_x = GameConfig.SCREEN_WIDTH // 2 - box_width // 2
        box_y = GameConfig.SCREEN_HEIGHT // 2 + 30
        
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, (255, 255, 255, 128), (0, 0, box_width, box_height), border_radius=10)
        pygame.draw.rect(box_surface, GameConfig.BLUE, (0, 0, box_width, box_height), width=2, border_radius=10)
        
        self.screen.blit(box_surface, (box_x, box_y))

        answer_surface = self.fonts['small'].render(self.answer_input, True, GameConfig.WHITE)
        answer_rect = answer_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(answer_surface, answer_rect)

    def draw_final_phase(self):
        """Draw the final phase of the game"""
        if not self.final_answer_correct:
            prompt_surface = self.fonts['medium'].render("Decode the picture!", True, GameConfig.WHITE)
            prompt_rect = prompt_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 - 200))
            self.screen.blit(prompt_surface, prompt_rect)

            python_rect = self.complete_python_img.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2))
            border_rect = python_rect.inflate(8, 8)
            pygame.draw.rect(self.screen, GameConfig.GOLD, border_rect, border_radius=10)
            self.screen.blit(self.complete_python_img, python_rect)

            blank_surface = self.fonts['large'].render(" ".join(self.blank_spaces), True, GameConfig.WHITE)
            blank_rect = blank_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 + 200))
            self.screen.blit(blank_surface, blank_rect)
        else:
            win_surface = self.fonts['large'].render("Congratulations!", True, GameConfig.WHITE)
            win_rect = win_surface.get_rect(center=(GameConfig.SCREEN_WIDTH // 2, GameConfig.SCREEN_HEIGHT // 2 - 100))
            self.screen.blit(win_surface, win_rect)

    def run(self):
        """Main game loop"""
        running = True
        while running:
            self.clock.tick(60)
            current_time = pygame.time.get_ticks()
            
            # Draw background
            self.screen.blit(self.background, (0, 0))
            
            # Update timer
            if not self.game_complete:
                self.timer.draw(self.screen, self.fonts['normal'])
                
                # Check timer status
                if self.timer.is_finished():
                    self.game_complete = True
                    self.feedback.show_gif('lost', 5000)
                    self.restart_pending = True
                    self.restart_time = current_time + 5000

            # Check for restart
            if self.restart_pending and current_time >= self.restart_time:
                self.reset_game()
                self.restart_pending = False
            
            # Show timer warning
            if self.timer.should_show_warning():
                self.feedback.show_gif('time', 5000)

            # Handle events
            result = self.handle_events()
            if result is not None:  # None means continue game, True/False means exit
                self.cleanup()
                return result

            # Draw game state
            if not self.end_game_started:
                self.draw_gameplay()
            else:
                self.draw_final_phase()

            # Draw feedback
            self.feedback.update(self.screen)
            
            # Update display
            pygame.display.flip()

        self.cleanup()
        return self.final_answer_correct

def main():
    """Main function with proper error handling"""
    try:
        # Initialize pygame if needed
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, 2, 512)
            except pygame.error:
                print("Warning: Could not initialize sound mixer")
        
        # Store original directory
        original_dir = os.getcwd()
        
        try:
            # Create and run game
            game = Game()
            result = game.run()
            game.cleanup()
            
            # Restore original directory
            os.chdir(original_dir)
            
            return result
            
        except Exception as e:
            print(f"Error during game execution: {e}")
            if pygame.mixer.get_init():
                pygame.mixer.stop()
            os.chdir(original_dir)
            return False
            
    except Exception as e:
        print(f"Error in main: {e}")
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        return False

if __name__ == "__main__":
    main()