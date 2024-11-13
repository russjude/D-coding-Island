"""
mini-game3.py

A Rock Paper Scissors word collection game with improved transitions
and resource management.
"""

import pygame
import random
import time
import sys
import os

# Constants
WIDTH = 1539
HEIGHT = 940
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (122, 92, 72)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Technology-related word bank
TECH_WORDS = [
    "CODING", "PYTHON", "ROUTER", "SERVER", "BINARY",
    "GITHUB", "LINUX", "DOCKER", "CLOUD", "GAMING",
    "RUSSS"  # Master word
]

class WordGame:
    def __init__(self):
        self.reset()

    def reset(self):
        self.target_word = random.choice(TECH_WORDS)
        self.collected_letters = []
        self.displayed_word = ["_"] * len(self.target_word)
        self.guessing_phase = False
        self.attempts_left = 3
        self.current_guess = ""
        self.message = ""
        self.game_over = False
        self.won = False
        self.scrambled_letters = []

    def add_letter(self):
        available_positions = []
        for i, char in enumerate(self.target_word):
            if self.displayed_word[i] == "_":
                available_positions.append(i)
                
        if available_positions:
            pos = random.choice(available_positions)
            letter = self.target_word[pos]
            self.collected_letters.append(letter)
            self.displayed_word[pos] = letter
            self.scrambled_letters.append(letter)
            
            if len(self.collected_letters) >= len(self.target_word):
                self.guessing_phase = True
                random.shuffle(self.scrambled_letters)
            return True
        return False

    def get_scrambled_display(self):
        return " ".join(self.scrambled_letters)

    def check_guess(self, guess):
        guess = guess.upper().strip()
        target = self.target_word.upper().strip()
        
        if guess == target:
            self.won = True
            self.game_over = True
            self.message = "Congratulations! You won!"
            return True
        self.attempts_left -= 1
        if self.attempts_left == 0:
            self.game_over = True
            self.message = f"Game Over! The word was {self.target_word}"
        else:
            self.message = f"Wrong guess! {self.attempts_left} attempts left"
        return False

class GameState:
    def __init__(self):
        self.reset_game()
    
    def reset_game(self):
        self.player_choice = None
        self.computer_choice = None
        self.result_text = "Pick an option"
        self.showing_result = False
        self.result_timer = 0
        self.choice_made = False
        self.word_game = WordGame()
        self.swipe_direction = 1
        self.hand_position = 0

