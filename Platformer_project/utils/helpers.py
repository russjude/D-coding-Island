import pickle
from os import path

def draw_text(text, font, color, x, y, screen):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def reset_level(level):
    if path.exists(f'levels/level{level}_data.pkl'):
        with open(f'levels/level{level}_data.pkl', 'rb') as file:
            world_data = pickle.load(file)
        return world_data
    return []
