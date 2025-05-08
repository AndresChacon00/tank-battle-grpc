import pygame
import math
from colors import Colors
from config import Config
from menu import MainMenu
from tank import Tank, TankCannon
from bullet import Bullet
from maps import Map, MAP_1_LAYOUT
from blocks import Block
from muzzleFlash import MuzzleFlash


class Game:
    """Clase que gestiona la ventana de juego."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("Tank Game")
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
        self.current_menu = self.main_menu
        # Game variables
        self.click_pos = None
        self.tank = Tank()
        self.cannon = TankCannon(self.tank)
        self.tank_sprites = pygame.sprite.Group()
        self.tank_sprites.add(self.tank)
        self.tank_sprites.add(self.cannon)
        self.explosions_group = pygame.sprite.Group()
        self.bullets_group = pygame.sprite.Group()
        self.map = Map("test_map", MAP_1_LAYOUT)
        self.blocks = self.map.generate_map()

    def game_loop(self):
        """Bucle principal del juego."""
        pygame.mouse.set_visible(True)
        while self.playing:
            pygame.mouse.set_visible(False)
            self.clock.tick(Config.FPS)
            self.check_events()
            # Actualizar entidades
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

            else:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.click_pos = pygame.mouse.get_pos()

    def draw_text(self, text: str, size: int, x: int, y: int, color=Colors.WHITE):
        """Dibuja texto en la pantalla."""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def reset_keys(self):
        """Reinicia las teclas de movimiento."""
        self.UP, self.DOWN, self.LEFT, self.RIGHT, self.START = (
            False,
            False,
            False,
            False,
            False,
        )
