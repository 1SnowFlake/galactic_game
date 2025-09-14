from entities import Asteroid, Bullet
from settings import *

# ================= MINI-GAME (Asteroid Shooting) ==================

def asteroid_mini_game():
    bullets = []
    asteroids = [Asteroid() for _ in range(5)]
    player = pygame.Rect(WIDTH//2, HEIGHT-60, 40, 40)
    score = 0

    clock = pygame.time.Clock()
    running = True
    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.x -= 5
        if keys[pygame.K_RIGHT]:
            player.x += 5
        if keys[pygame.K_SPACE]:
            if len(bullets) < 5:
                bullets.append(Bullet(player.centerx, player.top))
        if keys[pygame.K_ESCAPE]:
            running = False

        for bullet in bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                bullets.remove(bullet)

        for asteroid in asteroids:
            asteroid.update()
            for bullet in bullets[:]:
                if asteroid.rect.colliderect(bullet.rect):
                    bullets.remove(bullet)
                    score += 1   # ✅ add score when asteroid destroyed
                    asteroid.rect.y = -20
                    asteroid.rect.x = random.randint(50, WIDTH-50)

        pygame.draw.rect(screen, BLUE, player)
        for bullet in bullets:
            bullet.draw()
        for asteroid in asteroids:
            asteroid.draw()

        # ✅ Display score as kills, not time
        score_text = font.render(f"Meteors Destroyed: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        exit_text = font.render("Press ESC to return", True, WHITE)
        screen.blit(exit_text, (WIDTH//2 - 100, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)
