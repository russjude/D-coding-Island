import pygame
#fuck you russ
#pota
pygame.init()

screen_width = 1200
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Hi Russ')

player = pygame.Rect((300, 250, 50, 50)) #x axis, y axis, dim. of characters

tile_size = 100

def draw_grid():
    for line in range(0, int(screen_width/tile_size)):
        pygame.draw.line(screen, (255, 255, 255), (0, line * tile_size), (screen_width, line* tile_size))
        pygame.draw.line(screen, (255, 255, 255), (line * tile_size, 0), (line * tile_size, screen_height))


run = True
while run:
    screen.fill((0, 122, 100))

    draw_grid()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.draw.rect(screen, (255, 0, 0), player) #rgb

    key = pygame.key.get_pressed()
    if key[pygame.K_a] == True:
        player.move_ip(-1,0)
    elif key[pygame.K_d] == True:
        player.move_ip(1,0)
    elif key[pygame.K_w] == True:
        player.move_ip(0,-1)        
    elif key[pygame.K_s] == True:
        player.move_ip(0,1)

    pygame.display.update()

pygame.quit()