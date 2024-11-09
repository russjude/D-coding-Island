import pygame
import random
import time
import sys

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen settings
WIDTH = 1539
HEIGHT = 940
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rock Paper Scissors Word Collection Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (122, 92, 72)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Font settings
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)
end_font = pygame.font.Font(None, 80)

# Load background image
background_img = pygame.image.load("minigame3/BACKGROUND_IMAGE_1.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

# Load images for player's rock, paper, scissors
rock_img = pygame.image.load("minigame3/HUMAN_ROCK.png")
paper_img = pygame.image.load("minigame3/HUMAN_PAPER.png")
scissors_img = pygame.image.load("minigame3/HUMAN_SCISSORS.png")

# Load glowing images
glow_rock_img = pygame.image.load("minigame3/GLOWING_HUMAN_ROCK.png")
glow_paper_img = pygame.image.load("minigame3/GLOWING_HUMAN_PAPER.png")
glow_scissors_img = pygame.image.load("minigame3/GLOWING_HUMAN_SCISSORS.png")

# Load opponent images
opponent_rock_img = pygame.image.load("minigame3/OPPONENT_ROCK.png")
opponent_paper_img = pygame.image.load("minigame3/OPPONENT_PAPER.png")
opponent_scissors_img = pygame.image.load("minigame3/OPPONENT_SCISSORS.png")

# Default images
default_player_image = rock_img
default_opponent_image = rock_img

# Load audio
pygame.mixer.music.load("minigame3/BACKGROUND_MUSIC.mp3")
click_sound = pygame.mixer.Sound("minigame3/music/CLICK_SOUNDEFFECT.mp3")

# Scale settings
scale_size = (225, 225)
larger_scale_size = (300, 300)

# Scale game icons
rock_img = pygame.transform.scale(rock_img, scale_size)
paper_img = pygame.transform.scale(paper_img, scale_size)
scissors_img = pygame.transform.scale(scissors_img, scale_size)
glow_rock_img = pygame.transform.scale(glow_rock_img, larger_scale_size)
glow_paper_img = pygame.transform.scale(glow_paper_img, larger_scale_size)
glow_scissors_img = pygame.transform.scale(glow_scissors_img, larger_scale_size)
opponent_rock_img = pygame.transform.scale(opponent_rock_img, scale_size)
opponent_paper_img = pygame.transform.scale(opponent_paper_img, scale_size)
opponent_scissors_img = pygame.transform.scale(opponent_scissors_img, scale_size)

# Position settings
player_rock_pos = (WIDTH // 3 - 112.5, HEIGHT - 225)
player_paper_pos = (WIDTH // 2 - 112.5, HEIGHT - 225)
player_scissors_pos = (3 * WIDTH // 4.5 - 112.5, HEIGHT - 225)

# Create hitboxes
player_rock_rect = pygame.Rect(player_rock_pos, scale_size)
player_paper_rect = pygame.Rect(player_paper_pos, scale_size)
player_scissors_rect = pygame.Rect(player_scissors_pos, scale_size)

# Opponent settings
opponent_base_pos = WIDTH // 2 - 112.5
opponent_y_pos = 0
hand_position = opponent_base_pos

# Technology-related word bank
TECH_WORDS = [
    "CODING", "PYTHON", "ROUTER", "SERVER", "BINARY",
    "GITHUB", "LINUX", "DOCKER", "CLOUD", "GAMING"
]

class WordGame:
    def __init__(self):
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
        # Directly check if we have positions left in the word
        available_positions = []
        for i, char in enumerate(self.target_word):
            if self.displayed_word[i] == "_":  # If position is empty
                available_positions.append(i)
                
        if available_positions:
            pos = random.choice(available_positions)
            letter = self.target_word[pos]
            self.collected_letters.append(letter)
            self.displayed_word[pos] = letter
            self.scrambled_letters.append(letter)
            
            # Check if this was the last letter we needed
            if len(self.collected_letters) >= len(self.target_word):
                self.guessing_phase = True
                random.shuffle(self.scrambled_letters)
            return True
        return False

    def get_scrambled_display(self):
        return " ".join(self.scrambled_letters)

    def check_guess(self, guess):
        # Make sure both strings are in uppercase and stripped of whitespace
        guess = guess.upper().strip()
        target = self.target_word.upper().strip()
        
        # Print for debugging
        print(f"Guess: '{guess}', Target: '{target}'")  # This will help us see what's being compared
        
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

def determine_winner(player, computer):
    if player == computer:
        return "tie"
    elif (player == "rock" and computer == "scissors") or \
         (player == "paper" and computer == "rock") or \
         (player == "scissors" and computer == "paper"):
        return "player"
    else:
        return "computer"
    
def draw_word_progress(screen, word_game):
    # Draw centered box - moved down
    box_width = 650
    box_height = 200
    box_x = WIDTH//2 - box_width//2
    box_y = HEIGHT//2 - 120  # Adjusted to be more centered
    
    # Draw the box
    progress_box = pygame.Surface((box_width, box_height))
    progress_box.fill(BLACK)
    progress_box.set_alpha(128)
    screen.blit(progress_box, (box_x, box_y))
    
    # Center letters in box (vertically and horizontally)
    display_spaces = ["_" for _ in range(len(word_game.target_word))]
    for i, letter in enumerate(word_game.collected_letters):
        display_spaces[i] = letter
    
    letter_display = "  ".join(display_spaces)
    letter_surface = font.render(letter_display, True, WHITE)
    letter_rect = letter_surface.get_rect()
    # Center horizontally and place 1/3 down in box
    letter_rect.centerx = box_x + box_width//2
    letter_rect.centery = box_y + box_height//3
    screen.blit(letter_surface, letter_rect)
    
    # Center progress counter at bottom of box
    progress_text = f"Letters: {len(word_game.collected_letters)}/{len(word_game.target_word)}"
    progress_surface = small_font.render(progress_text, True, WHITE)
    progress_rect = progress_surface.get_rect()
    # Center horizontally and place 2/3 down in box
    progress_rect.centerx = box_x + box_width//2
    progress_rect.centery = box_y + 2*box_height//3
    screen.blit(progress_surface, progress_rect)

def draw_guessing_phase(screen, word_game):
    # Draw semi-transparent background
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Draw centered box
    box_width = 800
    box_height = 400
    box_x = WIDTH//2 - box_width//2
    box_y = HEIGHT//2 - box_height//2
    
    guess_box = pygame.Surface((box_width, box_height))
    guess_box.fill(BLACK)
    guess_box.set_alpha(128)
    screen.blit(guess_box, (box_x, box_y))
    
    # Draw content with even spacing
    total_elements = 5  # Number of text elements
    spacing = box_height // (total_elements + 1)
    current_y = box_y + spacing
    
    # Draw scrambled letters
    scrambled_text = "  ".join(word_game.scrambled_letters)
    scrambled_surface = font.render(scrambled_text, True, WHITE)
    scrambled_rect = scrambled_surface.get_rect()
    scrambled_rect.centerx = box_x + box_width//2
    scrambled_rect.centery = current_y
    screen.blit(scrambled_surface, scrambled_rect)
    current_y += spacing
    
    # Draw prompt
    prompt_text = "Unscramble these letters!"
    prompt_surface = small_font.render(prompt_text, True, WHITE)
    prompt_rect = prompt_surface.get_rect()
    prompt_rect.centerx = box_x + box_width//2
    prompt_rect.centery = current_y
    screen.blit(prompt_surface, prompt_rect)
    current_y += spacing
    
    # Draw current guess
    guess_text = f"Your guess: {word_game.current_guess}"
    guess_surface = font.render(guess_text, True, WHITE)
    guess_rect = guess_surface.get_rect()
    guess_rect.centerx = box_x + box_width//2
    guess_rect.centery = current_y
    screen.blit(guess_surface, guess_rect)
    current_y += spacing
    
    # Draw attempts
    attempts_text = f"Attempts remaining: {word_game.attempts_left}"
    attempts_surface = small_font.render(attempts_text, True, WHITE)
    attempts_rect = attempts_surface.get_rect()
    attempts_rect.centerx = box_x + box_width//2
    attempts_rect.centery = current_y
    screen.blit(attempts_surface, attempts_rect)
    current_y += spacing
    
    # Draw message if exists
    if word_game.message:
        message_surface = small_font.render(word_game.message, True, WHITE)
        message_rect = message_surface.get_rect()
        message_rect.centerx = box_x + box_width//2
        message_rect.centery = current_y
        screen.blit(message_surface, message_rect)

# Start background music
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Initialize game state
game_state = GameState()

# Animation variables
last_frame_change_time = pygame.time.get_ticks()
frame_change_time = 200

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    current_time = pygame.time.get_ticks()
    screen.fill(BROWN)
    screen.blit(background_img, (0, 0))

    if game_state.word_game.game_over:
        # Game over screen
        screen.fill(BLACK)
        end_text = "GAME OVER"
        final_result = "YOU WIN!" if game_state.word_game.won else "YOU LOSE!"
        
        end_surface = end_font.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(end_surface, end_rect)

        final_surface = end_font.render(final_result, True, WHITE)
        final_rect = final_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(final_surface, final_rect)

        # Show the correct word
        word_text = f"The word was: {game_state.word_game.target_word}"
        word_surface = small_font.render(word_text, True, WHITE)
        word_rect = word_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(word_surface, word_rect)

        restart_text = "PRESS SPACE TO RESTART"
        restart_surface = small_font.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150))
        screen.blit(restart_surface, restart_rect)
        
    elif game_state.word_game.guessing_phase:
        draw_guessing_phase(screen, game_state.word_game)
        
    else:  # Regular gameplay
        # Draw RPS game elements
        screen.blit(rock_img, player_rock_pos)
        screen.blit(paper_img, player_paper_pos)
        screen.blit(scissors_img, player_scissors_pos)
        
        # Draw word progress in center
        draw_word_progress(screen, game_state.word_game)
        
        # Draw result text below the box (only draw it here, not in draw_word_progress)
        if game_state.result_text:
            result_surface = small_font.render(game_state.result_text, True, WHITE)
            result_rect = result_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))  # Adjusted position
            screen.blit(result_surface, result_rect)
        
        # Draw opponent's hand with animation
        game_state.hand_position = opponent_base_pos + (25 * game_state.swipe_direction)
        if game_state.computer_choice:
            if game_state.computer_choice == "rock":
                opponent_hand_img = opponent_rock_img
            elif game_state.computer_choice == "paper":
                opponent_hand_img = opponent_paper_img
            else:
                opponent_hand_img = opponent_scissors_img
            
            opponent_hand_img_flipped = pygame.transform.flip(opponent_hand_img, False, True)
            screen.blit(opponent_hand_img_flipped, (game_state.hand_position, opponent_y_pos))
        elif not game_state.showing_result:
            opponent_hand_img_flipped = pygame.transform.flip(opponent_rock_img, False, True)
            screen.blit(opponent_hand_img_flipped, (opponent_base_pos, opponent_y_pos))
        
        # Show glowing effect if choice made
        if game_state.player_choice and not game_state.showing_result:
            if game_state.player_choice == "rock":
                screen.blit(glow_rock_img, (player_rock_pos[0] - 37.5, player_rock_pos[1] - 37.5))
            elif game_state.player_choice == "paper":
                screen.blit(glow_paper_img, (player_paper_pos[0] - 37.5, player_paper_pos[1] - 37.5))
            elif game_state.player_choice == "scissors":
                screen.blit(glow_scissors_img, (player_scissors_pos[0] - 37.5, player_scissors_pos[1] - 37.5))

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_state.word_game.game_over and event.key == pygame.K_SPACE:
                game_state = GameState()  # Reset game
            elif game_state.word_game.guessing_phase:
                if event.key == pygame.K_RETURN and game_state.word_game.current_guess:
                    print(f"Attempting guess: {game_state.word_game.current_guess}")  # Debug print
                    game_state.word_game.check_guess(game_state.word_game.current_guess)
                    game_state.word_game.current_guess = ""
                elif event.key == pygame.K_BACKSPACE:
                    game_state.word_game.current_guess = game_state.word_game.current_guess[:-1]
                elif event.unicode.isalpha() and len(game_state.word_game.current_guess) < len(game_state.word_game.target_word):
                    game_state.word_game.current_guess += event.unicode.upper()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_state.word_game.game_over and not game_state.word_game.guessing_phase and not game_state.showing_result:
            mouse_pos = pygame.mouse.get_pos()
            
            if player_rock_rect.collidepoint(mouse_pos):
                game_state.player_choice = "rock"
                game_state.computer_choice = random.choice(["rock", "paper", "scissors"])
                click_sound.play()
                game_state.showing_result = True
                game_state.result_timer = current_time
            elif player_paper_rect.collidepoint(mouse_pos):
                game_state.player_choice = "paper"
                game_state.computer_choice = random.choice(["rock", "paper", "scissors"])
                click_sound.play()
                game_state.showing_result = True
                game_state.result_timer = current_time
            elif player_scissors_rect.collidepoint(mouse_pos):
                game_state.player_choice = "scissors"
                game_state.computer_choice = random.choice(["rock", "paper", "scissors"])
                click_sound.play()
                game_state.showing_result = True
                game_state.result_timer = current_time
            
            if game_state.player_choice:
                winner = determine_winner(game_state.player_choice, game_state.computer_choice)
                game_state.result_text = f"You chose {game_state.player_choice}. Opponent chose {game_state.computer_choice}."
                
                if winner == "player":
                    letter_added = game_state.word_game.add_letter()
                    if letter_added:
                        game_state.result_text += " You win! Letter added!"
                    else:
                        game_state.result_text += " You win!"
                elif winner == "computer":
                    game_state.result_text += " You lose!"
                else:
                    game_state.result_text += " It's a tie!"
                
                # Check if all letters are collected
                if len(game_state.word_game.collected_letters) == len(game_state.word_game.target_word):
                    game_state.word_game.guessing_phase = True
                    game_state.result_text = "All letters collected! Time to guess the word!"

    # Handle result display timing
    if game_state.showing_result:
        if current_time - game_state.result_timer >= 1500:  # 1.5 seconds
            game_state.showing_result = False
            if not game_state.word_game.guessing_phase:
                game_state.player_choice = None
                game_state.computer_choice = None
                game_state.result_text = "Pick an option"

    # Update hand swipe animation
    if current_time - last_frame_change_time >= frame_change_time:
        game_state.swipe_direction *= -1 if random.random() < 0.1 else 1
        last_frame_change_time = current_time

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()