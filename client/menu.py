from typing import TYPE_CHECKING
import pygame
from config import Config
from colors import Colors

if TYPE_CHECKING:
    from game import Game


class Menu:
    """Clase base que representa un menú"""

    def __init__(self, game: "Game"):
        pygame.mouse.set_visible(True)
        self.game = game
        self.mid_w, self.mid_h = Config.WIDTH // 2, Config.HEIGHT // 2
        self.run_display = True
        self.cursor_rect = pygame.Rect(0, 0, 20, 20)
        self.offset = -100

    def draw_cursor(self):
        """Dibuja el cursor en la pantalla"""
        self.game.draw_text("*", 30, self.cursor_rect.x, self.cursor_rect.y)

    def blit_screen(self):
        """Actualiza la pantalla"""
        self.game.window.blit(self.game.screen, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    """Clase que representa el menú principal del juego"""

    MENU_START = "Empezar"
    MENU_QUIT = "Salir"

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.state = self.MENU_START
        self.start_x, self.start_y = self.mid_w, self.mid_h + 40
        self.play_button = pygame.Rect(self.mid_w - 50, self.mid_h + 50, 100, 50)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + 90
        self.quit_button = pygame.Rect(self.mid_w - 50, self.mid_h + 80, 100, 50)
        self.cursor_rect.midtop = (self.start_x + self.offset, self.start_y + 5)

    def display_menu(self):
        """Muestra el menú principal"""
        self.run_display = True
        while self.run_display:
            self.game.check_events()
            self.check_input()
            self.game.screen.fill(Colors.BLACK)
            self.game.draw_text("TANKS", 25, self.mid_w, self.mid_h - 25)
            self.game.draw_text("Empezar", 20, self.start_x, self.start_y)
            self.game.draw_text("Salir", 20, self.quit_x, self.quit_y)
            self.draw_cursor()
            self.blit_screen()

    def move_cursor(self):
        """Mueve el cursor en el menú"""
        if self.game.UP:
            if self.state == self.MENU_START:
                self.cursor_rect.midtop = (self.mid_w + self.offset, self.quit_y)
                self.state = self.MENU_QUIT
            elif self.state == self.MENU_QUIT:
                self.cursor_rect.midtop = (self.mid_w + self.offset, self.start_y)
                self.state = self.MENU_START
        elif self.game.DOWN:
            if self.state == self.MENU_START:
                self.cursor_rect.midtop = (self.mid_w + self.offset, self.start_y)
                self.state = self.MENU_QUIT
            elif self.state == self.MENU_QUIT:
                self.cursor_rect.midtop = (self.mid_w + self.offset, self.quit_y)
                self.state = self.MENU_START

    def check_input(self):
        """Actúa según la entrada del usuario"""
        self.move_cursor()
        if self.game.START:
            if self.state == self.MENU_START:
                self.game.playing = True
            elif self.state == self.MENU_QUIT:
                self.game.running = False
                self.game.playing = False

            self.run_display = False
