import pygame
import random
import math
import matplotlib.pyplot as plt
import numpy as np
from collections import deque

pygame.init()

WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (0, 0, 0)
BOX_COLOR = (255, 255, 255)
RESET_BUTTON_COLOR = (0, 0, 255)
TEXT_COLOR = (255, 255, 255)
PARTICLE_RADIUS = 11
ARROW_COLOR = (255, 255, 0)
MAGNETIC_FIELD_COLOR = (0, 255, 0)
LORENTZ_FORCE_COLOR = (255, 0, 255)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("\uc790\uae30\uc7a5 \uc785\uc790 \uc2dc\ubbfc\ub808\uc774\uc158")
font = pygame.font.Font(None, 24)

BOX_X, BOX_Y = 50, 50
BOX_WIDTH, BOX_HEIGHT = 700, 450
particles = []
magnetic_force = 3.0
magnetic_direction = 0
reset_button = pygame.Rect(WIDTH // 2 - 50, BOX_Y + BOX_HEIGHT + 20, 100, 30)

lorentz_force_data = deque(maxlen=100)
electric_force_data = deque(maxlen=100)
time_data = deque(maxlen=100)

plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, 100)
ax.set_ylim(-1, 1)
lorentz_line, = ax.plot([], [], label="Lorentz Force")
electric_line, = ax.plot([], [], label="Electric Force")
ax.legend()

def update_graph():
    lorentz_line.set_data(range(len(lorentz_force_data)), lorentz_force_data)
    electric_line.set_data(range(len(electric_force_data)), electric_force_data)
    ax.relim()
    ax.autoscale_view()
    plt.draw()
    plt.pause(0.01)

class Particle:
    charge_sequence = [2, -2]
    charge_index = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.charge = Particle.charge_sequence[Particle.charge_index]
        Particle.charge_index = (Particle.charge_index + 1) % len(Particle.charge_sequence)
        self.color = (255, 0, 0) if self.charge > 0 else (0, 0, 255)
        self.lorentz_fx = 0
        self.lorentz_fy = 0

    def move(self, magnetic_force, magnetic_direction):
        fx = magnetic_force * math.cos(magnetic_direction + math.pi / 2)
        fy = magnetic_force * math.sin(magnetic_direction + math.pi / 2)
        if self.charge < 0:
            fx = -fx
            fy = -fy
        self.lorentz_fx = fx
        self.lorentz_fy = fy
        self.vx = fx * 0.8
        self.vy = fy * 0.8
        self.x += self.vx
        self.y += self.vy
        self.x = max(BOX_X + PARTICLE_RADIUS, min(self.x, BOX_X + BOX_WIDTH - PARTICLE_RADIUS))
        self.y = max(BOX_Y + PARTICLE_RADIUS, min(self.y, BOX_Y + BOX_HEIGHT - PARTICLE_RADIUS))

    def apply_electrostatic_force(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.hypot(dx, dy)
        min_distance = PARTICLE_RADIUS * 2
        if distance < min_distance:
            distance = min_distance
        attraction_threshold = 50
        if self.charge * other.charge < 0 and distance < attraction_threshold:
            midpoint_x = (self.x + other.x) / 2
            midpoint_y = (self.y + other.y) / 2
            self.x += (midpoint_x - self.x) * 0.03
            self.y += (midpoint_y - self.y) * 0.03
            other.x += (midpoint_x - other.x) * 0.03
            other.y += (midpoint_y - other.y) * 0.03

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), PARTICLE_RADIUS)
        charge_sign = "+" if self.charge > 0 else "-"
        text = font.render(charge_sign, True, TEXT_COLOR)
        screen.blit(text, (self.x - 5, self.y - 10))
        self.draw_lorentz_arrow()

    def draw_lorentz_arrow(self):
        arrow_length = 30
        end_x = self.x + self.lorentz_fx * arrow_length
        end_y = self.y + self.lorentz_fy * arrow_length
        pygame.draw.line(screen, LORENTZ_FORCE_COLOR, (self.x, self.y), (end_x, end_y), 2)
        pygame.draw.circle(screen, LORENTZ_FORCE_COLOR, (int(end_x), int(end_y)), 3)

def create_particle(x, y):
    particles.append(Particle(x, y))

def draw_magnetic_field():
    center_x = BOX_X + BOX_WIDTH // 2
    center_y = BOX_Y + BOX_HEIGHT // 2
    arrow_length = 50
    end_x = center_x + math.cos(magnetic_direction) * arrow_length
    end_y = center_y + math.sin(magnetic_direction) * arrow_length
    pygame.draw.line(screen, MAGNETIC_FIELD_COLOR, (center_x, center_y), (end_x, end_y), 4)

def handle_collisions():
    for i, p1 in enumerate(particles):
        for j, p2 in enumerate(particles):
            if i < j:
                p1.apply_electrostatic_force(p2)
                p2.apply_electrostatic_force(p1)
                dx = p2.x - p1.x
                dy = p2.y - p1.y
                distance = math.hypot(dx, dy)
                if distance < 2 * PARTICLE_RADIUS:
                    overlap = 2 * PARTICLE_RADIUS - distance
                    angle = math.atan2(dy, dx)
                    p1.x -= math.cos(angle) * overlap / 2
                    p1.y -= math.sin(angle) * overlap / 2
                    p2.x += math.cos(angle) * overlap / 2
                    p2.y += math.sin(angle) * overlap / 2

def draw_lorentz_info():
    if particles:
        last_particle = particles[-1]
        fx, fy = last_particle.lorentz_fx, last_particle.lorentz_fy
        lorentz_force_data.append(math.hypot(fx, fy))
        electric_force_data.append(last_particle.charge * 0.1)
        update_graph()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if reset_button.collidepoint(event.pos):
                particles.clear()
            else:
                create_particle(*event.pos)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                magnetic_force = max(0, magnetic_force - 0.1)
            if event.key == pygame.K_e:
                magnetic_force += 0.1
            if event.key == pygame.K_LEFT:
                magnetic_direction -= math.pi / 16
            if event.key == pygame.K_RIGHT:
                magnetic_direction += math.pi / 16

    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, BOX_COLOR, (BOX_X, BOX_Y, BOX_WIDTH, BOX_HEIGHT), 2)
    pygame.draw.rect(screen, RESET_BUTTON_COLOR, reset_button)
    reset_text = font.render("Reset", True, TEXT_COLOR)
    screen.blit(reset_text, (reset_button.x + 28, reset_button.y + 9))
    draw_magnetic_field()

    for particle in particles:
        particle.move(magnetic_force, magnetic_direction)
        particle.draw()

    handle_collisions()
    draw_lorentz_info()

    force_text = font.render(f"Magnetic Force: {magnetic_force:.2f}", True, TEXT_COLOR)
    screen.blit(force_text, (50, BOX_Y + BOX_HEIGHT + 60))

    pygame.display.flip()
    pygame.time.delay(30)

pygame.quit()
plt.ioff()
plt.show()
