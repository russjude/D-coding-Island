import pygame
import cv2
from pygame.locals import *
from pygame import mixer
import os
import git
from threading import Thread
from queue import Queue
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Load Soundtrack
background_music = pygame.mixer.music.load("Audio/BACKGROUND_MUSIC.mp3")
sound_effect = pygame.mixer.Sound("Audio/SOUND_EFFECT.MP3")
sound_effect_channel = pygame.mixer.Channel(1)
sound_effect_channel.set_endevent(pygame.USEREVENT + 1)  # Set endevent for the sound channel

# Initialize Pygame
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

# Set the desired resolution
SCREEN_WIDTH = 1539
SCREEN_HEIGHT = 940

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Define tile size based on background height
TILE_SIZE = SCREEN_HEIGHT // 36  # 36 is the number of tiles vertically
GRAVITY = 0.79
JUMP_SPEED = -15
MOVE_SPEED = 7
game_over = 0
current_level = 0  # 0 for start screen, 1-5 for levels
keys_collected = 0
game_start_time = None
level_times = []
dialogue_states = {}

# Load and scale the background for each level
level_backgrounds = {}
for i in range(1, 6):  # Assuming you have 5 levels
    original_bg = pygame.image.load(f'Level Data/Level Image/LEVEL{i}.png')
    level_backgrounds[i] = pygame.transform.scale(original_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))

# You may need to adjust other elements (buttons, player size, etc.) to fit the new resolution
# For example:
# start_button = Button(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, start_btn)
# restart_button = Button(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100, restart_img)

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Center the window on the screen
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Decoding Island')

# Define tile size based on background height
TILE_SIZE = SCREEN_HEIGHT // 36  # 36 is the number of tiles vertically

pygame.display.set_caption('Game Menu')

def display_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Convert the frame to Pygame format and display it
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(frame, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                return

class VideoPlayer:
    def __init__(self, video_path, buffer_size=100, speed_multiplier=2):
        self.cap = cv2.VideoCapture(video_path)
        self.frame_buffer = Queue(maxsize=buffer_size)
        self.current_frame = None
        self.buffer_size = buffer_size
        self.running = True
        self.speed_multiplier = speed_multiplier
        
        original_fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.target_frame_time = (1.0 / original_fps) / self.speed_multiplier
        self.last_frame_time = time.time()
        
        self.load_thread = Thread(target=self._load_frames, daemon=True)
        self.load_thread.start()
    
    def _load_frames(self):
        while self.running:
            if self.frame_buffer.qsize() < self.buffer_size:
                ret, frame = self.cap.read()
                if not ret:
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                
                frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = pygame.surfarray.make_surface(frame)
                frame = pygame.transform.scale(frame, (SCREEN_WIDTH, SCREEN_HEIGHT))
                
                self.frame_buffer.put(frame)
            else:
                time.sleep(0.001)
    
    def get_frame(self):
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        if elapsed >= self.target_frame_time and not self.frame_buffer.empty():
            self.current_frame = self.frame_buffer.get()
            self.last_frame_time = current_time
            
        return self.current_frame
    
    def cleanup(self):
        self.running = False
        self.load_thread.join(timeout=1.0)
        if self.cap is not None:
            self.cap.release()

# Update the SplashScreen class to handle missing files more gracefully:
class SplashScreen:
    def __init__(self, video_path):
        self.video_player = VideoPlayer(video_path)
        self.font = pygame.font.Font(None, 50)
        self.text = self.font.render("Click to continue...", True, (255, 255, 255))
        self.text_rect = self.text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT - 100))
        
    def run(self):
        waiting = True
        while waiting:
            current_frame = self.video_player.get_frame()
            if current_frame:
                screen.blit(current_frame, (0, 0))
                screen.blit(self.text, self.text_rect)
                pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                # Handle both mouse clicks and key presses
                if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key != pygame.K_ESCAPE):
                    try:
                        sound_effect_channel.play(sound_effect, loops=-1)
                        pygame.mixer.music.play(-1)
                    except (pygame.error, AttributeError):
                        print("Warning: Could not play sound effects")
                    waiting = False
                    return True
                
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return False
                
                if event.type == pygame.USEREVENT + 1:
                    try:
                        sound_effect_channel.play(sound_effect, loops=-1)
                    except (pygame.error, AttributeError):
                        pass

        self.video_player.cleanup()
        return True

class MenuButton:
    def __init__(self, x, y, video_path=None, text=None, font_size=60, scale=0.7, speed_multiplier=0.5):
        self.using_video = video_path is not None
        self.rect = pygame.Rect(x, y, int(200 * scale), int(50 * scale))  # Placeholder for rect

        if self.using_video:
            self.video_player = VideoPlayer(video_path, speed_multiplier=speed_multiplier)
            # Set rect size based on video dimensions
            self.rect = pygame.Rect(x, y, int(self.video_player.cap.get(cv2.CAP_PROP_FRAME_WIDTH) * scale),
                                    int(self.video_player.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * scale))
        else:
            self.text = text
            self.font = pygame.font.Font(None, font_size)
            self.color = (200, 200, 200)
            self.hover_color = (255, 255, 255)
            self.text_color = (0, 0, 0)
        
        self.is_hovered = False
        self.clicked = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and not self.clicked:
                self.clicked = True
                return True
                
        if event.type == pygame.MOUSEBUTTONUP:
            self.clicked = False
            
        return False
    
    def draw(self, surface):
        if self.using_video:
            frame = self.video_player.get_frame()
            if frame:
                # Scale video frame to button size
                scaled_frame = pygame.transform.scale(frame, self.rect.size)
                surface.blit(scaled_frame, self.rect.topleft)
        else:
            color = self.hover_color if self.is_hovered else self.color
            pygame.draw.rect(surface, color, self.rect, border_radius=12)
            text_surface = self.font.render(self.text, True, self.text_color)
            text_rect = text_surface.get_rect(center=self.rect.center)
            surface.blit(text_surface, text_rect)

