import pygame, math
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config
from blocks import BlockTypes
from maps import Map
from bullet import Bullet
from muzzleFlash import MuzzleFlash

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

# Crear el grupo de explosiones
explosions_group = pygame.sprite.Group()

# Crear mapa
MAP_LAYOUT = [
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND, BlockTypes.GREEN_TREE] + [BlockTypes.SAND_BACKGROUND] * 9 + [BlockTypes.GRASS_BACKGROUND],
    [BlockTypes.SAND_BACKGROUND] * 2 + [BlockTypes.BROWN_TREE] + [BlockTypes.GRASS_BACKGROUND] * 9,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
    [BlockTypes.GRASS_BACKGROUND] * 12,
]
map = Map("test_map", MAP_LAYOUT)
blocks = map.generate_map()

# Grupo para las balas
bullets_group = pygame.sprite.Group()

# Longitud fija del cañón (ajusta este valor según el diseño de tu tanque)
cannon_length = cannon.rect.height

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detectar clic izquierdo para disparar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic izquierdo
            mouse_pos = pygame.mouse.get_pos()
            tank_pos = tank.rect.center  # Centro del tanque

            # Calcular el ángulo del cañón en relación al mouse
            dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]
            cannon_angle = math.degrees(math.atan2(-dy, dx))  # Invertir dy para corregir el eje Y

            # Calcular la dirección normalizada
            distance = math.hypot(dx, dy)
            direction = (dx / distance, dy / distance)  # Vector unitario

            # Calcular la posición inicial de la bala (alrededor de un círculo)
            circle_radius = cannon_length  # Radio del círculo alrededor del tanque
            rad_angle = math.radians(cannon_angle)  # Convertir el ángulo del cañón a radianes
            bullet_start_x = tank.rect.centerx + circle_radius * math.cos(rad_angle)
            bullet_start_y = tank.rect.centery - circle_radius * math.sin(rad_angle)
            bullet_start_pos = (bullet_start_x, bullet_start_y)

            # Crear una bala con la rotación del cañón
            bullet = Bullet(bullet_start_pos, direction, blocks, explosions_group)  # Pasar el grupo de explosiones
            bullet.image = pygame.transform.rotate(bullet.image, cannon_angle)  # Rotar la bala
            bullets_group.add(bullet)

    # Detectar si el tanque se ha movido
    if tank.rect.center != previous_tank_position:
        # Crear un rastro en la posición anterior del tanque
        track = Track(previous_tank_position)
        tracks_group.add(track)
        # Actualizar la posición anterior del tanque
        previous_tank_position = tank.rect.center

    tank.update(blocks)
    cannon.update()

    # Actualizar las balas
    bullets_group.update()

    # Actualizar los efectos de disparo (MuzzleFlash)
    explosions_group.update()

    # Limpiar la pantalla
    screen.fill(Colors.WHITE)

    # Dibujar bloques, tanque y cañón
    blocks.draw(screen)
    tank_sprites.draw(screen)

    # Dibujar las balas
    bullets_group.draw(screen)

    # Dibujar los efectos de disparo (MuzzleFlash)
    explosions_group.draw(screen)

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

    # Actualizar la pantalla
    pygame.display.flip()
pygame.quit()
