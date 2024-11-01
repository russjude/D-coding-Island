import pygame
import pickle

class World:
    def __init__(self, data):
        self.tile_list = []  # Store tiles here
        # Initialize the world data if needed
        # Example: self.tile_list = self.create_tiles(data)
    
    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

def reset_level(level, player, blobs, platforms, keys, lava, exits):
    player.reset(100, 850)
    blobs.empty()
    platforms.empty()
    keys.empty()
    lava.empty()
    exits.empty()
    with open(f'levels/level{level}_data', 'rb') as f:
        world_data = pickle.load(f)
    return World(world_data)

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.clicked = False  # Track if the button was clicked
    
    def draw(self, screen):
        action = False
        pos = pygame.mouse.get_pos()  # Get mouse position
        # Check if the mouse is hovering over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True  # Action triggered on click
                self.clicked = True  # Set clicked to True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False  # Reset clicked on mouse release
        # Draw the button
        screen.blit(self.image, self.rect)
        return self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]  # Return action status

def draw_text(text, font, text_color, x, y, screen):
    """Renders text to the screen at the given coordinates."""
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))
