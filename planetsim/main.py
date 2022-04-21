import math
from dataclasses import dataclass, field
from typing import ClassVar, List

import pygame

pygame.init()

WIDTH, HEIGHT = 2200, 2100
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Symulator Planet")

FPS = 60
SFPS = 60

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (200, 200, 20)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
GREEN = (0, 255, 0)
DARK_GREY = (80, 78, 81)

FONT_DISTANCE = pygame.font.SysFont("firacodeiscript", 32)
FONT_NAME = pygame.font.SysFont("firacodeiscript", 42)


@dataclass
class Planet:
    AU: ClassVar[float] = 149_597_870_700
    G: ClassVar[float] = 6.67408 * 10**-11
    SCALE: ClassVar[float] = 625 / AU  #  1AU = 100px
    TIMESTEP: ClassVar[int] = int(3600 * 24 * 7 / SFPS)  #  1h = 3600sec

    name: str
    x: float
    y: float
    radius: float
    color: tuple
    mass: float
    x_vel: float = 0
    y_vel: float = 0
    orbit: List[tuple[float, float]] = field(default_factory=list)
    sun: bool = False
    distance_to_sun: float = 0

    def draw(self):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                updated_points.append((x, y))

            pygame.draw.lines(WIN, self.color, False, updated_points, 2)

        if not self.sun:
            distance_text = FONT_DISTANCE.render(
                f"{round(self.distance_to_sun/1000000000,2)} mln km", True, GREEN
            )
            name_text = FONT_NAME.render(self.name, True, self.color)
            WIN.blits(
                [
                    (
                        distance_text,
                        (
                            x - distance_text.get_width() / 2,
                            y - distance_text.get_height() * 2,
                        ),
                    ),
                    (
                        name_text,
                        (x - name_text.get_width() / 2, y + name_text.get_height()),
                    ),
                ]
            )

        pygame.draw.circle(WIN, self.color, (x, y), self.radius)

    def attraction(self, other: "Planet"):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets: List["Planet"]):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))


def main():
    run = True
    global SFPS
    clock = pygame.time.Clock()

    sun = Planet("Słońce", 0, 0, 160, YELLOW, 1.98892 * 10**30, sun=True)
    mars = Planet(
        "Mars", -1.524 * Planet.AU, 0, 8, RED, 6.39 * 10**23, 0, 24.077 * 1000
    )
    earth = Planet(
        "Ziemia", -1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24, 0, 29.783 * 1000
    )
    venus = Planet(
        "Wenus", -0.723 * Planet.AU, 0, 15, WHITE, 4.87 * 10**24, 0, 35.02 * 1000
    )
    mercury = Planet(
        "Merkury", -0.387 * Planet.AU, 0, 6, DARK_GREY, 3.3 * 10**23, 0, 47.4 * 1000
    )

    planets: List[Planet] = [sun, earth, mars, mercury, venus]

    while run:
        clock.tick(FPS)
        WIN.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        clock.tick()
        SFPS = int(clock.get_fps())
        for planet in planets:
            planet.update_position(planets)
            planet.draw()

        pygame.display.update()
    pygame.quit()


if __name__ == "__main__":
    main()
