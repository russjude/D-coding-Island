"""
mini-game1.py

Primary Author: Palak Lakhani and Jessica Ng

An educational game combining Tic-Tac-Toe with Python programming questions.
Players must correctly answer programming questions to place their 'X' marks,
while competing against a computer opponent. Features include a graphical interface,
automated opponent moves, and immediate feedback on answers. The game includes
questions about Python operators, basic calculations, and programming concepts.
"""

import pygame
import random
import time

# Initialize game engine
pygame.init()

# Set the desired resolution
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Define tile size based on background height
TILE_SIZE = SCREEN_HEIGHT // 36  # 36 is the number of tiles vertically

# Load and scale the background for each level
level_backgrounds = {}
for i in range(1, 6):  # Assuming you have 5 levels
    original_bg = pygame.image.load(f'Level Data/Level Image/LEVEL{i}.png')
    level_backgrounds[i] = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# You may need to adjust other elements (buttons, player size, etc.) to fit the new resolution
# For example:
# start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, start_btn)
# restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)
PALAK_LEVEL_1 = {
    "blue": (46, 161, 213),      # Player X color
    "light_green": (205, 215, 191), # Background accent
    "dark_gray": (37, 34, 41),    # Text and lines
    "green": (84, 159, 99),      # Player O color
    "red": (255, 99, 71),        # Winning line
    "white": (255, 255, 255)     # Input box
}

# Game board layout settings
# Adjust board dimensions and positioning
BOARD_WIDTH, BOARD_HEIGHT = 500, 500  # Reduced from 700x700
BOARD_TOP_LEFT_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP_LEFT_Y = 200  # Fixed position from top

# Text rendering setup
FONT = pygame.font.Font(None, 36)  # Reduced from 48
QUESTION_FONT = pygame.font.Font(None, 32)  # Reduced from 36
INPUT_FONT = pygame.font.Font(None, 36)  # Reduced from 48

