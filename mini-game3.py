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
pygame.display.set_caption("Rock Paper Scissors Decoding Game")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BROWN = (122, 92, 72)

# Font settings
font = pygame.font.Font(None, 74)
small_font = pygame.font.Font(None, 40)
end_font = pygame.font.Font(None, 80)

# Center positions
center_x = WIDTH // 2 - 192 // 2
top_y = 20
center_x_round = WIDTH // 2 - 60 // 2

# Load background image
background_img = pygame.image.load("/Users/russeljudeb.rafanan/Documents/GitHub/D-coding-Island/Minigame3/BACKGROUND_IMAGE.png")
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

# Load UI images
score_img = pygame.image.load("minigame3/score/SCORE.png").convert_alpha()
round_img = pygame.image.load("minigame3/score/ROUND.png").convert_alpha()

# Load character animations
player_img = {
    1: pygame.image.load("minigame3/score/PLAYER.png").convert_alpha(),
    2: pygame.image.load("minigame3/score/PLAYER2.png").convert_alpha(),
    3: pygame.image.load("minigame3/score/PLAYER3.png").convert_alpha()
}

opponent_img = {
    1: pygame.image.load("minigame3/score/OPPONENT.png").convert_alpha(),
    2: pygame.image.load("minigame3/score/OPPONENT2.png").convert_alpha()
}

# Load score images
points_imgs = {
    1: pygame.image.load("minigame3/score/ONE.png").convert_alpha(),
    2: pygame.image.load("minigame3/score/TWO.png").convert_alpha(),
    3: pygame.image.load("minigame3/score/THREE.png").convert_alpha()
}

# Load round images
round_imgs = {
    1: pygame.image.load("minigame3/score/ROUND_1OF5.png").convert_alpha(),
    2: pygame.image.load("minigame3/score/ROUND_2OF5.png").convert_alpha(),
    3: pygame.image.load("minigame3/score/ROUND_3OF5.png").convert_alpha(),
    4: pygame.image.load("minigame3/score/ROUND_4OF5.png").convert_alpha(),
    5: pygame.image.load("minigame3/score/ROUND_5OF5.png").convert_alpha()
}

# Scale settings
small_size = (128, 64)
round_size = (192, 57)
smaller_size = (int(small_size[0] * 0.2), int(small_size[1] * 0.2))
larger_size = (300, 300)
scale_size = (225, 225)
larger_scale_size = (300, 300)

# Scale all images
score_img = pygame.transform.scale(score_img, smaller_size)
round_img = pygame.transform.scale(round_img, round_size)

# Scale score and round images
for i in points_imgs:
    points_imgs[i] = pygame.transform.scale(points_imgs[i], smaller_size)
for i in round_imgs:
    round_imgs[i] = pygame.transform.scale(round_imgs[i], (75, 25))

# Scale character images
for i in opponent_img:
    opponent_img[i] = pygame.transform.scale(opponent_img[i], larger_size)
