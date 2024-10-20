import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path


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
coin_fx = pygame.mixer.Sound('img/coin.wav')
coin_fx.set_volume(0.5)
jump_fx = pygame.mixer.Sound('img/jump.wav')
jump_fx.set_volume(0.5)
game_over_fx = pygame.mixer.Sound('img/game_over.wav')
game_over_fx.set_volume(0.5)


def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))


#function to reset level
def reset_level(level):
	player.reset(100, screen_height - 130)
	blob_group.empty()
	platform_group.empty()
	coin_group.empty()
	lava_group.empty()
	exit_group.empty()

	#load in level data and create world
	if path.exists(f'level{level}_data'):
		pickle_in = open(f'level{level}_data', 'rb')
		world_data = pickle.load(pickle_in)
	world = World(world_data)
	#create dummy coin for showing the score
	score_coin = Coin(tile_size // 2, tile_size // 2)
	coin_group.add(score_coin)
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
		self.dead_image = pygame.image.load('img/ghost.png')
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
					coin = Coin(col_count * tile_size + (tile_size // 2), row_count * tile_size + (tile_size // 2))
					coin_group.add(coin)
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


class Coin(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		img = pygame.image.load('img/coin.png')
		self.image = pygame.transform.scale(img, (tile_size // 2, tile_size // 2))
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
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#create dummy coin for showing the score
score_coin = Coin(tile_size // 2, tile_size // 2)
coin_group.add(score_coin)

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

	if main_menu == True:
		if exit_button.draw():
			run = False
		if start_button.draw():
			main_menu = False
			blink_and_reveal_text(screen, pygame.font.Font(None, 36))		
	else:
		world.draw()

		if game_over == 0:
			blob_group.update()
			platform_group.update()
			#update score
			#check if a coin has been collected
			if pygame.sprite.spritecollide(player, coin_group, True):
				score += 1
				coin_fx.play()
			draw_text('X ' + str(score), font_score, white, tile_size - 10, 10)

		blob_group.draw(screen)
		platform_group.draw(screen)
		lava_group.draw(screen)
		coin_group.draw(screen)
		exit_group.draw(screen)

		game_over = player.update(game_over)

		#if player has died
		if game_over == -1:
			if restart_button.draw():
				world_data = []
				world = reset_level(level)
				game_over = 0
				score = 0


		if game_over == 1:
			if ask_question(level):
				# Player answered correctly, move to next level
				level += 1
				if level <= max_levels:
					world_data = []
					world = reset_level(level)
					game_over = 0
				else:
					draw_text('YOU WIN!', font, blue, (screen_width // 2) - 140, screen_height // 2)
					if restart_button.draw():
						level = 1
						world_data = []
						world = reset_level(level)
						game_over = 0
						score = 0
			else:
				# Player answered incorrectly, show message and reset level
				draw_text('Incorrect! Try the level again.', font, blue, (screen_width // 2) - 200, screen_height // 2)
				pygame.display.update()
				pygame.time.wait(2000)  # Wait for 2 seconds before resetting
				world_data = []
				world = reset_level(level)
				game_over = 0


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False

	pygame.display.update()

pygame.quit()