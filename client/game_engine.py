import pygame, math
import grpc
from game.game_pb2 import Empty
from game.game_pb2_grpc import GameServiceStub
from game.game_pb2 import PlayerState
from game.game_pb2_grpc import GameServiceStub
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config
from blocks import BlockTypes, Block
from maps import Map, MAP_1_LAYOUT
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
map = Map(1, MAP_1_LAYOUT)
blocks = map.generate_map()

background_image = pygame.image.load("assets/Retina/tileGrass1.png")
background_image = pygame.transform.scale(
    background_image, (Block.BLOCK_SIZE, Block.BLOCK_SIZE)
)

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


# Función para obtener el mapa actual del servidor
def get_map_from_server():
    try:
        response = client.GetMap(Empty())
        print(f"Mapa recibido del servidor: {response.map_number}")
        return response.map_number
    except grpc.RpcError as e:
        print(f"Error al obtener el mapa del servidor: {e}")
        return None


# Obtener el mapa del servidor al inicio del juego
map_number = get_map_from_server()
if map_number is not None:
    print(f"Usando el mapa {map_number} para el juego.")
else:
    print("No se pudo obtener el mapa del servidor. Usando el mapa predeterminado.")


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
    clock.tick(Config.FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Obtener el estado del juego desde el servidor
    game_state = get_game_state()
    if not game_state:
        continue

    # Dibujar el fondo
    screen.fill(Colors.WHITE)
    for x in range(0, Config.WIDTH, Block.BLOCK_SIZE):
        for y in range(0, Config.HEIGHT, Block.BLOCK_SIZE):
            screen.blit(background_image, (x, y))
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
    bullets_group = pygame.sprite.Group(
        [bullet for bullet in bullets_group if bullet.bullet_id in active_bullet_ids]
    )

    # Mantener un conjunto de IDs de balas ya procesadas
    if "processed_bullet_ids" not in globals():
        processed_bullet_ids = set()

    # Procesar el evento de disparo recibido del servidor
    for bullet_state in game_state.bullets:
        print(len(game_state.bullets))
        if (
            bullet_state.bullet_id not in existing_bullets
            and bullet_state.bullet_id not in processed_bullet_ids
        ):
            # Crear una nueva bala si no existe y no ha sido procesada
            bullet = Bullet(
                (bullet_state.x, bullet_state.y), (bullet_state.dx, bullet_state.dy)
            )
            bullet.bullet_id = bullet_state.bullet_id  # Asignar el bullet_id
            bullets_group.add(bullet)
            processed_bullet_ids.add(bullet_state.bullet_id)
            print("Se ha disparado una bala " + bullet_state.bullet_id)

    # Eliminar balas que ya no están activas en el servidor
    for bullet in bullets_group:
        if (
            bullet.rect.right < 0
            or bullet.rect.left > pygame.display.get_surface().get_width()
            or bullet.rect.bottom < 0
            or bullet.rect.top > pygame.display.get_surface().get_height()
        ):
            try:
                from game.game_pb2 import BulletRemoveRequest
                client.RemoveBullet(BulletRemoveRequest(bullet_id=bullet.bullet_id))
                print(f"Bala eliminada del servidor: {bullet.bullet_id}")
            except grpc.RpcError as e:
                print(f"Error al eliminar la bala del servidor: {e}")
            bullet.kill()

    # Actualizar las balas existentes usando su método update
    bullets_group.update()

    # Dibujar las balas
    bullets_group.draw(screen)

    pygame.display.flip()

pygame.quit()
