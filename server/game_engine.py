import pygame
import grpc
import time
from game.game_pb2 import Empty
from game.game_pb2_grpc import GameServiceStub

# Configuración de la ventana
WIDTH, HEIGHT = 800, 600
TANK_SIZE = 50

class GameEngine:
    def __init__(self, server_address):
        # Conectar al servidor gRPC
        self.channel = grpc.insecure_channel(server_address)
        self.client = GameServiceStub(self.channel)

        # Inicializar pygame
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Game Engine")
        self.clock = pygame.time.Clock()

    def get_game_state(self):
        """Obtener el estado del juego desde el servidor"""
        try:
            return self.client.GetGameState(Empty())
        except grpc.RpcError as e:
            print(f"Error al obtener el estado del juego: {e}")
            return None

    def run(self):
        """Ejecutar el motor del juego"""
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Obtener el estado del juego
            game_state = self.get_game_state()
            if not game_state:
                continue

            # Dibujar el estado del juego
            self.screen.fill((0, 0, 0))  # Fondo negro
            for player in game_state.players:
                pygame.draw.rect(
                    self.screen,
                    (0, 255, 0),  # Color verde para los tanques
                    pygame.Rect(player.x, player.y, TANK_SIZE, TANK_SIZE),
                )

            pygame.display.flip()

        pygame.quit()

if __name__ == "__main__":
    engine = GameEngine("localhost:9000")  # Dirección del servidor gRPC
    engine.run()