import pygame
import sys
import random
import math
from settings import *

def play_gas_mix():
    running = True
    task_done = False
    WINDOW_WIDTH, WINDOW_HEIGHT = 1500, 1200

    class Slider:
        def __init__(self, x, color):
            self.rect = pygame.Rect(x, 200, 20, 200)
            self.knob_y = 300
            self.dragging = False
            self.color = color

        def handle_event(self, event):
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.dragging = True
            if event.type == pygame.MOUSEBUTTONUP:
                self.dragging = False
            if event.type == pygame.MOUSEMOTION and self.dragging:
                self.knob_y = max(200, min(400, event.pos[1]))

        def draw(self, surf):
            pygame.draw.rect(surf, GRAY, self.rect)
            pygame.draw.rect(surf, self.color, (self.rect.x, self.knob_y - 10, 20, 20))

        def value(self):
            return 100 - (self.knob_y - 200) / 2  # map slider position → % value

    # general setup 
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption('Gas Mix')
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 32)

    # sliders
    o2_slider = Slider(200, BLUE)
    n2_slider = Slider(400, GREEN)

    msg = ""
    confirmed = False
    success = False

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    task_done = False
                if event.key == pygame.K_RETURN and not confirmed:
                    o2 = o2_slider.value()
                    n2 = n2_slider.value()
                    total = o2 + n2
                    if abs(total - 100) > 5:
                        msg = "Gases must add to ~100%"
                    elif o2 > 25:
                        msg = "Too much oxygen! Fire risk!"
                    elif 20 <= o2 <= 22 and 78 <= n2 <= 80:
                        msg = "Success!"
                        success = True
                        confirmed = True
                        pygame.time.wait(1500)
                        running = False
                        task_done = True
                    else:
                        msg = "Incorrect ratio!"
                        confirmed = True

            o2_slider.handle_event(event)
            n2_slider.handle_event(event)

        # draw
        display_surface.fill(BLACK)
        o2_slider.draw(display_surface)
        n2_slider.draw(display_surface)

        total = o2_slider.value() + n2_slider.value()
        display_surface.blit(font.render("Gas Mix Task", True, WHITE), (300, 50))
        display_surface.blit(font.render(f"O2: {o2_slider.value():.1f}%", True, WHITE), (200, 420))
        display_surface.blit(font.render(f"N2: {n2_slider.value():.1f}%", True, WHITE), (400, 420))
        display_surface.blit(font.render(f"Total: {total:.1f}%", True, WHITE), (300, 470))
        display_surface.blit(font.render(msg, True, GREEN if success else RED), (200, 520))
        display_surface.blit(font.render("ENTER=Confirm  ESC=Exit", True, WHITE), (200, 600))

        pygame.display.update()

    return "done" if task_done else "inside"

