# ✅ MILESTONES.md

This document outlines the project roadmap for building a custom Pokémon-style card game engine, including conceptual layers, completed and upcoming milestones, and the long-term stretch goal of integrating a machine learning agent.

---

## ⚙️ Conceptual Layers

| Layer                    | Description                                                                                 |
|--------------------------|---------------------------------------------------------------------------------------------|
| **1. Data Layer**        | Direct mapping of database tables to Python dataclasses (e.g. `Card`, `Attack`, `Ability`). |
| **2. Domain Models**     | Game objects like `Player`, `Deck`, `Hand`, and `EnergyZone`.                               |
| **3. Game Logic**        | Core turn flow, game controller, player actions, and win conditions.                        |
| **4. Game State Engine** | Future layer to manage full game state, including stack resolution and timing windows.      |
| **5. UI/CLI**            | Optional layer for human testing and debugging. No web or GUI needed.                       |
| **6. AI/ML Agents**      | Machine learning agents that can simulate and play the game using the engine.               |

---

## ✅ Completed Milestones

### ✅ Milestone 1: Database and Loader Setup
- ✅ Define schema: energy, rarity, rules, supertypes, subtypes, cards, sets, boosters.
- ✅ Implement dataclass models with loader functions for all tables.
- ✅ Modularize loader structure.
- ✅ Verify data loading through test suite.

### ✅ Milestone 2: Basic Player Setup
- ✅ Create `Deck`, `Player`, `EnergyZone` models.
- ✅ Implement player setup including:
  - Drawing cards
  - Choosing an active Pokémon
  - Placing Basic Pokémon on the bench
- ✅ Enforce Basic Pokémon requirements in deck and opening hand.

### ✅ Milestone 3: Core Turn Flow
- ✅ Create `GameController` with `play_turn`, `start_game`, and winner detection.
- ✅ Implement basic attach/attack/draw logic.
- ✅ Add `GameLog` to trace all game activity and help with test/debug visibility.

---

## 🔧 Upcoming Milestones

### 🛠️ Milestone 4: Rule and Effect Engine
> *Implement handling for card rules, effects, and abilities.*

- Add support for passive and triggered abilities.
- Add `Effect` objects or DSL system for describing in-game effects.
- Implement rule parsing and runtime enforcement for Trainer cards.
- Handle timing (e.g., "when played", "while active", "once per turn").

### 🛠️ Milestone 5: Battle Logic
> *Damage resolution, weakness/resistance, knockout handling, and points.*

- Implement `apply_damage` with weakness/resistance.
- Add knockout logic and automatic promotion/discard.
- Enforce retreat cost and energy discard on retreat.
- Track and increment points when knockouts occur.

### 🛠️ Milestone 6: Special Actions
> *Retreat, evolve, and rule-limited plays (Supporter, Tool).*

- One Supporter per turn enforcement.
- Attach only one Tool per Pokémon.
- Add evolve action and valid evolution chains.
- Add manual retreat logic and card swapping.

### 🛠️ Milestone 7: Win Conditions
> *Implement all game-ending logic.*

- 3 points = win.
- No Basic Pokémon = loss.
- Empty deck with required draw = loss.
- Optional: timer or turn limit enforcement.

---

## 🌟 Stretch Goal: Machine Learning Agent

> *Train and deploy machine learning agents to play the game.*

- Implement a serializable `GameState` class for agents to consume.
- Add replay recording and state export.
- Train a basic rule-based agent, followed by reinforcement learning agents (e.g. Q-learning, PPO).
- Evaluate performance against scripted opponents and humans.

---

## 📌 Tips for Contributing

- Use `GameLog` for all actions that change state.
- Keep model logic and game logic separate.
- Add a test case for every major rule.
- When unsure, log game state after each action — even in tests.

