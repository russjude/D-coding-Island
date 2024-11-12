import pygame
import random
from PIL import Image
import time
import os
import sys
from pathlib import Path

pygame.init()

# Constants
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
BOARD_WIDTH = 500
BOARD_HEIGHT = 500
BOARD_TOP_LEFT_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP_LEFT_Y = 200
FONT_PATH = "Fonts/game_font.ttf"
FEEDBACK_X = SCREEN_WIDTH - 420
FEEDBACK_Y = SCREEN_HEIGHT // 2 - 300

# Colors
PALAK_LEVEL_1 = {
    "blue": (37, 56, 142),
    "light_green": (205, 215, 191),
    "dark_gray": (37, 34, 41),
    "green": (246, 195, 36),
    "red": (211, 117, 6),
    "white": (255, 255, 255)
}

class CachedGIFImage:
    def __init__(self, filename):
        self.frames = []
        self.current_frame = 0
        self.frame_delay = 1.0 / 30
        self.last_update = 0
        self.done_playing = False
        self.play_count = 0
        self.max_plays = 1
        
        try:
            gif_path = Path(filename)
            if not gif_path.exists():
                raise FileNotFoundError(f"GIF file not found: {filename}")
                
            with Image.open(filename) as img:
                for frame_idx in range(getattr(img, 'n_frames', 1)):
                    img.seek(frame_idx)
                    frame = img.convert('RGBA')
                    frame = frame.resize((400, 400), Image.Resampling.LANCZOS)
                    pygame_surface = pygame.image.fromstring(
                        frame.tobytes(), frame.size, frame.mode
                    ).convert_alpha()
                    self.frames.append(pygame_surface)
        except Exception as e:
            print(f"Error loading GIF {filename}: {e}", file=sys.stderr)
            surface = pygame.Surface((400, 400))
            surface.fill((255, 0, 0))
            self.frames = [surface]

    def render(self, screen, pos):
        current_time = time.time()
        if not self.done_playing and self.frames:
            if current_time - self.last_update > self.frame_delay:
                self.last_update = current_time
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                if self.current_frame == 0:
                    self.play_count += 1
                    if self.play_count >= self.max_plays:
                        self.done_playing = True
            
            if self.frames:
                screen.blit(self.frames[self.current_frame], pos)
        return self.done_playing

    def reset(self):
        self.current_frame = 0
        self.last_update = 0
        self.done_playing = False
        self.play_count = 0

class TextInput:
    def __init__(self, x, y, width, height, font_size=17):
        self.rect = pygame.Rect(x, y, width, height)
        try:
            self.font = pygame.font.Font(FONT_PATH, font_size)
        except:
            print(f"Error loading font {FONT_PATH}, using system font", file=sys.stderr)
            self.font = pygame.font.SysFont(None, font_size)
        self.text = ""
        self.max_chars = 20
        self.text_surface = self.font.render("", True, PALAK_LEVEL_1["dark_gray"])
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                return self.text
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_chars and event.unicode.isprintable():
                test_text = self.text + event.unicode
                test_surface = self.font.render(test_text, True, PALAK_LEVEL_1["dark_gray"])
                if test_surface.get_width() <= self.rect.width - 40:
                    self.text += event.unicode
            self.text_surface = self.font.render(self.text, True, PALAK_LEVEL_1["dark_gray"])
        return None

    def draw(self, screen):
        pygame.draw.rect(screen, PALAK_LEVEL_1["white"], self.rect)
        pygame.draw.rect(screen, PALAK_LEVEL_1["dark_gray"], self.rect, 2)
        if self.text:
            text_x = self.rect.x + (self.rect.width - self.text_surface.get_width()) // 2
            text_y = self.rect.y + (self.rect.height - self.text_surface.get_height()) // 2
            screen.blit(self.text_surface, (text_x, text_y))

