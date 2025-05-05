import pygame
import sys
import math
import random
from pygame import mixer

# Инициализация PyGame
pygame.init()
mixer.init()

# Настройки окна
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon-Hacker 2077")

# Цветовая схема
COLORS = {
    "background": (10, 15, 20),
    "neon_blue": (32, 132, 255),
    "neon_purple": (178, 102, 255),
    "text": (200, 220, 255)
}


# Генерация звуков
def generate_sound(freq, duration=0.1):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    wave = []
    for x in range(samples):
        value = int(32767 * math.sin(2 * math.pi * freq * x / sample_rate))
        wave.extend([value & 0xff, (value >> 8) & 0xff])
    return pygame.mixer.Sound(buffer=bytes(wave))


sounds = {
    "click": generate_sound(1200),
    "glitch": generate_sound(800, 0.2)
}


class HolographicButton:
    def __init__(self):
        self.radius = 120
        self.pos = (WIDTH // 2, HEIGHT // 2 + 80)
        self.glow_phase = 0
        self.particles = []
        self.flicker = 0

    def update(self):
        self.glow_phase += 0.05
        self.flicker = max(0, self.flicker - 1)

    def draw(self, surface):
        # Фоновое свечение
        glow_intensity = (math.sin(self.glow_phase) + 1) * 50 + 50
        glow_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        for i in range(3):
            radius = self.radius + 10 + i * 15
            alpha = int(glow_intensity * (1 - i / 3))
            pygame.draw.circle(glow_surf, (*COLORS["neon_blue"], alpha),
                               (150, 150), radius, 10 + i * 5)
        surface.blit(glow_surf, (self.pos[0] - 150, self.pos[1] - 150))

        # Основная кнопка
        pygame.draw.circle(surface, COLORS["neon_blue"],
                           self.pos, self.radius, 15)

        # Текст с эффектом глитча
        text_color = random.choice([COLORS["text"], COLORS["neon_purple"]]) if self.flicker else COLORS["text"]
        text_surf = pygame.font.SysFont('couriernew', 72, bold=True).render(
            "HACK", True, text_color
        )
        text_rect = text_surf.get_rect(center=self.pos)
        surface.blit(text_surf, text_rect)

        # Частицы
        for p in self.particles[:]:
            p.update()
            p.draw(surface)
            if p.lifetime <= 0:
                self.particles.remove(p)

    def trigger_effect(self):
        self.flicker = 5
        for _ in range(25):
            self.particles.append(Particle(self.pos))
        sounds["click"].play()
        sounds["glitch"].play()


class Particle:
    def __init__(self, pos):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(3, 8)
        self.pos = list(pos)
        self.vel = [math.cos(angle) * speed, math.sin(angle) * speed]
        self.lifetime = random.randint(20, 40)
        self.color = random.choice([COLORS["neon_blue"], COLORS["neon_purple"]])

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.vel[1] += 0.15
        self.lifetime -= 1

    def draw(self, surface):
        alpha = int(255 * (self.lifetime / 40))
        size = int(8 * (self.lifetime / 40)) + 2
        surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (size, size), size)
        surface.blit(surf, (int(self.pos[0]) - size, int(self.pos[1]) - size))


class Game:
    def __init__(self):
        self.button = HolographicButton()
        self.score = 0
        self.score_velocity = 0
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('couriernew', 42, bold=True)

    def draw_background(self):
        # Исправление: добавлен max() для alpha
        screen.fill(COLORS["background"])
        for y in range(0, HEIGHT, 4):
            alpha = max(0, 20 + int(30 * math.sin(y / 50 + pygame.time.get_ticks() / 1000)))
            line_surf = pygame.Surface((WIDTH, 2), pygame.SRCALPHA)
            line_surf.fill((*COLORS["neon_blue"], alpha))
            screen.blit(line_surf, (0, y))

    def draw_score(self):
        self.score_velocity += (self.score - self.score_velocity) * 0.1
        text = self.font.render(f"CREDITS: {int(self.score_velocity)}",
                                True, COLORS["text"])
        shadow = self.font.render(f"CREDITS: {int(self.score_velocity)}",
                                  True, COLORS["neon_purple"])

        screen.blit(shadow, (38, 28))
        screen.blit(shadow, (42, 32))
        screen.blit(text, (40, 30))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    distance = math.hypot(x - self.button.pos[0],
                                          y - self.button.pos[1])
                    if distance <= self.button.radius:
                        self.score += 1
                        self.button.trigger_effect()

            self.button.update()

            self.draw_background()
            self.button.draw(screen)
            self.draw_score()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    game = Game()
    game.run()