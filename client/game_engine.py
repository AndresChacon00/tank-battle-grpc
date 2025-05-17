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

# Obtener el estado del juego desde el servidor y reconstruir la pantalla
running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Obtener el estado del juego desde el servidor
    game_state = get_game_state()
    if not game_state:
        continue

    # Dibujar el fondo
    screen.fill(Colors.WHITE)
    blocks.draw(screen)

    # Crear tanque y cañón basado en el estado del juego
    tank_sprites = pygame.sprite.Group()
    for player in game_state.players:
        tank = Tank()
        tank.rect.center = (player.x, player.y)
        tank.angle = player.angle  # Suponiendo que el tanque tiene un atributo 'angle'
        # Rotar la imagen del tanque y mantener el centro
        original_center = tank.rect.center
        tank.image = pygame.transform.rotate(tank.original_image, player.angle)
        tank.rect = tank.image.get_rect(center=original_center)
        tank_sprites.add(tank)

    # Dibujar los tanques
    tank_sprites.draw(screen)

    # Crear un diccionario para rastrear las balas existentes por su bullet_id
    existing_bullets = {bullet.bullet_id: bullet for bullet in bullets_group}

    # Crear un conjunto de IDs de balas activas desde el estado del servidor
    active_bullet_ids = {bullet_state.bullet_id for bullet_state in game_state.bullets}

    # Eliminar balas que ya no están activas en el servidor
    bullets_group = pygame.sprite.Group([bullet for bullet in bullets_group if bullet.bullet_id in active_bullet_ids])

    # Mantener un conjunto de IDs de balas ya procesadas
    if 'processed_bullet_ids' not in globals():
        processed_bullet_ids = set()

    # Procesar el evento de disparo recibido del servidor
    for bullet_state in game_state.bullets:
        print(len(game_state.bullets))
        if bullet_state.bullet_id not in existing_bullets and bullet_state.bullet_id not in processed_bullet_ids:
            # Crear una nueva bala si no existe y no ha sido procesada
            bullet = Bullet((bullet_state.x, bullet_state.y), (bullet_state.dx, bullet_state.dy))
            bullet.bullet_id = bullet_state.bullet_id  # Asignar el bullet_id
            bullets_group.add(bullet)
            processed_bullet_ids.add(bullet_state.bullet_id)
            print("Se ha disparado una bala " + bullet_state.bullet_id)

    # Actualizar las balas existentes usando su método update
    bullets_group.update()

    # Dibujar las balas
    bullets_group.draw(screen)

    pygame.display.flip()

pygame.quit()
