import pygame
import math
from settings import celestial_bodies, font, WIDTH, HEIGHT, PURPLE, STARFIELD
from radar import draw_radar   # ✅ import from radar, not main


def handle_navigation(screen, astronaut_x, astronaut_y, path_history, closest_body, show_path, keys, events, game_mode):
    # Camera for free panning
    cam_speed = 20
    if keys[pygame.K_LEFT]:
        handle_navigation.cam_x -= cam_speed
    if keys[pygame.K_RIGHT]:
        handle_navigation.cam_x += cam_speed
    if keys[pygame.K_UP]:
        handle_navigation.cam_y -= cam_speed
    if keys[pygame.K_DOWN]:
        handle_navigation.cam_y += cam_speed

    # Draw black background
    screen.fill((0, 0, 0))

    # ✅ Draw moving starfield (parallax effect in navigation mode)
    for sx, sy in STARFIELD:
        star_x = (sx - int(handle_navigation.cam_x / 10)) % WIDTH
        star_y = (sy - int(handle_navigation.cam_y / 10)) % HEIGHT
        screen.set_at((star_x, star_y), (255, 255, 255))

    # Draw celestial bodies with camera offset
    for body in celestial_bodies:
        bx, by = body["pos"]
        screen_x = bx - handle_navigation.cam_x
        screen_y = by - handle_navigation.cam_y
        radius = 12 if body == closest_body else 6
        color = (0, 255, 0) if body == closest_body else body["color"]
        pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), radius)
        text = font.render(body["name"], True, (255, 255, 255))
        screen.blit(text, (screen_x - 20, screen_y - 20))

    # Draw astronaut (blue square)
    astro_screen_x = astronaut_x - handle_navigation.cam_x
    astro_screen_y = astronaut_y - handle_navigation.cam_y
    pygame.draw.rect(screen, (50, 150, 255), (astro_screen_x - 6, astro_screen_y - 6, 12, 12))

    # Path history
    if show_path and len(path_history) > 1:
        for i in range(1, len(path_history)):
            prev_x, prev_y = path_history[i - 1]
            curr_x, curr_y = path_history[i]
            line_start = (prev_x - handle_navigation.cam_x, prev_y - handle_navigation.cam_y)
            line_end = (curr_x - handle_navigation.cam_x, curr_y - handle_navigation.cam_y)
            pygame.draw.line(screen, (255, 255, 0), line_start, line_end, 2)

    # Handle events
    new_game_mode = "navigation"
    new_closest_body = closest_body
    new_show_path = show_path

    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                new_game_mode = "inside"
            if event.key == pygame.K_p:
                new_show_path = not show_path
            if event.key == pygame.K_c:
                # find closest body
                min_dist = float("inf")
                for body in celestial_bodies:
                    if "orbit_center" in body:
                        dist = math.hypot(body["pos"][0] - astronaut_x, body["pos"][1] - astronaut_y)
                        if dist < min_dist:
                            min_dist = dist
                            new_closest_body = body

    # Draw instructions
    instr1 = font.render("Arrow keys: Pan | C: Closest Planet | P: Toggle Path | ESC: Exit", True, (255, 255, 255))
    screen.blit(instr1, (20, 20))
    if new_closest_body:
        closest_msg = font.render(f"Closest: {new_closest_body['name']} (highlighted green)", True, (255, 255, 255))
        screen.blit(closest_msg, (20, 50))

    # ✅ draw minimap with highlight (using radar.py)
    draw_radar(screen, astronaut_x, astronaut_y,
               radar_center=(WIDTH - 120, 120),
               radar_radius=100,
               radar_range=2500,
               highlight=new_closest_body)

    return new_closest_body, new_show_path, new_game_mode


# static variables for camera
handle_navigation.cam_x = WIDTH // 2
handle_navigation.cam_y = HEIGHT // 2
