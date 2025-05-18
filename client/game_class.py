import pygame
import math
import grpc
import uuid
import threading
from typing import Union
from game.game_pb2_grpc import GameServiceStub
from game.game_pb2 import (
    Empty,
    PlayerState,
    BulletState,
    MapRequest,
    PlayerRequest,
)
from tank import Tank, TankCannon
from colors import Colors
from config import Config
from menu import MainMenu, Menu, LobbyCreatorMenu, InputLobbyIPMenu, LobbyJoinerMenu
from bullet import Bullet
from maps import Map, MAP_1_LAYOUT
from blocks import Block
# from muzzleFlash import MuzzleFlash


class Game:
    """Clase que gestiona la ventana de juego."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Tank Battle GRPC")
        pygame.display.set_icon(pygame.image.load("assets/menu/game-logo.png"))
        self.running, self.playing = True, False
        self.UP, self.DOWN, self.LEFT, self.RIGHT, self.START = (
            False,
            False,
            False,
            False,
            False,
        )
        self.screen = pygame.Surface((Config.WIDTH, Config.HEIGHT))
        self.clock = pygame.time.Clock()
        self.window = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        self.font_name = pygame.font.get_default_font()
        self.background_image = pygame.image.load("assets/Retina/tileGrass1.png")
        self.background_image = pygame.transform.scale(
            self.background_image, (Block.BLOCK_SIZE, Block.BLOCK_SIZE)
        )
        # Menu variables
        self.main_menu = MainMenu(self)
        self.start_lobby_menu = LobbyCreatorMenu(self)
        self.input_lobby_ip_menu = InputLobbyIPMenu(self)
        self.lobby_joiner_menu = LobbyJoinerMenu(self)
        self.current_menu: Menu = self.main_menu
        # Game variables
        self.click_pos = None
        self.key_pressed = None
        self.server_ip: Union[str, None] = None
        self.player_id = None
        self.player_name = "Jugador 0"

        self.explosions_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()

        self.map = Map(1, MAP_1_LAYOUT)
        self.blocks = self.map.generate_map()

        self.game_state = None  # Holds the latest GameState from the server
        self._start_game_state_stream()

        self.tanks = {}  # Store all tanks by player_id

    def init_tank(self, tank_id: str):
        """Inicializa el tanque del jugador."""
        x, y = Tank.get_initial_position(tank_id)
        self.tank = Tank(tank_id=tank_id, x=x, y=y)
        self.cannon = TankCannon(self.tank)
        self.tank_sprites = pygame.sprite.Group()
        self.cannon_sprites = pygame.sprite.Group()
        # self.tank_sprites.add(self.tank)
        # self.cannon_sprites.add(self.cannon)
        self.send_player_state(self.tank, self.cannon)

    def _start_game_state_stream(self):
        def stream():
            if not hasattr(self, "client"):
                return
            try:
                for state in self.client.StreamGameState(Empty()):
                    self.game_state = state
            except Exception as e:
                print(f"Error en StreamGameState: {e}")

        threading.Thread(target=stream, daemon=True).start()

    def game_loop(self):
        """Bucle principal del juego."""
        pygame.mouse.set_visible(True)
        while self.playing:
            pygame.mouse.set_visible(False)
            self.clock.tick(Config.FPS)
            self.check_events()
            # Posición del mouse
            mouse_x, mouse_y = pygame.mouse.get_pos()
            tank_x, tank_y = self.tank.rect.center
            dx = mouse_x - tank_x
            dy = mouse_y - tank_y
            mouse_angle = math.degrees(math.atan2(-dy, dx)) + 90
            self.cannon.angle = mouse_angle
            # Update from game state
            self.update_tanks_from_game_state()
            self.update_bullets_from_game_state()
            # Actualizar entidades
            self.send_player_state(self.tank, self.cannon)
            self.tank.update(self.blocks)
            self.cannon.update(mouse_angle)
            self.bullets_group.update()
            self.explosions_group.update()
            # Clear the screen before drawing
            self.screen.fill((0, 0, 0))  # Fill with black, or change color as needed
            # Dibujar entidades
            for x in range(0, Config.WIDTH, Block.BLOCK_SIZE):
                for y in range(0, Config.HEIGHT, Block.BLOCK_SIZE):
                    self.screen.blit(self.background_image, (x, y))
            self.blocks.draw(self.screen)
            # Draw all tanks
            self.tank_sprites.draw(self.screen)
            self.cannon_sprites.draw(self.screen)
            for tank in self.tank_sprites:
                if isinstance(tank, Tank):
                    tank.draw_health(self.screen)
            self.bullets_group.draw(self.screen)
            self.explosions_group.draw(self.screen)
            # Dibujar mira
            mouse_pos = pygame.mouse.get_pos()
            pygame.draw.circle(self.screen, Colors.RED, mouse_pos, 5)
            pygame.draw.line(
                self.screen,
                Colors.RED,
                (mouse_pos[0] - 15, mouse_pos[1]),
                (mouse_pos[0] + 15, mouse_pos[1]),
                2,
            )  # Línea horizontal
            pygame.draw.line(
                self.screen,
                Colors.RED,
                (mouse_pos[0], mouse_pos[1] - 15),
                (mouse_pos[0], mouse_pos[1] + 15),
                2,
            )  # Línea vertical

            # Blit the game surface to the window and update display only once
            self.window.blit(self.screen, (0, 0))
            pygame.display.flip()
            self.reset_keys()

    def update_bullets_from_game_state(self):
        """Update all bullets from the latest game state."""
        if self.game_state and hasattr(self.game_state, "bullets"):
            # Crear un diccionario para rastrear las balas existentes por su bullet_id
            existing_bullets = {
                bullet.bullet_id: bullet for bullet in self.bullets_group
            }

            # Crear un conjunto de IDs de balas activas desde el estado del servidor
            active_bullet_ids = {
                bullet_state.bullet_id for bullet_state in self.game_state.bullets
            }

            # Eliminar balas que ya no están activas en el servidor
            self.bullets_group = pygame.sprite.Group(
                [
                    bullet
                    for bullet in self.bullets_group
                    if bullet.bullet_id in active_bullet_ids
                ]
            )

            # Mantener un conjunto de IDs de balas ya procesadas
            processed_bullet_ids = set()

            # Procesar el evento de disparo recibido del servidor
            for bullet_state in self.game_state.bullets:
                if (
                    bullet_state.bullet_id not in existing_bullets
                    and bullet_state.bullet_id not in processed_bullet_ids
                ):
                    bullet = Bullet(
                        (bullet_state.x, bullet_state.y),
                        (bullet_state.dx, bullet_state.dy),
                        bullet_state.owner_id,
                    )
                    bullet.bullet_id = bullet_state.bullet_id
                    angle = math.degrees(math.atan2(-bullet_state.dy, bullet_state.dx))
                    bullet.image = pygame.transform.rotate(bullet.image, angle - 90)
                    self.bullets_group.add(bullet)
                    processed_bullet_ids.add(bullet_state.bullet_id)

    def update_tanks_from_game_state(self):
        """Update all tanks from the latest game state."""
        if self.game_state and hasattr(self.game_state, "players"):
            self.tank_sprites = pygame.sprite.Group()
            self.cannon_sprites = pygame.sprite.Group()
            for player in self.game_state.players:
                if player.player_id == self.player_id:
                    # Always update your own tank, even if health is 0
                    self.tank.health = player.health
                    continue

                if player.health <= 0:
                    continue

                tank = Tank(player.player_id, player.health, x=player.x, y=player.y)
                cannon = TankCannon(tank)
                cannon.angle = player.cannon_angle
                cannon.image = pygame.transform.rotate(
                    cannon.original_image, cannon.angle
                )
                cannon.rect = cannon.image.get_rect()
                rad_angle = math.radians(cannon.angle - 90)
                cannon.rect.centerx = int(
                    cannon.tank.rect.centerx + cannon.offset * math.cos(rad_angle)
                )
                cannon.rect.centery = int(
                    cannon.tank.rect.centery - cannon.offset * math.sin(rad_angle)
                )
                self.cannon_sprites.add(cannon)

                tank.angle = player.angle
                original_center = tank.rect.center
                tank.image = pygame.transform.rotate(tank.original_image, player.angle)
                tank.rect = tank.image.get_rect(center=original_center)
                self.tank_sprites.add(tank)

            # Only add your own tank if health > 0
            if hasattr(self, "tank") and self.tank.health > 0:
                self.tank_sprites.add(self.tank)
                self.cannon_sprites.add(self.cannon)

        # Ensure your own tank is always present in tank_sprites
        if self.player_id:
            found = any(
                isinstance(sprite, Tank)
                and getattr(sprite, "tank_id", None) == self.player_id
                for sprite in self.tank_sprites
            )
            if not found and hasattr(self, "tank") and self.tank.health > 0:
                self.tank_sprites.add(self.tank)

    def check_events(self):
        """Gestión de eventos de entrada del usuario."""
        self.click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Salir del juego
                self.running, self.playing = False, False
                self.current_menu.run_display = False

            if self.playing:
                if (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                    # and not self.tank.is_destroyed
                    and self.tank.health > 0
                ):
                    # Disparar
                    mouse_pos = pygame.mouse.get_pos()
                    tank_pos = self.tank.rect.center

                    # Calcular el ángulo del cañón en relación al mouse
                    dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]

                    # Calcular la dirección normalizada
                    distance = math.hypot(dx, dy)
                    direction = (dx / distance, dy / distance)  # Vector unitario

                    # Calcular la posición inicial de la bala (parte superior del cañón)
                    cannon_length = self.cannon.rect.height
                    bullet_start_x = tank_pos[0] + cannon_length * direction[0]
                    bullet_start_y = tank_pos[1] + cannon_length * direction[1]
                    bullet_start_pos = (bullet_start_x, bullet_start_y)

                    # Crear una bala con la rotación del cañón
                    bullet = Bullet(
                        bullet_start_pos,
                        direction,
                        self.player_id,
                    )
                    # Calcular el ángulo de rotación basado en la dirección de la bala
                    angle = math.degrees(math.atan2(-direction[1], direction[0]))
                    bullet.image = pygame.transform.rotate(bullet.image, angle - 90)
                    self.bullets_group.add(bullet)

                    # Enviar la bala al servidor una sola vez
                    self.send_bullet(bullet)

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click_pos = pygame.mouse.get_pos()
                elif event.type == pygame.KEYDOWN:
                    self.key_pressed = event.key

    def reset_keys(self):
        """Reinicia las teclas de movimiento."""
        self.UP, self.DOWN, self.LEFT, self.RIGHT, self.START = (
            False,
            False,
            False,
            False,
            False,
        )

    def draw_text(self, text: str, size: int, x: int, y: int, color=Colors.WHITE):
        """Dibuja texto en la pantalla."""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def add_player_to_server(self, player_name: str):
        """Agregar jugador al servidor"""
        try:
            response = self.client.AddPlayer(PlayerRequest(player_name=player_name))
            print(f"Jugador añadido: Nombre={player_name}, ID={response.player_id}")
            self.player_id = str(response.player_id)
            self.player_name = f"Jugador {self.player_id}"
            self.init_tank(self.player_id)  # Inicializar el tanque del jugador
            return str(response.player_id)
        except grpc.RpcError as e:
            print(f"Error al añadir el jugador al servidor: {e}")
            return None

    def send_map_to_server(self, map_id: int):
        try:
            self.client.SetMap(
                MapRequest(map_number=map_id)
            )  # Usar el nombre correcto del campo
            print(f"Mapa {map_id} enviado al servidor correctamente.")
        except grpc.RpcError as e:
            print(f"Error al enviar el mapa al servidor: {e}")

    def join_server(self):
        """Establecer conexión con el servidor"""
        self.channel = grpc.insecure_channel(f"{self.server_ip}:9000")
        self.client = GameServiceStub(self.channel)

    def send_bullet(self, bullet: Bullet):
        """Enviar la bala al servidor"""
        bullet_id = str(uuid.uuid4())
        bullet.bullet_id = bullet_id  # Asignar un ID único a la bala
        bullet_state = BulletState(
            bullet_id=bullet_id,
            x=bullet.rect.centerx,
            y=bullet.rect.centery,
            dx=bullet.direction[0],
            dy=bullet.direction[1],
            owner_id=self.player_id,  # ID del jugador que disparó la bala
            damage=bullet.damage,
        )
        try:
            self.client.AddBullet(
                bullet_state
            )  # Llamar al método AddBullet en el servidor
        except grpc.RpcError as e:
            print(f"Error al enviar la bala al servidor: {e}")

    def send_player_state(self, tank: Tank, cannon: TankCannon):
        """Enviar el estado del jugador al servidor"""
        player_state = PlayerState(
            player_id=self.player_id,
            x=tank.rect.centerx,
            y=tank.rect.centery,
            angle=tank.angle,  # Suponiendo que el tanque tiene un atributo 'angle'
            health=float(tank.health),
            cannon_angle=cannon.angle,
        )

        # Enviar el estado del jugador al servidor
        try:
            self.client.UpdateState(player_state)
        except grpc.RpcError as e:
            print(f"Error al enviar el estado del jugador: {e}")

    def get_game_state(self):
        """Obtener el estado del juego desde el servidor"""
        try:
            return self.client.GetGameState(Empty())
        except grpc.RpcError as e:
            print(f"Error al obtener el estado del juego: {e}")
            return None

    def get_player_list(self):
        """Obtener la lista de jugadores desde el servidor"""
        try:
            return self.client.GetPlayerList(Empty())
        except grpc.RpcError as e:
            print(f"Error al obtener la lista de jugadores: {e}")
            return None
