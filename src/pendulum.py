from util import Vec
from math import *


class Pendulum:
    def __init__(self):
        self.theta0 = 0
        self.theta1 = 0
        self.omega0 = 0
        self.omega1 = 0
        self.l0 = 0.5
        self.l1 = 0.5
        self.p0 = Vec(self.l0 * sin(self.theta0), -self.l0 * cos(self.theta0))
        self.p1 = Vec(self.l1 * sin(self.theta1), -self.l1 * cos(self.theta1)) + self.p0
        self.m0 = 0.1
        self.m1 = 0.1
        self.angle_vel0 = 0
        self.angle_acc0 = 0
        self.angle_vel1 = 0
        self.angle_acc1 = 0

        self.pivot = Vec(0, 0)
        self.pivot_vel = Vec(0, 0)

        self.EDGE = 1
        self.ANGULAR_DAMPING = 0.1
        self.HORIZONTAL_DAMPING = 0.3
        self.GRAVITY = 9.81
        self.DELTA_TIME = (
            1 / 60
        )  # Uncontrolled delta_time leads to uninterntional behaviour

    def apply_acceleration(self, acceleration: Vec):
        if (
            acceleration.x < 0
            and self.pivot.x <= -self.EDGE
            or acceleration.x > 0
            and self.pivot.x >= self.EDGE
        ):
            acceleration.x = 0

        # Rotational movement
        # force: Vec = acceleration * self.mass
        # moment_of_inertia = self.mass * self.radius**2
        # angular_acceleration = (
        #     force.cross(Vec.from_angle(self.angle) * self.radius) / moment_of_inertia
        # )
        #
        # angular_acceleration -= self.angular_damping * self.angular_velocity
        # self.angular_velocity += angular_acceleration * DELTA_TIME

        # Horizontal movement
        acceleration.x -= self.HORIZONTAL_DAMPING * self.pivot_vel.x
        self.pivot_vel.x += acceleration.x * self.DELTA_TIME

    def update(self):
        horizontal_acc = self.pivot_vel.x**2

        # Horizontal movement
        self.pivot.x += self.pivot_vel.x * self.DELTA_TIME
        if self.pivot.x < -self.EDGE:
            horizontal_acc -= self.pivot.x + self.EDGE
            self.pivot.x = -self.EDGE
            self.pivot_vel.x = 0
        elif self.pivot.x > self.EDGE:
            horizontal_acc += self.pivot.x - self.EDGE
            self.pivot.x = self.EDGE
            self.pivot_vel.x = 0

        # Horizontal friction
        self.pivot_vel.x -= self.pivot_vel.x * self.HORIZONTAL_DAMPING * self.DELTA_TIME

        # Acceleration of inner pendulum
        # self.angle_acc0 = -self.m1 / (self.m0 + self.m1) * (self.l1 / self.l0) * (
        #     self.angle_acc1 * cos(self.theta0 - self.theta1)
        #     + self.angle_vel1**2 * sin(self.theta0 - self.theta1)
        # ) - (self.GRAVITY / self.l0) * sin(self.theta0)
        num1 = -self.GRAVITY * (2 * self.m0 + self.m1) * sin(self.theta0)
        num2 = -self.m1 * self.GRAVITY * sin(self.theta0 - 2 * self.theta1)
        num3 = -2 * sin(self.theta0 - self.theta1) * self.m1
        num4 = self.angle_vel1**2 * self.l1 + self.angle_vel0**2 * self.l0 * cos(
            self.theta0 - self.theta1
        )
        num5 = -self.m0 * horizontal_acc * cos(self.theta0)
        denom = self.l0 * (
            2 * self.m0 + self.m1 - self.m1 * cos(2 * self.theta0 - 2 * self.theta1)
        )
        self.angle_acc0 = (num1 + num2 + num3 * num4 + num5) / denom

        # Acceleration of outer pendulum
        # self.angle_acc1 = -(self.l0 / self.l1) * (
        #     self.angle_acc0 * cos(self.theta0 - self.theta1)
        #     - self.angle_vel0**2 * sin(self.theta0 - self.theta1)
        # ) - (self.GRAVITY / self.l1) * sin(self.theta1)
        num1 = 2 * sin(self.theta0 - self.theta1)
        num2 = self.angle_vel0**2 * self.l0 * (self.m0 + self.m1)
        num3 = self.GRAVITY * (self.m0 + self.m1) * cos(self.theta0)
        num4 = self.angle_vel1**2 * self.l1 * self.m1 * cos(self.theta0 - self.theta1)
        num5 = self.m1 * horizontal_acc * cos(self.theta1)
        denom = self.l1 * (
            2 * self.m0 + self.m1 - self.m1 * cos(2 * self.theta0 - 2 * self.theta1)
        )
        self.angle_acc1 = num1 * (num2 + num3 + num4 + num5) / denom

        self.angle_vel0 += self.angle_acc0 * self.DELTA_TIME
        self.angle_vel1 += self.angle_acc1 * self.DELTA_TIME

        self.theta0 += self.angle_vel0 * self.DELTA_TIME
        self.theta1 += self.angle_vel1 * self.DELTA_TIME

        self.p0 = Vec(self.l0 * sin(self.theta0), -self.l0 * cos(self.theta0))
        self.p1 = Vec(self.l1 * sin(self.theta1), -self.l1 * cos(self.theta1)) + self.p0

    def derivatives(self, state, t):
        theta0, omega0, theta1, omega1, x, v = state

        # Equations of motion
        dtheta0 = omega0
        dtheta1 = omega1
        dx = v

        # Acceleration calculations
        horizontal_acc = 2 * v**2

        num1 = -self.GRAVITY * (2 * self.m0 + self.m1) * sin(theta0)
        num2 = -self.m1 * self.GRAVITY * sin(theta0 - 2 * theta1)
        num3 = -2 * sin(theta0 - theta1) * self.m1
        num4 = omega1**2 * self.l1 + omega0**2 * self.l0 * cos(theta0 - theta1)
        num5 = -self.m0 * horizontal_acc * cos(theta0)
        denom = self.l0 * (
            2 * self.m0 + self.m1 - self.m1 * cos(2 * theta0 - 2 * theta1)
        )
        domega0 = (num1 + num2 + num3 * num4 + num5) / denom

        num1 = 2 * sin(theta0 - theta1)
        num2 = omega0**2 * self.l0 * (self.m0 + self.m1)
        num3 = self.GRAVITY * (self.m0 + self.m1) * cos(theta0)
        num4 = omega1**2 * self.l1 * self.m1 * cos(theta0 - theta1)
        num5 = self.m1 * horizontal_acc * cos(theta1)
        denom = self.l1 * (
            2 * self.m0 + self.m1 - self.m1 * cos(2 * theta0 - 2 * theta1)
        )
        domega1 = num1 * (num2 + num3 + num4 + num5) / denom

        # Horizontal friction
        dv = -v * self.HORIZONTAL_DAMPING

        return [dtheta0, domega0, dtheta1, domega1, dx, dv]

    def rk4_step(self, state, t, dt):
        k1 = self.derivatives(state, t)
        k2 = self.derivatives(
            [s + 0.5 * dt * k for s, k in zip(state, k1)], t + 0.5 * dt
        )
        k3 = self.derivatives(
            [s + 0.5 * dt * k for s, k in zip(state, k2)], t + 0.5 * dt
        )
        k4 = self.derivatives([s + dt * k for s, k in zip(state, k3)], t + dt)

        return [
            s + (dt / 6) * (a + 2 * b + 2 * c + d)
            for s, a, b, c, d in zip(state, k1, k2, k3, k4)
        ]

    def update(self):
        state = [
            self.theta0,
            self.omega0,
            self.theta1,
            self.omega1,
            self.pivot.x,
            self.pivot_vel.x,
        ]
        new_state = self.rk4_step(state, 0, self.DELTA_TIME)
        (
            self.theta0,
            self.omega0,
            self.theta1,
            self.omega1,
            self.pivot.x,
            self.pivot_vel.x,
        ) = new_state

        # Apply boundary conditions for horizontal movement
        if self.pivot.x < -self.EDGE:
            self.pivot.x = -self.EDGE
            self.pivot_vel.x = 0
        elif self.pivot.x > self.EDGE:
            self.pivot.x = self.EDGE
            self.pivot_vel.x = 0

        # Calculate positions for visualization
        self.p0 = Vec(self.l0 * sin(self.theta0), -self.l0 * cos(self.theta0))
        self.p1 = Vec(
            self.l1 * sin(self.theta1) + self.p0[0],
            -self.l1 * cos(self.theta1) + self.p0[1],
        )
