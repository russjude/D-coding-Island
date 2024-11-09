import pygame
import random
import time
from PIL import Image

# Initialize game engine
pygame.init()

# Set the desired resolution
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Define tile size based on background height
TILE_SIZE = SCREEN_HEIGHT // 36

# Colors
PALAK_LEVEL_1 = {
    "blue": (37, 56, 142),
    "light_green": (205, 215, 191),
    "dark_gray": (37, 34, 41),
    "green": (246, 195, 36),
    "red": (211, 117, 6),
    "white": (255, 255, 255)
}

# Game board layout settings - centered position
BOARD_WIDTH, BOARD_HEIGHT = 500, 500
BOARD_TOP_LEFT_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP_LEFT_Y = 200

# Text rendering setup
FONT_PATH = "Minigame1/Palak minigame img/PRESSSTART2P.ttf"
FONT = pygame.font.Font(FONT_PATH, 25)
QUESTION_FONT = pygame.font.Font(FONT_PATH, 17)
INPUT_FONT = pygame.font.Font(FONT_PATH, 17)

# Load and scale background
background_image = pygame.image.load("Minigame1/Palak minigame img/Palak Minigame.png")
background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

class GIFImage:
    def __init__(self, filename):
        try:
            self.filename = filename
            self.image = Image.open(filename)
            self.frames = []
            self.get_frames()
            self.cur = 0
            self.ptime = time.time()
            self.running = True
            self.breakpoint = len(self.frames)-1
            self.startpoint = 0
            self.reversed = False
            self.current_frame = 0
            self.total_frames = len(self.frames)
            self.time_delta = 1.0 / 30
            self.last_state = None
        except Exception as e:
            print(f"Error loading GIF {filename}: {e}")
            surface = pygame.Surface((200, 200))
            surface.fill((100, 100, 100))
            self.frames = [surface]
            self.total_frames = 1
            self.current_frame = 0
            self.time_delta = 1.0 / 30

    def get_frames(self):
        image = self.image
        
        if hasattr(image, "palette"):
            palette = image.palette.getdata()[1]
        else:
            palette = None
        
        try:
            while True:
                if image.mode == 'P':
                    if palette:
                        image.putpalette(palette)
                    converted = image.convert('RGBA')
                else:
                    converted = image.convert('RGBA')

                mode = converted.mode
                size = converted.size
                data = converted.tobytes()
                
                py_image = pygame.image.fromstring(data, size, mode).convert_alpha()
                py_image = pygame.transform.scale(py_image, (400, 400))
                
                self.frames.append(py_image)
                image.seek(image.tell() + 1)
        except EOFError:
            pass
        except Exception as e:
            print(f"Error processing frame: {e}")
            if not self.frames:
                surface = pygame.Surface((200, 200))
                surface.fill((100, 100, 100))
                self.frames = [surface]

    def render(self, screen, pos):
        if self.running and self.frames:
            current_time = time.time()
            if current_time - self.ptime > self.time_delta:
                self.ptime = current_time
                self.current_frame = (self.current_frame + 1) % self.total_frames
            
            if self.frames:
                frame = self.frames[self.current_frame]
                screen.blit(frame, pos)

    def reset(self):
        self.current_frame = 0
        self.ptime = time.time()

# Initialize feedback GIFs
def load_feedback_gifs():
    gifs = {}
    gif_paths = {
        "initial": "Minigame1/Palak minigame img/1-unscreen.gif",
        "first_move": "Minigame1/Palak minigame img/2-unscreen (1).gif",
        "click_anywhere": "Minigame1/Palak minigame img/3-unscreen (1).gif",
        "type_answer": "Minigame1/Palak minigame img/4-unscreen (1).gif",
        "correct": "Minigame1/Palak minigame img/5-unscreen (1).gif",
        "incorrect": "Minigame1/Palak minigame img/6-unscreen (1).gif",
        "you_win": "Minigame1/Palak minigame img/7-unscreen (1).gif",
        "you_lose": "Minigame1/Palak minigame img/8-unscreen (1).gif",
        "tie": "Minigame1/Palak minigame img/9-unscreen (1).gif"
    }
    
    for key, path in gif_paths.items():
        try:
            gifs[key] = GIFImage(path)
        except Exception as e:
            print(f"Failed to load GIF {path}: {e}")
            surface = pygame.Surface((200, 200))
            surface.fill((100, 100, 100))
            gifs[key] = type('DummyGIF', (), {
                'render': lambda s, screen, pos: screen.blit(surface, pos),
                'reset': lambda s: None
            })()
    
    return gifs

# Position for feedback GIFs
FEEDBACK_X = SCREEN_WIDTH - 420
FEEDBACK_Y = SCREEN_HEIGHT // 2 - 300

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