# Load and scale background
background_image = pygame.image.load("Minigame1/bg.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Dictionary of game state feedback images
feedback_images = {
    "first_move": pygame.image.load("Minigame1/firstmove.png"),
    "click_anywhere": pygame.image.load("Minigame1/clickanywhere.png"),
    "type_answer": pygame.image.load("Minigame1/typeanswer.png"),
    "correct": pygame.image.load("Minigame1/correct.png"),
    "incorrect": pygame.image.load("Minigame1/incorrect.png"),
    "you_win": pygame.image.load("Minigame1/youwin.png"),
    "you_lose": pygame.image.load("Minigame1/youlose.png"),
    "tie": pygame.image.load("Minigame1/tie.png")
}

# Scale feedback images to smaller size
for key in feedback_images:
    feedback_images[key] = pygame.transform.scale(feedback_images[key], (700, 80))  # Reduced from 900x100

# Initialize game board and question bank
board = [' ' for _ in range(9)]
questions = [
    ("What operator is used to check for equality?", "=="),
    ("What symbol is used to start a comment in Python?", "#"),
    ("What is the output of 2 ** 3 in Python?", "8"),
    ("What is the result of 10//3?", "3"),
    ("What is the result of 2**3 ?", "8"),
    ("What operator is used to concatenate two strings in Python?", "+"),
    ("What is the result of 7 * 0?", "0"),
    ("What is the result of 2 ** 0?", "1"),
    ("What is the result of 7 % 2?", "1"),
    ("What is the result of 8 % 3?", "2"),
    ("What is the result of 25 // 4?", "6"),
    ("What is the result of 18 / 3 + 2?", "8.0")
]

# Set up display window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tic Tac Toe with Quiz")

def draw_winning_line(indices):
    """Draw a line through winning combination of moves"""
    start_idx, end_idx = indices[0], indices[2]
    start_x = BOARD_TOP_LEFT_X + (start_idx % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
    start_y = BOARD_TOP_LEFT_Y + (start_idx // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
    end_x = BOARD_TOP_LEFT_X + (end_idx % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
    end_y = BOARD_TOP_LEFT_Y + (end_idx // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
    pygame.draw.line(screen, PALAK_LEVEL_1["red"], (start_x, start_y), (end_x, end_y), 10)

# Modify draw_board function
def draw_board():
    """Draw game board grid and current player moves"""
    # Draw vertical and horizontal grid lines
    for row in range(1, 3):
        pygame.draw.line(screen, PALAK_LEVEL_1["dark_gray"], 
                        (BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y + row * BOARD_HEIGHT // 3), 
                        (BOARD_TOP_LEFT_X + BOARD_WIDTH, BOARD_TOP_LEFT_Y + row * BOARD_HEIGHT // 3), 4)  # Reduced line thickness
    for col in range(1, 3):
        pygame.draw.line(screen, PALAK_LEVEL_1["dark_gray"], 
                        (BOARD_TOP_LEFT_X + col * BOARD_WIDTH // 3, BOARD_TOP_LEFT_Y), 
                        (BOARD_TOP_LEFT_X + col * BOARD_WIDTH // 3, BOARD_TOP_LEFT_Y + BOARD_HEIGHT), 4)

    # Render X's and O's with adjusted sizes
    for i, cell in enumerate(board):
        x = BOARD_TOP_LEFT_X + (i % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
        y = BOARD_TOP_LEFT_Y + (i // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
        if cell == 'X':
            pygame.draw.line(screen, PALAK_LEVEL_1["blue"], (x - 25, y - 25), (x + 25, y + 25), 6)  # Reduced size and thickness
            pygame.draw.line(screen, PALAK_LEVEL_1["blue"], (x + 25, y - 25), (x - 25, y + 25), 6)
        elif cell == 'O':
            pygame.draw.circle(screen, PALAK_LEVEL_1["green"], (x, y), 30, 6)  # Reduced size and thickness

def display_feedback_image(image_key):
    """Display appropriate feedback image based on game state"""
    if image_key in feedback_images:
        image = feedback_images[image_key]
        image_rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100))  # Adjusted position
        screen.blit(image, image_rect)

def check_winner(player_symbol):
    """Check for winning combinations on the board"""
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]              # Diagonals
    ]
    for condition in win_conditions:
        if all(board[i] == player_symbol for i in condition):
            return True, condition
    return False, None

def is_full():
    """Check if board is completely filled"""
    return ' ' not in board

def player_move(pos):
    """Process player's attempt to place X on board"""
    x, y = pos
    if BOARD_TOP_LEFT_X <= x < BOARD_TOP_LEFT_X + BOARD_WIDTH and BOARD_TOP_LEFT_Y <= y < BOARD_TOP_LEFT_Y + BOARD_HEIGHT:
        col = (x - BOARD_TOP_LEFT_X) // (BOARD_WIDTH // 3)
        row = (y - BOARD_TOP_LEFT_Y) // (BOARD_HEIGHT // 3)
        idx = row * 3 + col
        if board[idx] == ' ':
            board[idx] = 'X'
            return True
    return False

def computer_move():
    """Execute random computer move in empty spot"""
    empty_spots = [i for i, spot in enumerate(board) if spot == ' ']
    if empty_spots:
        move = random.choice(empty_spots)
        board[move] = 'O'
        return True
    return False

def get_new_question():
    """Select random question from question bank"""
    question, answer = random.choice(questions)
    return question, answer.lower()

def reset_game():
    """Initialize new game state"""
    global board
    board = [' ' for _ in range(9)]
    question, answer = get_new_question()
    return {
        'current_question': question,
        'current_answer': answer,
        'game_over': False,
        'first_round': True,
        'winning_line': None,
        'input_text': "",
        'can_place_x': True,
        'current_feedback': "first_move",
        'feedback_time': pygame.time.get_ticks()
    }

def main():
    """Main game loop handling game states and user interaction"""
    clock = pygame.time.Clock()
    running = True
    game_vars = reset_game()
    FEEDBACK_DURATION = 2000
    END_GAME_DURATION = 3000
    end_game_time = None

    while running:
        current_time = pygame.time.get_ticks()
        
        # Handle game reset timing
        if game_vars['game_over'] and end_game_time is None:
            end_game_time = current_time
        
        if end_game_time and current_time - end_game_time >= END_GAME_DURATION:
            game_vars = reset_game()
            end_game_time = None
        
        # Render game elements
        screen.blit(background_image, (0, 0))
        draw_board()

        if game_vars['winning_line']:
            draw_winning_line(game_vars['winning_line'])

        # Update feedback display based on game state
        if game_vars['game_over']:
            display_feedback_image(game_vars['current_feedback'])
        elif game_vars['first_round']:
            display_feedback_image("first_move")
        elif game_vars['can_place_x']:
            display_feedback_image("click_anywhere")
        elif current_time - game_vars['feedback_time'] < FEEDBACK_DURATION:
            display_feedback_image(game_vars['current_feedback'])
        else:
            display_feedback_image("type_answer")

        # Display question interface after first move
        if not game_vars['first_round'] and not game_vars['game_over']:
            question_surface = QUESTION_FONT.render(f"Question: {game_vars['current_question']}", True, PALAK_LEVEL_1["dark_gray"])
            question_rect = question_surface.get_rect(center=(SCREEN_WIDTH // 2, BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 50))  # Adjusted position
            screen.blit(question_surface, question_rect)

            # Adjust input box size and position
            input_box = pygame.Rect(SCREEN_WIDTH // 2 - 150, BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 80, 300, 35)  # Adjusted size and position
            pygame.draw.rect(screen, PALAK_LEVEL_1["white"], input_box)
            pygame.draw.rect(screen, PALAK_LEVEL_1["dark_gray"], input_box, 2)
            input_surface = INPUT_FONT.render(game_vars['input_text'], True, PALAK_LEVEL_1["dark_gray"])
            screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN and not game_vars['first_round'] and not game_vars['game_over']:
                # Handle answer submission and input
                if event.key == pygame.K_RETURN:
                    if game_vars['input_text'].strip():
                        if game_vars['input_text'].strip().lower() == game_vars['current_answer']:
                            game_vars['current_feedback'] = "correct"
                            game_vars['feedback_time'] = current_time
                            game_vars['can_place_x'] = True
                        else:
                            game_vars['current_feedback'] = "incorrect"
                            game_vars['feedback_time'] = current_time
                            pygame.time.wait(1000)
                            computer_move()
                            won, line = check_winner('O')
                            if won:
                                game_vars['game_over'] = True
                                game_vars['winning_line'] = line
                                game_vars['current_feedback'] = "you_lose"
                            else:
                                game_vars['current_question'], game_vars['current_answer'] = get_new_question()
                        game_vars['input_text'] = ""
                
                elif event.key == pygame.K_BACKSPACE:
                    game_vars['input_text'] = game_vars['input_text'][:-1]
                
                elif event.unicode.isprintable():
                    game_vars['input_text'] += event.unicode

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_vars['game_over']:
                # Handle board clicks and move placement
                if game_vars['first_round'] or game_vars['can_place_x']:
                    if player_move(event.pos):
                        won, line = check_winner('X')
                        if won:
                            game_vars['game_over'] = True
                            game_vars['winning_line'] = line
                            game_vars['current_feedback'] = "you_win"
                            return True  # Return True when player wins
                        else:
                            computer_move()
                            won, line = check_winner('O')
                            if won:
                                game_vars['game_over'] = True
                                game_vars['winning_line'] = line
                                game_vars['current_feedback'] = "you_lose"
                                return False  # Return False when player loses
                            elif is_full():
                                game_vars['game_over'] = True
                                game_vars['current_feedback'] = "tie"
                        
                        if game_vars['first_round']:
                            game_vars['first_round'] = False
                            game_vars['can_place_x'] = False
                        else:
                            game_vars['can_place_x'] = False
                        
                        if not game_vars['game_over'] and not game_vars['first_round']:
                            game_vars['current_question'], game_vars['current_answer'] = get_new_question()
                            game_vars['input_text'] = ""

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()