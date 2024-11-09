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

# Feedback position constants
FEEDBACK_X = SCREEN_WIDTH - 420
FEEDBACK_Y = SCREEN_HEIGHT // 2 - 300

# Set up display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D'Code and Build")

# Initialize fonts
game_font = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 24)
game_font_large = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 36)
game_font_small = pygame.font.Font('Minigame4/PRESSSTART2P.ttf', 18)

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

# Load puzzle tile images
tile_images = [
    pygame.image.load(join('Minigame4/', f'Python_{i+1}.png')).convert_alpha() 
    for i in range(9)
]

initial_tile_images = [
    pygame.image.load(join('Minigame4/', f'initial_tile_{i+1}.png')).convert_alpha() 
    for i in range(9)
]

# Scale tile images
tile_images = [pygame.transform.scale(img, (200, 200)) for img in tile_images]
initial_tile_images = [pygame.transform.scale(img, (200, 200)) for img in initial_tile_images]

class GifPlayer:
    def __init__(self, gif_path):
        self.frames = []
        self.current_frame = 0
        self.last_update = 0
        self.frame_duration = 100
        
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
        
        # Victory glow properties
        self.victory_glow = False
        self.victory_glow_start = 0
        self.victory_glow_duration = 1000  # 1 second
        self.victory_glow_color = (255, 215, 0)  # Gold color
        
        # Permanent border properties
        self.border_thickness = 4
        self.border_color = (255, 215, 0)  # Gold color
        self.border_radius = 10
        
        self.final_image = tile_images[number - 1]
        self.initial_image = initial_tile_images[number - 1]
        self.moved_to_top = False
        self.final_position = None
        self.float_offset = 0
        self.float_speed = random.uniform(0.02, 0.05)
        self.float_time = 0

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

        if self.final_position and not self.pressing:
            self.float_time += self.float_speed
            self.float_offset = math.sin(self.float_time) * 10
            target_x, target_y = self.final_position
            current_x, current_y = self.rect.x, self.rect.y
            self.rect.x += (target_x - current_x) * 0.1
            self.rect.y = target_y + self.float_offset

        # Update victory glow
        if self.victory_glow:
            elapsed = pygame.time.get_ticks() - self.victory_glow_start
            if elapsed >= self.victory_glow_duration:
                self.victory_glow = False

    def draw_with_border(self, surface, image, rect):
        # Draw the gold border
        border_rect = rect.inflate(self.border_thickness * 2, self.border_thickness * 2)
        pygame.draw.rect(surface, self.border_color, border_rect, 
                        border_radius=self.border_radius)
        
        # Draw the main image
        screen.blit(image, rect)

    def draw(self, show_tiles=True):
        if show_tiles:
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
                    # Draw the permanent gold border and final image
                    self.draw_with_border(screen, self.final_image, self.rect)
                    
                    # Draw victory glow effect if active
                    if self.victory_glow:
                        elapsed = pygame.time.get_ticks() - self.victory_glow_start
                        progress = elapsed / self.victory_glow_duration
                        glow_alpha = int(255 * (1 - progress))
                        
                        # Create expanding glow effect
                        glow_size = int(20 * (1 + progress))
                        glow_surface = pygame.Surface(
                            (self.rect.width + glow_size * 2, 
                             self.rect.height + glow_size * 2), 
                            pygame.SRCALPHA
                        )
                        
                        # Draw multiple layers of glow for a more intense effect
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

        if self.flash_wrong:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash_surface.fill(self.flash_color)
            alpha = int(255 * (1 - (pygame.time.get_ticks() - self.flash_wrong_start) / self.flash_duration))
            flash_surface.set_alpha(alpha)
            screen.blit(flash_surface, (0, 0))

    def move_to_top(self):
        if not self.moved_to_top:
            self.final_position = (50 + (self.number - 1) * 220, 100)
            self.moved_to_top = True

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
    ("What is the keyword for defining an anonymous function?", "lambda"),
    ("What will \"banana\".find(\"na\") return?", "2"),
    ("What does \"Python\".startswith(\"Py\") return?", "True"),
    ("What keyword stops a loop from continuing to the next iteration?", "break"),
    ("What is the result of \"Hello\".replace(\"H\", \"J\")?", "Jello"),
    ("What is the result of \" space \".strip()?", "space"),
    ("Which keyword checks if an object exists within a list?", "in"),
    ("What is the result of \"True\" and \"False\"?", "False"),
]

