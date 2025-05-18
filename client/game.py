import pygame, math
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config
from blocks import BlockTypes
from maps import Map
from bullet import Bullet

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
pygame.display.set_caption("Tank Game")
clock = pygame.time.Clock()

# Ocultar el cursor del mouse
pygame.mouse.set_visible(False)

# Crear tanque del jugador
player_tank = Tank(tank_id=1, x=100, y=300, color="blue")
player_cannon = TankCannon(player_tank)  # Ajustar el cañón para que el eje esté en la parte trasera
player_tank.set_cannon(player_cannon)

# Crear tanques de otros jugadores
other_tanks = []
for i in range(2, 5):  # Simular 3 jugadores adicionales con IDs 2, 3 y 4
    other_tank = Tank(tank_id=i, x=100 * i, y=200, color="red")
    other_cannon = TankCannon(other_tank)  # Ajustar el cañón de los otros tanques
    other_tank.set_cannon(other_cannon)
    other_tanks.append((other_tank, other_cannon))

# Grupos de sprites
tank_sprites = pygame.sprite.Group()
tank_sprites.add(player_tank)
tank_sprites.add(player_cannon)
for tank, cannon in other_tanks:
    tank_sprites.add(tank)
    tank_sprites.add(cannon)

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
cannon_length = player_cannon.rect.height

# Detectar y conectar el joystick
joystick = None
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick conectado: {joystick.get_name()}")

# Variable para rastrear el estado del botón R2
r2_pressed = False

# Bucle principal del juego
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
# Detectar clic izquierdo para disparar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic izquierdo
            if not player_tank.is_destroyed:  # Solo permitir disparar si el tanque no está destruido
                mouse_pos = pygame.mouse.get_pos()
                tank_pos = player_tank.rect.center  # Centro del tanque

                # Calcular el ángulo del cañón en relación al mouse
                dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]
                cannon_angle = math.degrees(math.atan2(-dy, dx))  # Invertir dy para corregir el eje Y

                # Calcular la dirección normalizada
                distance = math.hypot(dx, dy)
                direction = (dx / distance, dy / distance)  # Vector unitario

                # Calcular la posición inicial de la bala (alrededor de un círculo)
                circle_radius = cannon_length  # Radio del círculo alrededor del tanque
                rad_angle = math.radians(cannon_angle)  # Convertir el ángulo del cañón a radianes
                bullet_start_x = player_tank.rect.centerx + circle_radius * math.cos(rad_angle)
                bullet_start_y = player_tank.rect.centery - circle_radius * math.sin(rad_angle)
                bullet_start_pos = (bullet_start_x, bullet_start_y)

                # Crear una bala con la rotación del cañón
                # Crear una bala con la rotación del cañón
                bullet = Bullet(
                    bullet_start_pos,
                    direction,
                    blocks,
                    explosions_group,
                    tank_id=player_tank.tank_id,
                    damage=15  # Daño personalizado para esta bala
                )
                bullet.image = pygame.transform.rotate(bullet.image, cannon_angle)  # Rotar la bala
                bullets_group.add(bullet)

    # Detectar disparo con el botón R2 del joystick
    if joystick:
        current_r2_state = joystick.get_button(10)  # Cambia el índice si es necesario
        if current_r2_state and not r2_pressed:  # Detectar el cambio de estado (de no presionado a presionado)
            print("Botón R2 presionado")
            if not player_tank.is_destroyed:  # Solo permitir disparar si el tanque no está destruido
                # Calcular la dirección del cañón
                cannon_angle = player_cannon.angle - 90
                rad_angle = math.radians(cannon_angle)
                direction = (math.cos(rad_angle), -math.sin(rad_angle))  # Vector unitario

                # Calcular la posición inicial de la bala
                bullet_start_x = player_tank.rect.centerx + cannon_length * direction[0]
                bullet_start_y = player_tank.rect.centery + cannon_length * direction[1]
                bullet_start_pos = (bullet_start_x, bullet_start_y)

                # Crear una bala con la rotación del cañón
                bullet = Bullet(
                    bullet_start_pos,
                    direction,
                    blocks,
                    explosions_group,
                    tank_id=player_tank.tank_id,
                    damage=15  # Daño personalizado para esta bala
                )
                bullet.image = pygame.transform.rotate(bullet.image, cannon_angle)  # Rotar la bala
                bullets_group.add(bullet)

        # Actualizar el estado del botón R2
        r2_pressed = current_r2_state

    # Controlar el tanque del jugador local
    keystate = pygame.key.get_pressed()
    player_tank.handle_movement(keystate)
    if joystick:
        player_tank.handle_joystick(joystick)
    # Actualizar el tanque del jugador local
    player_tank.update(blocks, bullets_group, [tank for tank, _ in other_tanks])      
    player_cannon.handle_rotation()  # Rotar hacia el mouse
    if joystick:
        player_cannon.handle_rotation_joystick(joystick)  # Controlar el cañón con el joystick
    player_cannon.update()

    # Controlar otros tanques
    for i, (tank, cannon) in enumerate(other_tanks):
        if i == 0:  # Ejemplo: mover el primer tanque con las flechas
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                tank.speed_x = -tank.max_speed
            if keys[pygame.K_RIGHT]:
                tank.speed_x = tank.max_speed
            if keys[pygame.K_UP]:
                tank.speed_y = -tank.max_speed
            if keys[pygame.K_DOWN]:
                tank.speed_y = tank.max_speed
        else:
            # Rotar el cañón automáticamente
            cannon.handle_rotation(target_angle=(pygame.time.get_ticks() % 360))

        tank.update(blocks, bullets_group, [player_tank] + [t for t, _ in other_tanks if t != tank])
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

    # Dibujar la vida de los tanques
    for tank in [player_tank] + [t[0] for t in other_tanks]:
        tank.draw_health(screen)

    # Actualizar la pantalla
    pygame.display.flip()
pygame.quit()
