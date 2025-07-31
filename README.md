# Pokemon TCG Pocket Sim

This is a Pokémon TCG Pocket Python implementation.

## Goals
1. Simulate a Pokémon TCG Pocket game, including cards, decks, and players
2. Run an AI that can create decks and play the simulator
3. Get feedback from the AI that will hopefully help us determine good strategies

## Usage
1. Build the tables using `build_tables.py`
2. Get the sets from tcgdex API using `get_sets.py`:
   - [TCGdex](https://tcgdex.dev)
   - This will create a `sets.json` file in the `resources/tcgdex` directory.
3. Build the sets into the database using `build_sets.py`
4. Get the cards from APIs using get_cards for each:
   - [TCGdex](https://tcgdex.dev)
   - [Limitlesstcg](https://pocket.limitlesstcg.com)
   - [PTCGPocket](https://ptcgpocket.gg/)
5. Merge the cards using `merge_cards.py`
6. Build the cards using `build_cards.py`
7. TBD

### Models

    Ability
    Attack
    Card
    Energy
    Rule
    Subtype
    Supertype

### Game Logic

    Collection (Not implemented yet)
    Deck
    EnergyZone
    Game
    Player

### Properties Per Class

#### Card

- `id`: Unique identifier for the card
- `name`: The name of the card
- `supertype`: The supertype of the card (e.g., Pokémon, Trainer)

- `abilities`: A list of abilities associated with the card
- `attacks`: A list of attacks associated with the card
- `code`: The code of the card (setId-localId, e.g., A1-001)
- `setId`: The set identifier of the card (e.g., A1, A1a, A2, A2a, A2b)
- `subtype`: The subtype of the card (e.g., Ultra Beast, Supporter, Fossil)
