package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"sync"
	"tank-battle-grpc/game"
	"time" // Importar el paquete de tiempo

	"google.golang.org/grpc"
)

// Añadir un contador global para los IDs de los jugadores
var playerIDCounter int32 = 1

type gameServer struct {
    game.UnimplementedGameServiceServer
    mu      sync.Mutex
    players map[string]*game.PlayerState
    bullets map[string]*game.BulletState // Mapa para almacenar las balas activas
    mapID   int                          // ID del mapa seleccionado
    gameStarted bool                     // Nuevo: indica si el juego ha comenzado
}

func (s *gameServer) UpdateState(ctx context.Context, state *game.PlayerState) (*game.GameState, error) {
    s.mu.Lock()

    // Actualizar el estado del jugador
    s.players[state.PlayerId] = state


    // Construir el estado del juego
    gameState := &game.GameState{}
    for _, player := range s.players {
        gameState.Players = append(gameState.Players, player)
    }
    for _, bullet := range s.bullets {
        gameState.Bullets = append(gameState.Bullets, bullet)
    }
    gameState.GameStarted = s.gameStarted // Nuevo: incluir estado de inicio de juego

    defer s.mu.Unlock()
    return gameState, nil
}

func (s *gameServer) AddBullet(ctx context.Context, bullet *game.BulletState) (*game.Empty, error) {
    s.mu.Lock()

    // Verificar si el BulletId ya existe antes de agregarlo
    if _, exists := s.bullets[bullet.BulletId]; exists {
        log.Printf("Advertencia: Se intentó registrar una bala con un BulletId duplicado: %s", bullet.BulletId)
    } else {
        
        s.bullets[bullet.BulletId] = bullet
        log.Printf("Bala registrada correctamente: ID=%s, Total de balas activas: %d", bullet.BulletId, len(s.bullets))
    }

    defer s.mu.Unlock()
    return &game.Empty{}, nil
}

func (s *gameServer) RemoveBullet(ctx context.Context, req *game.BulletRemoveRequest) (*game.Empty, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    // Verificar si la bala existe en el mapa de balas
    if _, exists := s.bullets[req.BulletId]; exists {
        delete(s.bullets, req.BulletId)
        log.Printf("Bala eliminada: ID=%s", req.BulletId)
    } else {
        log.Printf("Advertencia: Se intentó eliminar una bala inexistente: ID=%s", req.BulletId)
    }

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
    gameState.GameStarted = s.gameStarted // Nuevo: incluir estado de inicio de juego

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

// Implementar el método AddPlayer para asignar un ID único a un nuevo jugador
func (s *gameServer) AddPlayer(ctx context.Context, req *game.PlayerRequest) (*game.PlayerResponse, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    assignedID := playerIDCounter
    playerIDCounter++
    player := &game.PlayerState{
        PlayerId:   fmt.Sprintf("%d", assignedID),
    }
    s.players[req.PlayerName] = player

    log.Printf("Jugador agregado: Nombre=%s, ID=%d", req.PlayerName, assignedID)

    return &game.PlayerResponse{PlayerId: assignedID}, nil
}

func (s *gameServer) GetPlayerList(ctx context.Context, req *game.Empty) (*game.PlayerList, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    playerList := &game.PlayerList{}
    for _, player := range s.players {
        playerList.Players = append(playerList.Players, &game.PlayerListItem{
            PlayerId:   player.PlayerId,
        })
    }

    log.Printf("Lista de jugadores solicitada: %d jugadores activos", len(playerList.Players))
    return playerList, nil
}

func (s *gameServer) StreamGameState(empty *game.Empty, stream game.GameService_StreamGameStateServer) error {
    for {
        s.mu.Lock()

        // Construir el estado del juego
        gameState := &game.GameState{}
        for _, player := range s.players {
            gameState.Players = append(gameState.Players, player)
        }
        for _, bullet := range s.bullets {
            gameState.Bullets = append(gameState.Bullets, bullet)
        }
        gameState.GameStarted = s.gameStarted // Nuevo: incluir estado de inicio de juego

        s.mu.Unlock()

        // Enviar el estado del juego al cliente
        if err := stream.Send(gameState); err != nil {
            log.Printf("Error al enviar el estado del juego: %v", err)
            return err
        }

        // Esperar un intervalo antes de enviar la siguiente actualización
        time.Sleep(10 * time.Millisecond)
    }
}

// Implementar el método StartGame para cambiar el estado y notificar a los clientes
func (s *gameServer) StartGame(ctx context.Context, empty *game.Empty) (*game.Empty, error) {
    s.mu.Lock()
    s.gameStarted = true
    log.Printf("El juego ha comenzado (gameStarted=true)")
    s.mu.Unlock()
    return &game.Empty{}, nil
}

func main() {
    lis, err := net.Listen("tcp", ":9000")
    if (err != nil) {
        log.Fatalf("Failed to listen on port 9000: %v", err)
    }

    grpcServer := grpc.NewServer()

    server := &gameServer{
        bullets: make(map[string]*game.BulletState), // Inicializar el mapa de balas
        players: make(map[string]*game.PlayerState), // Inicializar el mapa de jugadores
        mapID:   0, // Inicializar el ID del mapa
    }
    game.RegisterGameServiceServer(grpcServer, server)

    log.Println("Game server is running on port 9000")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("Failed to serve gRPC server over port 9000: %v", err)
    }
}