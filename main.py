import pygame
import sys
import math
import os
from navigation import handle_navigation
from pytmx.util_pygame import load_pygame
from settings import *  # WIDTH/HEIGHT/colors/physics/STARFIELD/celestial_bodies/etc.
from entities import *
from shooter import *
from o2 import *
from tasks import asteroid_mini_game
from radar import draw_radar   # external radar.py

pygame.init()
pygame.font.init()

# ----------------- Load Spaceship Sprite (outside) -----------------
try:
    ship_img = pygame.image.load(os.path.join('resources', 'images', 'player.png')).convert_alpha()
    ship_base = pygame.transform.scale(ship_img, (75, 112))
except pygame.error as e:
    print("⚠️ Could not load player.png, using fallback shape:", e)
    ship_base = pygame.Surface((80, 40), pygame.SRCALPHA)
    pygame.draw.polygon(ship_base, (0, 120, 255), [(0, 0), (80, 20), (0, 40)])  # fallback

# ----------------- Collision Sprite (from Tiled) -----------------
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, size, group):
        super().__init__(group)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill((255, 0, 0, 0))  # fully transparent collider
        self.rect = self.image.get_rect(topleft=pos)

# ----------------- Animated Player (Inside Shuttle) -----------------
class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        base_path = "resources/player"

        def load_and_scale(path):
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale_by(img, 2)   # scale ×2

        self.animations = {
            "down":  [load_and_scale(os.path.join(base_path, "down",  f"{i}.png")) for i in range(4)],
            "up":    [load_and_scale(os.path.join(base_path, "up",    f"{i}.png")) for i in range(4)],
            "left":  [load_and_scale(os.path.join(base_path, "left",  f"{i}.png")) for i in range(4)],
            "right": [load_and_scale(os.path.join(base_path, "right", f"{i}.png")) for i in range(4)],
        }

        self.direction = "down"
        self.frame_index = 0
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_frect(center=pos)   # screen-space (we’ll center it each frame)
        self.hitbox_rect = self.rect.inflate(-100,0)
        # print(self.rect.__dir__())

        self.speed = 7
        self.animation_speed = 0.2

        # World coords inside shuttle (camera follows this)
        self.world_x = 2900
        self.world_y = 1205

    @property
    def world_rect(self) -> pygame.Rect:
        """A rect for collisions in WORLD space (not screen), sized to legs."""
        img_rect = self.image.get_rect()
        leg_width = img_rect.width // 2.5
        leg_height = int(img_rect.height / 4.5)
        # Position at bottom middle
        r = pygame.Rect(0, 0, leg_width, leg_height)
        r.midbottom = (self.world_x, self.world_y + img_rect.height // 2)
        return r

    def handle_input(self, collision_sprites):
        keys = pygame.key.get_pressed()
        moving = False

        dx = dy = 0
        if keys[pygame.K_UP]:
            dy = -self.speed
            self.direction = "up"; moving = True
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            self.direction = "down"; moving = True
        elif keys[pygame.K_LEFT]:
            dx = -self.speed
            self.direction = "left"; moving = True
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.direction = "right"; moving = True

        # ---- world-space collision checks ----
        # Try X
        if dx:
            self.world_x += dx
            if any(self.world_rect.colliderect(c.rect) for c in collision_sprites):
                self.world_x -= dx  # undo on hit

        # Try Y
        if dy:
            self.world_y += dy
            if any(self.world_rect.colliderect(c.rect) for c in collision_sprites):
                self.world_y -= dy  # undo on hit

        return moving

    def animate(self, moving):
        if moving:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.animations[self.direction]):
                self.frame_index = 0
        else:
            self.frame_index = 0
        self.image = self.animations[self.direction][int(self.frame_index)]

    def update(self, collision_sprites):
        moving = self.handle_input(collision_sprites)
        self.animate(moving)
        # Keep the sprite drawn at screen center (camera follows)
        self.rect.center = (WIDTH // 2, HEIGHT // 2)

# ---------------- Gravity Helper (outside) ----------------
def compute_net_gravity_at_point(x, y):
    net_x, net_y = 0.0, 0.0
    for body in celestial_bodies:
        bx, by = body["pos"]
        dx = bx - x
        dy = by - y
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            dist = MIN_DIST
        if dist < body["influence"]:
            nx = dx / dist
            ny = dy / dist
            factor = body["g"] * (1.0 - (dist / body["influence"]))
            net_x += nx * factor
            net_y += ny * factor
    return net_x, net_y

# ---------------- Setup ----------------
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Crew - Shuttle Interior + Navigation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 22)