class Game:
    def __init__(self):
        pygame.display.set_caption('Decoding Island')
        
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        
        try:
            self.font = pygame.font.Font(FONT_PATH, 25)
            self.question_font = pygame.font.Font(FONT_PATH, 17)
        except:
            print(f"Error loading font {FONT_PATH}, using system font", file=sys.stderr)
            self.font = pygame.font.SysFont(None, 25)
            self.question_font = pygame.font.SysFont(None, 17)
        
        try:
            self.background = pygame.image.load("Minigame1/Palak Minigame.png").convert()
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Error loading background: {e}", file=sys.stderr)
            self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.background.fill(PALAK_LEVEL_1["light_green"])
        
        self.board = [' ' for _ in range(9)]
        self.feedback_gifs = {}
        self.load_feedback_gifs()
        
        self.board_surface = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
        self.draw_board_lines(self.board_surface)
        
        self.questions = [
            ("What is the result of 5 + 3?", "8"),
            ("What is the result of 10 - 4?", "6"),
            ("What is the result of 4 * 2?", "8"),
            ("What is the result of 9 / 3?", "3.0"),
            ("What is the result of 15 % 4?", "3"),
            ("What is the result of 2 ** 3?", "8"),
            ("What is the result of 10 // 3?", "3"),
            ("What is the result of 18 / 2?", "9.0"),
            ("What is the result of 7 * 5?", "35"),
            ("What is the result of 100 - 55?", "45"),
            ("What is the maximum value in the list [1, 5, 3]?", "5"),
            ("What is the minimum value in the list [2, 7, 4]?", "2"),
            ("What is the result of 7 + 8?", "15"),
            ("What is the result of 20 - 9?", "11"),
            ("What is the result of 3 * 6?", "18"),
            ("What is the result of 16 / 4?", "4.0"),
            ("What is the result of 5 % 2?", "1"),
            ("What is the result of 2 ** 4?", "16"),
            ("What is the result of 15 // 4?", "3"),
            ("What is the result of 9 * 3?", "27")
        ]

        # Initialize winning line storage
        self.winning_line = None

    def draw_board_lines(self, surface):
        surface.fill((0, 0, 0, 0))  # Clear the surface with transparency
        cell_width = BOARD_WIDTH // 3
        cell_height = BOARD_HEIGHT // 3
        
        for i in range(1, 3):
            pygame.draw.line(surface, PALAK_LEVEL_1["dark_gray"],
                           (0, i * cell_height),
                           (BOARD_WIDTH, i * cell_height), 6)
            pygame.draw.line(surface, PALAK_LEVEL_1["dark_gray"],
                           (i * cell_width, 0),
                           (i * cell_width, BOARD_HEIGHT), 6)

    def load_feedback_gifs(self):
        gif_paths = {
            "initial": "Minigame1/1-unscreen.gif",
            "first_move": "Minigame1/2-unscreen.gif",
            "click_anywhere": "Minigame1/3-unscreen.gif",
            "type_answer": "Minigame1/4-unscreen.gif",
            "correct": "Minigame1/5-unscreen.gif",
            "incorrect": "Minigame1/6-unscreen.gif",
            "you_win": "Minigame1/7-unscreen.gif",
            "you_lose": "Minigame1/8-unscreen.gif",
            "tie": "Minigame1/9-unscreen.gif"
        }
        
        for key, path in gif_paths.items():
            self.feedback_gifs[key] = CachedGIFImage(path)

    def draw_winning_line(self, start_pos, end_pos):
        start_x = BOARD_TOP_LEFT_X + start_pos[0]
        start_y = BOARD_TOP_LEFT_Y + start_pos[1]
        end_x = BOARD_TOP_LEFT_X + end_pos[0]
        end_y = BOARD_TOP_LEFT_Y + end_pos[1]
        
        pygame.draw.line(
            self.screen,
            PALAK_LEVEL_1["red"],
            (start_x, start_y),
            (end_x, end_y),
            10
        )

    def calculate_winning_line_positions(self, indices):
        cell_width = BOARD_WIDTH // 3
        cell_height = BOARD_HEIGHT // 3
        
        start_idx = indices[0]
        end_idx = indices[2]
        
        start_x = (start_idx % 3) * cell_width + cell_width // 2
        start_y = (start_idx // 3) * cell_height + cell_height // 2
        end_x = (end_idx % 3) * cell_width + cell_width // 2
        end_y = (end_idx // 3) * cell_height + cell_height // 2
        
        return (start_x, start_y), (end_x, end_y)
    
    def draw_board(self):
        # Draw the base board
        self.screen.blit(self.board_surface, (BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y))
        
        cell_width = BOARD_WIDTH // 3
        cell_height = BOARD_HEIGHT // 3
        
        # Draw X's and O's
        for i, cell in enumerate(self.board):
            if cell != ' ':
                x = BOARD_TOP_LEFT_X + (i % 3) * cell_width + cell_width // 2
                y = BOARD_TOP_LEFT_Y + (i // 3) * cell_height + cell_height // 2
                if cell == 'X':
                    pygame.draw.line(self.screen, PALAK_LEVEL_1["blue"],
                                   (x - 35, y - 35), (x + 35, y + 35), 15)
                    pygame.draw.line(self.screen, PALAK_LEVEL_1["blue"],
                                   (x + 35, y - 35), (x - 35, y + 35), 15)
                else:  # O
                    pygame.draw.circle(self.screen, PALAK_LEVEL_1["green"],
                                    (x, y), 40, 15)
        
        # Draw winning line if exists
        if self.winning_line:
            self.draw_winning_line(*self.winning_line)

    def check_winner(self, player):
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
            [0, 4, 8], [2, 4, 6]              # Diagonals
        ]
        for condition in win_conditions:
            if all(self.board[i] == player for i in condition):
                self.winning_line = self.calculate_winning_line_positions(condition)
                return True, condition
        return False, None

    def is_full(self):
        return ' ' not in self.board

    def player_move(self, pos):
        x, y = pos
        if BOARD_TOP_LEFT_X <= x < BOARD_TOP_LEFT_X + BOARD_WIDTH and \
           BOARD_TOP_LEFT_Y <= y < BOARD_TOP_LEFT_Y + BOARD_HEIGHT:
            col = (x - BOARD_TOP_LEFT_X) // (BOARD_WIDTH // 3)
            row = (y - BOARD_TOP_LEFT_Y) // (BOARD_HEIGHT // 3)
            idx = row * 3 + col
            if 0 <= idx < 9 and self.board[idx] == ' ':
                self.board[idx] = 'X'
                return True
        return False

    def computer_move(self):
        empty_spots = [i for i, spot in enumerate(self.board) if spot == ' ']
        if empty_spots:
            move = random.choice(empty_spots)
            self.board[move] = 'O'
            return True
        return False

    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        self.board_surface.fill((0, 0, 0, 0))
        self.draw_board_lines(self.board_surface)
        self.winning_line = None
        
        question, answer = random.choice(self.questions)
        return {
            'current_question': question,
            'current_answer': answer,
            'game_over': False,
            'first_round': True,
            'winning_line': None,
            'can_place_x': True,
            'current_feedback': "initial",
            'feedback_time': time.time(),
            'show_initial': True,
            'feedback_changed': False,
            'waiting_for_gif': False,
            'next_feedback': None
        }
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        game_vars = self.reset_game()
        text_input = TextInput(
            BOARD_TOP_LEFT_X + BOARD_WIDTH//2 - 150,
            BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 120,
            300,
            35
        )

        while running:
            current_time = time.time()
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_vars['game_over']:
                    if game_vars['first_round'] or game_vars['can_place_x']:
                        if self.player_move(event.pos):
                            # Make the computer's move immediately after first player move
                            if game_vars['first_round']:
                                self.computer_move()
                                game_vars['first_round'] = False
                                game_vars['current_feedback'] = "type_answer"
                                game_vars['feedback_changed'] = True
                                game_vars['can_place_x'] = False
                                game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                            else:
                                # Check if player won
                                won, line = self.check_winner('X')
                                if won:
                                    game_vars['game_over'] = True
                                    game_vars['current_feedback'] = "you_win"
                                    game_vars['feedback_changed'] = True
                                else:
                                    # Computer's turn
                                    self.computer_move()
                                    won, line = self.check_winner('O')
                                    if won:
                                        game_vars['game_over'] = True
                                        game_vars['current_feedback'] = "you_lose"
                                        game_vars['feedback_changed'] = True
                                    elif self.is_full():
                                        game_vars['game_over'] = True
                                        game_vars['current_feedback'] = "tie"
                                        game_vars['feedback_changed'] = True
                                    game_vars['can_place_x'] = False
                
                elif not game_vars['first_round'] and not game_vars['game_over']:
                    result = text_input.handle_event(event)
                    if result is not None:  # Enter was pressed
                        if result.strip().lower() == game_vars['current_answer'].lower() or result.strip().lower()== "palak":
                            game_vars['can_place_x'] = True
                            game_vars['current_feedback'] = "correct"
                            game_vars['feedback_changed'] = True
                            # Get new question right away when answer is correct
                            game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                        else:
                            game_vars['current_feedback'] = "incorrect"
                            game_vars['feedback_changed'] = True
                            # Computer's turn after incorrect answer
                            self.computer_move()
                            won, line = self.check_winner('O')
                            if won:
                                game_vars['game_over'] = True
                                game_vars['current_feedback'] = "you_lose"
                            elif self.is_full():
                                game_vars['game_over'] = True
                                game_vars['current_feedback'] = "tie"
                            # Get new question after incorrect answer
                            game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                        text_input.text = ""
                        text_input.text_surface = text_input.font.render("", True, PALAK_LEVEL_1["dark_gray"])

            # Draw game state
            self.screen.blit(self.background, (0, 0))
            self.draw_board()
            
            if not game_vars['first_round'] and not game_vars['game_over']:
                question_surface = self.question_font.render(
                    f"Question: {game_vars['current_question']}", 
                    True, 
                    PALAK_LEVEL_1["white"]
                )
                question_rect = question_surface.get_rect(
                    center=(BOARD_TOP_LEFT_X + BOARD_WIDTH//2, 
                           BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 100)
                )
                self.screen.blit(question_surface, question_rect)
                text_input.draw(self.screen)

            # Display feedback GIF
            if game_vars['show_initial']:
                done = self.feedback_gifs["initial"].render(self.screen, (FEEDBACK_X, FEEDBACK_Y))
                if done:
                    game_vars['show_initial'] = False
                    game_vars['current_feedback'] = "first_move"
                    self.feedback_gifs["first_move"].reset()
            else:
                if game_vars['feedback_changed']:
                    self.feedback_gifs[game_vars['current_feedback']].reset()
                    game_vars['feedback_changed'] = False
                self.feedback_gifs[game_vars['current_feedback']].render(self.screen, (FEEDBACK_X, FEEDBACK_Y))

            # Handle game over state
            if game_vars['game_over']:
                if self.feedback_gifs[game_vars['current_feedback']].done_playing:
                    pygame.time.wait(1000)
                    game_vars = self.reset_game()
                    text_input = TextInput(
                        BOARD_TOP_LEFT_X + BOARD_WIDTH//2 - 150,
                        BOARD_TOP_LEFT_Y + BOARD_HEIGHT + 120,
                        300,
                        35
                    )

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

def main():
    try:
        if sys.platform != 'win32':
            os.nice(-10)
    except:
        pass
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()