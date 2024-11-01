import pygame

class World:
    def __init__(self, data):
        self.tile_list = []
        for row in data:
            for tile in row:
                if tile == 1:
                    # Add tile creation logic here
                    pass

    def draw(self, screen):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])

class key(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('img/key.png')
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Button:
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        return self.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]
