import pygame
import math
import grpc
import uuid
from typing import Union
from game.game_pb2_grpc import GameServiceStub
from game.game_pb2 import (
    Empty,
    PlayerState,
    BulletState,
    MapRequest,
    PlayerRequest,
)
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config
from menu import MainMenu, Menu, LobbyCreatorMenu, InputLobbyIPMenu, LobbyJoinerMenu
from bullet import Bullet
from maps import Map, MAP_1_LAYOUT
from blocks import Block
from muzzleFlash import MuzzleFlash


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
        self.tank = Tank()
        self.cannon = TankCannon(self.tank)
        self.tank_sprites = pygame.sprite.Group()
        self.tank_sprites.add(self.tank)
        self.tank_sprites.add(self.cannon)
        self.previous_tank_position = self.tank.rect.center
        self.player_id = None
        self.player_name = "Jugador 0"

        self.explosions_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.tracks_group = pygame.sprite.Group()

        self.map = Map(1, MAP_1_LAYOUT)
        self.blocks = self.map.generate_map()

    def game_loop(self):
        """Bucle principal del juego."""
        pygame.mouse.set_visible(True)
        while self.playing:
            pygame.mouse.set_visible(False)
            self.clock.tick(Config.FPS)
            self.check_events()
            # Actualizar entidades
            self.send_player_state(self.tank)
            self.tank.update(self.blocks)
            self.cannon.update()
            self.bullets_group.update()
            self.explosions_group.update()
            # Dibujar entidades
            for x in range(0, Config.WIDTH, Block.BLOCK_SIZE):
                for y in range(0, Config.HEIGHT, Block.BLOCK_SIZE):
                    self.screen.blit(self.background_image, (x, y))
            self.blocks.draw(self.screen)
            self.tank_sprites.draw(self.screen)
            self.bullets_group.draw(self.screen)
            self.explosions_group.draw(self.screen)
            if self.tank.rect.center != self.previous_tank_position:
                # Dejar rastro
                track = Track(self.previous_tank_position)
                self.tracks_group.add(track)
                self.previous_tank_position = self.tank.rect.center
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

            pygame.display.flip()
            self.window.blit(self.screen, (0, 0))
            pygame.display.update()
            self.reset_keys()

    def check_events(self):
        """Gestión de eventos de entrada del usuario."""
        self.click_pos = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Salir del juego
                self.running, self.playing = False, False
                self.current_menu.run_display = False

            if self.playing:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Disparar
                    mouse_pos = pygame.mouse.get_pos()
                    tank_pos = self.tank.rect.center

                    # Calcular el ángulo del cañón en relación al mouse
                    dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]
                    cannon_angle = math.degrees(
                        math.atan2(-dy, dx)
                    )  # Invertir dy para corregir el eje Y

                    # Calcular la dirección normalizada
                    distance = math.hypot(dx, dy)
                    direction = (dx / distance, dy / distance)  # Vector unitario

                    # Calcular la posición inicial de la bala (parte superior del cañón)
                    cannon_length = self.cannon.rect.height
                    bullet_start_x = tank_pos[0] + cannon_length * direction[0]
                    bullet_start_y = tank_pos[1] + cannon_length * direction[1]
                    bullet_start_pos = (bullet_start_x, bullet_start_y)

                    # Crear una bala con la rotación del cañón
                    bullet = Bullet(bullet_start_pos, direction)
                    bullet.image = pygame.transform.rotate(
                        bullet.image, cannon_angle - 90
                    )  # Rotar la bala
                    self.bullets_group.add(bullet)

                    # Crear un muzzle flash en la posición inicial de la bala
                    muzzle_flash = MuzzleFlash(bullet_start_pos)
                    muzzle_flash.image = pygame.transform.rotate(
                        muzzle_flash.image, cannon_angle + 90
                    )  # Rotar el muzzle flash
                    self.explosions_group.add(
                        muzzle_flash
                    )  # Agregar el muzzle flash al grupo de explosiones

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

    def add_player_to_server(self, player_name):
        """Agregar jugador al servidor"""
        try:
            response = self.client.AddPlayer(PlayerRequest(player_name=player_name))
            print(f"Jugador añadido: Nombre={player_name}, ID={response.player_id}")
            self.player_id = response.player_id
            self.player_name = f"Jugador {self.player_id}"
            return response.player_id
        except grpc.RpcError as e:
            print(f"Error al añadir el jugador al servidor: {e}")
            return None

    def send_map_to_server(self, map_id):
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
        bullet_state = BulletState(
            bullet_id=str(
                uuid.uuid4()
            ),  # Usar el ID único del objeto como identificador
            x=bullet.rect.centerx,
            y=bullet.rect.centery,
            dx=bullet.direction[0],
            dy=bullet.direction[1],
            owner_id=self.player_id,  # ID del jugador que disparó la bala
        )
        try:
            self.client.AddBullet(
                bullet_state
            )  # Llamar al método AddBullet en el servidor
        except grpc.RpcError as e:
            print(f"Error al enviar la bala al servidor: {e}")

    def send_player_state(self, tank: Tank):
        """Enviar el estado del jugador al servidor"""
        player_state = PlayerState(
            player_id=self.player_id,
            x=tank.rect.centerx,
            y=tank.rect.centery,
            angle=tank.angle,  # Suponiendo que el tanque tiene un atributo 'angle'
        )

        # Enviar el estado del jugador al servidor
        try:
            self.client.UpdateState(player_state)
        except grpc.RpcError as e:
            print(f"Error al enviar el estado del jugador: {e}")
