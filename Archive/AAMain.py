import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path
import time
from Archive.Wordle import main as wordle_game  # Import the Wordle game
import pytmx

pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1000
screen_height = 1000

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Platformer')

#define font
font = pygame.font.SysFont('Bauhaus 93', 70)
font_score = pygame.font.SysFont('Bauhaus 93', 30)


#define game variables
tile_size = 50
game_over = 0
main_menu = True
level = 1
max_levels = 7
score = 0

# In your settings.py or at the top of your main file
TILE_SIZE = 64  # TMX file uses 64x64 tiles
GRID_WIDTH = 36  # TMX map is 36 tiles wide
GRID_HEIGHT = 22  # TMX map is 22 tiles high
SCREEN_WIDTH = TILE_SIZE * GRID_WIDTH  # 36 * 64 = 2304
SCREEN_HEIGHT = TILE_SIZE * GRID_HEIGHT  # 22 * 64 = 1408


KEYS_REQUIRED = {
    1: 3,  # Level 1 requires 2 keys
    2: 2,  # Level 2 requires 3 keys
    3: 4,  # Level 3 requires 4 keys
    4: 5,  # Level 4 requires 5 keys
    5: 6,  # Level 5 requires 6 keys
    6: 7,  # Level 6 requires 7 keys
    7: 10   # Level 7 requires 8 keys
}

LEVEL_SOUNDTRACKS = {
    1: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 01 Harvest Tyrant- ORCHARD OGRE.mp3',
    2: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 02 Porcine Pilot- HOGWYLLD.mp3',
    3: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 03 Maladaptive Mallard- KWACKPOT.mp3',
    4: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 04 Corrupted Comrade- CITRUS KNIGHT.mp3',
    5: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 05 ______REST ZONE______.mp3',
    6: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 06 Mini Boss- MINNIE BUS.mp3',
    7: 'Louie Zong - BOSS RUSH/Louie Zong - BOSS RUSH - 07 Digital Goblin- LAN GNOME.mp3'
}

# Store original spawn point
original_spawn_x = 100
original_spawn_y = screen_height - 130

#define colours
white = (255, 255, 255)
blue = (0, 0, 255)



#load images
sun_img = pygame.image.load('img/sun.png')
bg_img = pygame.image.load('img/Background.png')
bg_img = pygame.transform.scale(bg_img, (screen_width, screen_height))
restart_img = pygame.image.load('img/restart_btn.png')
start_img = pygame.image.load('img/start_btn.png')
exit_img = pygame.image.load('img/exit_btn.png')

#load sounds
pygame.mixer.music.load('img/music.wav')
pygame.mixer.music.play(-1, 0.0, 5000)
key_fx = pygame.mixer.Sound('img/coin.wav')
key_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)


