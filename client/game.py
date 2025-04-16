import pygame
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Tank Game")
clock = pygame.time.Clock()

# Ocultar el cursor del mouse
pygame.mouse.set_visible(False)

# Crear tanque y cañón
tank = Tank()
cannon = TankCannon(tank)

tank_sprites = pygame.sprite.Group()
tank_sprites.add(tank)
tank_sprites.add(cannon)

previous_tank_position = tank.rect.center

# Crear un grupo para los rastros del tanque
tracks_group = pygame.sprite.Group()

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Detectar si el tanque se ha movido
    if tank.rect.center != previous_tank_position:
        # Crear un rastro en la posición anterior del tanque
        track = Track(previous_tank_position)
        tracks_group.add(track)
        # Actualizar la posición anterior del tanque
        previous_tank_position = tank.rect.center

    tank_sprites.update()

    screen.fill(Colors.WHITE)

    tank_sprites.draw(screen)

    # Dibujar la mira personalizada
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.circle(screen, Colors.RED, mouse_pos, 10, 2)  # Círculo exterior
    pygame.draw.line(
        screen,
        Colors.RED,
        (mouse_pos[0] - 15, mouse_pos[1]),
        (mouse_pos[0] + 15, mouse_pos[1]),
        2,
    )  # Línea horizontal
    pygame.draw.line(
        screen,
        Colors.RED,
        (mouse_pos[0], mouse_pos[1] - 15),
        (mouse_pos[0], mouse_pos[1] + 15),
        2,
    )  # Línea vertical

    pygame.display.flip()
pygame.quit()