class MainMenu:
    def __init__(self):
        self.video_player = VideoPlayer('Graphics/MAINMENU VIDEO.mp4')
        
        # Load and scale logo
        self.logo = pygame.image.load('Graphics/LOGO.png')
        logo_width = int(SCREEN_WIDTH * 0.6)  # Make logo 60% of screen width
        logo_height = int(logo_width * (634/1037))  # Maintain aspect ratio
        self.logo = pygame.transform.scale(self.logo, (logo_width, logo_height))
        self.logo_rect = self.logo.get_rect()
        self.logo_rect.centerx = SCREEN_WIDTH // 2
        
        # Increase logo's y position (adjust the 0.25 value to move it up or down)
        self.logo_rect.top = SCREEN_HEIGHT * 0.04  # Increased from 0.1 to 0.25
        
        # Calculate button positions and size
        button_spacing = int(SCREEN_HEIGHT * 0.01)  # Spacing between buttons
        
        # Decrease the space between logo and buttons (adjust the 0.05 value to change the gap)
        button_start_y = self.logo_rect.bottom + int(SCREEN_HEIGHT * 0.01)  # Decreased from 0.15 to 0.05
        
        # Smaller scale factor for buttons
        button_scale = (SCREEN_HEIGHT / 1440) * 0.25  # Adjust scale factor as needed
        
        # Create centered buttons
        self.buttons = {}
        button_paths = {
            'play': 'Graphics/PLAY BUTTON.mp4',
            'credits': 'Graphics/CREDITS BUTTON.mp4',
            'quit': 'Graphics/QUIT BUTTON.mp4'
        }
        
        for i, (button_name, video_path) in enumerate(button_paths.items()):
            # Create a temporary VideoPlayer to get the button dimensions
            temp_player = VideoPlayer(video_path)
            button_width = int(temp_player.cap.get(cv2.CAP_PROP_FRAME_WIDTH) * button_scale)
            button_height = int(temp_player.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * button_scale)
            temp_player.cleanup()
            
            # Calculate the centered x position for each button
            button_x = (SCREEN_WIDTH - button_width) // 2
            
            # Add vertical spacing between buttons
            button_y = button_start_y + (i * (button_height + button_spacing))
            
            self.buttons[button_name] = MenuButton(
                button_x, button_y,
                video_path=video_path,
                scale=button_scale,
                speed_multiplier=1.5
            )

    def run(self):
        clock = pygame.time.Clock()
        running = True

        while running:
            current_frame = self.video_player.get_frame()
            if current_frame:
                screen.blit(current_frame, (0, 0))
            
            screen.blit(self.logo, self.logo_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "quit"
                    elif event.key == pygame.K_F11:
                        toggle_fullscreen()

                for button_name, button in self.buttons.items():
                    if button.handle_event(event):
                        return button_name

            for button in self.buttons.values():
                button.draw(screen)

            pygame.display.flip()
            clock.tick(24)  # Reduce the frame rate
        
        self.video_player.cleanup()

def toggle_fullscreen():
    global screen, fullscreen
    fullscreen = not fullscreen
    if fullscreen:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

def switch_branch(MINI_GAME):
    repo = git.Repo(os.getcwd())
    if repo.active_branch.name != MINI_GAME:
        repo.git.checkout(MINI_GAME)
        print(f"Switched to branch '{MINI_GAME}'")

# Update the main function
def main():
    pygame.init()
    mixer.init()

    # Initialize audio channels if not already initialized
    if pygame.mixer.get_num_channels() < 2:
        pygame.mixer.set_num_channels(2)

    # Load and play the music during the splash screen
    splash = SplashScreen("Graphics/SPLASH VIDEO.mp4")
    try:
        mixer.music.load("Audio/Shining Sound Effect.mp3")
        mixer.music.play(1)  # Play once (1)
    except pygame.error:
        print("Warning: Could not load splash screen music")

    # Run the splash screen and stop if it doesn't complete
    if not splash.run():
        pygame.quit()
        return

    # Stop the music before the main menu opens
    mixer.music.stop()

    try:
        # Load menu background music
        mixer.music.load("Audio/BACKGROUND_MUSIC.mp3")
    except pygame.error:
        print("Warning: Could not load menu background music")

    # Initialize and run the main menu
    menu = MainMenu()
    
    while True:
        action = menu.run()
        
        if action == "quit":
            break
        elif action == "credits":
            try:
                import CREDITS
                print("Opened credits...")
            except ImportError:
                print("Could not load CREDITS module")
        elif action == "play":
            try:
                import FINAL_GAME
                print("Starting mini-game...")
            except ImportError:
                print("Could not load MINI_GAME module")
    
    pygame.quit()

# Run the main function
if __name__ == "__main__":
    main()