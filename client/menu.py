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

    def blit_screen(self):
        """Actualiza la pantalla"""
        self.game.window.blit(self.game.screen, (0, 0))
        pygame.display.update()
        self.game.reset_keys()


class MainMenu(Menu):
    """Clase que representa el menú principal del juego"""

    def __init__(self, game: "Game"):
        super().__init__(game)
        self.start_x, self.start_y = self.mid_w, self.mid_h + 40
        self.play_button = pygame.Rect(self.mid_w - 50, self.mid_h + 150, 100, 50)
        self.quit_x, self.quit_y = self.mid_w, self.mid_h + 120
        self.quit_button = pygame.Rect(self.mid_w - 50, self.mid_h + 210, 100, 50)
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
            pygame.draw.rect(self.game.screen, Colors.BLACK, self.play_button, 2)
            self.game.draw_text(
                "Empezar",
                20,
                self.play_button.centerx,
                self.play_button.centery,
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
            if self.play_button.collidepoint(self.game.click_pos):
                self.game.playing = True
                self.run_display = False

            elif self.quit_button.collidepoint(self.game.click_pos):
                self.game.playing = False
                self.run_display = False
                self.game.running = False
