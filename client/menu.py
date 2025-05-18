from typing import TYPE_CHECKING
import pygame
import socket
from config import Config
from colors import Colors
from components import InputBox
from game.game_pb2 import Empty


if TYPE_CHECKING:
    from game_class import Game


class Menu:
    """Clase base que representa un menú"""

    def __init__(self, game: "Game"):
        pygame.mouse.set_visible(True)
        self.game = game
        self.mid_w, self.mid_h = Config.WIDTH // 2, Config.HEIGHT // 2
        self.run_display = True

    def blit_screen(self):
        """Actualiza la pantalla"""
        self.game.window.blit(self.game.screen, (0, 0))
        pygame.display.update()
        self.game.reset_keys()

    def display_menu(self):
        """Método que debe ser implementado en las subclases"""
        pass


class MainMenu(Menu):
    """Clase que representa el menú principal del juego"""

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.start_x, self.start_y = self.mid_w, self.mid_h + 40
        self.start_lobby_button = pygame.Rect(
            self.mid_w - 75, self.mid_h + 150, 150, 50
        )
        self.join_lobby_button = pygame.Rect(self.mid_w - 75, self.mid_h + 210, 150, 50)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + 270
        self.quit_button = pygame.Rect(self.mid_w - 75, self.mid_h + 270, 150, 50)
        self.logo = pygame.image.load("assets/menu/game-logo.png")
        self.logo_rect = self.logo.get_rect(center=(self.mid_w, self.mid_h - 90))

    def display_menu(self):
        """Muestra el menú principal"""
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.screen.fill(Colors.PALE_YELLOW)
            self.game.screen.blit(self.logo, self.logo_rect)
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.start_lobby_button, 2)
            self.game.draw_text(
                "Crear sala",
                20,
                self.start_lobby_button.centerx,
                self.start_lobby_button.centery,
                color=Colors.BLACK,
            )
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.join_lobby_button, 2)
            self.game.draw_text(
                "Unirse a sala",
                20,
                self.join_lobby_button.centerx,
                self.join_lobby_button.centery,
                color=Colors.BLACK,
            )
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.quit_button, 2)
            self.game.draw_text(
                "Salir",
                20,
                self.quit_button.centerx,
                self.quit_button.centery,
                color=Colors.BLACK,
            )
            self.blit_screen()

    def check_input(self):
        """Actúa según la entrada del usuario"""
        if self.game.click_pos is not None:
            if self.start_lobby_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.game.add_player_to_server("Host")
                self.game.current_menu = self.game.start_lobby_menu
                self.run_display = False
            elif self.join_lobby_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.game.current_menu = self.game.input_lobby_ip_menu
                self.run_display = False
            elif self.quit_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.run_display = False
                self.game.running = False


