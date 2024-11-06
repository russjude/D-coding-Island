"""
Mini-Game 5: Programming Quiz Battle
Author: Jessica Ng
Contributor: Jacobo Testa

A Python-based educational game where players battle against Jacobo the Undead King 
by matching programming concepts with their definitions. Get matches right to deal 
damage to Jacobo, but be careful - wrong answers will damage you instead! Win by 
either depleting Jacobo's health or matching all pairs correctly.
"""

import pygame 
import sys
import random
from os.path import join

# Start up pygame
pygame.init()

# Set up the game window - using 2304x1408 for modern displays
screen_width = 1539
screen_height = 940

# Scaled game element sizes
RECT_WIDTH = int(screen_width * 0.13)        # Width of question/answer boxes
RECT_HEIGHT = int(screen_height * 0.04)      # Height of question/answer boxes
NUM_PAIRS = 12
HEALTH_BAR_WIDTH = int(screen_width * 0.13)  # Width of health bars
HEALTH_BAR_HEIGHT = int(screen_height * 0.02)  # Height of health bars
CHARACTER_SIZE = int(screen_height * 0.16)   # Size of character sprites
GAME_AREA_TOP = screen_height * 0.4  # Push gameplay area down
CHARACTER_Y_OFFSET = int(screen_height * 0.37)  # How far down to place characters
MARGIN = int(screen_width * 0.02)   # Space between boxes

# Basic colors we'll use
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GOLD = (212, 175, 55)

# Programming questions for the quiz
questions = [
    "What is Python?", 
    "What is a variable?", 
    "What is a function?", 
    "What is a loop?", 
    "What is a list?", 
    "What is inheritance?", 
    "What is a class?", 
    "What is debugging?",
    "What is an integer?",
    "What is a string?",
    "What is a dictionary?",
    "What is an algorithm?"
]

# Matching answers - order matches questions
answers = [
    "A programming language",
    "A container for data",
    "A reusable block of code",
    "Repeats a block of code",
    "An ordered collection",
    "A way to inherit attributes",
    "A blueprint for objects",
    "Finding and fixing errors",
    "A whole number value",
    "Text data in quotes",
    "Key-value pair collection",
    "Step-by-step problem solution"
]

def generate_random_positions(num_rects):
    cols = 6
    rows = (num_rects * 2 + cols - 1) // cols
    
    total_width = cols * (RECT_WIDTH + MARGIN)
    total_height = rows * (RECT_HEIGHT + MARGIN)
    
    start_x = (screen_width - total_width) // 2
    start_y = GAME_AREA_TOP + MARGIN + int(screen_height * 0.16)
    
    all_positions = []
    for row in range(rows):
        for col in range(cols):
            x = start_x + col * (RECT_WIDTH + MARGIN)
            y = start_y + row * (RECT_HEIGHT + MARGIN)
            if len(all_positions) < num_rects * 2:
                all_positions.append((x, y))
    
    random.shuffle(all_positions)
    return all_positions

def draw_text_in_rect(screen, text, rect):
    """Handle text wrapping inside our boxes"""
    font = pygame.font.Font(None, int(screen_height * 0.025))
    words = text.split()
    lines = []
    current_line = words[0]
    
    # Split text into lines that fit
    for word in words[1:]:
        test_line = current_line + " " + word
        if font.size(test_line)[0] <= rect.width - 10:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    # Center all lines vertically
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    current_y = rect.centery - (total_height / 2)
    
    # Draw each line
    for line in lines:
        text_surface = font.render(line, True, BLACK)
        text_rect = text_surface.get_rect(centerx=rect.centerx, y=current_y)
        screen.blit(text_surface, text_rect)
        current_y += line_height

