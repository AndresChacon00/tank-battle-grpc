import pygame

# Inicializar pygame y el módulo de joystick
pygame.init()
pygame.joystick.init()

# Verificar si hay joysticks conectados
joystick_count = pygame.joystick.get_count()
if joystick_count == 0:
    print("No se detectaron joysticks.")
else:
    print(f"Se detectaron {joystick_count} joystick(s).")
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"Joystick {i}: {joystick.get_name()}")
        print(f"  Número de ejes: {joystick.get_numaxes()}")
        print(f"  Número de botones: {joystick.get_numbuttons()}")
        print(f"  Número de hats: {joystick.get_numhats()}")

# Finalizar pygame
pygame.quit()