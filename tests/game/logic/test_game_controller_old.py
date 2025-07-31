class TestGameController:
    def test_game_controller(self):
        # Setup
        config = DatabaseConfig()
        with psycopg2.connect(**config.dict()) as conn:
            all_card_data = load_cards(conn)
            all_energies = load_energies(conn)

            # Choose 20 valid Pokémon cards for each deck (must be stage "Basic")
            pokemon_cards = [Card(c) for c in all_card_data if c.supertype and c.supertype.name == "Pokemon" and c.stage == "Basic"]
            assert len(pokemon_cards) >= 40, "Need at least 40 Basic Pokémon cards for two players."

            deck1 = Deck(cards=random.sample(pokemon_cards, 20))
            deck2 = Deck(cards=random.sample(pokemon_cards, 20))

            log = GameLog()

            # Setup players
            ash = setup_player("Ash", deck1, all_energies, log)
            misty = setup_player("Misty", deck2, all_energies, log)

            # Create and start the game
            controller = GameController([ash, misty])
            controller.start_game()

            # Output log at the end
            print("\n--- GAME LOG ---")
            print(log)
