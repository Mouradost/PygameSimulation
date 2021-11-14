import matplotlib.pyplot as plt
from matplotlib import rcParams
import pygame
import random
import sys

# Colors
BLACK, WHITE, RED, GREEN, BLUE, GREY = (
    0, 0, 0), (255, 255, 255), (255, 0, 0), (0, 255, 0), (0, 0, 255), (100, 100, 100)

# AI constants
AI_TOLERANCE = 2


class AI:
    def __init__(self, fps):
        self.actions = [(0, 0), (0, 1), (0, -1), (1, 0),
                        (-1, 0), (1, 1), (-1, 1), (1, -1), (-1, -1)]
        self.fps = fps
        self.tolerance = AI_TOLERANCE * self.fps
        self.choice = random.randint(0, len(self.actions)-1)
        self.current_score = 0
        pass

    def take_action(self, reward):
        if reward > self.current_score:
            self.current_score = reward
        else:
            self.tolerance -= 1
            if self.tolerance <= 0:
                self.tolerance = AI_TOLERANCE * self.fps
                self.choice = random.randint(0, len(self.actions)-1)
        x, y = self.actions[self.choice][0], self.actions[self.choice][1]
        return x, y


class Player(pygame.sprite.Sprite):
    def __init__(self, id, map_width, map_height, width, height, color, velocity, fps):
        super(Player, self).__init__()
        self.id = id
        self.velocity = velocity
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.center = [random.randint(
            100, map_width - 100), random.randint(100, map_height - 100)]
        self.map_width = map_width
        self.map_height = map_height
        self.score = 0
        self.brain = AI(fps)

    def move(self, step):
        if self.rect.midright[0] + step[0] < self.map_width and self.rect.midleft[0] + step[0] > 0:
            self.rect.x += int(step[0] * self.velocity)
        if self.rect.midbottom[1] + step[1] < self.map_height and self.rect.midtop[1] + step[1] > 0:
            self.rect.y += int(step[1] * self.velocity)

    def update(self):
        self.move(self.brain.take_action(reward=self.score))


class Food(pygame.sprite.Sprite):
    def __init__(self, sim_size):
        super(Food, self).__init__()
        self.height = 10
        self.width = 10
        self.image = pygame.Surface([self.height, self.width])
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = [random.randint(
            self.width, sim_size[0] - self.width), random.randint(self.height, sim_size[1] - self.height)]

    def update(self):
        pass


class Simulation(pygame.sprite.Sprite):
    def __init__(self, height, width, runtime, fps=60, population_size=5, nb_food=10):
        self.size = (height, width)
        self.simulation_time = runtime * fps
        self.fps = fps
        self.nb_food = nb_food
        self.population_size = population_size

    def initialize(self):
        # Setting up Pygame
        pygame.init()
        self.font = pygame.font.SysFont("timesnewroman", 22)
        self.screen = pygame.display.set_mode(
            self.size)  # , pygame.FULLSCREEN)
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("AI Simulation")

        # Simulation variables
        self.active = True
        self.foods = pygame.sprite.Group()
        [self.foods.add(Food(self.size))
         for o in range(self.nb_food)]
        self.players = pygame.sprite.Group()
        [self.players.add(Player(
            id=i + 1,
            map_width=self.size[0], map_height=self.size[1],
            width=20, height=20, color=GREEN, velocity=2, fps=self.fps
        )) for i in range(self.population_size)]

    def draw(self):
        self.screen.fill(BLACK)
        self.players.draw(self.screen)
        self.foods.draw(self.screen)

    def stats(self, ticker):
        stat = f"Time: {ticker // self.fps} | "
        for player in self.players:
            stat += f"Player {player.id}: {player.score} || "
        surface = self.font.render(
            stat,
            True, WHITE
        )
        rect = surface.get_rect(center=(self.size[0] // 2, 20))
        pygame.draw.rect(self.screen, BLACK, rect)
        self.screen.blit(surface, rect)

    def update(self):
        self.foods.update()
        self.players.update()

    def check_collision(self):
        for collision in pygame.sprite.groupcollide(self.players, self.foods, False, True):
            collision.score += 1

    def run(self):
        # Initialize the simulation
        self.initialize()
        ticker = 0

        # The main loop
        while(ticker < self.simulation_time and self.active):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.active = False

            # Update the simulation
            self.update()

            # Check for collision
            self.check_collision()

            # Drawing to the screen
            self.draw()

            # Show the score
            self.stats(ticker)
            ticker += 1

            pygame.display.update()
            self.clock.tick(self.fps)

        self.stop()

    def stop(self):
        pygame.quit()
        for player in self.players:
            plt.bar(player.id, player.score, label=f'Player {player.id}')
        plt.legend()
        plt.show()
        sys.exit()


if __name__ == '__main__':
    rcParams["figure.figsize"] = 12, 8
    sim = Simulation(
        height=1080, width=720, runtime=20,
        fps=60, population_size=5, nb_food=1000
    )
    sim.run()