class LobbyCreatorMenu(Menu):
    """Clase que representa el menú de la sala de espera (creador)"""

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.start_x, self.start_y = self.mid_w, self.mid_h + 40
        self.play_button = pygame.Rect(self.mid_w - 100, self.mid_h + 150, 200, 50)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + 120
        self.quit_button = pygame.Rect(self.mid_w - 100, self.mid_h + 210, 200, 50)
        # Obtener la IP local
        self.local_ip = self.get_local_ip()
        # Lista de jugadores (por ejemplo, con player_id "1", "2", etc.)
        self.players = ["Player 1", "Player 2"]
        # Logo reducido en la esquina superior izquierda
        self.logo = pygame.image.load("assets/menu/game-logo.png")
        self.logo_small = pygame.transform.scale(self.logo, (80, 80))
        self.logo_rect = self.logo_small.get_rect(topleft=(20, 20))
        # Cargar imágenes de tanques
        self.blue_tank_img = pygame.image.load("assets/Retina/tank_blue.png").convert_alpha()
        self.red_tank_img = pygame.image.load("assets/Retina/tank_red.png").convert_alpha()
        self.green_tank_img = pygame.image.load("assets/Retina/tank_green.png").convert_alpha()
        self.sand_tank_img = pygame.image.load("assets/Retina/tank_sand.png").convert_alpha()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            self.game.server_ip = "localhost"
            self.game.join_server()
            return ip
        except Exception:
            return "127.0.0.1"

    def display_menu(self):
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.screen.fill(Colors.PALE_YELLOW)
            player_list = self.game.get_player_list()
            # Logo en la esquina
            self.game.screen.blit(self.logo_small, self.logo_rect)
            # Mostrar la IP local
            self.game.draw_text(
                f"Sala de espera - IP: {self.local_ip}",
                28,
                self.mid_w,
                self.mid_h - 120,
                color=Colors.BLACK,
            )
            # Mostrar lista de jugadores con imagen y mayor separación
            if player_list is not None:
                # Usamos un offset vertical mayor, por ejemplo 60 px por jugador
                for player in player_list.players:
                    player_y = self.mid_h - 80 + (int(player.player_id) - 1) * 60
                    # Dibuja el nombre centrado
                    self.game.draw_text(
                        f"Jugador {player.player_id}",
                        24,
                        self.mid_w,
                        player_y,
                        color=Colors.BLACK,
                    )
                    # Seleccionar imagen según el ID del jugador
                    if player.player_id == "1":
                        tank_img = self.blue_tank_img
                    elif player.player_id == "2":
                        tank_img = self.red_tank_img
                    elif player.player_id == "3":
                        tank_img = self.green_tank_img
                    elif player.player_id == "4":
                        tank_img = self.sand_tank_img
                    else:
                        tank_img = None

                    if tank_img:
                        # Escalar la imagen a un tamaño adecuado (por ejemplo, 40x40)
                        tank_img_small = pygame.transform.scale(tank_img, (40, 40))
                        # Ubicar la imagen a la izquierda del nombre; ajusta la coordenada X (por ejemplo, mid_w - 220)
                        self.game.screen.blit(tank_img_small, (self.mid_w - 125, player_y - 20))
            # Dibujar botones
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.play_button, 2)
            self.game.draw_text(
                "Iniciar partida",
                20,
                self.play_button.centerx,
                self.play_button.centery,
                color=Colors.BLACK,
            )
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.quit_button, 2)
            self.game.draw_text(
                "Volver",
                20,
                self.quit_button.centerx,
                self.quit_button.centery,
                color=Colors.BLACK,
            )
            self.blit_screen()

            if hasattr(self.game, "game_state") and self.game.game_state is not None:
                if getattr(self.game.game_state, "game_started", False):
                    self.game.playing = True
                    self.run_display = False

    def check_input(self):
        """Actúa según la entrada del usuario"""
        if self.game.click_pos is not None:
            if self.play_button.collidepoint(self.game.click_pos):
                self.game.send_map_to_server(self.game.map.id)
                # --- NEW: Call StartGame RPC on the server ---
                if hasattr(self.game, "client"):
                    try:
                        self.game.client.StartGame(Empty())
                    except Exception as e:
                        print(f"Error al iniciar el juego en el servidor: {e}")
                self.game.playing = True
                self.run_display = False

            elif self.quit_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.run_display = False
                self.game.current_menu = self.game.main_menu


class InputLobbyIPMenu(Menu):
    """Clase que representa el menú de entrada de IP del lobby"""

    def __init__(self, game: "Game"):
        super().__init__(game)
        font = pygame.font.Font(pygame.font.get_default_font(), 24)
        self.input_box_component = InputBox(
            self.mid_w - 100, self.mid_h, 200, 50, font, self
        )
        self.logo = pygame.image.load("assets/menu/game-logo.png")
        self.logo_small = pygame.transform.scale(self.logo, (80, 80))
        self.logo_rect = self.logo_small.get_rect(topleft=(20, 20))
        self.join_button = pygame.Rect(self.mid_w - 110, self.mid_h + 100, 100, 45)
        self.back_button = pygame.Rect(self.mid_w + 10, self.mid_h + 100, 100, 45)

    def display_menu(self):
        """Muestra el menú para ingresar la IP del lobby"""
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.screen.fill(Colors.PALE_YELLOW)
            # Logo reducido en la esquina
            self.game.screen.blit(self.logo_small, self.logo_rect)
            # Texto de instrucción
            self.game.draw_text(
                "Ingresa la IP de la sala a la que deseas unirte:",
                24,
                self.mid_w,
                self.mid_h - 40,
                color=Colors.BLACK,
            )
            self.input_box_component.draw(self.game.screen)
            # Botones en la parte inferior
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.join_button, 2)
            self.game.draw_text(
                "Unirse",
                20,
                self.join_button.centerx,
                self.join_button.centery,
                color=Colors.BLACK,
            )
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.back_button, 2)
            self.game.draw_text(
                "Volver",
                20,
                self.back_button.centerx,
                self.back_button.centery,
                color=Colors.BLACK,
            )
            self.blit_screen()

    def check_input(self):
        """Maneja la entrada de texto para la IP y los botones"""
        # InputBox component event handling
        result = self.input_box_component.handle_event()
        if result == "submit":
            self.run_display = False
            self.game.current_menu = self.game.lobby_joiner_menu

        if self.game.click_pos is not None:
            # Botón Unirse
            if self.join_button.collidepoint(self.game.click_pos):
                self.game.server_ip = self.input_box_component.text
                self.game.add_player_to_server("Otro")
                self.run_display = False
                self.game.current_menu = self.game.lobby_joiner_menu
            # Botón Volver
            if self.back_button.collidepoint(self.game.click_pos):
                self.run_display = False
                self.game.current_menu = self.game.main_menu


