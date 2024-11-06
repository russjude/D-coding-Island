"""
mini-game4.py

Primary Author: Jessica Ng

An educational puzzle game that combines Python programming knowledge with visual
tile-based mechanics. Players solve programming questions to reveal pieces of a
larger image puzzle. Features include interactive tiles, programming questions,
animated transitions, and a final challenge where players must decode the word
'PYTHON'. The game incorporates visual effects like floating animations and
glowing borders to enhance user experience.
"""

import pygame
import sys
import time
import random
import math
from os.path import join

# Initialize game engine
pygame.init()

# Display configuration
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 128, 0)
RED = (255, 0, 0)
GOLD = (212, 175, 55)

# Set up display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("D'Code and Build")

# Initialize fonts with fallback options
try:
    game_font = pygame.font.Font('fonts/PressStart2P-Regular.ttf', 36)
    game_font_large = pygame.font.Font('fonts/PressStart2P-Regular.ttf', 48)
except:
    game_font = pygame.font.SysFont(None, 36)
    game_font_large = pygame.font.SysFont(None, 48)

font = game_font
large_font = game_font_large

# Load and process background image
try:
    background_img = pygame.image.load(join('Minigame4/jessbackground.png')).convert()
    background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Add semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(100)
    background_img.blit(overlay, (0, 0))
except:
    # Create gradient background if image loading fails
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

# Scale tile images to uniform size
tile_images = [pygame.transform.scale(img, (200, 200)) for img in tile_images]
initial_tile_images = [pygame.transform.scale(img, (200, 200)) for img in initial_tile_images]

def create_vignette():
    """Create darkened edge effect for visual depth"""
    vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    for i in range(100):
        alpha = int(i * 1.5)
        pygame.draw.rect(vignette, (0, 0, 0, alpha),
                        ((i, i), (SCREEN_WIDTH - 2*i, SCREEN_HEIGHT - 2*i)), 2)
    return vignette

vignette = create_vignette()

