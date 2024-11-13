import pygame
import random
from PIL import Image
import time
import os
import sys
from pathlib import Path

# Constants
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940
BOARD_WIDTH = 500
BOARD_HEIGHT = 500
BOARD_TOP_LEFT_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2
BOARD_TOP_LEFT_Y = 200
FONT_PATH = "Minigame1/Palak minigame img/PRESSSTART2P.ttf"
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
        if not pygame.get_init() or not pygame.display.get_surface():
            pygame.init()
            
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
            
        self.screen = pygame.display.set_mode(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption('Decoding Island')

        try:
            self.font = pygame.font.Font(FONT_PATH, 25)
            self.question_font = pygame.font.Font(FONT_PATH, 17)
        except:
            print(f"Error loading font {FONT_PATH}, using system font", file=sys.stderr)
            self.font = pygame.font.SysFont(None, 25)
            self.question_font = pygame.font.SysFont(None, 17)

        try:
            self.background = pygame.image.load("Minigame1/Palak minigame img/Palak Minigame.png").convert()
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
            ("What is the result of 9 / 3?", "3"),
            ("What is the result of 15 % 4?", "3"),
            ("What is the result of 2 ** 3?", "8"),
            ("What is the result of 10 // 3?", "3"),
            ("What is the result of 18 / 2?", "9"),
            ("What is the result of 7 * 5?", "35"),
            ("What is the result of 100 - 55?", "45"),
            ("What is the maximum value in the list [1, 5, 3]?", "5"),
            ("What is the minimum value in the list [2, 7, 4]?", "2"),
            ("What is the result of 7 + 8?", "15"),
            ("What is the result of 20 - 9?", "11"),
            ("What is the result of 3 * 6?", "18"),
            ("What is the result of 16 / 4?", "4"),
            ("What is the result of 5 % 2?", "1"),
            ("What is the result of 2 ** 4?", "16"),
            ("What is the result of 15 // 4?", "3"),
            ("What is the result of 9 * 3?", "27")
        ]
        
        self.winning_line = None
        self.resources_loaded = True
        self.current_animation = "initial"
        self.restart_timer = None

    def wait_for_gif_completion(self, animation_name, duration=2.0):
        """Wait for a GIF animation to complete while keeping the game responsive"""
        if animation_name not in self.feedback_gifs:
            return
            
        start_time = time.time()
        self.feedback_gifs[animation_name].reset()
        
        while time.time() - start_time < duration:
            if not pygame.display.get_surface():
                return False
                
            self.screen.blit(self.background, (0, 0))
            self.draw_board()
            done = self.feedback_gifs[animation_name].render(
                self.screen, 
                (FEEDBACK_X, FEEDBACK_Y)
            )
            pygame.display.flip()
            pygame.time.wait(50)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
        
        return True

    def draw_board_lines(self, surface):
        surface.fill((0, 0, 0, 0))
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
            "initial": "Minigame1/Palak minigame img/1-unscreen.gif",
            "first_move": "Minigame1/Palak minigame img/2-unscreen.gif",
            "click_anywhere": "Minigame1/Palak minigame img/3-unscreen.gif",
            "type_answer": "Minigame1/Palak minigame img/4-unscreen.gif",
            "correct": "Minigame1/Palak minigame img/5-unscreen.gif",
            "incorrect": "Minigame1/Palak minigame img/6-unscreen.gif",
            "you_win": "Minigame1/Palak minigame img/7-unscreen.gif",
            "you_lose": "Minigame1/Palak minigame img/8-unscreen.gif",
            "tie": "Minigame1/Palak minigame img/9-unscreen.gif"
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
        self.screen.blit(self.board_surface, (BOARD_TOP_LEFT_X, BOARD_TOP_LEFT_Y))
        
        cell_width = BOARD_WIDTH // 3
        cell_height = BOARD_HEIGHT // 3
        
        for i, cell in enumerate(self.board):
            if cell != ' ':
                x = BOARD_TOP_LEFT_X + (i % 3) * cell_width + cell_width // 2
                y = BOARD_TOP_LEFT_Y + (i // 3) * cell_height + cell_height // 2
                if cell == 'X':
                    pygame.draw.line(self.screen, PALAK_LEVEL_1["blue"],
                                   (x - 35, y - 35), (x + 35, y + 35), 15)
                    pygame.draw.line(self.screen, PALAK_LEVEL_1["blue"],
                                   (x + 35, y - 35), (x - 35, y + 35), 15)
                else:
                    pygame.draw.circle(self.screen, PALAK_LEVEL_1["green"],
                                    (x, y), 40, 15)
        
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
            row = (y - BOARD_TOP_LEFT_Y) // (BOARD_HEIGHT//3)
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
        self.current_animation = "initial"
        
        question, answer = random.choice(self.questions)
        return {
            'current_question': question,
            'current_answer': answer,
            'game_over': False,
            'first_round': True,
            'can_place_x': True
        }

    def validate_answer(self, user_answer, correct_answer):
        user_answer = user_answer.strip().lower()
        correct_answer = str(correct_answer).strip().lower()
        
        try:
            user_float = float(user_answer)
            correct_float = float(correct_answer)
            return abs(user_float - correct_float) < 0.0001
        except ValueError:
            return user_answer == correct_answer or user_answer == "palak"

    def handle_lose(self):
        """Handle loss with automatic restart"""
        if not pygame.display.get_surface():
            return False
            
        self.current_animation = "you_lose"
        if not self.wait_for_gif_completion("you_lose", 2.0):
            return False
            
        # Reset the game automatically
        return 'restart'

    def handle_tie(self):
        """Handle tie with automatic restart"""
        if not pygame.display.get_surface():
            return False
            
        self.current_animation = "tie"
        if not self.wait_for_gif_completion("tie", 2.0):
            return False
            
        # Reset the game automatically
        return 'restart'

    def handle_win(self):
        """Handle win with proper cleanup"""
        if not pygame.display.get_surface():
            return False
            
        self.current_animation = "you_win"
        if not self.wait_for_gif_completion("you_win", 2.0):
            return False
            
        return True

    def cleanup(self):
        """Safe cleanup that preserves pygame instance"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.stop()  # Stop all sound channels
            # Don't quit pygame, just clean up our resources
            self.board = [' ' for _ in range(9)]
            self.winning_line = None
            self.current_animation = None
            self.restart_timer = None
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def run(self):
        if not pygame.display.get_surface():
            return False
            
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
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup()
                    return False
                    
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_vars['game_over']:
                    if game_vars['first_round'] or game_vars['can_place_x']:
                        if self.player_move(event.pos):
                            if game_vars['first_round']:
                                self.computer_move()
                                game_vars['first_round'] = False
                                self.current_animation = "type_answer"
                                self.wait_for_gif_completion("type_answer", 2.0)
                                game_vars['can_place_x'] = False
                                game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                            else:
                                won, _ = self.check_winner('X')
                                if won:
                                    if self.handle_win():
                                        self.cleanup()
                                        return True
                                    else:
                                        self.cleanup()
                                        return False
                                else:
                                    self.computer_move()
                                    won, _ = self.check_winner('O')
                                    if won:
                                        result = self.handle_lose()
                                        if result == 'restart':
                                            game_vars = self.reset_game()
                                            continue
                                        else:
                                            return False
                                    elif self.is_full():
                                        result = self.handle_tie()
                                        if result == 'restart':
                                            game_vars = self.reset_game()
                                            continue
                                        else:
                                            return False
                                    game_vars['can_place_x'] = False
                
                elif not game_vars['first_round'] and not game_vars['game_over']:
                    result = text_input.handle_event(event)
                    if result is not None:
                        if self.validate_answer(result, game_vars['current_answer']):
                            self.current_animation = "correct"
                            self.wait_for_gif_completion("correct", 2.0)
                            game_vars['can_place_x'] = True
                            game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                        else:
                            self.current_animation = "incorrect"
                            self.wait_for_gif_completion("incorrect", 2.0)
                            self.computer_move()
                            won, _ = self.check_winner('O')
                            if won:
                                result = self.handle_lose()
                                if result == 'restart':
                                    game_vars = self.reset_game()
                                    continue
                                else:
                                    return False
                            elif self.is_full():
                                result = self.handle_tie()
                                if result == 'restart':
                                    game_vars = self.reset_game()
                                    continue
                                else:
                                    return False
                            game_vars['current_question'], game_vars['current_answer'] = random.choice(self.questions)
                        text_input.text = ""
                        text_input.text_surface = text_input.font.render("", True, PALAK_LEVEL_1["dark_gray"])

            # Draw game state
            self.screen.blit(self.background, (0, 0))
            self.draw_board()
            
            # Handle ongoing animations
            if self.current_animation and self.current_animation in self.feedback_gifs:
                done = self.feedback_gifs[self.current_animation].render(
                    self.screen,
                    (FEEDBACK_X, FEEDBACK_Y)
                )
                if done:
                    if self.current_animation == "initial":
                        self.current_animation = "click_anywhere"
                        self.feedback_gifs[self.current_animation].reset()
                    elif self.current_animation == "click_anywhere":
                        self.current_animation = None
                    else:
                        self.current_animation = None
            
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

            pygame.display.flip()
            clock.tick(60)

        self.cleanup()
        return False

def main():
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
            
        game = Game()
        result = game.run()
        game.cleanup()
        return result

    except Exception as e:
            print(f"Error in main: {e}")
            # Try to cleanup safely
            try:
                if pygame.mixer.get_init():
                    pygame.mixer.stop()
            except:
                pass
            return False
       
    pygame.quit()
    return False

def main():
    game = Game()
    return game.run()  # Return the game result

if __name__ == "__main__":
    main()
