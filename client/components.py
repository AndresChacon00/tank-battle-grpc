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

    def handle_event(self, event: pygame.event.Event):
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and self.parent.game.click_pos is not None
        ):
            # Toggle the active variable if the user clicked on the input_box rect.
            if self.rect.collidepoint(self.parent.game.click_pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return "submit"  # You can use this to trigger a submit action
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(self.text) < 20:
                    self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, (0, 0, 0))
        return None

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x + 10, self.rect.y + 10))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_value(self):
        return self.text