class Tile:
    """Represents an individual puzzle tile with animations and state management"""
    def __init__(self, x, y, number):
        self.original_rect = pygame.Rect(x, y, 200, 200)
        self.rect = self.original_rect.copy()
        self.number = number
        self.question = None
        self.answer = None
        self.solved = False
        self.expanding = False
        self.expanded = False
        self.final_image = tile_images[number - 1]
        self.initial_image = initial_tile_images[number - 1]
        self.display_image = False
        self.image_alpha = 0
        self.border_color = GOLD
        self.border_width = 0
        self.glow_alpha = 0
        self.transition_start = 0
        self.reveal_animation = 0
        self.current_initial_image = None
        self.moved_to_top = False
        self.shrinking = False
        self.final_position = None
        self.float_offset = 0
        self.float_speed = random.uniform(0.02, 0.05)
        self.float_time = 0

    def start_shrinking(self):
        """Reset tile to pre-expansion state"""
        self.shrinking = False
        self.expanding = False
        self.expanded = False

    def move_to_top(self):
        """Position tile in final top row arrangement"""
        if not self.moved_to_top:
            self.rect.width = int(200 * 0.0005)
            self.rect.height = int(200 * 0.0005)
            self.original_rect.y = 300
            self.rect = self.original_rect.copy()
            self.moved_to_top = True

    def draw(self):
        """Render tile with appropriate visual state"""
        if self.expanding:
            scaled_size = (self.rect.width, self.rect.height)
            scaled_pattern = pygame.transform.scale(self.initial_image, scaled_size)
            screen.blit(scaled_pattern, self.rect)

        elif self.expanded:
            if self.rect.width >= SCREEN_WIDTH and self.rect.height >= SCREEN_HEIGHT:
                pygame.draw.rect(screen, WHITE, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            if self.question:
                question_surface = large_font.render(self.question, True, BLACK)
                question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250))
                screen.blit(question_surface, question_rect)
        else:
            if self.solved:
                screen.blit(self.final_image, self.rect)
                if self.border_width < 4:
                    self.border_width += 0.2
                border_rect = self.rect.inflate(self.border_width * 2, self.border_width * 2)
                pygame.draw.rect(screen, self.border_color, border_rect, int(self.border_width))
                
                if self.glow_alpha < 128:
                    self.glow_alpha += 2
                    glow_surface = pygame.Surface((self.rect.width + 20, self.rect.height + 20), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*self.border_color, self.glow_alpha), 
                                  (0, 0, self.rect.width + 20, self.rect.height + 20), 
                                  border_radius=10)
                    screen.blit(glow_surface, self.rect.inflate(20, 20))
            else:
                screen.blit(self.initial_image, self.rect)
                pygame.draw.rect(screen, BLACK, self.rect, 2)

        if self.expanded and self.question:
            feedback_surface = font.render("Type your answer and press Enter", True, WHITE)
            feedback_rect = feedback_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            screen.blit(feedback_surface, feedback_rect)

    def update(self):
        """Update tile position and animations"""
        if self.expanding and not self.expanded:
            target_width = SCREEN_WIDTH
            target_height = SCREEN_HEIGHT
            growth_increment = 200
            
            if self.rect.width < target_width or self.rect.height < target_height:
                self.rect.width += growth_increment
                self.rect.height += growth_increment
                self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
                
                if self.rect.width >= target_width:
                    self.rect.width = target_width
                    self.rect.height = target_height
                    self.expanded = True
                    
        elif self.shrinking:
            shrink_increment = 20
            if self.rect.width > 200:
                self.rect.width -= shrink_increment
                self.rect.height -= shrink_increment
                self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
            else:
                self.shrinking = False
                self.rect.width = 200
                self.rect.height = 200
                self.final_position = (
                    50 + (self.number - 1) * 220,
                    100
                )
                
        elif self.final_position and not self.shrinking:
            self.float_time += self.float_speed
            self.float_offset = math.sin(self.float_time) * 10
            
            target_x, target_y = self.final_position
            current_x, current_y = self.rect.x, self.rect.y
            
            self.rect.x += (target_x - current_x) * 0.1
            self.rect.y = target_y + self.float_offset

    def reset(self):
        """Reset tile to original state"""
        self.rect = self.original_rect.copy()
        self.expanding = False
        self.expanded = False
        if self.solved:
            self.display_image = True
            self.border_width = 0
            self.glow_alpha = 0

# Programming quiz questions database
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