def play_overheating():
    running = True
    task_done = False
    WINDOW_WIDTH, WINDOW_HEIGHT = 1500, 1200

    # General setup
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Overheating")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 32)

    # Game state
    zones = [random.randint(100, 1000) for _ in range(5)]
    current_round = 0
    indicator_x = 0
    hits = 0
    completed = False
    space_pressed = False
    green_width = 100
    speed = 6
    results = []

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    task_done = False
                if event.key == pygame.K_SPACE and not completed and not space_pressed:
                    space_pressed = True
                    green_start = zones[current_round]
                    if green_start <= indicator_x <= green_start + green_width:
                        hits += 1
                        results.append("Hit!")
                    else:
                        results.append("Miss!")
                    current_round += 1
                    indicator_x = 0
                    if current_round >= 5:
                        completed = True
                        if hits >= 5:
                            task_done = True
                            running = False
                if event.key == pygame.K_SPACE and completed and not task_done:
                    # retry
                    zones = [random.randint(100, 1000) for _ in range(5)]
                    current_round = 0
                    indicator_x = 0
                    hits = 0
                    completed = False
                    space_pressed = False
                    results = []
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    space_pressed = False

        # update indicator if not done
        if not completed:
            indicator_x += speed
            if indicator_x > WINDOW_WIDTH - 100:
                indicator_x = 0
                if not space_pressed:
                    results.append("Miss!")
                space_pressed = False
                current_round += 1
                if current_round >= 5:
                    completed = True
                    if hits >= 5:
                        task_done = True
                        running = False

        # --- DRAW ---
        display_surface.fill(BLACK)
        display_surface.blit(font.render("Overheating Task", True, WHITE), (400, 50))
        display_surface.blit(font.render("Press SPACE in green zone", True, WHITE), (350, 100))

        # Progress bar
        pygame.draw.rect(display_surface, GRAY, (400, 150, 400, 20))
        progress_width = (hits / 5) * 400
        pygame.draw.rect(display_surface, GREEN, (400, 150, progress_width, 20))

        # Timing bar
        pygame.draw.rect(display_surface, GRAY, (100, 300, WINDOW_WIDTH-200, 20))
        if not completed and current_round < 5:
            green_start = zones[current_round]
            pygame.draw.rect(display_surface, GREEN, (100 + green_start, 300, green_width, 20))
        pygame.draw.circle(display_surface, WHITE, (100 + indicator_x, 310), 10)

        # Round results
        for i, res in enumerate(results):
            color = GREEN if res == "Hit!" else RED
            display_surface.blit(font.render(f"Round {i+1}: {res}", True, color), (400, 350 + i * 30))

        # End message
        if completed:
            if hits == 5:
                msg = "Issue Resolved"
                color = GREEN
            elif hits >= 3:
                msg = "Almost there, try again"
                color = RED
            else:
                msg = "Failed"
                color = RED
            display_surface.blit(font.render(msg, True, color), (400, 550))
            if not task_done:
                display_surface.blit(font.render("Press SPACE to retry, ESC to quit", True, WHITE), (300, 600))

        pygame.display.update()

    return "done" if task_done else "inside"

def play_leak_repair():
    running = True
    task_done = False
    
    WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
    # WINDOW_WIDTH, WINDOW_HEIGHT = 800, 700

    # General setup
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Leak Repair")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 32)

    # Leak (cracks) setup
    cracks = []
    for _ in range(5):
        cracks.append({
            "rect": pygame.Rect(random.randint(100, WINDOW_WIDTH-100), random.randint(100, WINDOW_HEIGHT-200), 40, 10),
            "fixed": False
        })

    patches = []
    selected_patch = None

    while running:
        dt = clock.tick(60) / 1000
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    task_done = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Grab a patch
                if selected_patch is None:
                    for patch in patches:
                        if patch.collidepoint(mouse_pos):
                            selected_patch = patch
                            break
                    else:
                        # Create new patch at mouse
                        new_patch = pygame.Rect(mouse_pos[0]-20, mouse_pos[1]-20, 40, 40)
                        patches.append(new_patch)
                        selected_patch = new_patch
                else:
                    # Drop patch
                    placed = False
                    for crack in cracks:
                        if not crack["fixed"] and crack["rect"].colliderect(selected_patch):
                            crack["fixed"] = True
                            placed = True
                            break
                    if not placed:
                        patches.remove(selected_patch)
                    selected_patch = None

        # Move patch with mouse if selected
        if selected_patch:
            selected_patch.center = mouse_pos

        # Check win condition
        if all(crack["fixed"] for crack in cracks):
            task_done = True
            running = False

        # --- DRAW ---
        display_surface.fill(BLACK)
        display_surface.blit(font.render("Leak Repair Task", True, WHITE), (450, 50))
        display_surface.blit(font.render("Drag patches over leaks to seal them", True, WHITE), (350, 100))

        # Draw cracks
        for crack in cracks:
            color = GREEN if crack["fixed"] else RED
            pygame.draw.rect(display_surface, color, crack["rect"])

        # Draw patches
        for patch in patches:
            pygame.draw.rect(display_surface, GRAY, patch)

        # Draw instructions
        display_surface.blit(font.render("ESC to quit", True, WHITE), (50, 650))

        pygame.display.update()

    return "done" if task_done else "inside"

