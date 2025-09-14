from settings import *
from pygame.sprite import Group

class Asteroid:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(50, WIDTH-50), -20, 30, 30)
        self.speed = random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = -20
            self.rect.x = random.randint(50, WIDTH-50)

    def draw(self):
        pygame.draw.rect(screen, GRAY, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 5, 10)

    def update(self):
        self.rect.y -= 10

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)





class Render_Sprite(pygame.sprite.Sprite):
    def __init__(self, image, pos, groups=None):
        # Accept: None, a single Group, or an iterable of Groups
        if groups is None:
            super().__init__()
        elif isinstance(groups, Group):
            super().__init__(groups)
        else:
            # assume iterable of groups
            super().__init__(*groups)

        self.image = image
        self.rect = self.image.get_rect(topleft=pos)