class DialogueBox:
	def __init__(self, screen, font):
		self.screen = screen
		self.font = font
		self.box_color = (0, 0, 0, 180)  # Semi-transparent black
		self.text_color = (255, 255, 255)  # White text
		self.box_rect = pygame.Rect(50, screen_height - 300, screen_width - 100, 200)
		self.active = False
		self.current_text = ""
		self.text_surface = None
		self.waiting_for_input = False  # Add this line
        
	def show_dialogue(self, text, duration = 3000, wait_for_input=False):
		print(f"Showing dialogue: {text}")
		self.active = True
		self.current_text = text
		self.waiting_for_input = wait_for_input  # Set the flag based on the parameter

		screen.blit(bg_img, (0, 0))
		screen.blit(sun_img, (100, 100))
    
		# Create semi-transparent surface for dialogue box
		s = pygame.Surface((self.box_rect.width, self.box_rect.height))
		s.set_alpha(128)
		s.fill(self.box_color)
		screen.blit(s, self.box_rect)
    
		# Render text
		words = text.split()
		lines = []
		current_line = []
		for word in words:
			current_line.append(word)
			test_line = ' '.join(current_line)
			if self.font.size(test_line)[0] > self.box_rect.width - 20:
				lines.append(' '.join(current_line[:-1]))
				current_line = [word]
		lines.append(' '.join(current_line))
    
		# Draw text
		for i, line in enumerate(lines):
			text_surface = self.font.render(line, True, self.text_color)
			screen.blit(text_surface, (self.box_rect.x + 10, self.box_rect.y + 10 + i * 30))
		
		# Only show continue prompt for non-input dialogues
		if not self.waiting_for_input:
			continue_text = self.font.render("Press SPACE to continue...", True, (255, 255, 255))
			screen.blit(continue_text, (self.box_rect.x + 10, self.box_rect.bottom - 30))
		
		pygame.display.update()
    
		# Only wait for space if not in input mode
		if wait_for_input:
			return
		start_time = pygame.time.get_ticks()
		while self.active:
			current_time = pygame.time.get_ticks()
			if current_time - start_time >= duration:
				self.active = False  # End the dialogue
				break
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						self.active = False
						break 
					
		self.active = False
		
	def update(self):
		if self.current_message:
			current_time = pygame.time.get_ticks()
			if current_time - self.message_timer > self.message_duration:
				self.current_message = None
			else:
				# Create semi-transparent surface for dialogue box
				s = pygame.Surface((self.box_rect.width, self.box_rect.height))
				s.set_alpha(128)
				s.fill(self.box_color)
				screen.blit(s, self.box_rect)
				
				# Render text
				words = self.current_message.split()
				lines = []
				current_line = []
				for word in words:
					current_line.append(word)
					test_line = ' '.join(current_line)
					if self.font.size(test_line)[0] > self.box_rect.width - 20:
						lines.append(' '.join(current_line[:-1]))
						current_line = [word]
				lines.append(' '.join(current_line))
				
				# Draw text
				for i, line in enumerate(lines):
					text_surface = self.font.render(line, True, self.text_color)
					screen.blit(text_surface, (self.box_rect.x + 10, self.box_rect.y + 10 + i * 30))
	
	def get_player_name(self):
		input_text = ""
		input_active = True
		prompt = "Enter your name:"
		
		while input_active:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					return None
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_RETURN and input_text.strip():
						input_active = False
					elif event.key == pygame.K_BACKSPACE:
						input_text = input_text[:-1]
					else:
						if len(input_text) < 20:  # Limit name length
							input_text += event.unicode
							
			screen.blit(bg_img, (0, 0))
			screen.blit(sun_img, (100, 100))
			
			# Draw input box
			s = pygame.Surface((self.box_rect.width, self.box_rect.height))
			s.set_alpha(128)
			s.fill(self.box_color)
			screen.blit(s, self.box_rect)
			
			# Draw prompt
			prompt_surface = self.font.render(prompt, True, self.text_color)
			screen.blit(prompt_surface, (self.box_rect.x + 10, self.box_rect.y + 10))
			
			# Draw input text
			input_surface = self.font.render(input_text, True, self.text_color)
			screen.blit(input_surface, (self.box_rect.x + 10, self.box_rect.y + 50))
			
			pygame.display.flip()
			
		return input_text