class TextInput:
    def __init__(self, x, y, width, height, font_size=17):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = pygame.font.Font(FONT_PATH, font_size)
        self.text = ""
        self.max_chars = 20  # Maximum characters allowed
        self.text_surface = self.font.render("", True, PALAK_LEVEL_1["dark_gray"])
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Only add new character if within max length and if it will fit in the box
                if len(self.text) < self.max_chars and event.unicode.isprintable():
                    test_text = self.text + event.unicode
                    test_surface = self.font.render(test_text, True, PALAK_LEVEL_1["dark_gray"])
                    if test_surface.get_width() <= self.rect.width - 40:  # Increased padding for centering
                        self.text += event.unicode
            
            # Update the text surface
            self.text_surface = self.font.render(self.text, True, PALAK_LEVEL_1["dark_gray"])
        return None

    def draw(self, screen):
        # Draw the text box
        pygame.draw.rect(screen, PALAK_LEVEL_1["white"], self.rect)
        pygame.draw.rect(screen, PALAK_LEVEL_1["dark_gray"], self.rect, 2)
        
        # Center the text both horizontally and vertically
        if self.text:
            text_width = self.text_surface.get_width()
            text_height = self.text_surface.get_height()
            text_x = self.rect.x + (self.rect.width - text_width) // 2
            text_y = self.rect.y + (self.rect.height - text_height) // 2
            screen.blit(self.text_surface, (text_x, text_y))

