from game_class import Game

if __name__ == "__main__":
    game = Game()
    while game.running:
        game.current_menu.display_menu()
        game.game_loop()