class GameTimer:
    def __init__(self):
        self.start_time = time.time()
        self.elapsed_time = 0
        self.font = pygame.font.SysFont('Bauhaus 93', 30)

    def update(self):
        self.elapsed_time = time.time() - self.start_time

    def draw(self, screen):
        minutes, seconds = divmod(int(self.elapsed_time), 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        time_surface = self.font.render(time_str, True, (255, 255, 255))
        screen.blit(time_surface, (screen_width - 100, 10))

    def reset(self):
        self.start_time = time.time()
        self.elapsed_time = 0

    def save_time(self, level):
        with open('level_times.txt', 'a') as f:
            f.write(f"Level {level}: {int(self.elapsed_time)} seconds\n")
			
class StoryManager:
    def __init__(self):
        self.player_name = ""
        self.current_stage = 0
        self.storyline = [
            "Welcome to Decoding Island! You've woken up on a mysterious island...",
            "You must escape by solving coding puzzles and platforming challenges!",
            "Be careful of the enemies and obstacles ahead...",
            "Each level brings you closer to freedom, but also closer to the final boss!",
            "The puzzles will get progressively harder. Are you ready for the challenge?"
        ]
        self.level_messages = {
            1: "Level 1: The Beach - Your journey begins here...",
            2: "Level 2: The Jungle - Things are getting trickier...",
            3: "Level 3: The Mountains - The path grows more treacherous...",
            4: "Level 4: The Temple - Ancient coding secrets lie within...",
            5: "Level 5: The Summit - The final boss awaits...",
            6: "Level 6: The Escape - One last challenge to freedom...",
            7: "Level 7: Victory - You've mastered the Decoding Island!"
        }
        self.puzzles = {
            1: {"question": "What does print('Hello') output?", "answer": "Hello"},
            2: {"question": "What is 2 + 2 in Python?", "answer": "4"},
            3: {"question": "What is len('code')?", "answer": "4"},
            4: {"question": "What is the first index in a Python list?", "answer": "0"},
            5: {"question": "Is Python case-sensitive? (yes/no)", "answer": "yes"},
            6: {"question": "What type is 'True' in Python?", "answer": "bool"},
            7: {"question": "What symbol is used for comments in Python?", "answer": "#"}
        }

def play_wordle():
    """Run the Wordle game and return True if the player wins, False otherwise."""
    return wordle_game()  # Assume the main function in Wordle.py returns True for a win, False for a loss

def solve_puzzle_wordle(dialogue_box, puzzle):
    wordle_result = play_wordle()
    if wordle_result:
        dialogue_box.show_dialogue("You solved the Wordle puzzle! Moving to the next level...")
        return True
    else:
        dialogue_box.show_dialogue("You didn't solve the Wordle puzzle. Try the level again!")
        return False

def load_tmx_level(level_number):
    tmx_data = pytmx.load_pygame(f'LEVEL{level_number}GAME.tmx')
    world_data = []
    
    # Convert TMX layers to our world data format
    for layer in tmx_data.visible_layers:
        if hasattr(layer, 'data'):
            layer_data = []
            for y in range(layer.height):
                row = []
                for x in range(layer.width):
                    # Get tile GID and convert to our tile system
                    gid = layer.data[y][x]
                    # Convert TMX tile IDs to your game's tile system
                    if gid == 0:  # Empty tile
                        row.append(0)
                    elif gid in [90, 91, 92]:  # Platform tiles
                        row.append(1)
                    elif gid in [96, 97]:  # Ground tiles
                        row.append(2)
                    # Add more tile conversions as needed
                row.append(row)
            world_data.append(layer_data)
    
    return world_data

def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

dialogue_box = DialogueBox(screen, font_score)
story_manager = StoryManager()

def reset(self, x, y):
    self.rect.x = x
    self.rect.y = y
    # Other initialization code remains the same

#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	platform_group.empty()
	key_group.empty()
	lava_group.empty()
	exit_group.empty()

	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	#create dummy key for showing the score
	score_key = Key(tile_size // 2, tile_size // 2)
	key_group.add(score_key)
	return world

def eye_blink_effect(blink_count=2, blink_speed=0.5):
    original_surface = screen.copy()

    for _ in range(blink_count):
        # Closing eye effect
        for i in range(20):
            screen.blit(original_surface, (0, 0))
            height = int(screen_height * (i / 20)**2)  # Use quadratic easing for more natural movement
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_width, height))
            pygame.draw.rect(screen, (0, 0, 0), (0, screen_height - height, screen_width, height))
            pygame.display.update()
            pygame.time.wait(int((blink_speed / 40) * 1000))

        # Eye closed
        screen.fill((0, 0, 0))
        pygame.display.update()
        pygame.time.wait(int(blink_speed * 500))  # Half the blink_speed for closed eye

        # Opening eye effect
        for i in range(20, 0, -1):
            screen.blit(original_surface, (0, 0))
            height = int(screen_height * (i / 20)**2)  # Use quadratic easing for more natural movement
            pygame.draw.rect(screen, (0, 0, 0), (0, 0, screen_width, height))
            pygame.draw.rect(screen, (0, 0, 0), (0, screen_height - height, screen_width, height))
            pygame.display.update()
            pygame.time.wait(int((blink_speed / 40) * 1000))

        # Pause between blinks
        screen.blit(original_surface, (0, 0))
        pygame.display.update()
        pygame.time.wait(int(blink_speed * 2000))  # 2 seconds pause between blinks

    # Ensure the original screen is restored
    screen.blit(original_surface, (0, 0))
    pygame.display.update()

