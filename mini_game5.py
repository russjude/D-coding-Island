"""
Programming Quiz Battle
Primary Author: Jacobo 
Secondary Author: Jessica Ng

A quiz-based battle game that tests programming knowledge through a matching mechanic.
Players face off against an opponent in two rounds of increasing difficulty, matching
programming concepts with their definitions while managing their health bar.

Game Features:
- Two-round battle system with health bars
- Time-based challenges with adaptive difficulty
- Visual feedback through animated character reactions
- Matching puzzle mechanics for learning programming concepts
- Progressive damage system
- Bonus time rewards for quick completion

Game Flow:
1. Round 1: Basic programming concepts (60 seconds)
   - Fast completion (<30s) unlocks more time for Round 2
   - Successful matches damage the opponent
   - Wrong matches damage the player
   
2. Round 2: Advanced programming concepts
   - Time limit based on Round 1 performance
   - Increased difficulty with harder concepts
   - Must win both rounds to complete the game

Required Assets:
- Character reaction animations
- Battle background
- Custom pixel font
- Sound effects
"""

import pygame 
import sys
import random
from os.path import join, exists
from PIL import Image
import time
import os

# Start up pygame
pygame.init()

# Set up the game window
screen_width = 1539
screen_height = 940

# Validate and load fonts with error handling
def load_game_fonts():
    try:
        font_path = 'Minigame5/PRESSSTART2P.ttf'
        if not exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
        
        return {
            'small': pygame.font.Font(font_path, int(screen_height * 0.010)),
            'medium': pygame.font.Font(font_path, int(screen_height * 0.025)),
            'large': pygame.font.Font(font_path, int(screen_height * 0.020)),
            'xlarge': pygame.font.Font(font_path, int(screen_height * 0.050))
        }
    except Exception as e:
        print(f"Error loading fonts: {e}")
        # Fallback to system font
        return {
            'small': pygame.font.SysFont(None, int(screen_height * 0.010)),
            'medium': pygame.font.SysFont(None, int(screen_height * 0.025)),
            'large': pygame.font.SysFont(None, int(screen_height * 0.020)),
            'xlarge': pygame.font.SysFont(None, int(screen_height * 0.050))
        }

game_fonts = load_game_fonts()

# Scaled game element sizes
RECT_WIDTH = int(screen_width * 0.2)
RECT_HEIGHT = int(screen_height * 0.05)
HEALTH_BAR_WIDTH = int(screen_width * 0.19)
HEALTH_BAR_HEIGHT = int(screen_height * 0.03)
MARGIN = int(screen_width * 0.02)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (40, 40, 40)
SOFT_GREEN = (100, 200, 100)
DARK_RED = (200, 50, 50)
GOLD = (255, 215, 0)
PURPLE_GLOW_COLOR = (128, 0, 128, 150)

# Split questions into two levels
questions_level1 = [
    "What is Python?", 
    "What is a variable?", 
    "What is a function?", 
    "What is a loop?", 
    "What is a list?", 
    "What is inheritance?"
]

questions_level2 = [
    "What is a class?", 
    "What is debugging?",
    "What is an integer?",
    "What is a string?",
    "What is a dictionary?",
    "What is an algorithm?"
]

# Split answers into two levels
answers_level1 = [
    "A programming language",
    "A container for data",
    "A reusable block of code",
    "Repeats a block of code",
    "An ordered collection",
    "A way to inherit attributes"
]

answers_level2 = [
    "A blueprint for objects",
    "Finding and fixing errors",
    "A whole number value",
    "Text data in quotes",
    "Key-value pair collection",
    "Step-by-step problem solution"
]

def validate_assets():
    """Validate all required game assets exist"""
    required_assets = [
        'Minigame5/Jacobo Background.png',
        'Minigame5/Jacobo Fast.gif',
        'Minigame5/Jacobo Slow.gif',
        'Minigame5/Jacobo Inst1.gif',
        'Minigame5/Jacobo Inst2.gif',
        'Minigame5/Jacobo Win.gif',
        'Minigame5/Jacobo Lost.gif'
    ]
    
    missing_assets = [asset for asset in required_assets if not exists(asset)]
    if missing_assets:
        raise FileNotFoundError(f"Missing required assets: {missing_assets}")

