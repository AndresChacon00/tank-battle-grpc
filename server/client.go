package main

import (
	"log"
	"time"

	"golang.org/x/net/context"
	"google.golang.org/grpc"

	game "tank-battle-grpc/game"
)

func main() {
	
	conn, err := grpc.Dial(":9000", grpc.WithInsecure())
	if err != nil {
		log.Fatal("Could not connect: %s", err)
	}
	defer conn.Close()

	client := game.NewGameServiceClient(conn)

	for{
		//Enviar el estado del jugador
		playerState := &game.PlayerState{
			PlayerId: "player1",
			X: 10.0,
			Y: 20.0,
		}

		gameState, err := client.UpdateState(context.Background(), playerState)
		if err != nil {
			log.Fatal("Error calling UpdateState: %v", err)
		}

		log.Println("Game State:")
		for _, player := range gameState.Players {
			log.Printf("Player %s is at (%f, %f)", player.PlayerId, player.X, player.Y)
		}

		time.Sleep(1 * time.Second)
	}
}