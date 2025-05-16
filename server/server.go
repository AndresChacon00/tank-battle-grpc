package main

import (
	"context"
	"log"
	"net"
	"sync"
	"tank-battle-grpc/game"

	"google.golang.org/grpc"
)

type gameServer struct {
    game.UnimplementedGameServiceServer
    mu      sync.Mutex
    players map[string]*game.PlayerState
    bullets map[string]*game.BulletState // Mapa para almacenar las balas activas
}

func (s *gameServer) UpdateState(ctx context.Context, state *game.PlayerState) (*game.GameState, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // Actualizar el estado del jugador
    s.players[state.PlayerId] = state

    // Actualizar la posición de las balas existentes
    for id, bullet := range s.bullets {
        bullet.X += bullet.Dx
        bullet.Y += bullet.Dy

        // Eliminar balas que salgan de los límites del mapa (ejemplo: 800x600)
        if bullet.X < 0 || bullet.X > 800 || bullet.Y < 0 || bullet.Y > 600 {
            delete(s.bullets, id)
        }
    }

    // Construir el estado del juego
    gameState := &game.GameState{}
    for _, player := range s.players {
        gameState.Players = append(gameState.Players, player)
    }
    for _, bullet := range s.bullets {
        gameState.Bullets = append(gameState.Bullets, bullet)
    }

    return gameState, nil
}

func (s *gameServer) AddBullet(ctx context.Context, bullet *game.BulletState) (*game.Empty, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // Agregar una nueva bala al mapa de balas
    s.bullets[bullet.BulletId] = bullet

    return &game.Empty{}, nil
}

func (s *gameServer) GetGameState(ctx context.Context, empty *game.Empty) (*game.GameState, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // Construir el estado del juego
    gameState := &game.GameState{}
    for _, player := range s.players {
        gameState.Players = append(gameState.Players, player)
    }
    for _, bullet := range s.bullets {
        gameState.Bullets = append(gameState.Bullets, bullet)
    }

    return gameState, nil
}

func main() {
    lis, err := net.Listen("tcp", ":9000")
    if (err != nil) {
        log.Fatalf("Failed to listen on port 9000: %v", err)
    }

    grpcServer := grpc.NewServer()

    server := &gameServer{
        players: make(map[string]*game.PlayerState),
        bullets: make(map[string]*game.BulletState), // Inicializar el mapa de balas
    }
    game.RegisterGameServiceServer(grpcServer, server)

    log.Println("Game server is running on port 9000")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("Failed to serve gRPC server over port 9000: %v", err)
    }
}