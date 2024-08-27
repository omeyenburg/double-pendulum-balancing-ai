from pendulum import Pendulum
from util import Vec, argv
import pygame.freetype
import pygame.gfxdraw
import pygame
import math


WIDTH = 540
HEIGHT = 675

WHITE = (200, 200, 200)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


class Window:
    def __init__(self):
        self.pendulum = Pendulum()
        # self.pendulum.angular_damping = argv(
        #     "angular-damping", self.pendulum.angular_damping
        # )
        # self.pendulum.horizontal_damping = argv(
        #     "horizontal-damping", self.pendulum.horizontal_daming
        # )
        # self.pendulum.gravity = argv("gravity", self.pendulum.gravity)

        pygame.init()
        self.window = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.center = Vec(WIDTH // 2, HEIGHT // 2)
        self.unit_length = abs(WIDTH // 8 - WIDTH // 2) / self.pendulum.EDGE
        self.trail = []
        self.trail_length = 30
        self.scroll_mult = 10

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.MOUSEWHEEL:
                acceleration = (-event.x or event.y) * self.scroll_mult
                self.pendulum.apply_acceleration(Vec(acceleration, 0))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset
                    self.pendulum = Pendulum()

        self.draw()
        self.pendulum.update()

        pygame.display.flip()
        self.clock.tick(60)
        self.window.fill(BLACK)

    def draw(self):
        # Draw pendulum trail
        self.draw_trail()

        # Draw rail
        self.draw_rail()

        # Draw pendulum
        self.draw_pendulum()

    def draw_trail(self):
        for i, p in enumerate(self.trail):
            r = int(1 + i // (self.trail_length / 3))
            f = i / self.trail_length
            c = (200 * f, 30 * f, 150 * f)

            pygame.gfxdraw.filled_circle(self.window, round(p.x), round(p.y), r, c)
            pygame.gfxdraw.aacircle(self.window, round(p.x), round(p.y), r, c)

    def draw_rail(self):
        rail_start = self.center + Vec(self.unit_length, 0)
        rail_end = self.center - Vec(self.unit_length, 0)
        pygame.draw.line(self.window, GRAY, rail_start.tolist(), rail_end.tolist(), 2)
        rail_sections = 4

        for i in range(rail_sections + 1):
            x = rail_start.x * i / rail_sections + rail_end.x * (1 - i / rail_sections)
            rail_top = (x, rail_start.y + 3)
            rail_bottom = (x, rail_start.y + -3)
            pygame.draw.line(self.window, WHITE, rail_top, rail_bottom, 1)

    def draw_pendulum(self):
        cart = self.center + Vec(self.pendulum.pivot.x * self.unit_length, 0)
        b0 = Vec.from_angle(self.pendulum.theta0 + math.pi / 2)
        b0 = b0 * 0.5 * self.unit_length * self.pendulum.l0 + cart
        b1 = Vec.from_angle(self.pendulum.theta1 + math.pi / 2)
        b1 = b1 * 0.5 * self.unit_length * self.pendulum.l1 + b0

        self.trail.append(b1)
        if len(self.trail) > self.trail_length:
            self.trail.pop(0)

        # for i in range(-1, 2):
        #     offset = Vec(
        #         math.sin(self.pendulum.angle) * i, -math.cos(self.pendulum.angle) * i
        #     )
        #     pygame.draw.aaline(
        #         self.window, GRAY, (cart + offset).tolist(), (b0 + offset).tolist()
        #     )
        #
        #     pygame.draw.aaline(
        #         self.window, GRAY, (b0 + offset).tolist(), (b1 + offset).tolist()
        #     )

        pygame.draw.line(self.window, GRAY, cart.tolist(), b0.tolist(), 1)
        pygame.draw.line(self.window, GRAY, b0.tolist(), b1.tolist(), 1)

        pygame.draw.circle(self.window, WHITE, cart.tolist(), 4)
        pygame.draw.circle(self.window, WHITE, b0.tolist(), 4)
        pygame.draw.circle(self.window, WHITE, b1.tolist(), 4)


if __name__ == "__main__":
    window = Window()
    while True:
        window.update()
