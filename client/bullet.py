import pygame
import math
# from tank import Tank


class Bullet(pygame.sprite.Sprite):
    """Clase para las balas disparadas por el tanque"""

    def __init__(self, position, direction, tank_id, damage = 10):
        super().__init__()
        self.tank_id = tank_id
        self.damage = damage
        self.image = self.get_bullet_image()
        self.rect = self.image.get_rect(center=position)
        self.speed = 5
        self.direction = list(direction)  # Convertir la dirección a una lista
        # self.collision_group = (
        #     collision_group  # Grupo de bloques con los que la bala puede colisionar
        # )
        self.bounces = 1  # Número de rebotes permitidos
        self.spawn_time = pygame.time.get_ticks()  # Tiempo de creación de la bala

        # Ajustar la posición del MuzzleFlash
        # muzzle_offset_x = direction[0] * 20  # Ajusta este valor según el diseño
        # muzzle_offset_y = direction[1] * 20  # Ajusta este valor según el diseño
        # muzzle_position = (position[0] + muzzle_offset_x, position[1] + muzzle_offset_y)

        # Crear un MuzzleFlash en la posición ajustada
        # muzzle_flash = MuzzleFlash(muzzle_position, direction)
        # muzzle_flash_group.add(muzzle_flash)

    def update(self):
        # Mover la bala en la dirección calculada
        self.rect.x += self.direction[0] * self.speed
        self.rect.y += self.direction[1] * self.speed

        # Detectar colisiones con bloques sólidos
        # colliding_blocks = pygame.sprite.spritecollide(
        #     self, self.collision_group, False
        # )
        # solid_collision = next(
        #     (block for block in colliding_blocks if getattr(block, "solid", False)),
        #     None,
        # )

        # if solid_collision:
        #     if self.bounces > 0:
        #         # Rebote: invertir la dirección según el eje de colisión
        #         if abs(self.rect.centerx - solid_collision.rect.centerx) > abs(
        #             self.rect.centery - solid_collision.rect.centery
        #         ):
        #             # Colisión en el eje X: invertir dirección horizontal
        #             self.direction[0] *= -1
        #         else:
        #             # Colisión en el eje Y: invertir dirección vertical
        #             self.direction[1] *= -1
        #         self.bounces -= 1  # Reducir el contador de rebotes
        #     else:
        #         # Si no quedan rebotes, eliminar la bala
        #         self.kill()

        # # Detectar colisiones con tanques
        # current_time = pygame.time.get_ticks()
        # for tank in [
        #     sprite for sprite in self.collision_group if isinstance(sprite, Tank)
        # ]:
        #     if self.rect.colliderect(tank.rect):
        #         if tank.tank_id == self.tank_id:
        #             # Si es el tanque que disparó, esperar 1 segundo antes de destruirlo
        #             if current_time - self.spawn_time > 1000:  # 1000 ms = 1 segundo
        #                 tank.is_destroyed = True  # Marcar el tanque como destruido
        #                 tank.kill()  # Eliminar el tanque
        #                 self.kill()  # Eliminar la bala
        #         else:
        #             # Si es un tanque enemigo, destruirlo inmediatamente
        #             tank.is_destroyed = True
        #             tank.kill()
        #             self.kill()

        # # Detectar colisiones con los límites de la pantalla
        # screen_width = pygame.display.get_surface().get_width()
        # screen_height = pygame.display.get_surface().get_height()

        # if self.rect.left <= 0 or self.rect.right >= screen_width:
        #     if self.bounces > 0:
        #         # Rebote en el eje X
        #         self.direction[0] *= -1
        #         self.bounces -= 1  # Reducir el contador de rebotes
        #     else:
        #         # Si no quedan rebotes, eliminar la bala
        #         self.kill()

        # if self.rect.top <= 0 or self.rect.bottom >= screen_height:
        #     if self.bounces > 0:
        #         # Rebote en el eje Y
        #         self.direction[1] *= -1
        #         self.bounces -= 1  # Reducir el contador de rebotes
        #     else:
        #         # Si no quedan rebotes, eliminar la bala
        #         self.kill()

        # # Actualizar el ángulo de la imagen basado en la dirección
        # angle = math.degrees(math.atan2(-self.direction[1], self.direction[0])) - 90
        # self.image = pygame.transform.rotate(self.original_image, angle)
        # self.rect = self.image.get_rect(center=self.rect.center)

    def get_bullet_image(self):
        """Devuelve la imagen de la bala según el ID del tanque"""
        if self.tank_id == 1:
            return pygame.image.load(
                "assets/Retina/bulletBlue1_outline.png"
            ).convert_alpha()
        elif self.tank_id == 2:
            return pygame.image.load(
                "assets/Retina/bulletRed1_outline.png"
            ).convert_alpha()
        else:
            return pygame.image.load(
                "assets/Retina/bulletGreen1_outline.png"
            ).convert_alpha()


class MuzzleFlash(pygame.sprite.Sprite):
    """Clase para el efecto de disparo del cañón"""

    def __init__(self, position, direction):
        super().__init__()
        self.original_image = pygame.image.load(
            "assets/retina/shotLarge.png"
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=position)

        # Calcular el ángulo del efecto basado en la dirección
        angle = math.degrees(math.atan2(-direction[1], direction[0])) + 90
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=position)

        # Tiempo de vida del efecto
        self.spawn_time = pygame.time.get_ticks()

    def update(self):
        # Eliminar el efecto después de 100 ms
        if pygame.time.get_ticks() - self.spawn_time > 100:
            self.kill()
