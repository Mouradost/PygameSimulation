import numpy as np
import random
import pygame
import sys


# Constants
SIZE = WIDTH, HIGHT = 1080, 720
BLACK, WHITE, RED, GREEN, BLUE, GREY = (
    0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)
BLOB_NB, BLOB_SIZE, PLAYER_SIZE = 500, 10, 20
VELOCITY = 1
FPS = 60


class Blob(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, velocity, step=None):
        super(Blob, self).__init__()
        self.velocity = velocity
        self.image = pygame.Surface([width, height])
        self.image.fill(random.choice([GREEN, BLUE, WHITE]))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        if step is None:
            self.step = random.choice(
                [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)])
        else:
            self.step = step

    def move(self, x, y):
        self.rect.x += int(x * self.velocity)
        self.rect.y += int(y * self.velocity)
        if self.rect.midright[0] > WIDTH:
            self.rect.center = [0 + BLOB_SIZE, self.rect.center[1]]
        if self.rect.midleft[0] < 0:
            self.rect.center = [WIDTH - BLOB_SIZE, self.rect.center[1]]

        if self.rect.midbottom[1] > HIGHT:
            self.rect.center = [self.rect.center[0], 0 + BLOB_SIZE]
        if self.rect.midtop[1] < 0:
            self.rect.center = [self.rect.center[0], HIGHT - BLOB_SIZE]

    def respawn(self):
        return Blob(self.rect.center[0], self.rect.center[1], BLOB_SIZE, BLOB_SIZE, -self.velocity, self.step)

    def update(self):
        # Random movement
        self.move(self.step[0], self.step[1])


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, velocity):
        super(Player, self).__init__()
        self.velocity = velocity
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.score = 0

    def move(self, x, y):
        if self.rect.midright[0] + x < WIDTH and self.rect.midleft[0] + x > 0:
            self.rect.x += int(x * self.velocity)
        if self.rect.midbottom[1] + y < HIGHT and self.rect.midtop[1] + y > 0:
            self.rect.y += int(y * self.velocity)

    def update(self):
        # Keyboard inputs to move
        # key = pygame.key.get_pressed()
        # if key[pygame.K_LEFT]:
        #     self.move(-1, 0)
        # if key[pygame.K_RIGHT]:
        #     self.move(1, 0)
        # if key[pygame.K_UP]:
        #     self.move(0, -1)
        # if key[pygame.K_DOWN]:
        #     self.move(0, 1)

        # Follow the mouse
        self.rect.center = pygame.mouse.get_pos()


def main():
    # Setting up Pygame
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    clock = pygame.time.Clock()
    pygame.display.set_caption("Eat me")
    font = pygame.font.SysFont("timesnewroman", 22)

    # Player
    player = pygame.sprite.GroupSingle()
    player.add(Player(200, 200, PLAYER_SIZE, PLAYER_SIZE, RED, VELOCITY))

    # Blobs
    blobs = pygame.sprite.Group()
    blobs.add([Blob(np.random.randint(0, WIDTH), np.random.randint(
        0, HIGHT), BLOB_SIZE, BLOB_SIZE, VELOCITY) for _ in range(BLOB_NB)])

    # The main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # Take action
        blobs.update()
        player.update()

        # Check for collision
        for _ in pygame.sprite.spritecollide(
                player.sprite, blobs, True):
            player.sprite.score += 1

        # Drawing to the screen
        screen.fill(BLACK)
        blobs.draw(screen)
        player.draw(screen)
        surface = font.render(f"Score: {player.sprite.score}", True, WHITE)
        rect = surface.get_rect(center=(WIDTH // 2, 20))
        pygame.draw.rect(screen, BLACK, rect)
        screen.blit(surface, rect)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()
