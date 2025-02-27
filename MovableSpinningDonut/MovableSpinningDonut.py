import os
from math import cos, sin
import pygame
import colorsys

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
hue = 0

os.environ['SDL_VIDEO_CENTERED'] = '1'
RES = WIDTH, HEIGHT = 800, 800
FPS = 60

pixel_width = 20
pixel_height = 20

x_pixel = 0
y_pixel = 0

x_offset = 0  # Horizontal movement variable
y_offset = 0  # Vertical movement variable
move_speed = 5  # Movement speed

screen_width = WIDTH // pixel_width
screen_height = HEIGHT // pixel_height
screen_size = screen_width * screen_height

A, B = 0, 0

theta_spacing = 10
phi_spacing = 3

chars = ".,-~:;=!*#$@"

R1 = 10
R2 = 20
K2 = 200
K1 = screen_height * K2 * 3 / (8 * (R1 + R2))

pygame.init()

screen = pygame.display.set_mode(RES)
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 20, bold=True)

def hsv2rgb(h, s, v):
    return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h, s, v))

def text_display(char, x, y):
    text = font.render(str(char), True, hsv2rgb(hue, 1, 1))
    text_rect = text.get_rect(center=(x, y))
    screen.blit(text, text_rect)

k = 0
paused = False
running = True
keys = {pygame.K_w: False, pygame.K_s: False, pygame.K_a: False, pygame.K_d: False}
while running:
    clock.tick(FPS)
    pygame.display.set_caption("FPS: {:.2f}".format(clock.get_fps()))
    screen.fill(BLACK)

    output = [' '] * screen_size
    zbuffer = [0] * screen_size

    for theta in range(0, 628, theta_spacing):  # Theta goes around the cross-sectional circle of a torus
        for phi in range(0, 628, phi_spacing):  # Phi goes around the center of revolution of a torus

            cosA = cos(A)
            sinA = sin(A)
            cosB = cos(B)
            sinB = sin(B)

            costheta = cos(theta)
            sintheta = sin(theta)
            cosphi = cos(phi)
            sinphi = sin(phi)

            # x, y coordinates before revolving
            circlex = R2 + R1 * costheta
            circley = R1 * sintheta

            # 3D (x, y, z) coordinates after rotation
            x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
            y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
            z = K2 + cosA * circlex * sinphi + circley * sinA
            ooz = 1 / z  # one over z

            # x, y projection with wrapping
            xp = (int(screen_width / 2 + K1 * ooz * x) + x_offset) % screen_width
            yp = (int(screen_height / 2 - K1 * ooz * y) + y_offset) % screen_height

            position = xp + screen_width * yp
            # Luminance (L ranges from -sqrt(2) to sqrt(2))
            L = cosphi * costheta * sinB - cosA * costheta * sinphi - sinA * sintheta + cosB * (
                        cosA * sintheta - costheta * sinA * sinphi)

            if ooz > zbuffer[position]:
                zbuffer[position] = ooz  # Larger ooz means the pixel is closer to the viewer than what's already plotted
                luminance_index = int(L * 8)  # Multiply by 8 to get luminance_index range (8 * sqrt(2) = 11)
                output[position] = chars[luminance_index if luminance_index > 0 else 0]

    for i in range(screen_height):
        y_pixel += pixel_height
        for j in range(screen_width):
            x_pixel += pixel_width
            text_display(output[k], x_pixel, y_pixel)
            k += 1
        x_pixel = 0
    y_pixel = 0
    k = 0

    A += 0.15
    B += 0.035

    hue += 0.005

    if not paused:
        pygame.display.update()

    # Smooth movement
    if keys[pygame.K_w]:
        y_offset -= move_speed
    if keys[pygame.K_s]:
        y_offset += move_speed
    if keys[pygame.K_a]:
        x_offset -= move_speed
    if keys[pygame.K_d]:
        x_offset += move_speed

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE:
                paused = not paused
            if event.key in keys:
                keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in keys:
                keys[event.key] = False