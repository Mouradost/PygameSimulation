import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import random
import pygame
import pymunk
import sys


# Constants
WIDTH, HIGHT = 1080, 720
SIZE = (WIDTH + 20, HIGHT)
FPS = 60
BLACK, WHITE, RED, GREEN, BLUE, GREY = (
    0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)
BLOB_SIZE, BLOB_RADIUS = 10, 5


class Blob(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color, velocity, mortality_rate, recovery_time, radius=BLOB_RADIUS):
        super(Blob, self).__init__()
        self.body = pymunk.Body()
        self.body.position = (x, y)
        self.body.velocity = velocity
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.density = 1
        self.shape.elasticity = 1

        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

        self.velocity = velocity
        self.dead = False
        self.infected = False
        self.infected_time = 0
        self.luck = random.random()
        self.mortality_rate = mortality_rate
        self.recovery_time = recovery_time

    def respawn(self, color):
        if color == RED:
            self.infected = True
        self.image.fill(color)
        return self

    def move(self):
        x, y = self.body.position
        self.rect.x = int(x)
        self.rect.y = int(y)

    def update(self):
        self.move()
        if self.infected:
            if self.infected_time <= self.recovery_time and self.luck * self.infected_time <= self.mortality_rate:
                self.infected_time += 1
            elif self.infected_time > self.recovery_time:
                self.infected = False
                self.infected_time = 0
            else:
                self.dead = True


class Wall:
    def __init__(self, start, end):
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.shape = pymunk.Segment(self.body, start, end, 5)
        self.shape.elasticity = 1


class Simulation:
    def __init__(self, population_size, infected_ratio, mortality_rate, recovery_time, simulation_time):
        self.population_size = population_size
        self.infected_ratio = infected_ratio
        self.recovery_time = recovery_time * FPS
        self.mortality_rate = mortality_rate * self.recovery_time
        self.simulation_time = simulation_time * FPS

        self.bar_length = HIGHT
        self.ratio = self.population_size / self.bar_length

    def initialize(self):
        # Setting up Pygame
        pygame.init()
        self.font = pygame.font.SysFont("timesnewroman", 22)
        self.screen = pygame.display.set_mode(SIZE)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Simulation")

        # Setting pymunk
        self.space = pymunk.Space()

        # Containers
        self.blobs_infected = pygame.sprite.Group()
        self.blobs_healthy = pygame.sprite.Group()
        self.blobs_recovered = pygame.sprite.Group()

        # Creating the walls
        walls = []
        walls.append(Wall((0, 0), (WIDTH, 0)))
        walls.append(Wall((0, 0), (0, HIGHT)))
        walls.append(Wall((WIDTH, 0), (WIDTH, HIGHT)))
        walls.append(Wall((0, HIGHT), (WIDTH, HIGHT)))
        for wall in walls:
            self.space.add(wall.body, wall.shape)

        # Creating the blobs
        for _ in range(int(self.population_size - self.population_size * self.infected_ratio)):
            blob = Blob(random.randint(0, WIDTH),
                        random.randint(0, HIGHT),
                        BLOB_SIZE, BLOB_SIZE, WHITE,
                        (random.randint(-100, 100), random.randint(-100, 100)),
                        self.mortality_rate,
                        random.randint(self.recovery_time - (5 * FPS), self.recovery_time))
            self.space.add(blob.body, blob.shape)
            self.blobs_healthy.add(blob)

        for _ in range(int(self.population_size * self.infected_ratio)):
            blob = Blob(random.randint(0, WIDTH),
                        random.randint(0, HIGHT),
                        BLOB_SIZE, BLOB_SIZE, RED,
                        (random.randint(-100, 100), random.randint(-100, 100)),
                        self.mortality_rate,
                        random.randint(self.recovery_time - (5 * FPS), self.recovery_time))
            self.space.add(blob.body, blob.shape)
            self.blobs_infected.add(blob)

        self.history = {
            "Day": [0],
            "Healthy": [len(self.blobs_healthy)],
            "Infected": [len(self.blobs_infected)],
            "Recovered": [len(self.blobs_recovered)],
            "Dead": [0]
        }

    def update(self):
        self.blobs_infected.update()
        self.blobs_healthy.update()
        self.blobs_recovered.update()

    def check_collision(self):
        for collision in pygame.sprite.groupcollide(self.blobs_healthy, self.blobs_infected, True, False):
            self.blobs_infected.add(collision.respawn(RED))

    def check_recovery(self):
        for infected in self.blobs_infected:
            if not infected.infected:
                self.blobs_recovered.add(infected.respawn(GREEN))
                self.blobs_infected.remove(infected)
            if infected.dead:
                self.space.remove(infected.body)
                infected.kill()

    def show_bar(self):
        healthy_bar = pygame.Rect(
            WIDTH, 0, 20, self.history["Healthy"][-1] // self.ratio)
        pygame.draw.rect(self.screen, WHITE, healthy_bar)

        infected_bar = pygame.Rect(
            WIDTH, healthy_bar.bottom, 20, self.history["Infected"][-1] // self.ratio)
        pygame.draw.rect(self.screen, RED, infected_bar)

        recovered_bar = pygame.Rect(
            WIDTH, infected_bar.bottom, 20, self.history["Recovered"][-1] // self.ratio)
        pygame.draw.rect(self.screen, GREEN, recovered_bar)

        pygame.draw.rect(self.screen, GREY, pygame.Rect(
            WIDTH, 0, 20, self.bar_length), 6)

    def draw(self):
        self.screen.fill(BLACK)
        self.blobs_infected.draw(self.screen)
        self.blobs_healthy.draw(self.screen)
        self.blobs_recovered.draw(self.screen)
        self.show_bar()

    def stat(self, day):
        self.history["Day"].append(day // FPS)
        self.history["Healthy"].append(len(self.blobs_healthy))
        self.history["Infected"].append(len(self.blobs_infected))
        self.history["Recovered"].append(len(self.blobs_recovered))
        self.history["Dead"].append(self.population_size - (
            len(self.blobs_healthy) + len(self.blobs_infected) + len(self.blobs_recovered)))

        print("="*20)
        print(
            f"Dead ratio: {1-(len(self.blobs_healthy) + len(self.blobs_infected) + len(self.blobs_recovered))/self.population_size:.2%}")
        print(
            f"Healthy ratio: {len(self.blobs_healthy)/self.population_size:.2%}")
        print(
            f"Infected ratio: {len(self.blobs_infected)/self.population_size:.2%}")
        print(
            f"Recovered ratio: {len(self.blobs_recovered)/self.population_size:.2%}")
        print("="*20)

    def show_graph(self):
        df = pd.DataFrame(self.history)
        df.groupby("Day").mean().plot()
        plt.title("Overview of the simulation")
        plt.grid(True)
        plt.style.use("ggplot")
        plt.show()

    def run(self):
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

            # Check for recovery
            self.check_recovery()

            # Drawing to the screen
            self.draw()

            # Stats
            self.stat(day)

            pygame.display.update()
            self.clock.tick(FPS)
            self.space.step(1/FPS)

        self.stop()

    def stop(self):
        pygame.quit()
        self.show_graph()
        sys.exit()


if __name__ == '__main__':
    rcParams["figure.figsize"] = 12, 8
    sim = Simulation(
        population_size=500,
        infected_ratio=0.2,
        mortality_rate=0.5,
        recovery_time=10,
        simulation_time=20
    )
    sim.run()
