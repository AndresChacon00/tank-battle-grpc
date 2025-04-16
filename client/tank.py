import pygame, random, math, time

WIDTH = 800
HEIGHT = 600
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tank Game")
clock = pygame.time.Clock()

# Ocultar el cursor del mouse
pygame.mouse.set_visible(False)

class Tank(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = pygame.image.load("assets/Retina/tankBody_blue_outline.png").convert_alpha()  # Imagen original
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed_x = 0
        self.speed_y = 0
        self.angle = 0
        self.target_angle = 0  # Nuevo: Ángulo objetivo

    def update(self):
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
            diagonal_speed = 5 / (2 ** 0.5)  # Velocidad ajustada para movimiento diagonal
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

        # Actualizar posición
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Rotar la imagen usando la original
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        # Limitar movimiento dentro de la pantalla
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

class TankCannon(pygame.sprite.Sprite):
    def __init__(self, tank):
        super().__init__()
        self.tank = tank  # Referencia al tanque base
        self.original_image = pygame.image.load("assets/Retina/tankBlue_barrel1_outline.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.tank.rect.center)
        self.angle = 0

        # Calcular el desplazamiento desde el centro del cañón hasta su base
        self.offset = int(self.rect.height * 0.4)  # Asume que la base está en el centro inferior del sprite
        

    def update(self):
        # Rotar hacia el cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        rel_x, rel_y = mouse_x - self.tank.rect.centerx, mouse_y - self.tank.rect.centery
        self.angle = math.degrees(math.atan2(-rel_y, rel_x)) + 90  # Calcular ángulo hacia el cursor

        # Rotar la imagen del cañón
        self.image = pygame.transform.rotate(self.original_image, self.angle)

        # Ajustar el rectángulo del cañón para que el eje de rotación esté en la base
        self.rect = self.image.get_rect()
        rad_angle = math.radians(self.angle - 90)  # Convertir el ángulo a radianes
        self.rect.centerx = self.tank.rect.centerx + self.offset * math.cos(rad_angle)
        self.rect.centery = self.tank.rect.centery - self.offset * math.sin(rad_angle)


# Crear un grupo para los rastros
tracks_group = pygame.sprite.Group()

class Track(pygame.sprite.Sprite):
    def __init__(self, position):
        super().__init__()
        self.image = pygame.Surface((20, 10), pygame.SRCALPHA)  # Superficie transparente
        pygame.draw.rect(self.image, (100, 100, 100, 150), (0, 0, 20, 10))  # Rectángulo semitransparente
        self.rect = self.image.get_rect(center=position)
        self.spawn_time = time.time()  # Registrar el tiempo de creación

    def update(self):
        # Eliminar el rastro después de 2 segundos
        if time.time() - self.spawn_time > 2:
            self.kill()

# Crear tanque y cañón
tank = Tank()  # Tu clase de tanque
cannon = TankCannon(tank)

# Añadir ambos al grupo de sprites
all_sprites = pygame.sprite.Group()
all_sprites.add(tank)
all_sprites.add(cannon)

# Variable para rastrear la posición anterior del tanque
previous_tank_position = tank.rect.center

running = True
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    # Detectar si el tanque se ha movido
    if tank.rect.center != previous_tank_position:
        # Crear un rastro en la posición anterior del tanque
        track = Track(previous_tank_position)
        tracks_group.add(track)
        # Actualizar la posición anterior del tanque
        previous_tank_position = tank.rect.center    
    
    all_sprites.update()

    screen.fill(WHITE)

    all_sprites.draw(screen)

    # Dibujar la mira personalizada
    mouse_pos = pygame.mouse.get_pos()
    pygame.draw.circle(screen, RED, mouse_pos, 10, 2)  # Círculo exterior
    pygame.draw.line(screen, RED, (mouse_pos[0] - 15, mouse_pos[1]), (mouse_pos[0] + 15, mouse_pos[1]), 2)  # Línea horizontal
    pygame.draw.line(screen, RED, (mouse_pos[0], mouse_pos[1] - 15), (mouse_pos[0], mouse_pos[1] + 15), 2)  # Línea vertical

    pygame.display.flip()
pygame.quit()