def reveal_text_gradually(screen, text, font, color, x, y, delay=150):
    """Reveal text one character at a time, keeping the event loop active."""
    start_time = pygame.time.get_ticks()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # Ensure the game quits

        elapsed_time = pygame.time.get_ticks() - start_time
        char_count = elapsed_time // delay

        # Clear the screen
        screen.fill((0, 0, 0))  
        
        # Draw "Unknown Voice:" at the top
        voice_font = pygame.font.Font(None, 48)
        voice_surface = voice_font.render("Unknown Voice:", True, color)
        voice_rect = voice_surface.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(voice_surface, voice_rect)

        # Draw the gradually revealed text
        text_surface = font.render(text[:char_count], True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)

        pygame.display.update()

        if char_count >= len(text):
            running = False  # Stop when all characters are revealed

def shake_text(screen, text, font, color, x, y, duration=1000, intensity=5):
    """Shake text for a given duration, keeping the event loop active."""
    start_time = pygame.time.get_ticks()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # Ensure the game quits

        elapsed_time = pygame.time.get_ticks() - start_time
        if elapsed_time > duration:
            running = False  # Stop after the duration

        # Clear the screen
        screen.fill((0, 0, 0))  

        # Draw "Unknown Voice:" at the top
        voice_font = pygame.font.Font(None, 48)
        voice_surface = voice_font.render("Unknown Voice:", True, color)
        voice_rect = voice_surface.get_rect(center=(screen.get_width() // 2, 50))
        screen.blit(voice_surface, voice_rect)

        # Draw the shaking text
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x + offset_x, y + offset_y))
        screen.blit(text_surface, text_rect)

        pygame.display.update()
        pygame.time.delay(50)  # Keep shaking at intervals

def blink_and_reveal_text(screen, font):
    """Simulate eye blink effect and reveal text with various effects."""
    # Define text properties
    text_color = (255, 255, 255)  # White color
    center_x = screen.get_width() // 2
    center_y = screen.get_height() // 2

    # Use a smaller font for the quotes
    quote_font = pygame.font.Font(None, 36)

    # Reveal each line of text gradually
    reveal_text_gradually(screen, "\"Hello?\"", quote_font, text_color, center_x, center_y, delay=150)
    pygame.time.wait(1500)  # Wait between lines

    reveal_text_gradually(screen, "\"Helloooo?\"", quote_font, text_color, center_x, center_y, delay=150)
    pygame.time.wait(1500)  # Wait between lines

    reveal_text_gradually(screen, "\"HELLO!!!\"", quote_font, text_color, center_x, center_y, delay=100)

    pygame.time.wait(1000)  # Wait after shaking

    # Fade back to the game
    original_surface = pygame.display.get_surface().copy()
    for alpha in range(0, 255, 5):
        screen.fill((0, 0, 0))
        original_surface.set_alpha(alpha)
        screen.blit(original_surface, (0, 0))
        pygame.display.update()
        pygame.time.wait(20)
		
def change_music(level):
    pygame.mixer.music.fadeout(500)  # Fade out current music
    pygame.time.wait(500)  # Wait for fadeout to complete
    if level in LEVEL_SOUNDTRACKS:
        try:
            pygame.mixer.music.load(LEVEL_SOUNDTRACKS[level])
            pygame.mixer.music.play(-1)  # Loop indefinitely
            pygame.mixer.music.set_volume(0.5)  # Adjust volume as needed
        except Exception as e:
            print(f"Could not load music for level {level}: {e}")

change_music(level)  # Start the music for level 1

