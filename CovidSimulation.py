import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import numpy as np
import random
import pygame
import sys


# Constants
SIZE = WIDTH, HIGHT = 1080, 720
BLACK, WHITE, RED, GREEN, BLUE, GREY = (
    0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)
BLOB_SIZE, VELOCITY = 10, 1


class Blob(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, velocity, recovery_time, step=None):
        super(Blob, self).__init__()
        self.velocity = velocity
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        if step is None:
            self.step = random.choice(
                [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1)])
        else:
            self.step = step

        if color == RED:
            self.is_infected = True
        else:
            self.is_infected = False
        self.recovery_time = recovery_time
        self.to_recovery = 0

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

    def respawn(self, color):
        if color == RED:
            self.is_infected = True
        return Blob(self.rect.center[0], self.rect.center[1], BLOB_SIZE, BLOB_SIZE, color, -self.velocity, self.recovery_time, self.step)

    def update(self):
        # Random movement
        self.move(self.step[0], self.step[1])

        # Countdown to recovery
        if self.is_infected:
            self.to_recovery += 1
            if self.recovery_time <= self.to_recovery:
                self.to_recovery = 0
                self.is_infected = False


class Simulation:
    def __init__(self, population_size=100, initial_infected=10, initial_suspected=5, recovery_time=10, simulation_time=1000, width=1080, hight=720, stat_size=200, FPS=60):
        self.hight = hight
        self.width = width
        self.stat_size = stat_size
        self.size = (self.width, self.hight + self.stat_size)
        self.FPS = FPS

        self.population_size = population_size
        self.initial_infected = initial_infected
        self.initial_suspected = initial_suspected
        self.initial_healthy = self.population_size - \
            (self.initial_infected + self.initial_suspected)

        self.recovery_time = recovery_time * self.FPS

        self.healthy = pygame.sprite.Group()
        self.infected = pygame.sprite.Group()
        self.recovered = pygame.sprite.Group()
        self.suspected = pygame.sprite.Group()

        self.simulation_time = simulation_time * self.FPS

        self.history = {
            "Day": [],
            "Healthy": [],
            "Suspected": [],
            "Infected": [],
            "Recovered": []
        }

        # Setting up Pygame
        pygame.init()
        self.font = pygame.font.SysFont("timesnewroman", 22)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Simulation")

    def initialize(self):
        self.healthy.add([Blob(np.random.randint(0, self.width), np.random.randint(
            0, self.hight), BLOB_SIZE, BLOB_SIZE, WHITE, VELOCITY, self.recovery_time, None) for _ in range(self.initial_healthy)])
        self.infected.add([Blob(np.random.randint(0, self.width), np.random.randint(
            0, self.hight), BLOB_SIZE, BLOB_SIZE, RED, VELOCITY, self.recovery_time, None) for _ in range(self.initial_infected)])
        self.suspected.add([Blob(np.random.randint(0, self.width), np.random.randint(
            0, self.hight), BLOB_SIZE, BLOB_SIZE, BLUE, VELOCITY, self.recovery_time, None) for _ in range(self.initial_suspected)])

    def check_collision(self):
        for collision in pygame.sprite.groupcollide(self.suspected, self.infected, True, False):
            self.infected.add(collision.respawn(RED))

        for collision in pygame.sprite.groupcollide(self.healthy, self.infected, True, False):
            self.suspected.add(collision.respawn(BLUE))

    def check_recovery(self):
        for infected in self.infected:
            if not infected.is_infected:
                self.recovered.add(infected.respawn(GREEN))
                self.infected.remove(infected)
                infected.kill()

    def update(self):
        self.healthy.update()
        self.infected.update()
        self.suspected.update()
        self.recovered.update()

    def draw(self):
        self.screen.fill(BLACK)
        pygame.draw.rect(self.screen, GREY, pygame.Rect(
            0, self.hight, self.width, self.stat_size), 2)

        pygame.draw.rect(self.screen, WHITE, pygame.Rect(
            220, self.hight + (self.stat_size // 16), BLOB_SIZE * 10, BLOB_SIZE))
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(
            400, self.hight + (self.stat_size // 16), BLOB_SIZE * 10, BLOB_SIZE))
        pygame.draw.rect(self.screen, RED, pygame.Rect(
            580, self.hight + (self.stat_size // 16), BLOB_SIZE * 10, BLOB_SIZE))
        pygame.draw.rect(self.screen, GREEN, pygame.Rect(
            760, self.hight + (self.stat_size // 16), BLOB_SIZE * 10, BLOB_SIZE))

        self.healthy.draw(self.screen)
        self.infected.draw(self.screen)
        self.suspected.draw(self.screen)
        self.recovered.draw(self.screen)

    def show_text(self, surface, position, background=BLACK):
        rect = surface.get_rect(center=position)
        pygame.draw.rect(self.screen, background, rect)
        self.screen.blit(surface, rect)

    def stats(self, day):
        self.history["Day"].append(day // self.FPS)
        self.history["Healthy"].append(len(self.healthy))
        self.history["Suspected"].append(len(self.suspected))
        self.history["Infected"].append(len(self.infected))
        self.history["Recovered"].append(len(self.recovered))

        self.show_text(
            self.font.render(f"Day: {day // self.FPS}", True, WHITE),
            (self.width // 16,
             self.hight + (self.stat_size // 8))
        )

        stat_surface = self.font.render(
            f"{f'Healthy':^25}"
            f"{f'Suspected':^25}"
            f"{f'Infected':^25}"
            f"{f'Recovered':^25}",
            True, WHITE
        )
        self.show_text(stat_surface, (self.width // 2,
                       self.hight + (self.stat_size // 4)))

        stat_surface = self.font.render(
            f"{len(self.healthy):^30}"
            f"{len(self.suspected):^30}"
            f"{len(self.infected):^30}"
            f"{len(self.recovered):^30}",
            True, WHITE
        )
        self.show_text(stat_surface, (self.width // 2,
                       self.hight + (self.stat_size // 2)))

        stat_surface = self.font.render(
            f"{f'{len(self.healthy) / self.population_size:.1%}':^28}"
            f"{f'{len(self.suspected) / self.population_size:.1%}':^28}"
            f"{f'{len(self.infected) / self.population_size:.1%}':^28}"
            f"{f'{len(self.recovered) / (self.population_size + len(self.healthy)):.1%}':^28}",
            True, WHITE
        )
        self.show_text(stat_surface, (self.width // 2,
                       self.hight + self.stat_size - 50))

    def start(self):
        # Initialize the simulation
        self.initialize()

        # The main loop
        for day in range(self.simulation_time):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

            # Movement
            self.update()

            # Check for collision
            self.check_collision()

            # Check recovered
            self.check_recovery()

            # Drawing to the screen
            self.draw()

            # Display the current stats
            self.stats(day)

            pygame.display.update()
            self.clock.tick(self.FPS)

        self.stop()

    def stop(self):
        pygame.quit()
        self.show_graph()
        sys.exit()

    def show_graph(self):
        df = pd.DataFrame(self.history)
        df.groupby("Day").mean().plot()
        plt.title("Overview of the simulation")
        plt.grid(True)
        plt.style.use("ggplot")
        plt.show()


if __name__ == '__main__':
    rcParams["figure.figsize"] = 12, 8
    covid = Simulation(
        population_size=800,
        initial_infected=1,
        initial_suspected=5,
        simulation_time=20,
        recovery_time=10
    )
    covid.start()
