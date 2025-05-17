import pygame
import math
import time
from config import Config
from colors import Colors  # Importar Colors


class Tank(pygame.sprite.Sprite):
    """Tank body class"""

    def __init__(self, tank_id, x=None, y=None, color=None, health=100, score=0):
        super().__init__()
        self.tank_id = tank_id
        self.x = x if x is not None else Config.WIDTH // 2
        self.y = y if y is not None else Config.HEIGHT - 10
        self.angle = 0
        self.target_angle = 0
        self.speed_x = 0
        self.speed_y = 0
        self.max_speed = 3
        self.health = health
        self.score = score
        self.is_destroyed = False
        self.color = color or "blue"

        # Cargar la imagen del tanque según el color
        self.original_image = self.get_tank_image()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.cannon = None

        # Fuente para mostrar la vida
        self.font = pygame.font.Font(None, 24)

    def get_tank_image(self):
        """Devuelve la imagen del tanque según el color"""
        if self.color == "blue":
            return pygame.image.load("assets/Retina/tankBody_blue_outline.png").convert_alpha()
        elif self.color == "red":
            return pygame.image.load("assets/Retina/tankBody_red_outline.png").convert_alpha()
        elif self.color == "green":
            return pygame.image.load("assets/Retina/tankBody_green_outline.png").convert_alpha()
        else:
            return pygame.image.load("assets/Retina/tankBody_gray_outline.png").convert_alpha()

    def set_cannon(self, cannon):
        """Asociar un cañón al tanque"""
        self.cannon = cannon

    def handle_joystick(self, joystick):
        """Manejar el movimiento del tanque y la rotación del cañón con un joystick"""
        if joystick:
            # Movimiento del tanque (joystick izquierdo)
            move_x = joystick.get_axis(0)  # Eje X del joystick izquierdo
            move_y = joystick.get_axis(1)  # Eje Y del joystick izquierdo
            self.speed_x = move_x * self.max_speed
            self.speed_y = move_y * self.max_speed

            # Calcular el ángulo objetivo basado en el joystick
            if abs(move_x) > 0.1 or abs(move_y) > 0.1:  # Evitar ruido en el joystick
                self.target_angle = math.degrees(math.atan2(-move_y, move_x)) + 90  # Invertir Y para corregir el eje
                self.target_angle %= 360  # Asegurarse de que el ángulo esté en el rango [0, 360]

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

    def handle_movement(self, keys):
        """Manejar el movimiento del tanque basado en las teclas presionadas"""
        self.speed_x = 0
        self.speed_y = 0

        # Movimiento básico
        if keys[pygame.K_a]:
            self.speed_x = -self.max_speed
        if keys[pygame.K_d]:
            self.speed_x = self.max_speed
        if keys[pygame.K_w]:
            self.speed_y = -self.max_speed
        if keys[pygame.K_s]:
            self.speed_y = self.max_speed

        # Normalizar la velocidad en caso de movimiento diagonal
        if self.speed_x != 0 and self.speed_y != 0:
            diagonal_speed = self.max_speed / (2**0.5)  # Velocidad ajustada para movimiento diagonal
            self.speed_x = self.speed_x / abs(self.speed_x) * diagonal_speed
            self.speed_y = self.speed_y / abs(self.speed_y) * diagonal_speed

        # Ajustar el ángulo objetivo para movimientos diagonales
        if keys[pygame.K_w] and keys[pygame.K_a]:
            self.target_angle = 225  # Arriba-izquierda
        elif keys[pygame.K_w] and keys[pygame.K_d]:
            self.target_angle = 135  # Arriba-derecha
        elif keys[pygame.K_s] and keys[pygame.K_a]:
            self.target_angle = -45  # Abajo-izquierda
        elif keys[pygame.K_s] and keys[pygame.K_d]:
            self.target_angle = 45  # Abajo-derecha
        elif keys[pygame.K_w]:
            self.target_angle = 180  # Arriba
        elif keys[pygame.K_s]:
            self.target_angle = 0  # Abajo
        elif keys[pygame.K_a]:
            self.target_angle = -90  # Izquierda
        elif keys[pygame.K_d]:
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

    def update(self, blocks: pygame.sprite.Group, bullets_group: pygame.sprite.Group, other_tanks: list):
        """Actualizar el estado del tanque"""
        if self.is_destroyed:
            return

        # Actualizar posición
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Detectar colisiones con bloques
        colliding_blocks = pygame.sprite.spritecollide(self, blocks, False)
        if any(block.solid for block in colliding_blocks):
            self.rect.x -= self.speed_x
            self.rect.y -= self.speed_y

        # Detectar colisiones con otros tanques
        self.handle_tank_collision(other_tanks)

        # Rotar la imagen del tanque
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

        # Manejar colisiones con balas
        self.handle_bullet_collision(bullets_group)

    def handle_bullet_collision(self, bullets_group):
        """Manejar colisiones con balas"""
        current_time = pygame.time.get_ticks()  # Tiempo actual en milisegundos
        colliding_bullets = pygame.sprite.spritecollide(self, bullets_group, False)

        for bullet in colliding_bullets:
            # Ignorar colisión si la bala fue disparada por este tanque y tiene menos de 1 segundo
            if bullet.tank_id == self.tank_id and current_time - bullet.spawn_time < 250:
                continue

            # Aplicar daño
            self.health -= bullet.damage
            bullet.kill()
            if self.health <= 0:
                self.is_destroyed = True
                if self.cannon:
                    self.cannon.kill()
                self.kill()
    
    def handle_tank_collision(self, other_tanks):
        """Manejar colisiones con otros tanques"""
        for other_tank in other_tanks:
            if other_tank != self and not other_tank.is_destroyed and self.rect.colliderect(other_tank.rect):
                # Revertir el movimiento si hay colisión
                self.rect.x -= self.speed_x
                self.rect.y -= self.speed_y
                break  # Salir del bucle después de manejar la colisión

    def draw_health(self, screen):
        """Dibujar la vida del tanque encima de él"""
        if not self.is_destroyed:
            life_text = self.font.render(f"{self.health}", True, Colors.RED)
            text_rect = life_text.get_rect(center=(self.rect.centerx, self.rect.top - 10))
            screen.blit(life_text, text_rect)