def draw_character(screen, x, y, image):
    """Place a character sprite on screen"""
    char_rect = pygame.Rect(x - CHARACTER_SIZE//2, y, CHARACTER_SIZE, CHARACTER_SIZE)
    screen.blit(image, char_rect)
    return char_rect

def draw_health_bar(screen, x, y, health, max_health=100):
    """Draw a health bar with current/max health"""
    bar_rect = pygame.Rect(x - HEALTH_BAR_WIDTH//2, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    health_width = (health / max_health) * HEALTH_BAR_WIDTH
    
    # Red background, green for current health
    pygame.draw.rect(screen, RED, bar_rect)
    pygame.draw.rect(screen, GREEN, (bar_rect.x, bar_rect.y, health_width, HEALTH_BAR_HEIGHT))
    pygame.draw.rect(screen, WHITE, bar_rect, 2)
    
    # Show health percentage
    font = pygame.font.Font(None, int(screen_height * 0.025))
    health_text = font.render(f"{health}%", True, WHITE)
    text_rect = health_text.get_rect(midtop=(x, y - int(screen_height * 0.026)))
    screen.blit(health_text, text_rect)

def draw_feedback(screen, message, color):
    font = pygame.font.Font(None, int(screen_height * 0.05))
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(screen_width // 2, CHARACTER_Y_OFFSET - int(screen_height * 0.053)))
    screen.blit(text, text_rect)

def match_game():
    """Main game function - runs the matching quiz battle"""
    # Set up the game window
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Battle Against Jacobo the Undead King")
    
    # Load in all our images
    try:
        background = pygame.image.load('Minigame5/jessbackground.png')
        background = pygame.transform.scale(background, (screen_width, screen_height))
    except:
        # If no background, use a dark gray
        background = pygame.Surface((screen_width, screen_height))
        background.fill((50, 50, 50))
    
    # Load character sprites
    try:
        hero_image = pygame.image.load('Minigame5/hero.png')
        hero_image = pygame.transform.scale(hero_image, (CHARACTER_SIZE, CHARACTER_SIZE))
    except:
        # Backup blue rectangle if image missing
        hero_image = pygame.Surface((CHARACTER_SIZE, CHARACTER_SIZE))
        hero_image.fill(BLUE)

    try:
        jacobo_image = pygame.image.load('Minigame5/jacobo.png')
        jacobo_image = pygame.transform.scale(jacobo_image, (CHARACTER_SIZE, CHARACTER_SIZE))
    except:
        # Backup red rectangle if image missing
        jacobo_image = pygame.Surface((CHARACTER_SIZE, CHARACTER_SIZE))
        jacobo_image.fill(RED)
    
    # Set up the question/answer grid
    positions = generate_random_positions(NUM_PAIRS)
    
    # Mix up questions and answers
    question_answer_pairs = list(zip(questions, answers))
    random.shuffle(question_answer_pairs)
    shuffled_questions, shuffled_answers = zip(*question_answer_pairs)
    
    # Create all the question boxes
    left_rectangles = [{'rect': pygame.Rect(pos[0], pos[1], RECT_WIDTH, RECT_HEIGHT),
                        'text': shuffled_questions[i], 
                        'matched': False,
                        'answer': shuffled_answers[i]} 
                       for i, pos in enumerate(positions[:NUM_PAIRS])]
    
    # Create all the answer boxes
    right_rectangles = [{'rect': pygame.Rect(pos[0], pos[1], RECT_WIDTH, RECT_HEIGHT),
                         'text': shuffled_answers[i], 
                         'matched': False} 
                        for i, pos in enumerate(positions[NUM_PAIRS:])]
    
    # Position the characters
    jacobo_pos = (screen_width // 4, CHARACTER_Y_OFFSET)
    hero_pos = (3 * screen_width // 4, CHARACTER_Y_OFFSET)
    
    # Game state variables
    selected_left = None  # Currently selected question
    selected_right = None  # Currently selected answer
    matched_pairs = 0     # How many correct matches made
    connections = []      # Lines showing matches
    feedback_message = "Match the questions with their answers!"
    feedback_color = WHITE
    feedback_timer = pygame.time.get_ticks()
    hero_health = 100
    jacobo_health = 100
    game_over = False
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Draw background
        screen.blit(background, (0, 0))
        
        # Draw characters and health bars
        jacobo_rect = draw_character(screen, jacobo_pos[0], jacobo_pos[1], jacobo_image)
        hero_rect = draw_character(screen, hero_pos[0], hero_pos[1], hero_image)
        
        # Draw character names
        font = pygame.font.Font(None, int(screen_height * 0.038))
        hero_label = font.render("Hero", True, WHITE)
        jacobo_label = font.render("Jacobo the Undead King", True, WHITE)
        screen.blit(jacobo_label, (jacobo_pos[0] - jacobo_label.get_width()//2, jacobo_pos[1] - int(screen_height * 0.032)))
        screen.blit(hero_label, (hero_pos[0] - hero_label.get_width()//2, hero_pos[1] - int(screen_height * 0.032)))
        
        # Draw health bars
        draw_health_bar(screen, jacobo_pos[0], jacobo_pos[1] - int(screen_height * 0.064), jacobo_health)
        draw_health_bar(screen, hero_pos[0], hero_pos[1] - int(screen_height * 0.064), hero_health)
        
        # Handle mouse and keyboard input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle matching attempts
            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # First click - select a question
                if selected_left is None:
                    for i, rect_info in enumerate(left_rectangles):
                        if rect_info['rect'].collidepoint(mouse_pos) and not rect_info['matched']:
                            selected_left = i
                            feedback_message = "Now select an answer"
                            feedback_color = WHITE
                            feedback_timer = pygame.time.get_ticks()
                            break
                
                # Second click - select an answer and check if correct
                elif selected_right is None:
                    for i, rect_info in enumerate(right_rectangles):
                        if rect_info['rect'].collidepoint(mouse_pos) and not rect_info['matched']:
                            selected_right = i
                            
                            # Check if match is correct
                            if right_rectangles[selected_right]['text'] == left_rectangles[selected_left]['answer']:
                                # Correct match - damage Jacobo
                                jacobo_health = max(0, jacobo_health - 8)
                                feedback_message = "Correct match! Jacobo takes damage!"
                                feedback_color = GREEN
                                left_rectangles[selected_left]['matched'] = True
                                right_rectangles[selected_right]['matched'] = True
                                matched_pairs += 1
                                connections.append((left_rectangles[selected_left]['rect'].center,
                                                 right_rectangles[selected_right]['rect'].center,
                                                 GREEN))
                            else:
                                # Wrong match - take damage
                                hero_health = max(0, hero_health - 8)
                                feedback_message = "Wrong match! You take damage!"
                                feedback_color = RED
                                connections.append((left_rectangles[selected_left]['rect'].center,
                                                 right_rectangles[selected_right]['rect'].center,
                                                 RED))
                            
                            feedback_timer = pygame.time.get_ticks()
                            selected_left = None
                            selected_right = None
        
        # Draw connection lines between matches
        for connection in connections:
            pygame.draw.line(screen, connection[2], connection[0], connection[1], 2)
        
        # Draw all boxes
        for rect_info in left_rectangles + right_rectangles:
            color = GREEN if rect_info['matched'] else WHITE
            pygame.draw.rect(screen, color, rect_info['rect'])
            pygame.draw.rect(screen, BLACK, rect_info['rect'], 2)
            draw_text_in_rect(screen, rect_info['text'], rect_info['rect'])
        
        # Highlight selected question
        if selected_left is not None:
            pygame.draw.rect(screen, BLUE, left_rectangles[selected_left]['rect'], 3)
        
        # Show feedback messages
        if feedback_message:
            draw_feedback(screen, feedback_message, feedback_color)
            if pygame.time.get_ticks() - feedback_timer > 2000:
                feedback_message = ""
        
        # Check if game is over
        if not game_over:
            if hero_health <= 0:
                game_over = True
                feedback_message = "You have been defeated by Jacobo!"
                feedback_color = RED
            elif jacobo_health <= 0 or matched_pairs == NUM_PAIRS:
                game_over = True
                feedback_message = "You have defeated Jacobo the Undead King!"
                feedback_color = GREEN
        
        if game_over:
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.fill(BLACK)
            overlay.set_alpha(128)
            screen.blit(overlay, (0, 0))
            
            font = pygame.font.Font(None, int(screen_height * 0.079))
            text = font.render(feedback_message, True, feedback_color)
            text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + int(screen_height * 0.106)))
            screen.blit(text, text_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    return hero_health > 0

if __name__ == "__main__":
    match_game()