class Game:
    def __init__(self):
        # Initialize display only if needed
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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Decoding Island - Rock Paper Scissors")

        # Load resources
        self.load_resources()
        
        # Initialize game state
        self.game_state = GameState()
        self.clock = pygame.time.Clock()
        
        # Animation variables
        self.last_frame_change_time = pygame.time.get_ticks()
        self.frame_change_time = 200
        
        # Position settings
        self.setup_positions()

    def load_resources(self):
        """Load and initialize all game resources"""
        try:
            # Load fonts
            self.font = pygame.font.Font(None, 74)
            self.small_font = pygame.font.Font(None, 40)
            self.end_font = pygame.font.Font(None, 80)

            # Load background
            self.background_img = pygame.image.load("minigame3/BACKGROUND_IMAGE_1.png")
            self.background_img = pygame.transform.scale(self.background_img, (WIDTH, HEIGHT))

            # Scale settings
            scale_size = (225, 225)
            larger_scale_size = (300, 300)

            # Load and scale player images
            self.rock_img = pygame.transform.scale(
                pygame.image.load("minigame3/HUMAN_ROCK.png"), scale_size)
            self.paper_img = pygame.transform.scale(
                pygame.image.load("minigame3/HUMAN_PAPER.png"), scale_size)
            self.scissors_img = pygame.transform.scale(
                pygame.image.load("minigame3/HUMAN_SCISSORS.png"), scale_size)

            # Load and scale glowing images
            self.glow_rock_img = pygame.transform.scale(
                pygame.image.load("minigame3/GLOWING_HUMAN_ROCK.png"), larger_scale_size)
            self.glow_paper_img = pygame.transform.scale(
                pygame.image.load("minigame3/GLOWING_HUMAN_PAPER.png"), larger_scale_size)
            self.glow_scissors_img = pygame.transform.scale(
                pygame.image.load("minigame3/GLOWING_HUMAN_SCISSORS.png"), larger_scale_size)

            # Load and scale opponent images
            self.opponent_rock_img = pygame.transform.scale(
                pygame.image.load("minigame3/OPPONENT_ROCK.png"), scale_size)
            self.opponent_paper_img = pygame.transform.scale(
                pygame.image.load("minigame3/OPPONENT_PAPER.png"), scale_size)
            self.opponent_scissors_img = pygame.transform.scale(
                pygame.image.load("minigame3/OPPONENT_SCISSORS.png"), scale_size)

            # Load audio
            if pygame.mixer.get_init():
                try:
                    pygame.mixer.music.load("minigame3/BACKGROUND_MUSIC.mp3")
                    self.click_sound = pygame.mixer.Sound("minigame3/music/CLICK_SOUNDEFFECT.mp3")
                except pygame.error:
                    print("Warning: Could not load some audio files")

        except Exception as e:
            print(f"Error loading resources: {e}")
            raise

    def setup_positions(self):
        """Set up all position-related variables"""
        self.player_rock_pos = (WIDTH // 3 - 112.5, HEIGHT - 225)
        self.player_paper_pos = (WIDTH // 2 - 112.5, HEIGHT - 225)
        self.player_scissors_pos = (3 * WIDTH // 4.5 - 112.5, HEIGHT - 225)

        # Create hitboxes
        self.player_rock_rect = pygame.Rect(self.player_rock_pos, (225, 225))
        self.player_paper_rect = pygame.Rect(self.player_paper_pos, (225, 225))
        self.player_scissors_rect = pygame.Rect(self.player_scissors_pos, (225, 225))

        # Opponent settings
        self.opponent_base_pos = WIDTH // 2 - 112.5
        self.opponent_y_pos = 0

    def cleanup(self):
        """Safe cleanup that preserves pygame instance"""
        try:
            if pygame.mixer.get_init():
                pygame.mixer.stop()
                pygame.mixer.music.stop()
            
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

    def draw_word_progress(self):
        """Draw the word progress display"""
        box_width = 650
        box_height = 200
        box_x = WIDTH//2 - box_width//2
        box_y = HEIGHT//2 - 120
        
        progress_box = pygame.Surface((box_width, box_height))
        progress_box.fill(BLACK)
        progress_box.set_alpha(128)
        self.screen.blit(progress_box, (box_x, box_y))
        
        display_spaces = ["_" for _ in range(len(self.game_state.word_game.target_word))]
        for i, letter in enumerate(self.game_state.word_game.collected_letters):
            display_spaces[i] = letter
        
        letter_display = "  ".join(display_spaces)
        letter_surface = self.font.render(letter_display, True, WHITE)
        letter_rect = letter_surface.get_rect(
            center=(box_x + box_width//2, box_y + box_height//3))
        self.screen.blit(letter_surface, letter_rect)
        
        progress_text = f"Letters: {len(self.game_state.word_game.collected_letters)}/{len(self.game_state.word_game.target_word)}"
        progress_surface = self.small_font.render(progress_text, True, WHITE)
        progress_rect = progress_surface.get_rect(
            center=(box_x + box_width//2, box_y + 2*box_height//3))
        self.screen.blit(progress_surface, progress_rect)

    def draw_guessing_phase(self):
        """Draw the guessing phase interface"""
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        box_width = 800
        box_height = 400
        box_x = WIDTH//2 - box_width//2
        box_y = HEIGHT//2 - box_height//2
        
        guess_box = pygame.Surface((box_width, box_height))
        guess_box.fill(BLACK)
        guess_box.set_alpha(128)
        self.screen.blit(guess_box, (box_x, box_y))
        
        spacing = box_height // 6
        current_y = box_y + spacing
        
        # Draw scrambled letters
        scrambled_text = "  ".join(self.game_state.word_game.scrambled_letters)
        scrambled_surface = self.font.render(scrambled_text, True, WHITE)
        scrambled_rect = scrambled_surface.get_rect(center=(box_x + box_width//2, current_y))
        self.screen.blit(scrambled_surface, scrambled_rect)
        
        # Draw prompt
        current_y += spacing
        prompt_surface = self.small_font.render("Unscramble these letters!", True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(box_x + box_width//2, current_y))
        self.screen.blit(prompt_surface, prompt_rect)
        
        # Draw current guess
        current_y += spacing
        guess_text = f"Your guess: {self.game_state.word_game.current_guess}"
        guess_surface = self.font.render(guess_text, True, WHITE)
        guess_rect = guess_surface.get_rect(center=(box_x + box_width//2, current_y))
        self.screen.blit(guess_surface, guess_rect)
        
        # Draw attempts remaining
        current_y += spacing
        attempts_text = f"Attempts remaining: {self.game_state.word_game.attempts_left}"
        attempts_surface = self.small_font.render(attempts_text, True, WHITE)
        attempts_rect = attempts_surface.get_rect(center=(box_x + box_width//2, current_y))
        self.screen.blit(attempts_surface, attempts_rect)
        
        # Draw message if any
        if self.game_state.word_game.message:
            current_y += spacing
            message_surface = self.small_font.render(self.game_state.word_game.message, True, WHITE)
            message_rect = message_surface.get_rect(center=(box_x + box_width//2, current_y))
            self.screen.blit(message_surface, message_rect)

    def determine_winner(self, player, computer):
        """Determine the winner of the round"""
        if player == computer:
            return "tie"
        elif (player == "rock" and computer == "scissors") or \
             (player == "paper" and computer == "rock") or \
             (player == "scissors" and computer == "paper"):
            return "player"
        else:
            return "computer"

    def handle_events(self):
        """Handle all game events"""
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if self.game_state.word_game.game_over and event.key == pygame.K_SPACE:
                    return self.game_state.word_game.won
                elif self.game_state.word_game.guessing_phase:
                    if event.key == pygame.K_RETURN and self.game_state.word_game.current_guess:
                        self.game_state.word_game.check_guess(self.game_state.word_game.current_guess)
                        self.game_state.word_game.current_guess = ""
                    elif event.key == pygame.K_BACKSPACE:
                        self.game_state.word_game.current_guess = self.game_state.word_game.current_guess[:-1]
                    elif event.unicode.isalpha() and len(self.game_state.word_game.current_guess) < len(self.game_state.word_game.target_word):
                        self.game_state.word_game.current_guess += event.unicode.upper()

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_state.word_game.game_over and \
               not self.game_state.word_game.guessing_phase and not self.game_state.showing_result:
                mouse_pos = pygame.mouse.get_pos()
                self.handle_click(mouse_pos, current_time)

        return None

    def handle_click(self, mouse_pos, current_time):
        """Handle mouse click events"""
        if self.player_rock_rect.collidepoint(mouse_pos):
            self.game_state.player_choice = "rock"
        elif self.player_paper_rect.collidepoint(mouse_pos):
            self.game_state.player_choice = "paper"
        elif self.player_scissors_rect.collidepoint(mouse_pos):
            self.game_state.player_choice = "scissors"
        
        if self.game_state.player_choice:
            self.click_sound.play()
            self.game_state.computer_choice = random.choice(["rock", "paper", "scissors"])
            self.game_state.showing_result = True
            self.game_state.result_timer = current_time
            
            winner = self.determine_winner(self.game_state.player_choice, self.game_state.computer_choice)
            self.game_state.result_text = f"You chose {self.game_state.player_choice}. Opponent chose {self.game_state.computer_choice}."
            
            if winner == "player":
                letter_added = self.game_state.word_game.add_letter()
                if letter_added:
                    self.game_state.result_text += " You win! Letter added!"
                else:
                    self.game_state.result_text += " You win!"
            elif winner == "computer":
                self.game_state.result_text += " You lose!"
            else:
                self.game_state.result_text += " It's a tie!"
            
            if len(self.game_state.word_game.collected_letters) == len(self.game_state.word_game.target_word):
                self.game_state.word_game.guessing_phase = True
                self.game_state.result_text = "All letters collected! Time to guess the word!"

    def run(self):
        """Main game loop"""
        if not pygame.display.get_surface():
            return False

        # Start background music
        if pygame.mixer.get_init():
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)

        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle events
            result = self.handle_events()
            if result is not None:  # None means continue game, True/False means exit
                self.cleanup()
                return result

            # Draw game state
            self.screen.blit(self.background_img, (0, 0))
            
            if self.game_state.word_game.game_over:
                self.draw_game_over()
            elif self.game_state.word_game.guessing_phase:
                self.draw_guessing_phase()
            else:
                self.draw_game_state(current_time)

            # Update display
            pygame.display.flip()
            self.clock.tick(60)

        self.cleanup()
        return False

    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(BLACK)
        
        end_text = "GAME OVER"
        final_result = "YOU WIN!" if self.game_state.word_game.won else "YOU LOSE!"
        
        end_surface = self.end_font.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        self.screen.blit(end_surface, end_rect)

        final_surface = self.end_font.render(final_result, True, WHITE)
        final_rect = final_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        self.screen.blit(final_surface, final_rect)

        word_text = f"The word was: {self.game_state.word_game.target_word}"
        word_surface = self.small_font.render(word_text, True, WHITE)
        word_rect = word_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        self.screen.blit(word_surface, word_rect)

        restart_text = "PRESS SPACE TO RESTART"
        restart_surface = self.small_font.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
        self.screen.blit(restart_surface, restart_rect)

    def draw_game_state(self, current_time):
        """Draw main game state"""
        # Draw player choices
        self.screen.blit(self.rock_img, self.player_rock_pos)
        self.screen.blit(self.paper_img, self.player_paper_pos)
        self.screen.blit(self.scissors_img, self.player_scissors_pos)
        
        # Draw word progress
        self.draw_word_progress()
        
        # Draw result text
        if self.game_state.result_text:
            result_surface = self.small_font.render(self.game_state.result_text, True, WHITE)
            result_rect = result_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
            self.screen.blit(result_surface, result_rect)
        
        # Update and draw opponent
        self.update_opponent(current_time)

    def update_opponent(self, current_time):
        """Update and draw opponent state"""
        self.game_state.hand_position = self.opponent_base_pos + (25 * self.game_state.swipe_direction)
        
        if self.game_state.computer_choice:
            if self.game_state.computer_choice == "rock":
                opponent_hand_img = self.opponent_rock_img
            elif self.game_state.computer_choice == "paper":
                opponent_hand_img = self.opponent_paper_img
            else:
                opponent_hand_img = self.opponent_scissors_img
            
            opponent_hand_img_flipped = pygame.transform.flip(opponent_hand_img, False, True)
            self.screen.blit(opponent_hand_img_flipped, (self.game_state.hand_position, self.opponent_y_pos))
        elif not self.game_state.showing_result:
            opponent_hand_img_flipped = pygame.transform.flip(self.opponent_rock_img, False, True)
            self.screen.blit(opponent_hand_img_flipped, (self.opponent_base_pos, self.opponent_y_pos))
        
        # Draw glowing effect for player choice
        if self.game_state.player_choice and not self.game_state.showing_result:
            if self.game_state.player_choice == "rock":
                self.screen.blit(self.glow_rock_img, 
                               (self.player_rock_pos[0] - 37.5, self.player_rock_pos[1] - 37.5))
            elif self.game_state.player_choice == "paper":
                self.screen.blit(self.glow_paper_img,
                               (self.player_paper_pos[0] - 37.5, self.player_paper_pos[1] - 37.5))
            elif self.game_state.player_choice == "scissors":
                self.screen.blit(self.glow_scissors_img,
                               (self.player_scissors_pos[0] - 37.5, self.player_scissors_pos[1] - 37.5))

        # Handle result display timing
        if self.game_state.showing_result:
            if current_time - self.game_state.result_timer >= 1500:  # 1.5 seconds
                self.game_state.showing_result = False
                if not self.game_state.word_game.guessing_phase:
                    self.game_state.player_choice = None
                    self.game_state.computer_choice = None
                    self.game_state.result_text = "Pick an option"

        # Update hand swipe animation
        if current_time - self.last_frame_change_time >= self.frame_change_time:
            self.game_state.swipe_direction *= -1 if random.random() < 0.1 else 1
            self.last_frame_change_time = current_time

def main():
    """Main function with proper error handling"""
    try:
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
                pygame.mixer.music.stop()
            os.chdir(original_dir)
            return False
            
    except Exception as e:
        print(f"Error in main: {e}")
        # Try to cleanup safely
        if pygame.mixer.get_init():
            pygame.mixer.stop()
            pygame.mixer.music.stop()
        return False

if __name__ == "__main__":
    main()