for i in player_img:
    player_img[i] = pygame.transform.scale(player_img[i], larger_size)

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
player_rock_pos = (WIDTH // 4 - 112.5, HEIGHT - 225)
player_paper_pos = (WIDTH // 2 - 112.5, HEIGHT - 225)
player_scissors_pos = (3 * WIDTH // 4 - 112.5, HEIGHT - 225)

# Create hitboxes
player_rock_rect = pygame.Rect(player_rock_pos, scale_size)
player_paper_rect = pygame.Rect(player_paper_pos, scale_size)
player_scissors_rect = pygame.Rect(player_scissors_pos, scale_size)

# Opponent settings
opponent_base_pos = WIDTH // 2 - 112.5
opponent_y_pos = 0  # Reset to original position
hand_position = opponent_base_pos

# Word list
words = [
    "DECODE", "PYTHON", "GADGET", "OUTPUT", "WIZARD", "FACTOR", "STRING", "IMPORT",
    "UPDATE", "BUFFER", "SYNTAX", "METHOD", "PACKET", "SOCKET", "SCRIPT", "WIDGET"
]

# Game state variables
choices = ["rock", "paper", "scissors"]
player_choice = None
computer_choice = None
result_text = "Pick an option"
round_wins = 0
computer_wins = 0
current_round = 1
rounds_played = 0
max_rounds = 5
game_over = False
current_word = random.choice(words)
revealed_word = ["_"] * 6
available_hints = list(range(6))
given_hints = []
guesses_remaining = 3
in_guessing_phase = False
guess_input = ""
guess_message = ""
showing_result = False
result_timer = 0
choice_made = False
swipe_direction = 1

# Animation variables
current_opponent_frame = 1
current_player_frame = 1
last_frame_change_time = pygame.time.get_ticks()
last_player_frame_change_time = pygame.time.get_ticks()
frame_change_time = 200
player_frame_change_time = 200

def reset_game():
    global round_wins, computer_wins, current_round, result_text, game_over
    global computer_choice, player_choice, current_word, revealed_word
    global available_hints, given_hints, guesses_remaining, in_guessing_phase
    global guess_input, guess_message, showing_result, result_timer, choice_made, rounds_played
    
    round_wins = 0
    computer_wins = 0
    current_round = 1
    rounds_played = 0
    result_text = "Pick an option"
    game_over = False
    computer_choice = None
    player_choice = None
    showing_result = False
    result_timer = 0
    choice_made = False
    
    # Reset word guessing game
    current_word = random.choice(words)
    revealed_word = ["_"] * 6
    available_hints = list(range(6))
    given_hints = []
    guesses_remaining = 3
    in_guessing_phase = False
    guess_input = ""
    guess_message = ""

def determine_winner(player, computer):
    if player == computer:
        return "tie"
    elif (player == "rock" and computer == "scissors") or \
         (player == "paper" and computer == "rock") or \
         (player == "scissors" and computer == "paper"):
        return "player"
    else:
        return "computer"

# Start background music
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.5)

# Animation  variables for player
current_player_frame = 1
last_player_frame_change_time = pygame.time.get_ticks()
player_frame_change_time = 200
picked_state = 0

# Game loop
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    screen.fill(BROWN)
    screen.blit(background_img, (0, 0))

    if not game_over and not in_guessing_phase:
        # Draw base RPS game elements
        screen.blit(rock_img, player_rock_pos)
        screen.blit(paper_img, player_paper_pos)
        screen.blit(scissors_img, player_scissors_pos)
        
        # Draw characters
        screen.blit(player_img[current_player_frame], (10, 0))
        screen.blit(opponent_img[current_opponent_frame], (WIDTH - 300, -30))

        # Draw result text
        result_surface = small_font.render(result_text, True, WHITE)
        result_rect = result_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        screen.blit(result_surface, result_rect)

        if current_round in round_imgs:
            screen.blit(round_imgs[current_round], (537, 80))

        # Show glowing effect if choice made
        if player_choice and not showing_result:
            if player_choice == "rock":
                screen.blit(glow_rock_img, (player_rock_pos[0] - 37.5, player_rock_pos[1] - 37.5))
            elif player_choice == "paper":
                screen.blit(glow_paper_img, (player_paper_pos[0] - 37.5, player_paper_pos[1] - 37.5))
            elif player_choice == "scissors":
                screen.blit(glow_scissors_img, (player_scissors_pos[0] - 37.5, player_scissors_pos[1] - 37.5))

        hand_position += swipe_direction * 5
        if hand_position >= WIDTH // 2 + 25:
            swipe_direction = -1
        elif hand_position <= opponent_base_pos - 130:
            swipe_direction = 1

        # Draw opponent's hand only during RPS phase with fixed position
        if computer_choice:
            if computer_choice == "rock":
                opponent_hand_img = opponent_rock_img
            elif computer_choice == "paper":
                opponent_hand_img = opponent_paper_img
            elif computer_choice == "scissors":
                opponent_hand_img = opponent_scissors_img
            
            opponent_hand_img_flipped = pygame.transform.flip(opponent_hand_img, False, True)
            screen.blit(opponent_hand_img_flipped, (hand_position, opponent_y_pos))
        elif not showing_result:
            # Show default hand in fixed position
            opponent_hand_img_flipped = pygame.transform.flip(opponent_rock_img, False, True)
            screen.blit(opponent_hand_img_flipped, (opponent_base_pos, opponent_y_pos))

    elif in_guessing_phase:
        # Draw word guessing interface
        wins_text = f"You won {round_wins} out of 5 rounds!"
        wins_surface = small_font.render(wins_text, True, WHITE)
        wins_rect = wins_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 - 50))
        screen.blit(wins_surface, wins_rect)

        word_display = " ".join(revealed_word)
        word_surface = font.render(word_display, True, WHITE)
        word_rect = word_surface.get_rect(center=(WIDTH // 2, HEIGHT // 3 + 50))
        screen.blit(word_surface, word_rect)

        guess_prompt = f"Enter your guess ({guesses_remaining} tries left):"
        prompt_surface = small_font.render(guess_prompt, True, WHITE)
        prompt_rect = prompt_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        screen.blit(prompt_surface, prompt_rect)

        input_surface = font.render(guess_input, True, WHITE)
        input_rect = input_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(input_surface, input_rect)

        if guess_message:
            message_surface = small_font.render(guess_message, True, WHITE)
            message_rect = message_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 200))
            screen.blit(message_surface, message_rect)

    elif game_over:
        # Game over screen
        screen.fill(BLACK)
        end_text = "GAME OVER"
        final_result = "YOU WIN!" if guesses_remaining > 0 else "YOU LOSE!"
        
        end_surface = end_font.render(end_text, True, WHITE)
        end_rect = end_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
        screen.blit(end_surface, end_rect)

        final_surface = end_font.render(final_result, True, WHITE)
        final_rect = final_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
        screen.blit(final_surface, final_rect)

        restart_text = "PRESS BACKSPACE TO RESTART"
        restart_surface = small_font.render(restart_text, True, WHITE)
        restart_rect = restart_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        screen.blit(restart_surface, restart_rect)

    # Draw UI elements (adjusted positions)
    screen.blit(round_img, (center_x, top_y))
    if round_wins in points_imgs:
        screen.blit(points_imgs[round_wins], (WIDTH - 100, 20))  # Moved to top right
    if current_round in round_imgs:
        screen.blit(round_imgs[current_round], (center_x + 55, top_y + 55))

    #event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_BACKSPACE:
                reset_game()
            elif in_guessing_phase:
                if event.key == pygame.K_RETURN and guess_input:
                    if guess_input.upper() == current_word:
                        guess_message = "Congratulations! You won!"
                        game_over = True
                        pygame.time.delay(1000)
                    else:
                        guesses_remaining -= 1
                        if guesses_remaining > 0:
                            guess_message = f"Wrong guess! {guesses_remaining} tries remaining"
                        else:
                            guess_message = "Game Over! Starting new game..."
                            pygame.time.delay(1000)
                            reset_game()
                    guess_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    guess_input = guess_input[:-1]
                elif event.unicode.isalpha() and len(guess_input) < 6:
                    guess_input += event.unicode.upper()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not in_guessing_phase and not showing_result and not choice_made:
            mouse_pos = pygame.mouse.get_pos()
            if player_rock_rect.collidepoint(mouse_pos):
                player_choice = "rock"
                computer_choice = random.choice(choices)
                click_sound.play()
                choice_made = True
                showing_result = True
                result_timer = current_time
            elif player_paper_rect.collidepoint(mouse_pos):
                player_choice = "paper"
                computer_choice = random.choice(choices)
                click_sound.play()
                choice_made = True
                showing_result = True
                result_timer = current_time
            elif player_scissors_rect.collidepoint(mouse_pos):
                player_choice = "scissors"
                computer_choice = random.choice(choices)
                click_sound.play()
                choice_made = True
                showing_result = True
                result_timer = current_time

            if player_choice:
                result_text = f"You chose {player_choice}. Opponent chose {computer_choice}."
                winner = determine_winner(player_choice, computer_choice)

                if winner == "player":
                    round_wins += 1
                    result_text += " You win this round!"
                    if available_hints and round_wins <= 5:
                        hint_pos = random.choice(available_hints)
                        revealed_word[hint_pos] = current_word[hint_pos]
                        available_hints.remove(hint_pos)
                        given_hints.append(current_word[hint_pos])
                    rounds_played += 1
                    current_round += 1
                        
                elif winner == "computer":
                    computer_wins += 1
                    result_text += " Opponent wins this round!"
                    rounds_played += 1
                    current_round += 1
                
                else:  # Handle tie
                    result_text += " It's a tie!"
                    pygame.time.delay(500)
                    player_choice = None
                    computer_choice = None
                    showing_result = False
                    choice_made = False

                # Check if 5 rounds have been played
                if rounds_played >= 5:
                    showing_result = False
                    in_guessing_phase = True
                    result_text = f"5 rounds completed! You won {round_wins} rounds. Now guess the word!"
                    pygame.time.delay(1000)

    # Handle result display timing
    if showing_result:
        if current_time - result_timer >= 1500:  # Show result for 1.5 seconds
            showing_result = False
            choice_made = False
            if not in_guessing_phase:
                player_choice = None
                computer_choice = None
                result_text = "Pick an option"

    # Animation updates
    if not showing_result and not in_guessing_phase:
        # Update opponent animation
        if current_time - last_frame_change_time >= frame_change_time:
            current_opponent_frame = 2 if current_opponent_frame == 1 else 1
            last_frame_change_time = current_time

        # Update player animation
        if current_time - last_player_frame_change_time >= player_frame_change_time:
            current_player_frame = 2 if current_player_frame == 1 else 1
            last_player_frame_change_time = current_time

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()