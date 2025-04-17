import pygame

class MuzzleFlash(pygame.sprite.Sprite):
    """Clase para manejar la explosión de disparo (muzzle flash)"""

    def __init__(self, position):
        super().__init__()
        # Cargar la imagen de la explosión
        self.image = pygame.image.load("assets/retina/shotLarge.png").convert_alpha()
        self.rect = self.image.get_rect(center=position)
        self.start_time = pygame.time.get_ticks()
        self.duration = 50  # Duración de la explosión en milisegundos

    def update(self):
        # Eliminar la explosión después de que pase la duración
        if pygame.time.get_ticks() - self.start_time > self.duration:
            self.kill()