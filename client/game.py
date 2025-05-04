import pygame
import math
from tank import Tank, TankCannon, Track
from colors import Colors
from config import Config
from blocks import BlockTypes
from maps import Map
from bullet import Bullet
from muzzleFlash import MuzzleFlash
from menu import MainMenu

# pygame.init()
# pygame.mixer.init()
# screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
# pygame.display.set_caption("Tank Game")
# clock = pygame.time.Clock()

# # Ocultar el cursor del mouse
# pygame.mouse.set_visible(False)

# # Crear tanque y cañón
# tank = Tank()
# cannon = TankCannon(tank)

# tank_sprites = pygame.sprite.Group()
# tank_sprites.add(tank)
# tank_sprites.add(cannon)

# previous_tank_position = tank.rect.center

# # Crear un grupo para los rastros del tanque
# tracks_group = pygame.sprite.Group()

# # Crear el grupo de explosiones
# explosions_group = pygame.sprite.Group()

# # Crear mapa
# MAP_LAYOUT = [
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND, BlockTypes.GREEN_TREE]
#     + [BlockTypes.SAND_BACKGROUND] * 9
#     + [BlockTypes.GRASS_BACKGROUND],
#     [BlockTypes.SAND_BACKGROUND] * 2
#     + [BlockTypes.BROWN_TREE]
#     + [BlockTypes.GRASS_BACKGROUND] * 9,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
#     [BlockTypes.GRASS_BACKGROUND] * 12,
# ]
# map = Map("test_map", MAP_LAYOUT)
# blocks = map.generate_map()

# # Grupo para las balas
# bullets_group = pygame.sprite.Group()

# # Longitud fija del cañón (ajusta este valor según el diseño de tu tanque)
# cannon_length = cannon.rect.height

# running = True
# while running:
#     clock.tick(60)
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False
#         # Detectar clic izquierdo para disparar
#         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic izquierdo
#             mouse_pos = pygame.mouse.get_pos()
#             tank_pos = tank.rect.center  # Suponiendo que el tanque tiene un rectángulo

#             # Calcular el ángulo del cañón en relación al mouse
#             dx, dy = mouse_pos[0] - tank_pos[0], mouse_pos[1] - tank_pos[1]
#             cannon_angle = math.degrees(
#                 math.atan2(-dy, dx)
#             )  # Invertir dy para corregir el eje Y

#             # Calcular la dirección normalizada
#             distance = math.hypot(dx, dy)
#             direction = (dx / distance, dy / distance)  # Vector unitario

#             # Calcular la posición inicial de la bala (parte superior del cañón)
#             bullet_start_x = tank_pos[0] + cannon_length * direction[0]
#             bullet_start_y = tank_pos[1] + cannon_length * direction[1]
#             bullet_start_pos = (bullet_start_x, bullet_start_y)

#             # Crear una bala con la rotación del cañón
#             bullet = Bullet(bullet_start_pos, direction)
#             bullet.image = pygame.transform.rotate(
#                 bullet.image, cannon_angle - 90
#             )  # Rotar la bala
#             bullets_group.add(bullet)

#             # Crear un muzzle flash en la posición inicial de la bala
#             muzzle_flash = MuzzleFlash(bullet_start_pos)
#             muzzle_flash.image = pygame.transform.rotate(
#                 muzzle_flash.image, cannon_angle + 90
#             )  # Rotar el muzzle flash
#             explosions_group.add(
#                 muzzle_flash
#             )  # Agregar el muzzle flash al grupo de explosiones

#     # Detectar si el tanque se ha movido
#     if tank.rect.center != previous_tank_position:
#         # Crear un rastro en la posición anterior del tanque
#         track = Track(previous_tank_position)
#         tracks_group.add(track)
#         # Actualizar la posición anterior del tanque
#         previous_tank_position = tank.rect.center

#     tank.update(blocks)
#     cannon.update()

#     # Actualizar las balas
#     bullets_group.update()
#     explosions_group.update()  # Actualizar el grupo de explosiones

#     screen.fill(Colors.WHITE)

#     blocks.draw(screen)  # Dibujar bloques
#     tank_sprites.draw(screen)

#     # Dibujar la mira personalizada
#     mouse_pos = pygame.mouse.get_pos()
#     pygame.draw.circle(screen, Colors.RED, mouse_pos, 10, 2)  # Círculo exterior
#     pygame.draw.line(
#         screen,
#         Colors.RED,
#         (mouse_pos[0] - 15, mouse_pos[1]),
#         (mouse_pos[0] + 15, mouse_pos[1]),
#         2,
#     )  # Línea horizontal
#     pygame.draw.line(
#         screen,
#         Colors.RED,
#         (mouse_pos[0], mouse_pos[1] - 15),
#         (mouse_pos[0], mouse_pos[1] + 15),
#         2,
#     )  # Línea vertical
#     bullets_group.draw(screen)
#     explosions_group.draw(screen)  # Dibujar el grupo de explosiones
#     pygame.display.flip()
# pygame.quit()


class Game:
    """Clase que gestiona la ventana de juego."""

    def __init__(self):
        pygame.init()
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
        self.current_menu = MainMenu(self)

    def game_loop(self):
        """Bucle principal del juego."""
        while self.playing:
            self.check_events()
            self.screen.fill(Colors.WHITE)
            self.draw_text("Hola mundo", 64, Config.WIDTH // 2, Config.HEIGHT // 2)
            self.window.blit(self.screen, (0, 0))
            pygame.display.update()
            self.reset_keys()

    def check_events(self):
        """Gestión de eventos de entrada del usuario."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running, self.playing = False, False
                self.current_menu.run_display = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.UP = True
                elif event.key == pygame.K_DOWN:
                    self.DOWN = True
                elif event.key == pygame.K_LEFT:
                    self.LEFT = True
                elif event.key == pygame.K_RIGHT:
                    self.RIGHT = True
                elif event.key == pygame.K_RETURN:
                    self.START = True

    def draw_text(self, text: str, size: int, x: int, y: int):
        """Dibuja texto en la pantalla."""
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, Colors.WHITE)
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
