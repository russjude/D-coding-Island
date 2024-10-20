import pygame
import pickle

class World:
    def __init__(self, data):
        self.tile_list = data  # Store tiles here

    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])  # Ensure you have a list of tuples (image, position)

def reset_level(level, player, blobs, platforms, coins, lava, exits):
    player.reset(100, 850)
    blobs.empty()
    platforms.empty()
    coins.empty()
    lava.empty()
    exits.empty()

    with open(f'levels/level{level}_data', 'rb') as f:
        world_data = pickle.load(f)
    return World(world_data)

# In your main game loop
world = reset_level(current_level, player, blobs, platforms, coins, lava, exits)

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    screen.fill((0, 0, 0))
    world.draw(screen)  # Make sure to pass the screen here
    start_button.draw(screen)
    exit_button.draw(screen)

    pygame.display.update()
