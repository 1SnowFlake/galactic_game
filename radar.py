import pygame
import math
from settings import WIDTH, HEIGHT, WHITE, YELLOW, RED, celestial_bodies, font

def draw_radar(screen, player_x, player_y, radar_center=(WIDTH-120, 120), radar_radius=100, radar_range=2500, highlight=None):
    # Radar background + border
    pygame.draw.circle(screen, (30, 30, 30), radar_center, radar_radius)
    pygame.draw.circle(screen, WHITE, radar_center, radar_radius, 2)

    # Draw planets within radar range
    for body in celestial_bodies:
        bx, by = body["pos"]
        dx, dy = bx - player_x, by - player_y
        dist = math.hypot(dx, dy)
        if dist < radar_range:
            rx = radar_center[0] + int(dx / radar_range * radar_radius)
            ry = radar_center[1] + int(dy / radar_range * radar_radius)

            if highlight and body == highlight:
                # Red ring around closest planet
                pygame.draw.circle(screen, RED, (rx, ry), 10, 2)

            pygame.draw.circle(screen, body["color"], (rx, ry), 4)

    # Player marker
    pygame.draw.circle(screen, YELLOW, radar_center, 5)

    # If closest planet is OUTSIDE radar → draw arrow at edge
    if highlight:
        bx, by = highlight["pos"]
        dx, dy = bx - player_x, by - player_y
        dist = math.hypot(dx, dy)
        if dist >= radar_range:
            nx, ny = dx / dist, dy / dist
            arrow_x = radar_center[0] + int(nx * radar_radius)
            arrow_y = radar_center[1] + int(ny * radar_radius)

            size = 10
            points = [
                (arrow_x, arrow_y),
                (arrow_x - ny*size, arrow_y + nx*size),
                (arrow_x + ny*size, arrow_y - nx*size)
            ]
            pygame.draw.polygon(screen, RED, points)

        # Distance text (always shown if highlight exists)
        dist_text = font.render(f"{int(dist)}", True, RED)
        screen.blit(dist_text, (radar_center[0]-20, radar_center[1]+radar_radius+10))