class LobbyJoinerMenu(Menu):
    """Clase que representa el menú de unión a un lobby"""

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + 120
        self.quit_button = pygame.Rect(self.mid_w - 100, self.mid_h + 210, 200, 50)
        # Lista de jugadores
        self.players = ["Player 1", "Player 2"]
        # Logo reducido en la esquina superior izquierda
        self.logo = pygame.image.load("assets/menu/game-logo.png")
        self.logo_small = pygame.transform.scale(self.logo, (80, 80))
        self.logo_rect = self.logo_small.get_rect(topleft=(20, 20))
        # Cargar imágenes de tanques (agregar esta parte)
        self.blue_tank_img = pygame.image.load("assets/Retina/tank_blue.png").convert_alpha()
        self.red_tank_img = pygame.image.load("assets/Retina/tank_red.png").convert_alpha()
        self.green_tank_img = pygame.image.load("assets/Retina/tank_green.png").convert_alpha()
        self.sand_tank_img = pygame.image.load("assets/Retina/tank_sand.png").convert_alpha()

    def display_menu(self):
        """Muestra el menú principal"""
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            player_list = self.game.get_player_list()
            self.check_input()
            self.game.screen.fill(Colors.PALE_YELLOW)
            # Logo en la esquina
            self.game.screen.blit(self.logo_small, self.logo_rect)
            # Mostrar la IP de la sala
            self.game.draw_text(
                f"Sala de espera - IP de la sala: {self.game.server_ip}",
                28,
                self.mid_w,
                self.mid_h - 120,
                color=Colors.BLACK,
            )
            # Mostrar lista de jugadores con imagen y mayor separación
            if player_list is not None:
                for player in player_list.players:
                    player_y = self.mid_h - 80 + (int(player.player_id) - 1) * 60
                    self.game.draw_text(
                        f"Jugador {player.player_id}",
                        24,
                        self.mid_w,
                        player_y,
                        color=Colors.BLACK,
                    )
                    if player.player_id == "1":
                        tank_img = self.blue_tank_img
                    elif player.player_id == "2":
                        tank_img = self.red_tank_img
                    elif player.player_id == "3":
                        tank_img = self.green_tank_img
                    elif player.player_id == "4":
                        tank_img = self.sand_tank_img
                    else:
                        tank_img = None

                    if tank_img:
                        tank_img_small = pygame.transform.scale(tank_img, (40, 40))
                        self.game.screen.blit(tank_img_small, (self.mid_w - 125, player_y - 20))
            # Botón Volver
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.quit_button, 2)
            self.game.draw_text(
                "Volver",
                20,
                self.quit_button.centerx,
                self.quit_button.centery,
                color=Colors.BLACK,
            )
            self.blit_screen()
            
            # Si el juego ya inició, salir del menú
            if hasattr(self.game, "game_state") and self.game.game_state is not None:
                if getattr(self.game.game_state, "game_started", False):
                    self.game.playing = True
                    self.run_display = False

    def check_input(self):
        """Actúa según la entrada del usuario"""
        if self.game.click_pos is not None:
            if self.quit_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.run_display = False
                self.game.current_menu = self.game.main_menu
