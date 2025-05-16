import pygame, math
import grpc 
from game.game_pb2 import Empty
from game.game_pb2_grpc import GameServiceStub
from game.game_pb2 import PlayerState
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

# Cosas del servidor
# Establecer conexion gRPC
channel = grpc.insecure_channel("localhost:9000")
client = GameServiceStub(channel)

# Identificador único para el jugador
PLAYER_ID = "player2"

# Función para enviar el estado del jugador al servidor
def send_player_state(tank):
    player_state = PlayerState(
        player_id=PLAYER_ID,
        x=tank.rect.centerx,
        y=tank.rect.centery,
        angle=tank.angle,  # Suponiendo que el tanque tiene un atributo 'angle'
    )
    try:
        client.UpdateState(player_state)
    except grpc.RpcError as e:
        print(f"Error al enviar el estado del jugador: {e}")

# Obtener el estado del juego desde el servidor
def get_game_state():
    try:
        return client.GetGameState(Empty())
    except grpc.RpcError as e:
        print(f"Error al obtener el estado del juego: {e}")
        return None

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
            bullet = Bullet(bullet_start_pos, direction)
            bullet.image = pygame.transform.rotate(bullet.image, cannon_angle - 90)  # Rotar la bala
            bullets_group.add(bullet)

            # Crear un muzzle flash en la posición inicial de la bala
            muzzle_flash = MuzzleFlash(bullet_start_pos)
            muzzle_flash.image = pygame.transform.rotate(muzzle_flash.image, cannon_angle + 90)  # Rotar el muzzle flash
            explosions_group.add(muzzle_flash)  # Agregar el muzzle flash al grupo de explosiones

    # Obtener el estado del juego desde el servidor
    game_state = get_game_state()
    if not game_state:
        continue

    # Dibujar el estado del juego
    screen.fill(Colors.WHITE)
    for player in game_state.players:
        # Dibujar el tanque
        tank_rect = pygame.Rect(player.x, player.y, 50, 50)  # Suponiendo un tamaño de 50x50 para el tanque
        pygame.draw.rect(screen, Colors.GREEN, tank_rect)

        # Dibujar la dirección del tanque
        angle = player.angle
        pygame.draw.line(
            screen,
            Colors.RED,
            (player.x + 25, player.y + 25),  # Centro del tanque
            (
                player.x + 25 + 50 * math.cos(math.radians(angle)),
                player.y + 25 - 50 * math.sin(math.radians(angle)),
            ),
            2,
        )

    # Dibujar las balas
    for bullet in game_state.bullets:
        # Dibujar cada bala como un pequeño círculo
        pygame.draw.circle(
            screen,
            Colors.RED,  # Color de la bala
            (int(bullet.x), int(bullet.y)),  # Posición de la bala
            5,  # Radio de la bala
        )

    pygame.display.flip()

pygame.quit()
