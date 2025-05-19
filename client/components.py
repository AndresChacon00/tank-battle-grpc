import pygame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from menu import Menu


class InputBox:
    """Input box component for text input in pygame"""

    def __init__(
        self,
        x,
        y,
        w,
        h,
        font,
        parent: "Menu",
        text="",
        color_inactive=(0, 0, 0),
        color_active=(255, 0, 0),
    ):
        self.rect = pygame.Rect(x, y, w, h)
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.parent = parent
        self.txt_surface = self.font.render(self.text, True, self.color)
        self.active = False

    def handle_event(self):
        """Handle events for the input box"""
        if self.parent.game.click_pos is not None:
            # Toggle the active variable if the user clicked on the input_box rect.
            if self.rect.collidepoint(self.parent.game.click_pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive

        if self.parent.game.key_pressed is not None and self.active:
            key_pressed = self.parent.game.key_pressed
            if key_pressed == pygame.K_RETURN:
                self.parent.game.key_pressed = None  # Reset key pressed after handling
                return "submit"

            elif key_pressed == pygame.K_BACKSPACE:
                self.text = self.text[:-1]

            else:
                # Solo permitir números y punto
                key_name = pygame.key.name(key_pressed)
                if len(self.text) < 20 and (key_name.isdigit() or key_name == "."):
                    self.text += key_name
            self.txt_surface = self.font.render(self.text, True, self.color)
            self.parent.game.key_pressed = None  # Reset key pressed after handling

        return None

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        return self.text