game_mode = "outside"
closest_body = None
show_path = False

# Outside astronaut physics (overrides in settings if you want)
astronaut_x, astronaut_y = 2453.97, 630.742
astronaut_dx, astronaut_dy = 0.0, 0.0
path_history = [(astronaut_x, astronaut_y)]

# Load shuttle interior
tmx = load_pygame("Tiled/untitled.tmx")

# Image layers (as you had)
map_layers = []
for obj in tmx.get_layer_by_name("Layout"):
    if obj.image:
        map_layers.append((obj.image, (obj.x, obj.y)))


# Inside astronaut (animated)
player = Player((2000, 3000))
all_sprites = pygame.sprite.Group(player)

# Collision group (Tiled object layer named exactly "collider")
collision_sprites = pygame.sprite.Group()
for obj in tmx.get_layer_by_name("collider"):
    CollisionSprite((obj.x, obj.y), (obj.width, obj.height), collision_sprites)

# ---------------- Main Loop ----------------
angle = 0
DEBUG_DRAW_COLLIDERS = True  # set False to hide red boxes

while True:
    screen.fill(BLACK)
    events = pygame.event.get()

    # Handle events (QUIT/ESC) — inside the loop!
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit(); sys.exit()

    keys = pygame.key.get_pressed()

    # ============== OUTSIDE MODE ==============
    if game_mode == "outside":
        g_x, g_y = compute_net_gravity_at_point(astronaut_x, astronaut_y)

        # Movement
        thrust_dx = thrust_dy = 0.0
        if keys[pygame.K_UP]: thrust_dy -= manual_thrust
        if keys[pygame.K_DOWN]: thrust_dy += manual_thrust
        if keys[pygame.K_LEFT]: thrust_dx -= manual_thrust
        if keys[pygame.K_RIGHT]: thrust_dx += manual_thrust
        if keys[pygame.K_SPACE]:
            if keys[pygame.K_UP]: thrust_dy -= boost_thrust
            if keys[pygame.K_DOWN]: thrust_dy += boost_thrust
            if keys[pygame.K_LEFT]: thrust_dx -= boost_thrust
            if keys[pygame.K_RIGHT]: thrust_dx += boost_thrust

        astronaut_dx += thrust_dx + g_x
        astronaut_dy += thrust_dy + g_y
        astronaut_x += astronaut_dx
        astronaut_y += astronaut_dy
        astronaut_dx *= OUTSIDE_FRICTION
        astronaut_dy *= OUTSIDE_FRICTION

        # Camera follows
        camera_x = astronaut_x - WIDTH // 2
        camera_y = astronaut_y - HEIGHT // 2

        # Celestial bodies
        for body in celestial_bodies:
            bx, by = body["pos"]
            screen_x = bx - camera_x
            screen_y = by - camera_y
            pygame.draw.circle(screen, body["color"], (int(screen_x), int(screen_y)), body["radius"])
            text = font.render(body["name"], True, WHITE)
            screen.blit(text, (screen_x - 20, screen_y - body["radius"] - 20))

        # Shuttle sprite aligned to thrust direction
        if thrust_dx != 0 or thrust_dy != 0:
            angle = math.degrees(math.atan2(-thrust_dy, thrust_dx))
        display_angle = angle - 90
        rotated_ship = pygame.transform.rotate(ship_base, display_angle)
        ship_rect = rotated_ship.get_rect(center=(astronaut_x - camera_x, astronaut_y - camera_y))
        screen.blit(rotated_ship, ship_rect)

        # Radar
        draw_radar(screen, astronaut_x, astronaut_y, highlight=closest_body)

        # Enter shuttle
        msg = font.render("Press E to enter your Shuttle", True, WHITE)
        screen.blit(msg, (300, 750))
        if keys[pygame.K_e]:
            game_mode = "inside"
            # Put the player at a door spawn (adjust to your map)
            player.world_x, player.world_y = 2300, 1005  # <— set to your shuttle door in WORLD coords

        # Starfield parallax
        for sx, sy in STARFIELD:
            star_x = (sx - int(astronaut_x / 10)) % WIDTH
            star_y = (sy - int(astronaut_y / 10)) % HEIGHT
            screen.set_at((star_x, star_y), (255, 255, 255))

    # ============== INSIDE MODE ==============
    elif game_mode == "inside":
        all_sprites.update(collision_sprites)

        # Draw shuttle (offset relative to player world coords)
        for img, pos in map_layers:
            screen.blit(
                img,
                (pos[0] - player.world_x + WIDTH // 2, pos[1] - player.world_y + HEIGHT // 2)
            )

        # Debug: draw collider boxes with same camera offset
        if DEBUG_DRAW_COLLIDERS:
            for c in collision_sprites:
                screen.blit(
                    c.image,
                    (c.rect.x - player.world_x + WIDTH // 2, c.rect.y - player.world_y + HEIGHT // 2)
                )

        # Draw astronaut (sprite kept centered in Player.update)
        all_sprites.draw(screen)

        # Draw player's collision hitbox in red--------------------------
        hitbox_rect = player.world_rect
        hitbox_screen_rect = hitbox_rect.copy()
        hitbox_screen_rect.x = hitbox_rect.x - player.world_x + WIDTH // 2
        hitbox_screen_rect.y = hitbox_rect.y - player.world_y + HEIGHT // 2
        pygame.draw.rect(screen, (255, 0, 0), hitbox_screen_rect, 2)  # 2px border

        # Debug coords (world)
        coords_text = font.render(f"Coords: ({int(player.world_x)}, {int(player.world_y)})", True, WHITE)
        screen.blit(coords_text, (20, 20))

        # ----- Task zones (defined in WORLD coords) -----
        shooter_zone = pygame.Rect(1445, 1460, 1635 - 1445, 1860 - 1460)
        if shooter_zone.collidepoint(player.world_x, player.world_y):
            msg = font.render("Press Y to start Asteroid Defense", True, WHITE)
            screen.blit(msg, (400, 720))
            if keys[pygame.K_y]:
                play_shooter()

        O2_zone = pygame.Rect(333, 869, 557 - 333, 1065 - 869)
        if O2_zone.collidepoint(player.world_x, player.world_y):
            msg = font.render("Press Y to start O2", True, WHITE)
            screen.blit(msg, (400, 720))
            if keys[pygame.K_y]:
                play_gas_mix()

        repair_zone = pygame.Rect(3945, 2759, 4148 - 3945, 2962 - 2759)
        if repair_zone.collidepoint(player.world_x, player.world_y):
            msg = font.render("Press Y to start repair leak", True, WHITE)
            screen.blit(msg, (400, 720))
            if keys[pygame.K_y]:
                play_leak_repair()

        Overheating_zone = pygame.Rect(1726, 2591, 1866 - 1726, 2703 - 2591)
        if Overheating_zone.collidepoint(player.world_x, player.world_y):
            msg = font.render("Press Y to start control heating", True, WHITE)
            screen.blit(msg, (400, 720))
            if keys[pygame.K_y]:
                play_overheating()

        nav_zone = pygame.Rect(5830, 990, 6150 - 5830, 1440 - 990)
        if nav_zone.collidepoint(player.world_x, player.world_y):
            msg = font.render("Press Y to open Navigation Console", True, WHITE)
            screen.blit(msg, (400, 760))
            if keys[pygame.K_y]:
                game_mode = "navigation"

        # Exit to space
        msg = font.render("Press Q to exit Shuttle", True, WHITE)
        screen.blit(msg, (500, 770))
        if keys[pygame.K_q]:
            game_mode = "outside"
            astronaut_dx = astronaut_dy = 0.0

    # ============== NAVIGATION MODE ==============
    elif game_mode == "navigation":
        msg = font.render("Navigation Console Active (Press Y to Exit)", True, WHITE)
        screen.blit(msg, (300, 50))

        closest_body, show_path, new_game_mode = handle_navigation(
            screen, astronaut_x, astronaut_y, path_history,
            closest_body, show_path, keys, events, game_mode
        )
        if keys[pygame.K_y]:
            game_mode = "inside"

    pygame.display.flip()
    clock.tick(60)