class TankCannon(pygame.sprite.Sprite):
    """Cañón del tanque"""

    def __init__(self, tank):
        super().__init__()
        self.tank = tank
        self.angle = 0
        self.original_image = self.get_cannon_image()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.tank.rect.center)
        self.offset = int(self.rect.height * 0.4)

    def get_cannon_image(self):
        """Devuelve la imagen del cañón según el color del tanque"""
        if self.tank.color == "blue":
            return pygame.image.load("assets/Retina/tankBlue_barrel1_outline.png").convert_alpha()
        elif self.tank.color == "red":
            return pygame.image.load("assets/Retina/tankRed_barrel1_outline.png").convert_alpha()
        elif self.tank.color == "green":
            return pygame.image.load("assets/Retina/tankGreen_barrel1_outline.png").convert_alpha()
        else:
            return pygame.image.load("assets/Retina/tankGray_barrel1_outline.png").convert_alpha()

    def handle_rotation(self, target_angle=None):
        """Manejar la rotación del cañón"""
        if target_angle is not None:
            self.angle = target_angle
        else:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rel_x, rel_y = mouse_x - self.tank.rect.centerx, mouse_y - self.tank.rect.centery
            self.angle = math.degrees(math.atan2(-rel_y, rel_x)) + 90

    def handle_rotation_joystick(self, joystick):
        """Manejar la rotación del cañón usando el joystick derecho"""
        aim_x = joystick.get_axis(2)  # Eje X del joystick derecho
        aim_y = joystick.get_axis(3)  # Eje Y del joystick derecho

        # Evitar ruido en el joystick
        if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
            self.angle = math.degrees(math.atan2(-aim_y, aim_x)) + 90 # Calcular el ángulo del cañón


    def update(self):
        """Actualizar la posición y rotación del cañón"""
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        rad_angle = math.radians(self.angle - 90)
        self.rect = self.image.get_rect()
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