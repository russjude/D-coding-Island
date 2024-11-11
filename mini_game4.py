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
from os.path import join
from PIL import Image

# Initialize game engine
pygame.init()

# Display configuration
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# Feedback position constants
FEEDBACK_X = SCREEN_WIDTH - 420
FEEDBACK_Y = SCREEN_HEIGHT // 2 - 400

# Set up display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D'Code and Build")

# Initialize fonts
game_font = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 24)
game_font_large = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 36)
game_font_small = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 18)
game_font_medium = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 28)

# Load and scale background image
try:
    background_img = pygame.image.load(join('Minigame4/Jessica Background.png')).convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    background_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for i in range(SCREEN_HEIGHT):
        color = (
            min(255, 20 + i * 0.1),
            min(255, 30 + i * 0.1),
            min(255, 50 + i * 0.1)
        )
        pygame.draw.line(background_img, color, (0, i), (SCREEN_WIDTH, i))

# Load puzzle tile images and complete Python image
tile_images = []
initial_tile_images = []

# Add error handling for loading tile images
for i in range(9):
    try:
        tile_img = pygame.image.load(join('Minigame4/', f'Python_{i+1}.png')).convert_alpha()
        initial_img = pygame.image.load(join('Minigame4/', f'initial_tile_{i+1}.png')).convert_alpha()
        tile_images.append(tile_img)
        initial_tile_images.append(initial_img)
    except:
        print(f"Failed to load tile image {i+1}")
        # Create fallback colored rectangles
        fallback = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(fallback, (100, 100, 100, 255), fallback.get_rect())
        tile_images.append(fallback)
        initial_tile_images.append(fallback)

complete_python_img = pygame.image.load(join('Minigame4/complete_python.png')).convert_alpha()
complete_python_img = pygame.transform.scale(complete_python_img, (200, 200))  # Changed to 200x200

# Scale tile images
tile_images = [pygame.transform.scale(img, (200, 200)) for img in tile_images]
initial_tile_images = [pygame.transform.scale(img, (200, 200)) for img in initial_tile_images]

class GifPlayer:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.frame_duration = 30  # Further reduced for smoother playback
        
        try:
            gif = Image.open(gif_path)
            while True:
                frame = gif.copy()
                frame = pygame.image.fromstring(
                    frame.convert('RGBA').tobytes(), frame.size, 'RGBA')
                self.frames.append(frame)
                gif.seek(gif.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"Error loading gif {gif_path}: {e}")
            # Create a fallback frame
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

    def show_gif(self, gif_name, duration=5000):  # Increased duration to 5 seconds
        self.current_gif = self.gifs[gif_name]
        self.display_time = pygame.time.get_ticks() + duration
        self.last_gif = gif_name

    def is_playing(self):
        return pygame.time.get_ticks() < self.display_time

    def update(self, screen):
        if self.current_gif and pygame.time.get_ticks() < self.display_time:
            self.current_gif.update()
            frame = self.current_gif.get_current_frame()
            if frame:
                screen.blit(frame, (FEEDBACK_X, FEEDBACK_Y))

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.is_running = True
        self.one_minute_warning_shown = False

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
            text_surface = font.render(time_text, True, WHITE)
            screen.blit(text_surface, (20, 20))

    def should_show_warning(self):
        seconds_left = self.get_time_left()
        if seconds_left <= 60 and not self.one_minute_warning_shown:
            self.one_minute_warning_shown = True
            return True
        return False

class Tile:
    def __init__(self, x, y, number):
        self.original_rect = pygame.Rect(x, y, 200, 200)
        self.rect = self.original_rect.copy()
        self.number = number
        self.question = None
        self.answer = None
        self.solved = False
        
        self.pressing = False
        self.press_scale = 1.0
        self.press_duration = 300
        self.press_start_time = 0
        self.question_ready = False
        self.flash_alpha = 0
        self.flash_wrong = False
        self.flash_wrong_start = 0
        self.flash_duration = 500
        self.flash_color = RED
        
        self.victory_glow = False
        self.victory_glow_start = 0
        self.victory_glow_duration = 1000
        self.victory_glow_color = (255, 215, 0)
        
        self.border_thickness = 4
        self.border_color = (255, 215, 0)
        self.border_radius = 10
        
        self.final_image = tile_images[number - 1]
        self.initial_image = initial_tile_images[number - 1]
        self.moved_to_top = False
        self.final_position = None
        self.show_in_question_phase = True

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
        if self.pressing:
            elapsed = pygame.time.get_ticks() - self.press_start_time
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

        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - 10)

        if self.flash_wrong:
            elapsed = pygame.time.get_ticks() - self.flash_wrong_start
            if elapsed >= self.flash_duration:
                self.flash_wrong = False

        if self.victory_glow:
            elapsed = pygame.time.get_ticks() - self.victory_glow_start
            if elapsed >= self.victory_glow_duration:
                self.victory_glow = False

    def draw_with_border(self, surface, image, rect):
        border_rect = rect.inflate(self.border_thickness * 2, self.border_thickness * 2)
        pygame.draw.rect(surface, self.border_color, border_rect, 
                        border_radius=self.border_radius)
        screen.blit(image, rect)

    def draw(self, show_tiles=True):
        if not show_tiles or not self.show_in_question_phase:
            return
            
        if not self.question_ready or self.solved:
            if self.pressing:
                scaled_width = int(self.rect.width * self.press_scale)
                scaled_height = int(self.rect.height * self.press_scale)
                scaled_image = pygame.transform.scale(
                    self.initial_image if not self.solved else self.final_image,
                    (scaled_width, scaled_height)
                )
                scaled_rect = scaled_image.get_rect(center=self.rect.center)
                
                if self.solved:
                    self.draw_with_border(screen, scaled_image, scaled_rect)
                else:
                    screen.blit(scaled_image, scaled_rect)
            else:
                if self.solved:
                    self.draw_with_border(screen, self.final_image, self.rect)
                    
                    if self.victory_glow:
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
                        screen.blit(glow_surface, glow_rect)
                else:
                    screen.blit(self.initial_image, self.rect)

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

