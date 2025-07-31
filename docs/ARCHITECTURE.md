## Layered Architecture Diagram
```
+---------------------------------------------------------------------+
|    Presentation Layer (Future: UI, AI Controller)                   |
|       - Handles user input or AI decisions.                         |
|       - Renders the game state.                                     |
|       - Communicates intentions (e.g., "Attack with this card")     |
|         to the Game Logic Layer.                                    |
+---------------------------------------------------------------------+
        ^                                                             |
        | (Calls/Sends Events to)                                     | (Receives Game State)
        v                                                             |
+---------------------------------------------------------------------+
|    Game Logic / State Layer (Your "Game-state classes")             |
|       - GameController: The central mediator. Orchestrates game flow. |
|       - RuleEngine: The "referee". Evaluates game state against rules.|
|       - GameEvent: Data objects representing actions (e.g., AttackEvent).|
|       - GameLog: Records what happens.                             |
|       - BattleLogic, Effects, SpecialActions, WinConditions         |
+---------------------------------------------------------------------+
        ^                                                             |
        | (Manipulates)                                               | (Reads from)
        v                                                             |
+---------------------------------------------------------------------+
|    Game Object / Domain Layer (Your "Game-related classes")         |
|       - Player: Manages hand, bench, deck, graveyard.               |
|       - Deck, Card, EnergyZone: Core components of the game.        |
|       - These are the "nouns" of your game.                         |
+---------------------------------------------------------------------+
        ^                                                             |
        | (Populated by)                                              |
        v                                                             |
+---------------------------------------------------------------------+
|    Data Access / Infrastructure Layer                               |
|       - Models: Python classes that mirror DB tables (e.g., CardModel).|
|       - Loaders: Functions that query the DB and create             |
|         Game Objects (e.g., `load_card_from_db("Dragon")`).         |
|       - Your `setup_player`, `test_data_loading` live here.         |
+---------------------------------------------------------------------+
        ^
        | (Reads/Writes)
        v
+---------------------------------------------------------------------+
|    Data Source Layer                                                |
|       - PostgreSQL Database                                         |
|       - (Could also be JSON files, etc.)                            |
+---------------------------------------------------------------------+
```