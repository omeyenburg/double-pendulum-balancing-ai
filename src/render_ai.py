from pendulum import Pendulum
from util import Vec, argv
import pygame.freetype
import pygame.gfxdraw
import pygame
import math
import ai


FPS = 60
WIDTH = 540
HEIGHT = 675
GENERATION = argv("gen", -1)

WHITE = (200, 200, 200)
GRAY = (100, 100, 100)
BLACK = (0, 0, 0)


class Window:
    def __init__(self):
        self.agent: ai.Agent = ai.Agent.load(GENERATION)
        self.ai_enabled = True

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
        self.font = pygame.freetype.SysFont(None, 14)

        self.real_time = ai.seconds_to_str(self.agent.time)
        self.virtual_time = ai.seconds_to_str(self.agent.ticks / 60)

        self.center = Vec(WIDTH // 2, HEIGHT * 2 // 3)
        self.unit_length = abs(WIDTH // 8 - WIDTH // 2)

        self.trail = []
        self.trail_length = 30

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.MOUSEWHEEL:  # Accelerate with mouse wheel
                acceleration = (-event.x or event.y) * 5
                self.pendulum.apply_acceleration(Vec(acceleration, 0))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Reset
                    self.pendulum = Pendulum()
                elif event.key == pygame.K_t:  # Toggle ai
                    self.ai_enabled = not self.ai_enabled

        self.draw()
        self.forward_ai()
        self.pendulum.update()

        pygame.display.flip()
        self.clock.tick(FPS)
        self.window.fill(BLACK)

    def draw(self):
        # Draw pendulum trail
        self.draw_trail()

        # Draw rail
        self.draw_rail()

        # Draw pendulum
        self.draw_pendulum()

        # Draw neurons
        neuron_positions = self.get_neuron_positions()
        for i, layer in enumerate(self.agent.layers):
            for j in range(layer):
                self.draw_neuron(i, j, neuron_positions)

        # Draw info texts
        self.draw_info()

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

        pygame.draw.line(self.window, GRAY, cart.tolist(), b0.tolist(), 1)
        pygame.draw.line(self.window, GRAY, b0.tolist(), b1.tolist(), 1)

        pygame.draw.circle(self.window, WHITE, cart.tolist(), 4)
        pygame.draw.circle(self.window, WHITE, b0.tolist(), 4)
        pygame.draw.circle(self.window, WHITE, b1.tolist(), 4)

    def get_neuron_positions(self):
        w = WIDTH // (len(self.agent.layers) + 1)
        h = max(self.agent.layers)

        positions = [
            [(w + w * x, 20 + 30 * (h / 2 - layer / 2 + y)) for y in range(layer)]
            for x, layer in enumerate(self.agent.layers)
        ]
        # for x, layer in enumerate(self.agent.layers):
        #     positions.append([])
        #     for y in range(layer):
        #         positions[-1].append((w + w * x, 20 + 30 * (h / 2 - layer / 2 + y)))

        return positions

    def draw_neuron(self, i, j, positions):
        node_size = 10
        pos = positions[i][j]

        # Draw weight lines
        if i + 1 < len(self.agent.layers):
            for k, pos2 in enumerate(positions[i + 1]):
                weight = abs(self.agent.weights[i][j][k])
                color = (
                    200 - 50 * weight,
                    200 - 50 * weight,
                    200 - 50 * weight,
                )
                for y in range(round(weight * 3)):
                    pygame.draw.aaline(
                        self.window,
                        color,
                        (pos[0], pos[1] + y * 0.8 - weight),
                        (pos2[0], pos2[1] + y * 0.8 - weight),
                    )

        # Draw neuron background
        pygame.draw.circle(self.window, BLACK, pos, node_size)

        # Draw neuron value
        value = self.agent.values[i][j]
        neuron_size = round(node_size * max(min(abs(value), 1), 0.1))
        value = ai.ActivationFunction.tanh(value * -5)

        if value > 0:
            color = (100, 100 + int(150 * (1 - value)), 100 + int(150 * value))
        else:
            color = (100 + int(150 * -value), 100 + int(150 * (1 + value)), 100)

        pygame.draw.circle(self.window, color, pos, neuron_size)

        # Draw neuron border
        pygame.draw.circle(self.window, WHITE, pos, node_size, 1)

        # Draw neuron labels
        labels = (
            "cart.x",
            "cart.vel",
            "b0.x",
            "b0.y",
            "b0.vel",
            "b1.x",
            "b1.y",
            "b1.vel",
        )
        if i == 0:
            self.font.render_to(
                self.window,
                (10, pos[1] - 5),
                labels[j],
                WHITE,
                size=14,
            )
        elif i + 1 == len(self.agent.layers):
            self.font.render_to(
                self.window,
                (WIDTH - 90, pos[1] - 5),
                "acc",
                WHITE,
                size=14,
            )

    def draw_info(self):
        texts = (
            "Real training time: " + self.real_time,
            "Simulated training time: " + self.virtual_time,
            "Generation: " + str(self.agent.generation),
        )

        for i, text in enumerate(texts):
            self.font.render_to(
                self.window,
                (10, HEIGHT - 110 - 30 * i),
                text,
                WHITE,
                size=14,
            )

    def forward_ai(self):
        if not self.ai_enabled:
            return

        output = self.agent.run(
            self.pendulum.pivot.x,
            self.pendulum.pivot_vel.x,
            *self.pendulum.p0.tolist(),
            self.pendulum.angle_vel0,
            *self.pendulum.p1.tolist(),
            self.pendulum.angle_vel1,
        )

        acceleration = Vec(output[0] * 30, 0)
        self.pendulum.apply_acceleration(acceleration)


if __name__ == "__main__":
    window = Window()
    while True:
        window.update()
