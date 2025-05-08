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

func (s *gameServer) GetGameState(ctx context.Context, empty *game.Empty) (*game.GameState, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	// Construir el estado del juego
	gameState := &game.GameState{}
	for _, player := range s.players {
		gameState.Players = append(gameState.Players, player)
	}

	return gameState, nil
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