def solve_puzzle(dialogue_box, puzzle):
    answer = ""
    solving = True
    print("Entering solve_puzzle function")  # Debug print
    dialogue_box.show_dialogue(f"Puzzle: {puzzle['question']}\nYour answer: ", wait_for_input=True)
    
    while solving:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                print(f"Key pressed: {event.unicode}")  # Debug print
                if event.key == pygame.K_RETURN and answer.strip():
                    print(f"Submitted answer: {answer}")  # Debug print
                    return answer.strip().lower() == puzzle['answer'].lower()
                elif event.key == pygame.K_BACKSPACE:
                    answer = answer[:-1]
                else:
                    answer += event.unicode
                
                # Update the dialogue box with the current answer
                dialogue_box.show_dialogue(f"Puzzle: {puzzle['question']}\nYour answer: {answer}", wait_for_input=True)
        
        pygame.display.flip()
        clock.tick(fps)
        
        screen.blit(bg_img, (0, 0))
        screen.blit(sun_img, (100, 100))
        
        dialogue_box.show_dialogue(f"Puzzle: {puzzle['question']}\nYour answer: {answer}", 0)
        
        pygame.display.flip()
    
    return answer.strip().lower() == puzzle['answer'].lower()
		
class Button():
	def __init__(self, x, y, image):
		self.image = image
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.clicked = False

	def draw(self):
		action = False

		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				action = True
				self.clicked = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False


		#draw button
		screen.blit(self.image, self.rect)

		return action