def play_gif_sequence(screen, gif_path, duration, background_path=None, player_health=None, opponent_health=None, gif_width=None, gif_height=None, position=(1185, 205), move_speed=(0, 0)):
    """Play a GIF with improved error handling and frame timing"""
    try:
        if not exists(gif_path):
            raise FileNotFoundError(f"GIF file not found: {gif_path}")
        
        # Load and prepare background if provided
        bg = None
        if background_path:
            if not exists(background_path):
                raise FileNotFoundError(f"Background file not found: {background_path}")
            bg = pygame.image.load(background_path)
            bg = pygame.transform.scale(bg, (screen_width, screen_height))
            screen.blit(bg, (0, 0))
            pygame.display.flip()
        
        # Load and process GIF frames
        with Image.open(gif_path) as gif:
            frames = []
            for frame_idx in range(gif.n_frames):
                gif.seek(frame_idx)
                frame_surface = pygame.image.fromstring(
                    gif.convert('RGBA').tobytes(), gif.size, 'RGBA')
                
                # Scale the GIF frame if width and height are provided
                if gif_width and gif_height:
                    frame_surface = pygame.transform.scale(frame_surface, (gif_width, gif_height))
                
                frames.append(frame_surface)

        start_time = time.time()
        frame_duration = duration / len(frames)
        
        while time.time() - start_time < duration:
            current_time = time.time() - start_time
            frame_index = int(current_time / frame_duration) % len(frames)
            
            if background_path:
                screen.blit(bg, (0, 0))
            
            # Clear the opponent's health bar area
            if opponent_health is not None:
                draw_health_bar(screen, screen_width * 0.88, screen_height * 0.4, 0)  # Clear health bar
            
            # Blit the scaled GIF frame at the specified position
            screen.blit(frames[frame_index], position)
            
            # Draw only player health bar if provided
            if player_health is not None:
                draw_health_bar(screen, screen_width * 0.12, screen_height * 0.4, player_health)
            
            pygame.display.flip()
            
            # Update position based on move_speed
            position = (position[0] + move_speed[0], position[1] + move_speed[1])
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False
            
            pygame.time.Clock().tick(60)
            
    except Exception as e:
        print(f"Error playing GIF sequence: {e}")
        return False
    
    return True

def create_glow_surface(width, height, color, alpha=100):
    """Create a surface with a glowing effect"""
    glow = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
    pygame.draw.rect(glow, (*color, alpha), (5, 5, width, height), border_radius=10)
    return glow

def generate_random_positions(num_rects):
    """Generate positions for two columns of rectangles"""
    cols = 2
    rows = num_rects
    
    total_width = cols * (RECT_WIDTH + MARGIN)
    total_height = rows * (RECT_HEIGHT + MARGIN)
    
    start_x = (screen_width - total_width) // 2
    start_y = screen_height * 0.25
    
    left_positions = []
    for row in range(rows):
        x = start_x
        y = start_y + row * (RECT_HEIGHT + MARGIN * 2)
        left_positions.append((x, y))
    
    right_positions = []
    for row in range(rows):
        x = start_x + RECT_WIDTH + MARGIN * 2
        y = start_y + row * (RECT_HEIGHT + MARGIN * 2)
        right_positions.append((x, y))
    
    random.shuffle(right_positions)
    return left_positions + right_positions

def draw_text_in_rect(screen, text, rect):
    """Handle text wrapping inside boxes"""
    font = game_fonts['small']
    words = text.split()
    lines = []
    current_line = words[0]
    
    for word in words[1:]:
        test_line = current_line + " " + word
        if font.size(test_line)[0] <= rect.width - 20:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    
    line_height = font.get_linesize()
    total_height = line_height * len(lines)
    current_y = rect.centery - (total_height / 2)
    
    for line in lines:
        text_surface = font.render(line, True, WHITE)
        text_rect = text_surface.get_rect(centerx=rect.centerx, y=current_y)
        screen.blit(text_surface, text_rect)
        current_y += line_height