def main():
    def restart_game():
        nonlocal tiles, timer, feedback, user_input, selected_tile, answer_input
        nonlocal end_game_started, final_answer, final_answer_correct, game_complete
        nonlocal blank_spaces, questions_copy

        questions_copy = questions.copy()
        random.shuffle(questions_copy)
        tiles = [Tile(SCREEN_WIDTH // 2 - 300 + i % 3 * 220, 
                     SCREEN_HEIGHT // 2 - 250 + i // 3 * 220, i + 1) for i in range(9)]
        timer = Timer(180)
        user_input = ""
        selected_tile = None
        answer_input = ""
        end_game_started = False
        final_answer = ""
        final_answer_correct = False
        game_complete = False
        blank_spaces = ["_"] * 6

        feedback.show_gif('welcome', 5000)  # Increased duration
        feedback.show_gif('instructions', 5000)  # Increased duration

    # Initialize game state
    questions_copy = questions.copy()
    random.shuffle(questions_copy)
    tiles = [Tile(SCREEN_WIDTH // 2 - 300 + i % 3 * 220, 
                  SCREEN_HEIGHT // 2 - 250 + i // 3 * 220, i + 1) for i in range(9)]
    
    timer = Timer(180)
    feedback = FeedbackSystem()
    
    user_input = ""
    selected_tile = None
    answer_input = ""
    end_game_started = False
    final_answer = ""
    final_answer_correct = False
    game_complete = False
    blank_spaces = ["_"] * 6
    correct_word = "PYTHON"
    restart_pending = False
    restart_time = 0
    
    feedback.show_gif('welcome', 5000)  # Increased duration
    feedback.show_gif('instructions', 5000)  # Increased duration

    running = True
    clock = pygame.time.Clock()
    
    while running:
        clock.tick(60)
        current_time = pygame.time.get_ticks()
        screen.blit(background_img, (0, 0))
        timer.draw(screen, game_font)
        
        if timer.is_finished() and not game_complete:
            game_complete = True
            feedback.show_gif('lost', 5000)  # Increased duration
            restart_pending = True
            restart_time = current_time + 5000  # Set restart timer after lost animation

        if restart_pending and current_time >= restart_time:
            restart_game()
            restart_pending = False
        
        if timer.should_show_warning():
            feedback.show_gif('time', 5000)  # Increased duration

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if not end_game_started and not timer.is_finished():
                    if event.key == pygame.K_RETURN:
                        if not selected_tile:
                            if user_input.isdigit() and 1 <= int(user_input) <= 9:
                                tile_num = int(user_input)
                                if questions_copy:
                                    for tile in tiles:
                                        if tile.number == tile_num and not tile.solved:
                                            selected_tile = tile
                                            tile.start_press_animation()
                                            tile.question, tile.answer = questions_copy.pop()
                                            break
                                user_input = ""
                        else:
                            if answer_input.lower() == "jessica" or answer_input.lower() == selected_tile.answer.lower():
                                selected_tile.solved = True
                                selected_tile.start_victory_glow()
                                selected_tile.question_ready = False
                                selected_tile = None
                                answer_input = ""
                                
                                unsolved_count = sum(1 for tile in tiles if not tile.solved)
                                if unsolved_count == 6:
                                    feedback.show_gif('6initial', 5000)
                                elif unsolved_count == 3:
                                    feedback.show_gif('3initial', 5000)
                                elif unsolved_count == 0:
                                    feedback.show_gif('decode', 5000)
                                    end_game_started = True
                            else:
                                selected_tile.start_wrong_flash()
                                selected_tile.question_ready = False
                                selected_tile = None
                                answer_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        if selected_tile and selected_tile.question_ready:
                            answer_input = answer_input[:-1]
                        else:
                            user_input = user_input[:-1]
                    elif event.unicode.isprintable():
                        if selected_tile and selected_tile.question_ready:
                            test_text = answer_input + event.unicode 
                            test_surface = game_font_small.render(test_text, True, (0, 0, 0))
                            if test_surface.get_width() <= 360:
                                answer_input += event.unicode
                        else:
                            user_input += event.unicode
                elif not game_complete:
                    if event.key == pygame.K_RETURN:
                        if final_answer.upper() == correct_word:
                            final_answer_correct = True
                            game_complete = True
                            feedback.show_gif('win', 5000)
                        else:
                            for tile in tiles:
                                tile.start_wrong_flash()
                            final_answer = ""
                            blank_spaces = ["_"] * 6
                    elif event.key == pygame.K_BACKSPACE:
                        if final_answer:
                            final_answer = final_answer[:-1]
                            blank_spaces[len(final_answer)] = "_"
                    elif event.unicode.isalpha() and len(final_answer) < 6:
                        final_answer += event.unicode.upper()
                        blank_spaces[len(final_answer)-1] = event.unicode.upper()

        # Draw game state
        if not end_game_started:
            show_other_tiles = not (selected_tile and selected_tile.question_ready)
            
            for tile in tiles:
                tile.update()
                if selected_tile and selected_tile.question_ready:
                    if tile == selected_tile:
                        tile.show_in_question_phase = True
                    else:
                        tile.show_in_question_phase = False
                else:
                    tile.show_in_question_phase = True
                tile.draw()

            if not selected_tile or not selected_tile.question_ready:
                prompt_surface = game_font.render("Enter a number (1-9):", True, WHITE)
                prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 350))
                screen.blit(prompt_surface, prompt_rect)

                input_surface = game_font.render(user_input, True, WHITE)
                input_rect = input_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 300))
                screen.blit(input_surface, input_rect)

            if selected_tile and selected_tile.question_ready:
                words = selected_tile.question.split()
                lines = []
                current_line = []
                for word in words:
                    current_line.append(word)
                    if len(' '.join(current_line)) > 40:
                        lines.append(' '.join(current_line[:-1]))
                        current_line = [word]
                if current_line:
                    lines.append(' '.join(current_line))

                y_offset = SCREEN_HEIGHT // 2 - 250
                for line in lines:
                    question_surface = game_font_small.render(line, True, WHITE)
                    question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                    screen.blit(question_surface, question_rect)
                    y_offset += 40

                textbox_width = 400
                textbox_height = 50
                textbox_x = SCREEN_WIDTH // 2 - textbox_width // 2
                textbox_y = SCREEN_HEIGHT // 2 + 30
                
                textbox_surface = pygame.Surface((textbox_width, textbox_height), pygame.SRCALPHA)
                pygame.draw.rect(textbox_surface, (255, 255, 255, 128),
                               (0, 0, textbox_width, textbox_height),
                               border_radius=10)
                pygame.draw.rect(textbox_surface, (0, 0, 139, 255),
                               (0, 0, textbox_width, textbox_height),
                               width=2, border_radius=10)
                
                screen.blit(textbox_surface, (textbox_x, textbox_y))

                answer_surface = game_font_small.render(answer_input, True, WHITE)
                answer_rect = answer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(answer_surface, answer_rect)

        else:
            # Final game sequence
            if not final_answer_correct:
                prompt_surface = game_font_medium.render("Decode the picture!", True, WHITE)
                prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))  # Moved higher
                screen.blit(prompt_surface, prompt_rect)

                # Draw complete Python image in the middle
                python_rect = complete_python_img.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                border_rect = python_rect.inflate(8, 8)
                pygame.draw.rect(screen, GOLD, border_rect, border_radius=10)
                screen.blit(complete_python_img, python_rect)

                # Draw blank spaces lower
                blank_surface = game_font_large.render(" ".join(blank_spaces), True, WHITE)
                blank_rect = blank_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 200))  # Moved lower
                screen.blit(blank_surface, blank_rect)
            else:
                win_surface = game_font_large.render("Congratulations!", True, WHITE)
                win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(win_surface, win_rect)

        # Draw wrong answer flash over entire screen
        if any(tile.flash_wrong for tile in tiles):
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(RED)
            max_alpha = max(int(255 * (1 - (pygame.time.get_ticks() - tile.flash_wrong_start) / tile.flash_duration)) 
                          for tile in tiles if tile.flash_wrong)
            flash_surface.set_alpha(max_alpha)
            screen.blit(flash_surface, (0, 0))

        # Update feedback system
        feedback.update(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()