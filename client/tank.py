import pygame
import math
import time
from config import Config


class Tank(pygame.sprite.Sprite):
    """Tank body class"""

    def __init__(self, tank_id, health=100):
        super().__init__()
        self.tank_id = tank_id
        self.health = health
        self.original_image = pygame.image.load(
            "assets/Retina/tankBody_blue_outline.png"
        ).convert_alpha()  # Imagen original
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = Config.WIDTH // 2
        self.rect.bottom = Config.HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.angle = 0
        self.target_angle = 0  # Nuevo: Ángulo objetivo

        self.font = pygame.font.Font(None, 24)

    def update(self, blocks: pygame.sprite.Group):
        self.speed_x = 0
        self.speed_y = 0
        keystate = pygame.key.get_pressed()
        # Movimiento en el eje X
        if keystate[pygame.K_a]:
            self.speed_x = -5
        if keystate[pygame.K_d]:
            self.speed_x = 5

        # Movimiento en el eje Y
        if keystate[pygame.K_w]:
            self.speed_y = -5
        if keystate[pygame.K_s]:
            self.speed_y = 5

        # Normalizar la velocidad en caso de movimiento diagonal
        if self.speed_x != 0 and self.speed_y != 0:
            diagonal_speed = 5 / (2**0.5)  # Velocidad ajustada para movimiento diagonal
            self.speed_x = self.speed_x / abs(self.speed_x) * diagonal_speed
            self.speed_y = self.speed_y / abs(self.speed_y) * diagonal_speed

        # Ajustar el ángulo objetivo para movimientos diagonales
        if keystate[pygame.K_w] and keystate[pygame.K_a]:
            self.target_angle = 225  # Arriba-izquierda
        elif keystate[pygame.K_w] and keystate[pygame.K_d]:
            self.target_angle = 135  # Arriba-derecha
        elif keystate[pygame.K_s] and keystate[pygame.K_a]:
            self.target_angle = -45  # Abajo-izquierda
        elif keystate[pygame.K_s] and keystate[pygame.K_d]:
            self.target_angle = 45  # Abajo-derecha
        elif keystate[pygame.K_w]:
            self.target_angle = 180  # Arriba
        elif keystate[pygame.K_s]:
            self.target_angle = 0  # Abajo
        elif keystate[pygame.K_a]:
            self.target_angle = -90  # Izquierda
        elif keystate[pygame.K_d]:
            self.target_angle = 90  # Derecha

        # Rotación gradual hacia el ángulo objetivo
        rotation_speed = 5  # Velocidad de rotación (grados por frame)
        angle_difference = (self.target_angle - self.angle + 360) % 360

        # Determinar la dirección de rotación más corta
        if angle_difference > 180:
            # Rotar en sentido antihorario
            self.angle -= rotation_speed
            if self.angle < 0:
                self.angle += 360  # Mantener el ángulo en el rango [0, 360]
        else:
            # Rotar en sentido horario
            self.angle += rotation_speed
            if self.angle >= 360:
                self.angle -= 360  # Mantener el ángulo en el rango [0, 360]

        # Asegurarse de no sobrepasar el ángulo objetivo
        if abs(angle_difference) < rotation_speed:
            self.angle = self.target_angle

        # Guardar la posición anterior
        previous_x = self.rect.x
        previous_y = self.rect.y

        # Actualizar posición
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Detectar colisiones con bloques sólidos
        colliding_blocks = pygame.sprite.spritecollide(self, blocks, False)
        if any([block.solid for block in colliding_blocks]):
            # Revertir posición si hay colisión
            self.rect.x = previous_x
            self.rect.y = previous_y

        # Rotar la imagen usando la original
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Limitar movimiento dentro de la pantalla
        if self.rect.right > Config.WIDTH:
            self.rect.right = Config.WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > Config.HEIGHT:
            self.rect.bottom = Config.HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0



    def handle_bullet_collision(self, bullets_group):
        """Manejar colisiones con balas"""
        colliding_bullets = pygame.sprite.spritecollide(self, bullets_group, False)

        for bullet in colliding_bullets:
            # Ignorar colisión si la bala fue disparada por este tanque y tiene menos de 1 segundo
            print("BAla impacto")
            if bullet.tank_id == self.tank_id:
                print("mismoid")
                continue

            # Aplicar daño
            self.health -= bullet.damage
            
           # bullet.kill()
            if self.health <= 0:
                print("murio")
            #    self.kill()  

    def draw_health(self, screen):
            """Dibujar la vida del tanque encima de él"""
            
            life_text = self.font.render(f"{self.health}", True, (255, 0, 0))
            text_rect = life_text.get_rect(center=(self.rect.centerx, self.rect.top - 10))
            screen.blit(life_text, text_rect)

class TankCannon(pygame.sprite.Sprite):
    """Cannon attached to a tank body"""

    def __init__(self, tank):
        super().__init__()
        self.tank = tank  # Referencia al tanque base
        self.original_image = pygame.image.load(
            "assets/Retina/tankBlue_barrel1_outline.png"
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.tank.rect.center)
        self.angle = 0

        # Calcular el desplazamiento desde el centro del cañón hasta su base
        self.offset = int(
            self.rect.height * 0.4
        )  # Asume que la base está en el centro inferior del sprite

    def update(self, cursor_angle):
        self.angle = cursor_angle

        # Rotar la imagen del cañón
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        # Ajustar el rectángulo del cañón para que el eje de rotación esté en la base
        self.rect = self.image.get_rect()
        rad_angle = math.radians(self.angle - 90)  # Convertir el ángulo a radianes
        self.rect.centerx = self.tank.rect.centerx + self.offset * math.cos(rad_angle)
        self.rect.centery = self.tank.rect.centery - self.offset * math.sin(rad_angle)


class Track(pygame.sprite.Sprite):
    """Track left by tank movement"""

    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface(
            (20, 10), pygame.SRCALPHA
        )  # Superficie transparente
        pygame.draw.rect(
            self.image, (100, 100, 100, 150), (0, 0, 20, 10)
        )  # Rectángulo semitransparente
        self.rect = self.image.get_rect(center=position)
        self.spawn_time = time.time()  # Registrar el tiempo de creación

    def update(self):
        # Eliminar el rastro después de 2 segundos
        if time.time() - self.spawn_time > 2:
            self.kill()

