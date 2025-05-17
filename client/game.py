import pygame, math
import grpc 
import uuid
from game.game_pb2 import Empty, PlayerState, BulletState, MapRequest, PlayerRequest  # Importar PlayerRequest para añadir jugadores
from game.game_pb2_grpc import GameServiceStub
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
tank = Tank(tank_id="1")
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

# Cosas del servidor
# Establecer conexion gRPC
channel = grpc.insecure_channel("localhost:9000")
client = GameServiceStub(channel)

# Función para añadir un jugador al servidor
def add_player_to_server(player_name):
    try:
        response = client.AddPlayer(PlayerRequest(player_name=player_name))
        print(f"Jugador añadido: Nombre={player_name}, ID={response.player_id}")
        return response.player_id
    except grpc.RpcError as e:
        print(f"Error al añadir el jugador al servidor: {e}")
        return None

# Añadir un jugador al inicio del juego
PLAYER_NAME = "player1"  # Cambiar este valor según el nombre del jugador
PLAYER_ID = add_player_to_server(PLAYER_NAME)

# Función para enviar el mapa al servidor
def send_map_to_server(map_id):
    try:
        client.SetMap(MapRequest(map_number=map_id))  # Usar el nombre correcto del campo
        print(f"Mapa {map_id} enviado al servidor correctamente.")
    except grpc.RpcError as e:
        print(f"Error al enviar el mapa al servidor: {e}")

# Enviar el mapa al servidor al inicio del juego
MAP_ID = 1  # Cambiar este valor según el mapa deseado
send_map_to_server(MAP_ID)

# Función para enviar una bala al servidor
def send_bullet(bullet):
    bullet_state = BulletState(
        bullet_id=str(uuid.uuid4()),  # Usar el ID único del objeto como identificador
        x=bullet.rect.centerx,
        y=bullet.rect.centery,
        dx=bullet.direction[0],
        dy=bullet.direction[1],
        owner_id=str(PLAYER_ID),  # ID del jugador que disparó la bala
        damage=bullet.damage,  # Agregar el daño de la bala
    )
    try:
        client.AddBullet(bullet_state)  # Llamar al método AddBullet en el servidor
    except grpc.RpcError as e:
        print(f"Error al enviar la bala al servidor: {e}")

# Función para enviar el estado del jugador al servidor
def send_player_state(tank):
    player_state = PlayerState(
        player_id=str(PLAYER_ID),  # Convertir a string
        x=float(tank.rect.centerx),  # Asegurar que sea float
        y=float(tank.rect.centery),  # Asegurar que sea float
        angle=float(tank.angle),  # Asegurar que sea float
        health=float(tank.health),  # Agregar la vida del jugador
    )

    # Enviar el estado del jugador al servidor
    try:
        client.UpdateState(player_state)
    except grpc.RpcError as e:
        print(f"Error al enviar el estado del jugador: {e}")

# Bucle principal del juego
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Detectar clic izquierdo para disparar
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic izquierdo
            mouse_pos = pygame.mouse.get_pos()
            tank_pos = tank.rect.center  # Suponiendo que el tanque tiene un rectángulo

            # Calcular el ángulo del cañón en relación al mouse
            dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]
            cannon_angle = math.degrees(math.atan2(-dy, dx))  # Invertir dy para corregir el eje Y

            # Calcular la dirección normalizada
            distance = math.hypot(dx, dy)
            direction = (dx / distance, dy / distance)  # Vector unitario            

            # Calcular la posición inicial de la bala (parte superior del cañón)            
            bullet_start_x = tank_pos[0] + cannon_length * direction[0]
            bullet_start_y = tank_pos[1] + cannon_length * direction[1]
            bullet_start_pos = (bullet_start_x, bullet_start_y)

            # Crear una bala con la rotación del cañón
            bullet = Bullet(bullet_start_pos, direction, PLAYER_ID)
            bullet.image = pygame.transform.rotate(bullet.image, cannon_angle - 90)  # Rotar la bala
            bullets_group.add(bullet)

            # Enviar la bala al servidor una sola vez
            send_bullet(bullet)

            # Crear un muzzle flash en la posición inicial de la bala
            muzzle_flash = MuzzleFlash(bullet_start_pos)
            muzzle_flash.image = pygame.transform.rotate(muzzle_flash.image, cannon_angle + 90)  # Rotar el muzzle flash
            explosions_group.add(muzzle_flash)  # Agregar el muzzle flash al grupo de explosiones

    # Detectar si el tanque se ha movido
    if tank.rect.center != previous_tank_position:
        # Crear un rastro en la posición anterior del tanque
        track = Track(previous_tank_position)
        tracks_group.add(track)
        # Actualizar la posición anterior del tanque
        previous_tank_position = tank.rect.center

    # Enviar el estado del jugador al servidor
    send_player_state(tank)

    tank.update(blocks)
    cannon.update()

    # Actualizar las balas
    bullets_group.update()
    explosions_group.update()  # Actualizar el grupo de explosiones

    screen.fill(Colors.WHITE)

    blocks.draw(screen)  # Dibujar bloques
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
    bullets_group.draw(screen)
    explosions_group.draw(screen)  # Dibujar el grupo de explosiones
    pygame.display.flip()
pygame.quit()