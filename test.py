import pygame, sys
from pytmx.util_pygame import load_pygame
from settings import *
from entities import Render_Sprite

pygame.init()

all_sprites = pygame.sprite.Group()

tmx = load_pygame("Tiled/untitled.tmx")
# /home/chris_sunny/Documents/galactic_games/Tiled/untitled.tmx
for obj in tmx.get_layer_by_name("Layout"):
    Render_Sprite(obj.image, (obj.x-1200, obj.y-800), all_sprites) 

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite Render Test")
clock = pygame.time.Clock()

# Camera offset for auto-move
offset_x, offset_y = 0, 0
speed_x, speed_y = 2, 2   # diagonal speed

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update offset (auto movement)
    offset_x -= speed_x
    # offset_y -= speed_y

    # Clear screen
    screen.fill(BLACK)

    # Draw all sprites with offset applied
    for sprite in all_sprites:
        screen.blit(sprite.image, (sprite.rect.x + offset_x, sprite.rect.y + offset_y))

    pygame.display.flip()
    clock.tick(60)
