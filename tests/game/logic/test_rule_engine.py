import pytest
from ptcgp_sim.game.logic import RuleEngine, GameState, GameEvent, Effect
from ptcgp_sim.game.logic.rules import Rule

# --- Mock/Dummy Classes for Testing ---
class MockEffect(Effect):
    def apply(self, game_state): pass

class AlwaysTrueRule(Rule):
    """A mock rule that always triggers."""
    def condition(self, event, game_state) -> bool:
        return True
    def action(self, event, game_state):
        return [MockEffect()]

class NeverTrueRule(Rule):
    """A mock rule that never triggers."""
    def condition(self, event, game_state) -> bool:
        return False
    def action(self, event, game_state):
        return [MockEffect()]

# --- Tests ---
def test_rule_engine_no_rules_triggered():
    """Tests that no effects are returned if no rule conditions are met."""
    # Arrange
    engine = RuleEngine()
    engine.rules = [NeverTrueRule()]
    game_state = GameState([]) # Dummy game state
    event = GameEvent()

    # Act
    effects = engine.process_event(event, game_state)

    # Assert
    assert len(effects) == 0

def test_rule_engine_one_rule_triggered():
    """Tests that a single matching rule returns its effects."""
    # Arrange
    engine = RuleEngine()
    engine.rules = [NeverTrueRule(), AlwaysTrueRule()]
    game_state = GameState([])
    event = GameEvent()

    # Act
    effects = engine.process_event(event, game_state)

    # Assert
    assert len(effects) == 1
    assert isinstance(effects[0], MockEffect)

def test_rule_engine_multiple_rules_triggered():
    """Tests that effects from multiple matching rules are aggregated."""
    # Arrange
    engine = RuleEngine()
    engine.rules = [AlwaysTrueRule(), NeverTrueRule(), AlwaysTrueRule()]
    game_state = GameState([])
    event = GameEvent()

    # Act
    effects = engine.process_event(event, game_state)

    # Assert
    assert len(effects) == 2