def draw_health_bar(screen, x, y, health, max_health=100):
    """Draw a health bar with glow effect and percentage text inside"""
    
    # Define a new font size for the health percentage text
    HEALTH_PERCENTAGE_FONT_SIZE = int(screen_height * 0.018)  # Adjust as needed
    
    # Load the font for health percentage text
    health_percentage_font = pygame.font.Font('Minigame5/PRESSSTART2P.ttf', HEALTH_PERCENTAGE_FONT_SIZE)

    # Define the health bar rectangle
    bar_rect = pygame.Rect(x - HEALTH_BAR_WIDTH // 2, y, HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT)
    
    # Calculate the width of the filled portion of the health bar
    health_width = (health / max_health) * HEALTH_BAR_WIDTH
    
    # Draw the glow effect for the health bar
    if health > 0:
        glow_color = SOFT_GREEN if health > 50 else DARK_RED
        glow = create_glow_surface(health_width, HEALTH_BAR_HEIGHT, glow_color)
        screen.blit(glow, (bar_rect.x - 5, bar_rect.y - 5))
    
    # Draw the health bar background
    pygame.draw.rect(screen, GRAY, bar_rect)
    
    # Draw the filled portion of the health bar
    if health > 0:
        health_color = SOFT_GREEN if health > 50 else DARK_RED
        pygame.draw.rect(screen, health_color, (bar_rect.x, bar_rect.y, health_width, HEALTH_BAR_HEIGHT))
    
    # Draw the border of the health bar
    pygame.draw.rect(screen, WHITE, bar_rect, 2)
    
    # Render health percentage text inside the health bar using the new font
    health_text = health_percentage_font.render(f"{int(health)}%", True, WHITE)
    text_rect = health_text.get_rect(center=(x, y + HEALTH_BAR_HEIGHT // 2))  # Center text vertically in the health bar
    screen.blit(health_text, text_rect)

def draw_feedback(screen, message, color):
    """Draw feedback message with glow effect"""
    text = game_fonts['large'].render(message, True, color)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height * 0.17))
    
    glow = create_glow_surface(text_rect.width + 20, text_rect.height + 10, color, 50)
    screen.blit(glow, (text_rect.x - 10, text_rect.y - 5))
    screen.blit(text, text_rect)

def draw_timer(screen, time_left, total_time):
    """Draw countdown timer with color gradient"""
    timer_width = int(screen_width * 0.15)
    timer_height = int(screen_height * 0.02)
    timer_x = screen_width - timer_width - 40
    timer_y = 100
    
    pygame.draw.rect(screen, GRAY, (timer_x, timer_y, timer_width, timer_height))
    
    time_ratio = max(0, min(time_left / total_time, 1))
    time_width = int(timer_width * time_ratio)
    
    time_color = (
        int(255 * (1 - time_ratio)),
        int(255 * time_ratio),
        0
    )
    
    pygame.draw.rect(screen, time_color, (timer_x, timer_y, time_width, timer_height))
    pygame.draw.rect(screen, WHITE, (timer_x, timer_y, timer_width, timer_height), 2)
    
    time_text = game_fonts['medium'].render(f"{int(time_left)}s", True, WHITE)
    text_rect = time_text.get_rect(center=(timer_x + timer_width // 2, timer_y - 25))
    screen.blit(time_text, text_rect)

def run_level(screen, level_num, questions, answers, time_limit, background):
    """Run a single level of the game"""
    start_time = time.time()
    positions = generate_random_positions(len(questions))
    
    left_rectangles = [{'rect': pygame.Rect(pos[0], pos[1], RECT_WIDTH, RECT_HEIGHT),
                        'text': questions[i], 
                        'matched': False,
                        'answer': answers[i]} 
                    for i, pos in enumerate(positions[:len(questions)])]
    
    right_rectangles = [{'rect': pygame.Rect(pos[0], pos[1], RECT_WIDTH, RECT_HEIGHT),
                        'text': answers[i], 
                        'matched': False} 
                        for i, pos in enumerate(positions[len(questions):])]
    
    selected_left = None
    selected_right = None
    matched_pairs = 0
    connections = []
    feedback_message = f"Level {level_num}: Match the pairs!"
    feedback_color = GOLD
    feedback_timer = pygame.time.get_ticks()
    player_health = 100
    opponent_health = 100
    game_over = False
    initial_message_shown = False
    
    total_matches_needed = len(questions)
    damage_per_hit = 100 / total_matches_needed  # This ensures even distribution
    clock = pygame.time.Clock()
    
    while True:
        current_time = time.time()
        time_left = max(0, time_limit - (current_time - start_time))
        
        screen.blit(background, (0, 0))
        draw_timer(screen, time_left, time_limit)
        
        if not initial_message_shown and pygame.time.get_ticks() - feedback_timer > 2000:
            feedback_message = "Pick a box from the left column"
            feedback_color = GOLD
            feedback_timer = pygame.time.get_ticks()
            initial_message_shown = True
        
        # Ensure opponent health is exactly 0 if all matches are complete
        if matched_pairs == len(questions):
            opponent_health = 0
        
        draw_health_bar(screen, screen_width * 0.12, screen_height * 0.4, player_health)
        draw_health_bar(screen, screen_width * 0.88, screen_height * 0.4, opponent_health)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            
            if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if selected_left is None:
                    for i, rect_info in enumerate(left_rectangles):
                        if rect_info['rect'].collidepoint(mouse_pos) and not rect_info['matched']:
                            selected_left = i
                            feedback_message = "Now select the matching definition"
                            feedback_color = GOLD
                            feedback_timer = pygame.time.get_ticks()
                            break
                
                if selected_right is None:
                    for i, rect_info in enumerate(right_rectangles):
                        if rect_info['rect'].collidepoint(mouse_pos) and not rect_info['matched']:
                            selected_right = i
                            
                            # Check for correct match
                            if right_rectangles[selected_right]['text'] == left_rectangles[selected_left]['answer']:
                                # Calculate damage - ensure it hits exactly 0 on final match
                                remaining_matches = total_matches_needed - matched_pairs
                                if remaining_matches == 1:  # If this is the last match
                                    opponent_health = 0  # Force to exactly 0
                                else:
                                    opponent_health = max(0, opponent_health - damage_per_hit)
                                
                                feedback_message = "Correct! Jacobo takes damage!"
                                feedback_color = SOFT_GREEN
                                left_rectangles[selected_left]['matched'] = True
                                right_rectangles[selected_right]['matched'] = True
                                matched_pairs += 1
                                connections.append((left_rectangles[selected_left]['rect'].center,
                                                    right_rectangles[selected_right]['rect'].center,
                                                    SOFT_GREEN))
                                
                                left_rectangles[selected_left]['glow'] = PURPLE_GLOW_COLOR
                                right_rectangles[selected_right]['glow'] = PURPLE_GLOW_COLOR
                            else:
                                # Wrong match damage calculation
                                player_health = max(0, player_health - (100 / (total_matches_needed + 2)))
                                feedback_message = "Wrong match! You take damage!"
                                feedback_color = DARK_RED
                                connections.append((left_rectangles[selected_left]['rect'].center,
                                                    right_rectangles[selected_right]['rect'].center,
                                                    DARK_RED))
                            
                            feedback_timer = pygame.time.get_ticks()
                            selected_left = None
                            selected_right = None
        
        # Draw connections
        for start, end, color in connections:
            pygame.draw.line(screen, (*color, 50), start, end, 6)
            pygame.draw.line(screen, color, start, end, 2)
        
        # Draw boxes
        for rect_info in left_rectangles + right_rectangles:
            if rect_info['matched']:
                glow_color = rect_info.get('glow', PURPLE_GLOW_COLOR)
                glow = create_glow_surface(RECT_WIDTH, RECT_HEIGHT, glow_color[:3], glow_color[3])
                screen.blit(glow, (rect_info['rect'].x - 5, rect_info['rect'].y - 5))
            pygame.draw.rect(screen, GRAY, rect_info['rect'])
            pygame.draw.rect(screen, WHITE, rect_info['rect'], 2)
            draw_text_in_rect(screen, rect_info['text'], rect_info['rect'])
        
        if selected_left is not None:
            glow = create_glow_surface(RECT_WIDTH, RECT_HEIGHT, GOLD)
            screen.blit(glow, (left_rectangles[selected_left]['rect'].x - 5, 
                            left_rectangles[selected_left]['rect'].y - 5))
        
        if feedback_message:
            draw_feedback(screen, feedback_message, feedback_color)
            if pygame.time.get_ticks() - feedback_timer > 2000 and not game_over:
                feedback_message = ""
        
        # Check end conditions
        if not game_over:
            if time_left <= 0:
                game_over = True
                feedback_message = "Time's up!"
                feedback_color = DARK_RED
            elif player_health <= 0:
                game_over = True
                player_health = 0
                feedback_message = "You've been defeated!"
                feedback_color = DARK_RED
            elif matched_pairs == len(questions):
                game_over = True
                opponent_health = 0  # Force opponent health to exactly 0
                feedback_message = "Level Complete!"
                feedback_color = SOFT_GREEN
        
        pygame.display.flip()
        clock.tick(60)
        
        if game_over:
            # Ensure one final frame is drawn with the correct health values
            screen.blit(background, (0, 0))
            draw_health_bar(screen, screen_width * 0.12, screen_height * 0.4, player_health)
            draw_health_bar(screen, screen_width * 0.88, screen_height * 0.4, opponent_health)
            draw_feedback(screen, feedback_message, feedback_color)
            pygame.display.flip()
            
            pygame.time.wait(2000)
            completion_time = time_limit - time_left
            return {
                'success': opponent_health <= 0 or matched_pairs == len(questions),
                'time': completion_time,
                'health': player_health
            }
    
    return None

def match_game():
    """Main game function with proper error handling"""
    try:
        # Initialize display
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Programming Quiz Battle")

        # Validate assets
        try:
            validate_assets()
        except FileNotFoundError as e:
            print(f"Error: Missing required assets - {e}")
            return False

        # Load background
        try:
            background = pygame.image.load('Minigame5/Jacobo Background.png')
            background = pygame.transform.scale(background, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading background: {e}")
            background = pygame.Surface((screen_width, screen_height))
            background.fill((40, 40, 40))

        running = True
        while running:
            try:
                # Run Level 1
                level1_results = run_level(screen, 1, questions_level1, answers_level1, 60, background)
                
                if level1_results is None:  # Window was closed
                    running = False
                    continue
                
                if level1_results['success']:
                    # Play transition based on completion time
                    if level1_results['time'] <= 30:
                        play_gif_sequence(screen, 'Minigame5/Jacobo Fast.gif', 2, player_health=level1_results['health'])
                        time_for_level2 = 45
                    else:
                        play_gif_sequence(screen, 'Minigame5/Jacobo Slow.gif', 2, player_health=level1_results['health'])
                        time_for_level2 = 30
                    
                    play_gif_sequence(screen, 'Minigame5/Jacobo Inst1.gif', 2, player_health=level1_results['health'])
                    play_gif_sequence(screen, 'Minigame5/Jacobo Inst2.gif', 2, player_health=level1_results['health'])
                    
                    # Run Level 2
                    level2_results = run_level(screen, 2, questions_level2, answers_level2, 
                                           time_for_level2, background)
                    
                    if level2_results is None:
                        running = False
                        continue
                    
                    if level2_results['success']:
                        play_gif_sequence(screen, 'Minigame5/Jacobo Win.gif', 3, player_health=level2_results['health'])
                        return True
                    else:
                        play_gif_sequence(screen, 'Minigame5/Jacobo Lost.gif', 3, player_health=level2_results['health'])
                        pygame.time.wait(2000)
                else:
                    play_gif_sequence(screen, 'Minigame5/Jacobo Lost.gif', 3, player_health=level1_results['health'])
                    pygame.time.wait(2000)
                
            except Exception as e:
                print(f"Error during gameplay: {e}")
                traceback.print_exc()
                pygame.time.wait(2000)
                continue

        return False

    except Exception as e:
        print(f"Critical error in match_game: {e}")
        traceback.print_exc()
        return False

def main():
    """Main function for minigame 5 with proper initialization and cleanup"""
    try:
        # Store original display settings
        original_dir = os.getcwd()
        original_display = None
        if pygame.display.get_surface():
            original_display = pygame.display.get_surface().copy()
            was_fullscreen = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
            original_resolution = pygame.display.get_surface().get_size()
            
        # Initialize pygame if needed
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(44100, -16, 2, 512)
            except pygame.error:
                print("Warning: Could not initialize sound mixer")
        
        # Run the game
        result = match_game()
        
        # Show completion message
        if result:
            screen = pygame.display.set_mode((screen_width, screen_height))
            screen.fill((0, 0, 0))
            font = pygame.font.SysFont('Bauhaus 93', 32)
            text = font.render("Challenge Complete! Returning to main game...", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_width//2, screen_height//2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            pygame.time.wait(1500)
        
        # Cleanup and return to original state
        if pygame.mixer.get_init():
            pygame.mixer.stop()
        
        # Restore original display if exists
        if original_display and original_resolution:
            try:
                if was_fullscreen:
                    screen = pygame.display.set_mode(original_resolution, pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(original_resolution)
                pygame.display.set_caption('Decoding Island')
            except pygame.error as e:
                print(f"Error restoring display: {e}")
                
        return result
        
    except Exception as e:
        print(f"Error in minigame 5: {e}")
        traceback.print_exc()
        return False
    finally:
        # Always restore original directory and cleanup
        if 'original_dir' in locals():
            os.chdir(original_dir)
        try:
            if pygame.mixer.get_init():
                pygame.mixer.stop()
                pygame.mixer.music.stop()
        except:
            pass

if __name__ == "__main__":
    main()