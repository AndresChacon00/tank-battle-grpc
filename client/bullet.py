import pygame
import math
import time

class Bullet(pygame.sprite.Sprite):
    """Clase para las balas disparadas por el tanque"""

    def __init__(self, position, direction, tank_id, damage = 10):
        super().__init__()
        self.tank_id = tank_id
        self.damage = damage
        self.image = pygame.image.load(
            "assets/Retina/bulletBlue1_outline.png"
        ).convert_alpha()  # Asegúrate de que el archivo esté en el mismo directorio
        self.rect = self.image.get_rect(center=position)
        self.speed = 5
        self.direction = direction

    def update(self):
        # Mover la bala en la dirección calculada
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Eliminar la bala se sale de la pantalla
        #if (
         #   self.rect.right < 0
          #  or self.rect.left > pygame.display.get_surface().get_width()
           # or self.rect.bottom < 0
           # or self.rect.top > pygame.display.get_surface().get_height()
        #):
         #   self.kill()