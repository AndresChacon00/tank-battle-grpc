package main

import (
	"context"
	"log"
	"net"
	"sync"
	"tank-battle-grpc/game"
	"time"

	"google.golang.org/grpc"
)

type gameServer struct {
	game.UnimplementedGameServiceServer
	mu sync.Mutex
	players map[string]*game.PlayerState
}

func (s *gameServer) UpdateState(ctx context.Context, state *game.PlayerState) (*game.GameState, error) {
	s.mu.Lock()
	s.players[state.PlayerId] = state
	s.mu.Unlock()

	// Construir el estado del juego
	gameState := &game.GameState{}
	s.mu.Lock()
	for _, player := range s.players {
		gameState.Players = append(gameState.Players, player)
	}
	s.mu.Unlock()

	return gameState, nil

}

func (s *gameServer) PerformAction(ctx context.Context, action *game.ActionRequest) (*game.ActionResponse, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    _, exists := s.players[action.PlayerId]
    if !exists {
        return &game.ActionResponse{
            Success: false,
            Message: "Player not found",
        }, nil
    }

    // Aquí puedes implementar la lógica para manejar la acción (ejemplo: disparar)
    log.Printf("Player %s performed action %s targeting (%f, %f)", action.PlayerId, action.ActionType, action.TargetX, action.TargetY)

    return &game.ActionResponse{
        Success: true,
        Message: "Action performed successfully",
    }, nil
}

func (s *gameServer) StreamGameState(empty *game.Empty, stream game.GameService_StreamGameStateServer) error {
    for {
        s.mu.Lock()
        gameState := &game.GameState{}
        for _, player := range s.players {
            gameState.Players = append(gameState.Players, player)
        }
        s.mu.Unlock()

        if err := stream.Send(gameState); err != nil {
            return err
        }

        time.Sleep(1 * time.Second) // Enviar actualizaciones cada segundo
    }
}

func main() {
	lis, err := net.Listen("tcp", ":9000")
	if err != nil {
		log.Fatal("Failed to listen on port 9000: %v",err)
	}

	grpcServer := grpc.NewServer()

	server := &gameServer{players: make(map[string]*game.PlayerState)}
	game.RegisterGameServiceServer(grpcServer, server)

	log.Println("Game server is running on port 9000")
	if err := grpcServer.Serve(lis); err != nil {
		log.Fatal("Failed to serve gRPC server over port 9000: %v", err)
	}
}