class Player():
	def __init__(self, x, y):
		self.reset(x, y)

	def update(self, game_over):
		dx = 0
		dy = 0
		walk_cooldown = 5
		col_thresh = 20

		if game_over == 0:
			#get keypresses
			key = pygame.key.get_pressed()
			if key[pygame.K_SPACE] and self.jumped == False and self.in_air == False:
				jump_fx.play()
				self.vel_y = -15
				self.jumped = True
			if key[pygame.K_SPACE] == False:
				self.jumped = False
			if key[pygame.K_LEFT]:
				dx -= 5
				self.counter += 1
				self.direction = -1
			if key[pygame.K_RIGHT]:
				dx += 5
				self.counter += 1
				self.direction = 1
			if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
				self.counter = 0
				self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#handle animation
			if self.counter > walk_cooldown:
				self.counter = 0
				self.index += 1
				if self.index >= len(self.images_right):
					self.index = 0
				if self.direction == 1:
					self.image = self.images_right[self.index]
				if self.direction == -1:
					self.image = self.images_left[self.index]


			#add gravity
			self.vel_y += 1
			if self.vel_y > 10:
				self.vel_y = 10
			dy += self.vel_y

			#check for collision
			self.in_air = True
			for tile in world.tile_list:
				#check for collision in x direction
				if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#check for collision in y direction
				if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below the ground i.e. jumping
					if self.vel_y < 0:
						dy = tile[1].bottom - self.rect.top
						self.vel_y = 0
					#check if above the ground i.e. falling
					elif self.vel_y >= 0:
						dy = tile[1].top - self.rect.bottom
						self.vel_y = 0
						self.in_air = False


			#check for collision with enemies
			if pygame.sprite.spritecollide(self, blob_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with lava
			if pygame.sprite.spritecollide(self, lava_group, False):
				game_over = -1
				game_over_fx.play()

			#check for collision with exit
			if pygame.sprite.spritecollide(self, exit_group, False):
				game_over = 1


			#check for collision with platforms
			for platform in platform_group:
				#collision in the x direction
				if platform.rect.colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
					dx = 0
				#collision in the y direction
				if platform.rect.colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
					#check if below platform
					if abs((self.rect.top + dy) - platform.rect.bottom) < col_thresh:
						self.vel_y = 0
						dy = platform.rect.bottom - self.rect.top
					#check if above platform
					elif abs((self.rect.bottom + dy) - platform.rect.top) < col_thresh:
						self.rect.bottom = platform.rect.top - 1
						self.in_air = False
						dy = 0
					#move sideways with the platform
					if platform.move_x != 0:
						self.rect.x += platform.move_direction


			#update player coordinates
			self.rect.x += dx
			self.rect.y += dy


		elif game_over == -1:
			self.image = self.dead_image
			draw_text('GAME OVER!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if self.rect.y > 200:
				self.rect.y -= 5

		#draw player onto screen
		screen.blit(self.image, self.rect)

		return game_over

	
	def reset(self, x, y):
		self.images_right = []
		self.images_left = []
		self.index = 0
		self.counter = 0
		for num in range(1, 5):
			img_right = pygame.image.load(f'img/dino{num}.png')
			img_right = pygame.transform.scale(img_right, (30, 40))
			img_left = pygame.transform.flip(img_right, True, False)
			self.images_right.append(img_right)
			self.images_left.append(img_left)
		self.dead_image = pygame.image.load('img/Skeleton.png')
		self.image = self.images_right[self.index]
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.vel_y = 0
		self.jumped = False
		self.direction = 0
		self.in_air = True



class World():
	def __init__(self, data):
		self.tile_list = []

		#load images
		dirt_block_img = pygame.image.load('img/dirt_block.png')
		grass_block_img = pygame.image.load('img/grass_block.png')
		self.dirt_img = pygame.image.load('img/dirt.png')
		self.grass_img = pygame.image.load('img/grass.png')
		self.platform_img = pygame.image.load('img/platform.png')

		row_count = 0
		for row in data:
			col_count = 0
			for tile in row:
				if tile == 1:
					img = pygame.transform.scale(dirt_block_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 2:
					img = pygame.transform.scale(grass_block_img, (tile_size, tile_size))
					img_rect = img.get_rect()
					img_rect.x = col_count * tile_size
					img_rect.y = row_count * tile_size
					tile = (img, img_rect)
					self.tile_list.append(tile)
				if tile == 3:
					blob = Enemy(col_count * tile_size, row_count * tile_size + 15)
					blob_group.add(blob)
				if tile == 4:
					platform = Platform(col_count * tile_size, row_count * tile_size, 1, 0)
					platform_group.add(platform)
				if tile == 5:
					platform = Platform(col_count * tile_size, row_count * tile_size, 0, 1)
					platform_group.add(platform)
				if tile == 6:
					lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size // 2))
					lava_group.add(lava)
				if tile == 7:
					key = Key(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					key_group.add(key)
				if tile == 8:
					exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size // 2))
					exit_group.add(exit)
				col_count += 1
			row_count += 1


	def draw(self):
		for tile in self.tile_list:
			screen.blit(tile[0], tile[1])



class Enemy(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load('img/Zombie.png')
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_direction = 1
		self.move_counter = 0

	def update(self):
		self.rect.x += self.move_direction
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Platform(pygame.sprite.Sprite):
	def __init__(self, x, y, move_x, move_y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/grass_plat.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.move_counter = 0
		self.move_direction = 1
		self.move_x = move_x
		self.move_y = move_y


	def update(self):
		self.rect.x += self.move_direction * self.move_x
		self.rect.y += self.move_direction * self.move_y
		self.move_counter += 1
		if abs(self.move_counter) > 50:
			self.move_direction *= -1
			self.move_counter *= -1


class Lava(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/lava.png')
		self.image = pygame.transform.scale(img, (tile_size, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y


class Key(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/key.png')
		self.image = pygame.transform.scale(img, (tile_size // 2.5, tile_size // 2))
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)


class Exit(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/exit.png')
		self.image = pygame.transform.scale(img, (tile_size, int(tile_size * 1.5)))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

level_questions = {
    1: {"question": "What does this code print? print('Hello, World!')", "answer": "Hello, World!"},
    2: {"question": "Decode this: print(str(2 + 2))", "answer": "4"},
    3: {"question": "What's the output? print('Python'[1:4])", "answer": "yth"},
    4: {"question": "Decode: print(len('code'))", "answer": "4"},
    5: {"question": "Result of: print(list(range(3)))", "answer": "[0, 1, 2]"},
    6: {"question": "Output of: print('a' * 3)", "answer": "aaa"},
    7: {"question": "What prints? x = 5; print(f'{x + 2}')", "answer": "7"},
    # Add more questions for each level
}
game_timer = GameTimer()

def show_level_banner(screen, level, duration=2000):
    """Show a level transition banner"""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((0, 0, 0))
    overlay.set_alpha(128)
    screen.blit(overlay, (0, 0))
    
    # Draw level text
    level_text = f"Level {level}"
    draw_text(level_text, font, white, (screen_width // 2) - 100, screen_height // 2 - 50)
    
    # Draw keys required text
    keys_text = f"Collect {KEYS_REQUIRED[level]} keys to proceed"
    draw_text(keys_text, font_score, white, (screen_width // 2) - 150, screen_height // 2 + 20)
    
    pygame.display.update()
    pygame.time.wait(duration)

# Then modify your level transition code:
if game_over == 1:
    if score >= KEYS_REQUIRED[level]:
        game_timer.save_time(level)
        level += 1
        if level <= max_levels:
            world_data = []
            world = reset_level(level)
            game_over = 0
            score = 0
            game_timer.reset()
            # Change music for new level
            change_music(level)
            # Show level banner
            show_level_banner(screen, level)

class LevelIndicator:
    def __init__(self):
        self.font = pygame.font.SysFont('Bauhaus 93', 30)
        self.bg_color = (0, 0, 0, 128)  # Semi-transparent black
        self.text_color = white
        self.padding = 10
        
    def draw(self, screen, level, score, required_keys):
        # Draw level indicator box
        level_text = f"Level {level}"
        key_text = f"keys: {score}/{required_keys}"
        
        # Create text surfaces
        level_surface = self.font.render(level_text, True, self.text_color)
        key_surface = self.font.render(key_text, True, self.text_color)
        
        # Calculate box dimensions
        box_width = max(level_surface.get_width(), key_surface.get_width()) + self.padding * 2
        box_height = level_surface.get_height() + key_surface.get_height() + self.padding * 3
        
        # Create semi-transparent background
        bg_surface = pygame.Surface((box_width, box_height))
        bg_surface.fill((0, 0, 0))
        bg_surface.set_alpha(128)
        
        # Position the box in the top-right corner
        box_x = screen_width - box_width - 10
        box_y = 10
        
        # Draw background
        screen.blit(bg_surface, (box_x, box_y))
        
        # Draw text
        screen.blit(level_surface, (box_x + self.padding, box_y + self.padding))
        screen.blit(key_surface, (box_x + self.padding, 
                                 box_y + self.padding * 2 + level_surface.get_height()))

# Initialize the level indicator
level_indicator = LevelIndicator()

def ask_question(level):
    if level not in level_questions:
        return True  # If no question for this level, assume correct

    question_data = level_questions[level]
    question = question_data["question"]
    correct_answer = question_data["answer"]
    user_answer = ""

    while True:
        screen.fill((0, 0, 0))
        draw_text("Level " + str(level) + " Question:", font, white, screen_width // 2 - 200, screen_height // 2 - 100)
        draw_text(question, font_score, white, screen_width // 2 - 200, screen_height // 2 - 50)
        draw_text("Your Answer: " + user_answer, font, white, screen_width // 2 - 200, screen_height // 2 + 50)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if user_answer.lower().strip() == correct_answer.lower().strip():
                        return True
                    else:
                        return False
                elif event.key == pygame.K_BACKSPACE:
                    user_answer = user_answer[:-1]
                else:
                    user_answer += event.unicode

        pygame.display.update()


player = Player(100, screen_height - 130)

blob_group = pygame.sprite.Group()
platform_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
key_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_key = Key(tile_size // 2, tile_size // 2)
key_group.add(score_key)

#load in level data and create world
if path.exists(f'level{level}_data'):
	pickle_in = open(f'level{level}_data', 'rb')
	world_data = pickle.load(pickle_in)
world = World(world_data)


#create buttons
restart_button = Button(screen_width // 2 - 50, screen_height // 2 + 100, restart_img)
start_button = Button(screen_width // 2 - 350, screen_height // 2, start_img)
exit_button = Button(screen_width // 2 + 150, screen_height // 2, exit_img)


run = True
while run:

	clock.tick(fps)

	screen.blit(bg_img, (0, 0))
	screen.blit(sun_img, (100, 100))

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	if main_menu:
		if start_button.draw():
			if not story_manager.player_name:
				story_manager.player_name = dialogue_box.get_player_name()
				for intro_text in story_manager.storyline:
					dialogue_box.show_dialogue(intro_text)
				main_menu = False	
		if exit_button.draw():
			run = False
	
	else:
		world.draw()
		
		if game_over == 0:
			blob_group.update()
			platform_group.update()
			game_timer.update()  # Update the timer
			game_timer.draw(screen)  # Draw the timer
			#update score
			#check if a key has been collected
			if pygame.sprite.spritecollide(player, key_group, True):
				score += 1
				key_fx.play()
				if level == 2 and not hasattr(story_manager, 'level_2_message_shown'):
					dialogue_box.show_dialogue("Your better than I thought...")
					story_manager.level_2_message_shown = True
					pygame.time.wait(500)  # Short pause before continuing
				# Add level-specific story elements
				if level == 3 and not hasattr(story_manager, 'level_3_message_shown'):
					dialogue_box.show_dialogue("You've reached the mountains. The air is getting thinner...")
					story_manager.level_3_message_shown = True
				
				if level == 5 and not hasattr(story_manager, 'boss_warning_shown'):
					dialogue_box.show_dialogue("Be careful! The final boss is near. Prepare for the ultimate challenge!")
					story_manager.boss_warning_shown = True
			draw_text(f'Keys: {score}/{KEYS_REQUIRED[level]}', font_score, white, tile_size - 10, 10)

			# When player reaches exit, check keys
			if pygame.sprite.spritecollide(player, exit_group, False):
				if score >= KEYS_REQUIRED[level]:
					if level in story_manager.puzzles:
						puzzle = story_manager.puzzles[level]
						dialogue_box.show_dialogue(f"Solve this puzzle to proceed to the next level:")
						pygame.display.update()
						pygame.time.wait(1000)
					game_over = 1
				else:
					draw_text(f'Need {KEYS_REQUIRED[level] - score} more keys!', 
							font_score, white, 
							screen_width // 2 - 100, screen_height // 2)
					pygame.display.update()
					pygame.time.wait(1000)
					# Respawn player at the original spawn point
					player.reset(original_spawn_x, original_spawn_y)  # Reset to original spawn
					game_over = 0  # Allow the player to continue playing
					
		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		key_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		if game_over == -1:
			draw_text(f'GAME OVER, {story_manager.player_name}!', font, blue, (screen_width // 2) - 200, screen_height // 2)
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0

# In your main game loop, replace the level completion section with:

		if game_over == 1:
			if score >= KEYS_REQUIRED[level]:
				if level in story_manager.puzzles:
					puzzle = story_manager.puzzles[level]
					dialogue_box.show_dialogue(f"Solve this puzzle to proceed to the next level:")
					pygame.display.update()
					pygame.time.wait(1000)
					if solve_puzzle_wordle(dialogue_box, puzzle):
						game_timer.save_time(level)
						level += 1
						if level <= max_levels:
							world_data = []
							world = reset_level(level)
							game_over = 0
							score = 0
							change_music(level)
							show_level_banner(screen, level)
						else:
							dialogue_box.show_dialogue(f"Congratulations {story_manager.player_name}!\nYou've escaped Decoding Island!")
					else:
						game_over = 0  # Allow the player to try the level again
				else:
					# If there's no puzzle for this level, just proceed
					game_timer.save_time(level)
					level += 1
					if level <= max_levels:
						world_data = []
						world = reset_level(level)
						game_over = 0
						score = 0
						change_music(level)
						show_level_banner(screen, level)
					else:
						dialogue_box.show_dialogue(f"Congratulations {story_manager.player_name}!\nYou've escaped Decoding Island!")
			else:
				# Not enough keys
				keys_needed = KEYS_REQUIRED[level] - score
				draw_text(f'Need {keys_needed} more keys!', font_score, white, screen_width // 2 - 100, screen_height // 2)
				pygame.display.update()
				pygame.time.wait(1000)
				game_over = 0  # Allow the player to continue playing the current level

	if main_menu == False:  # Only show when not in main menu
		# Draw level indicator
		draw_text(f'Level: {level}', font_score, white, screen_width - 550, 10)
		# Draw key counter
		

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()