# Initialize game state
random.shuffle(questions)
tiles = [Tile(SCREEN_WIDTH // 2 - 300 + i % 3 * 220, SCREEN_HEIGHT // 2 - 250 + i // 3 * 220, i + 1) for i in range(9)]

# Game state variables
user_input = ""
prompt_text = "Enter a number from 1 to 9: "
selected_tile = None
answer_input = ""
wrong_answer = False
end_game_started = False
final_answer = ""
final_answer_correct = False
game_complete = False
show_try_again = False
blank_spaces = ["_"] * 6
correct_word = "PYTHON"

reached_final_question = False

feedback_text = ""

# Main game loop with 60 FPS cap
clock = pygame.time.Clock()
proceed_surface = font.render("Press any key to proceed", True, WHITE)

while True:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN:
            if not end_game_started:
                if event.key == pygame.K_RETURN:
                    if user_input.isdigit() and 1 <= int(user_input) <= 9:
                        for tile in tiles:
                            if int(user_input) == tile.number and not tile.solved:
                                selected_tile = tile
                                tile.expanding = True
                                if questions:
                                    tile.question, tile.answer = questions.pop()
                    elif answer_input:
                        if selected_tile and answer_input.lower() == selected_tile.answer.lower():
                            selected_tile.solved = True
                            selected_tile.display_image = True
                        else:
                            wrong_answer = True
                        if selected_tile:
                            if answer_input.lower() == "jessica":
                                selected_tile.solved = True
                                selected_tile.display_image = True
                                feedback_text = "You used the master word 'jessica' to solve this question!"
                            elif answer_input.lower() == selected_tile.answer.lower():
                                selected_tile.solved = True
                                selected_tile.display_image = True
                            else:
                                wrong_answer = True
                            if selected_tile:
                                selected_tile.reset()
                            answer_input = ""
                            selected_tile = None
                            wrong_answer = False
                    user_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    if selected_tile:
                        answer_input = answer_input[:-1]
                    else:
                        user_input = user_input[:-1]
                elif event.unicode.isprintable():
                    if selected_tile:
                        answer_input += event.unicode
                    else:
                        user_input += event.unicode
            else:
                if not final_answer_correct and not game_complete:
                    if event.key == pygame.K_RETURN:
                        if final_answer.upper() == correct_word:
                            final_answer_correct = True
                            game_complete = True
                        else:
                            show_try_again = True
                            final_answer = ""
                            blank_spaces = ["_"] * 6
                    elif event.key == pygame.K_BACKSPACE:
                        if final_answer:
                            final_answer = final_answer[:-1]
                            blank_spaces[len(final_answer)] = "_"
                    elif event.unicode.isalpha() and len(final_answer) < 6:
                        final_answer += event.unicode.upper()
                        blank_spaces[len(final_answer)-1] = event.unicode.upper()

    screen.fill(WHITE)
    screen.blit(background_img, (0,0))

    # Check if all tiles are solved
    all_solved = all(tile.solved for tile in tiles)
    
    if all_solved and not end_game_started:
        end_game_started = True
        for tile in tiles:
            tile.move_to_top()

    if not end_game_started:
        for tile in tiles:
            if not selected_tile:
                tile.draw()
                tile.update()
        
        if selected_tile:
            if selected_tile.expanded == False:
                selected_tile.update()
                selected_tile.draw()

        if not selected_tile:
            prompt_surface = font.render(prompt_text, True, WHITE)
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 350))
            screen.blit(prompt_surface, prompt_rect)

            input_surface = font.render(user_input, True, WHITE)
            input_rect = input_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 300))
            screen.blit(input_surface, input_rect)
        elif selected_tile.expanded:
            question_surface = large_font.render(selected_tile.question, True, WHITE)
            question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250))
            screen.blit(question_surface, question_rect)

            answer_prompt_surface = font.render("Enter your answer: ", True, WHITE)
            answer_prompt_rect = answer_prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 200))
            screen.blit(answer_prompt_surface, answer_prompt_rect)

            answer_surface = font.render(answer_input, True, WHITE)
            answer_rect = answer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))
            screen.blit(answer_surface, answer_rect)

        if wrong_answer:
            wrong_answer_surface = font.render("Wrong answer! Try again!", True, RED)
            wrong_answer_rect = wrong_answer_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(wrong_answer_surface, wrong_answer_rect)

    else:
        # Draw solved tiles at the top
        if not reached_final_question:
            for tile in tiles:
                tile.draw()

        if not final_answer_correct:
            reached_final_question = True
            prompt_surface = large_font.render("You have decoded. Now tell the island what you have created.", True, WHITE)
            prompt_rect = prompt_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(prompt_surface, prompt_rect)

            # Draw blank spaces
            blank_space_surface = large_font.render(" ".join(blank_spaces), True, WHITE)
            blank_space_rect = blank_space_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(blank_space_surface, blank_space_rect)

            if show_try_again:
                try_again_surface = font.render("Incorrect! Try again!", True, RED)
                try_again_rect = try_again_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
                screen.blit(try_again_surface, try_again_rect)
        else:
            congrats_surface = large_font.render("Congratulations!", True, WHITE)
            congrats_rect = congrats_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
            screen.blit(congrats_surface, congrats_rect)

            message_surface = font.render("You have defeated Jessica the Wraith's puzzle.", True, WHITE)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(message_surface, message_rect)

            proceed_rect = proceed_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            screen.blit(proceed_surface, proceed_rect)

    screen.blit(vignette, (0, 0))
    pygame.display.flip()