def draw_winning_line(indices):
    start_idx, end_idx = indices[0], indices[2]
    start_x = BOARD_TOP_LEFT_X + (start_idx % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
    start_y = BOARD_TOP_LEFT_Y + (start_idx // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
    end_x = BOARD_TOP_LEFT_X + (end_idx % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
    end_y = BOARD_TOP_LEFT_Y + (end_idx // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
    pygame.draw.line(screen, PALAK_LEVEL_1["red"], (start_x, start_y), (end_x, end_y), 10)

def draw_board():
    # Draw vertical and horizontal lines with increased thickness
    for row in range(1, 3):
        pygame.draw.line(screen, PALAK_LEVEL_1["dark_gray"], 
                        (BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y + row * BOARD_HEIGHT // 3), 
                        (BOARD_TOP_LEFT_X + BOARD_WIDTH, BOARD_TOP_LEFT_Y + row * BOARD_HEIGHT // 3), 6)
    for col in range(1, 3):
        pygame.draw.line(screen, PALAK_LEVEL_1["dark_gray"], 
                        (BOARD_TOP_LEFT_X + col * BOARD_WIDTH // 3, BOARD_TOP_LEFT_Y), 
                        (BOARD_TOP_LEFT_X + col * BOARD_WIDTH // 3, BOARD_TOP_LEFT_Y + BOARD_HEIGHT), 6)

    # Draw X's and O's with increased thickness
    for i, cell in enumerate(board):
        x = BOARD_TOP_LEFT_X + (i % 3) * BOARD_WIDTH // 3 + BOARD_WIDTH // 6
        y = BOARD_TOP_LEFT_Y + (i // 3) * BOARD_HEIGHT // 3 + BOARD_HEIGHT // 6
        if cell == 'X':
            pygame.draw.line(screen, PALAK_LEVEL_1["blue"], (x - 35, y - 35), (x + 35, y + 35), 15)
            pygame.draw.line(screen, PALAK_LEVEL_1["blue"], (x + 35, y - 35), (x - 35, y + 35), 15)
        elif cell == 'O':
            pygame.draw.circle(screen, PALAK_LEVEL_1["green"], (x, y), 40, 15)

def display_feedback_gif(gif_key, force_reset=False):
    if gif_key in feedback_gifs:
        gif = feedback_gifs[gif_key]
        if hasattr(gif, 'last_state') and (gif.last_state != gif_key or force_reset):
            gif.reset()
            gif.last_state = gif_key
        gif.render(screen, (FEEDBACK_X, FEEDBACK_Y))

def check_winner(player_symbol):
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
    return ' ' not in board

def player_move(pos):
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
    empty_spots = [i for i, spot in enumerate(board) if spot == ' ']
    if empty_spots:
        move = random.choice(empty_spots)
        board[move] = 'O'
        return True
    return False

def get_new_question():
    question, answer = random.choice(questions)
    return question, answer.lower()

def reset_game():
    global board
    board = [' ' for _ in range(9)]
    question, answer = get_new_question()
    return {
        'current_question': question,
        'current_answer': answer,
        'game_over': False,
        'first_round': True,
        'winning_line': None,
        'can_place_x': True,
        'current_feedback': "initial",
        'feedback_time': pygame.time.get_ticks(),
        'show_initial': True,
        'feedback_changed': False
    }

def main():
    global feedback_gifs
    feedback_gifs = load_feedback_gifs()
    
    clock = pygame.time.Clock()
    running = True
    game_vars = reset_game()
    FEEDBACK_DURATION = 2000
    END_GAME_DURATION = 3000
    INITIAL_DURATION = 3000
    end_game_time = None
    initial_start_time = pygame.time.get_ticks()
    last_feedback_change = pygame.time.get_ticks()

    # Create text input box
    text_input = TextInput(
        BOARD_TOP_LEFT_X + BOARD_WIDTH//2 - 150,
        BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 120,
        300,
        35
    )

    # Draw initial state immediately
    screen.blit(background_image, (0, 0))
    draw_board()
    pygame.display.flip()

    while running:
        current_time = pygame.time.get_ticks()
        
        if game_vars['show_initial']:
            if current_time - initial_start_time >= INITIAL_DURATION:
                game_vars['show_initial'] = False
                game_vars['current_feedback'] = "first_move"
                game_vars['feedback_changed'] = True
                last_feedback_change = current_time
            screen.blit(background_image, (0, 0))
            draw_board()
            display_feedback_gif("initial", game_vars['feedback_changed'])
            pygame.display.flip()
            clock.tick(60)
            continue

        # Reset feedback_changed flag after a delay
        if game_vars['feedback_changed'] and current_time - last_feedback_change >= FEEDBACK_DURATION:
            game_vars['feedback_changed'] = False

        if game_vars['game_over'] and end_game_time is None:
            end_game_time = current_time
            game_vars['feedback_changed'] = True
            last_feedback_change = current_time
        
        if end_game_time and current_time - end_game_time >= END_GAME_DURATION:
            game_vars = reset_game()
            end_game_time = None
            initial_start_time = current_time
            text_input = TextInput(
                BOARD_TOP_LEFT_X + BOARD_WIDTH//2 - 150,
                BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 120,
                300,
                35
            )
        
        # Render game elements
        screen.blit(background_image, (0, 0))
        draw_board()

        if game_vars['winning_line']:
            draw_winning_line(game_vars['winning_line'])

        if not game_vars['first_round'] and not game_vars['game_over']:
            question_surface = QUESTION_FONT.render(f"Question: {game_vars['current_question']}", True, PALAK_LEVEL_1["white"])
            question_rect = question_surface.get_rect(center=(BOARD_TOP_LEFT_X + BOARD_WIDTH//2, BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 100))
            screen.blit(question_surface, question_rect)
            text_input.draw(screen)

        display_feedback_gif(game_vars['current_feedback'], game_vars['feedback_changed'])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif not game_vars['first_round'] and not game_vars['game_over']:
                result = text_input.handle_event(event)
                if result is not None:  # Enter was pressed
                    if result.strip():
                        if result.strip().lower() == game_vars['current_answer']:
                            game_vars['current_feedback'] = "correct"
                            game_vars['feedback_changed'] = True
                            last_feedback_change = current_time
                            game_vars['can_place_x'] = True
                        else:
                            game_vars['current_feedback'] = "incorrect"
                            game_vars['feedback_changed'] = True
                            last_feedback_change = current_time
                            pygame.time.wait(1000)
                            computer_move()
                            won, line = check_winner('O')
                            if won:
                                game_vars['game_over'] = True
                                game_vars['winning_line'] = line
                                game_vars['current_feedback'] = "you_lose"
                                game_vars['feedback_changed'] = True
                                last_feedback_change = current_time
                            else:
                                game_vars['current_question'], game_vars['current_answer'] = get_new_question()
                        text_input = TextInput(
                            BOARD_TOP_LEFT_X + BOARD_WIDTH//2 - 150,
                            BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 120,
                            300,
                            35
                        )

            elif event.type == pygame.MOUSEBUTTONDOWN and not game_vars['game_over']:
                if game_vars['first_round'] or game_vars['can_place_x']:
                    if player_move(event.pos):
                        won, line = check_winner('X')
                        if won:
                            game_vars['game_over'] = True
                            game_vars['winning_line'] = line
                            game_vars['current_feedback'] = "you_win"
                            game_vars['feedback_changed'] = True
                            last_feedback_change = current_time
                        else:
                            computer_move()
                            won, line = check_winner('O')
                            if won:
                                game_vars['game_over'] = True
                                game_vars['winning_line'] = line
                                game_vars['current_feedback'] = "you_lose"
                                game_vars['feedback_changed'] = True
                                last_feedback_change = current_time
                            elif is_full():
                                game_vars['game_over'] = True
                                game_vars['current_feedback'] = "tie"
                                game_vars['feedback_changed'] = True
                                last_feedback_change = current_time
                        
                        if game_vars['first_round']:
                            game_vars['first_round'] = False
                            game_vars['can_place_x'] = False
                            game_vars['current_feedback'] = "type_answer"
                            game_vars['feedback_changed'] = True
                            last_feedback_change = current_time
                        else:
                            game_vars['can_place_x'] = False
                        
                        if not game_vars['game_over'] and not game_vars['first_round']:
                            game_vars['current_question'], game_vars['current_answer'] = get_new_question()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()