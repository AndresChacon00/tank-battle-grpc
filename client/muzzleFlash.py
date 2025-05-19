import pygame
import math

class MuzzleFlash(pygame.sprite.Sprite):
    """Clase para el efecto de disparo del cañón"""

    def __init__(self, position, direction):
        super().__init__()
        self.original_image = pygame.image.load(
            "assets/retina/shotLarge.png"
        ).convert_alpha()  # Imagen del efecto
        self.image = self.original_image
        self.rect = self.image.get_rect(center=position)

        # Calcular el ángulo del efecto basado en la dirección
        angle = math.degrees(math.atan2(-direction[1], direction[0]))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=position)

        # Tiempo de vida del efecto
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        # Eliminar el efecto después de 100 ms
        if pygame.time.get_ticks() - self.spawn_time > 100:
            self.kill()