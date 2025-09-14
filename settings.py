import pygame
import sys
import math
import random

# Screen
WIDTH, HEIGHT = 1500, 1200
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galactic Crew - Multi-Planet Gravity + Shuttle + Task")


# Colors
BLACK = (0,0,0)
WHITE = (255,255,255)
BLUE = (50,150,255)
GRAY = (100,100,100)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)
ORANGE = (255,165,0)
PURPLE = (180,0,255)

pygame.font.init()
font = pygame.font.SysFont("Arial", 20)


# ================= OUTSIDE MODE (Space Travel) ==================
astronaut_x, astronaut_y = 3253.97,3900.742
astronaut_dx, astronaut_dy = 0.0, 0.0
ASTRONAUT_SIZE = 40

# Thruster system
manual_thrust = 0.15   # manual nudge power
boost_thrust = 0.4     # thrust when auto/space engaged

# Celestial bodies
celestial_bodies = [
    # Sun
    {"name": "Sun", "pos": (10000, 8000), "color": (255, 255, 0), "influence": 4000, "radius": 80, "g": 1.5},

    # Planets (distances in thousands of pixels for exploration)
    {"name": "Mercury", "pos": (10000 + 2000, 8000), "color": (200, 200, 200), "orbit_center": (10000, 8000), "orbit_radius": 2000, "influence": 300, "radius": 18, "g": 0.04},
    {"name": "Venus", "pos": (10000 + 3800, 8000), "color": (255, 220, 180), "orbit_center": (10000, 8000), "orbit_radius": 3800, "influence": 400, "radius": 30, "g": 0.9},
    {"name": "Earth", "pos": (10000 + 5200, 8000), "color": (100, 150, 255), "orbit_center": (10000, 8000), "orbit_radius": 5200, "influence": 500, "radius": 32, "g": 1.0},
    {"name": "Mars", "pos": (10000 + 7900, 8000), "color": (255, 100, 50), "orbit_center": (10000, 8000), "orbit_radius": 7900, "influence": 400, "radius": 28, "g": 0.38},
    {"name": "Jupiter", "pos": (10000 + 27000, 8000), "color": (255, 200, 100), "orbit_center": (10000, 8000), "orbit_radius": 27000, "influence": 1200, "radius": 70, "g": 2.5},
    {"name": "Saturn", "pos": (10000 + 50000, 8000), "color": (220, 220, 180), "orbit_center": (10000, 8000), "orbit_radius": 50000, "influence": 1000, "radius": 60, "g": 1.1},
    {"name": "Uranus", "pos": (10000 + 100000, 8000), "color": (180, 220, 255), "orbit_center": (10000, 8000), "orbit_radius": 100000, "influence": 800, "radius": 44, "g": 0.9},
    {"name": "Neptune", "pos": (10000 + 160000, 8000), "color": (100, 100, 255), "orbit_center": (10000, 8000), "orbit_radius": 160000, "influence": 800, "radius": 44, "g": 1.1},

    # Moons (placed near their planets)
    {"name": "Moon", "pos": (10000 + 5200 + 120, 8000), "color": (220, 220, 220), "orbit_center": (10000 + 5200, 8000), "orbit_radius": 120, "influence": 60, "radius": 10, "g": 0.16},
    {"name": "Phobos", "pos": (10000 + 7900 + 40, 8000), "color": (180, 180, 180), "orbit_center": (10000 + 7900, 8000), "orbit_radius": 40, "influence": 20, "radius": 6, "g": 0.01},
    {"name": "Deimos", "pos": (10000 + 7900 + 70, 8000), "color": (200, 200, 200), "orbit_center": (10000 + 7900, 8000), "orbit_radius": 70, "influence": 20, "radius": 6, "g": 0.003},
    {"name": "Ganymede", "pos": (10000 + 27000 + 200, 8000), "color": (200, 200, 180), "orbit_center": (10000 + 27000, 8000), "orbit_radius": 200, "influence": 80, "radius": 14, "g": 0.15},
    {"name": "Titan", "pos": (10000 + 50000 + 300, 8000), "color": (210, 180, 140), "orbit_center": (10000 + 50000, 8000), "orbit_radius": 300, "influence": 80, "radius": 14, "g": 0.14},
    # Add more moons as desired...
]

# Tuning parameters
OUTSIDE_FRICTION = 0.998
INSIDE_GRAVITY_SCALE = 0.45
INSIDE_MANUAL_MULT = 1.0
MIN_DIST = 10.0

# ================= INSIDE MODE (Shuttle Rooms) ==================
astronaut_inside = pygame.Rect(150, 150, 40, 40)
astronaut_inside_x = float(astronaut_inside.x)
astronaut_inside_y = float(astronaut_inside.y)
astronaut_speed_inside = 4

walls = [
    pygame.Rect(0, 0, WIDTH, 10),
    pygame.Rect(0, HEIGHT-10, WIDTH, 10),
    pygame.Rect(0, 0, 10, HEIGHT),
    pygame.Rect(WIDTH-10, 0, 10, HEIGHT),
    pygame.Rect(300, 0, 10, 300),
    pygame.Rect(0, 300, WIDTH, 10),
]

doors = [
    pygame.Rect(280, 140, 40, 40),
    pygame.Rect(430, 290, 40, 40),
]

task_terminal = pygame.Rect(600, 150, 40, 40)
navigation_terminal = pygame.Rect(1000, 150, 40, 40)  # New navigation terminal


def draw_shuttle():
    for wall in walls:
        pygame.draw.rect(screen, GRAY, wall)
    for door in doors:
        pygame.draw.rect(screen, GREEN, door)
    pygame.draw.rect(screen, RED, task_terminal)
    pygame.draw.rect(screen, PURPLE, navigation_terminal)  # Draw navigation terminal
    cockpit = font.render("Cockpit", True, WHITE)
    control = font.render("Control Room", True, WHITE)
    engine = font.render("Engine Room", True, WHITE)
    navigation = font.render("Navigation Room", True, WHITE)
    screen.blit(cockpit, (100, 50))
    screen.blit(control, (500, 50))
    screen.blit(engine, (400, 400))
    screen.blit(navigation, (950, 50))

def check_collision(rect, move_x, move_y):
    future_rect = rect.move(move_x, move_y)
    for wall in walls:
        if future_rect.colliderect(wall):
            allowed = False
            for door in doors:
                if future_rect.colliderect(door):
                    allowed = True
            if not allowed:
                return False
    return True

STAR_COUNT = 500
STARFIELD = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(STAR_COUNT)]