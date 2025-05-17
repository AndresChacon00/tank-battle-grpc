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
    mapID   int                          // ID del mapa seleccionado
}

// Eliminar la lógica de actualización de balas en UpdateState
func (s *gameServer) UpdateState(ctx context.Context, state *game.PlayerState) (*game.GameState, error) {
    s.mu.Lock()

    // Actualizar el estado del jugador
    s.players[state.PlayerId] = state

    // Eliminar balas que salgan de los límites del mapa (ejemplo: 800x600)
    for id, bullet := range s.bullets {
        if bullet.X < 0 || bullet.X > 800 || bullet.Y < 0 || bullet.Y > 600 {
            log.Printf("Eliminando bala fuera de límites: ID=%s, Posición=(%f, %f)", id, bullet.X, bullet.Y)
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

    // Depuración para verificar el estado del juego antes de devolverlo
    //log.Printf("Estado del juego antes de devolverlo: Jugadores=%v, Balas=%v", gameState.Players, gameState.Bullets)
	
    defer s.mu.Unlock()
    return gameState, nil
}

// Modificar AddBullet para solo registrar la posición inicial de las balas
func (s *gameServer) AddBullet(ctx context.Context, bullet *game.BulletState) (*game.Empty, error) {
    s.mu.Lock()
    
    // Verificar si el BulletId ya existe antes de agregarlo
    if _, exists := s.bullets[bullet.BulletId]; exists {
        log.Printf("Advertencia: Se intentó registrar una bala con un BulletId duplicado: %s", bullet.BulletId)
    } else {
        s.bullets[bullet.BulletId] = &game.BulletState{
            BulletId: bullet.BulletId,
            X:       bullet.X,
            Y:       bullet.Y,
            Dx:      bullet.Dx,
            Dy:      bullet.Dy,
            OwnerId: bullet.OwnerId,
        }
        log.Printf("Bala registrada correctamente: ID=%s, Total de balas activas: %d", bullet.BulletId, len(s.bullets))
    }

    // Registrar la acción de disparar una bala
    log.Printf("Bala disparada por el jugador %s en la posición inicial (%f, %f)", bullet.OwnerId, bullet.X, bullet.Y)
	log.Printf("Total de balas activas: %d", len(s.bullets))
    
	defer s.mu.Unlock()
    return &game.Empty{}, nil
}

func (s *gameServer) GetGameState(ctx context.Context, empty *game.Empty) (*game.GameState, error) {
    s.mu.Lock()

    // Construir el estado del juego
    gameState := &game.GameState{}
    for _, player := range s.players {
        gameState.Players = append(gameState.Players, player)
    }
    for _, bullet := range s.bullets {
        gameState.Bullets = append(gameState.Bullets, bullet)
    }

	
    defer s.mu.Unlock()
    return gameState, nil
}

// Implementar el método SetMap para recibir y almacenar el número del mapa
func (s *gameServer) SetMap(ctx context.Context, req *game.MapRequest) (*game.Empty, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    s.mapID = int(req.MapNumber)
    log.Printf("Mapa seleccionado: %d", s.mapID)

    return &game.Empty{}, nil
}

// Implementar el método GetMap para devolver el número del mapa actual
func (s *gameServer) GetMap(ctx context.Context, empty *game.Empty) (*game.MapResponse, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    log.Printf("Mapa actual solicitado: %d", s.mapID)
    return &game.MapResponse{MapNumber: int32(s.mapID)}, nil
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