def main():
    # Initialize game state
    random.shuffle(questions)
    tiles = [Tile(SCREEN_WIDTH // 2 - 300 + i % 3 * 220, 
                  SCREEN_HEIGHT // 2 - 250 + i // 3 * 220, i + 1) for i in range(9)]
    
    timer = Timer(180)  # 3 minutes
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
    
    # Show welcome and instructions
    feedback.show_gif('welcome', 3000)
    feedback.show_gif('instructions', 3000)

    # Main game loop
    running = True
    clock = pygame.time.Clock()
    
    while running:
        clock.tick(60)
        screen.blit(background_img, (0, 0))
        timer.draw(screen, game_font)
        
        if timer.is_finished() and not game_complete:
            game_complete = True
            feedback.show_gif('lost')
            
        if timer.should_show_warning():
            feedback.show_gif('time')

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if not end_game_started and not timer.is_finished():
                    if event.key == pygame.K_RETURN:
                        if not selected_tile:
                            if user_input.isdigit() and 1 <= int(user_input) <= 9:
                                tile_num = int(user_input)
                                for tile in tiles:
                                    if tile.number == tile_num and not tile.solved:
                                        selected_tile = tile
                                        tile.start_press_animation()
                                        if questions:
                                            tile.question, tile.answer = questions.pop()
                                user_input = ""
                        else:
                            if answer_input.lower() == selected_tile.answer.lower():
                                selected_tile.solved = True
                                selected_tile.start_victory_glow()  # Start the victory glow effect
                                selected_tile.question_ready = False
                                selected_tile = None
                                answer_input = ""
                                
                                unsolved_count = sum(1 for tile in tiles if not tile.solved)
                                if unsolved_count == 6:
                                    feedback.show_gif('6initial')
                                elif unsolved_count == 3:
                                    feedback.show_gif('3initial')
                                elif unsolved_count == 0:
                                    feedback.show_gif('decode')
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
                            test_surface = game_font_small.render (test_text, True, (0, 0, 0))

                            if test_surface.get_width() <= textbox_width - 40:
                             answer_input += event.unicode
                        else:
                            user_input += event.unicode
                elif not game_complete:
                    if event.key == pygame.K_RETURN:
                        if final_answer.upper() == correct_word:
                            final_answer_correct = True
                            game_complete = True
                            feedback.show_gif('win')
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
            # Draw tiles
            for tile in tiles:
                tile.update()
                tile.draw(not (selected_tile and selected_tile.question_ready))

            if not selected_tile or not selected_tile.question_ready:
                prompt_surface = game_font.render("Enter a number (1-9):", True, WHITE)
                prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 350))
                screen.blit(prompt_surface, prompt_rect)

                input_surface = game_font.render(user_input, True, WHITE)
                input_rect = input_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 300))
                screen.blit(input_surface, input_rect)

            if selected_tile and selected_tile.question_ready:
                # Question phase - maintain background
                screen.blit(background_img, (0, 0))

                timer.draw(screen, game_font)

                # Split question into multiple lines if needed
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

                # Draw each line of the question
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
                
                # Create semi-translucent white background
                textbox_surface = pygame.Surface((textbox_width, textbox_height), pygame.SRCALPHA)
                pygame.draw.rect(textbox_surface, (255, 255, 255, 128), # White with 128 alpha (semi-transparent)
                               (0, 0, textbox_width, textbox_height),
                               border_radius=10)
                
                # Draw dark blue border
                pygame.draw.rect(textbox_surface, (0, 0, 139, 255), # Dark blue
                               (0, 0, textbox_width, textbox_height),
                               width=2, border_radius=10)
                
                screen.blit(textbox_surface, (textbox_x, textbox_y))

                max_text_width = textbox_width - 40 

                test_surface = game_font.render(selected_tile.answer, True, WHITE)
                if test_surface.get_width() > max_text_width: 
                    answer_input = answer_input[:-1]

                answer_surface = game_font_small.render(answer_input, True, WHITE)
                answer_rect = answer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(answer_surface, answer_rect)

        else:
            # Draw solved tiles at the top
            for tile in tiles:
                if not tile.moved_to_top:
                    tile.move_to_top()
                tile.update()
                tile.draw()

            if not final_answer_correct:
                prompt_surface = game_font_large.render("Decode the final word!", True, WHITE)
                prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(prompt_surface, prompt_rect)

                blank_surface = game_font_large.render(" ".join(blank_spaces), True, WHITE)
                blank_rect = blank_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(blank_surface, blank_rect)
            else:
                win_surface = game_font_large.render("Congratulations!", True, WHITE)
                win_rect = win_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(win_surface, win_rect)

        # Update feedback system
        feedback.update(screen)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()