import uuid
from dataclasses import dataclass, field

from ptcgp_sim.models.card import CardData
from ptcgp_sim.models.energy import Energy


@dataclass
class Card:
    """
    Represents a single, unique instance of a card.
    """
    card_data: CardData
    instance_id: uuid.UUID = field(default_factory=uuid.uuid4)

    # Game state attributes
    max_hp: int | None = field(init=False)
    current_hp: int | None = field(init=False)
    attached_energy: list[Energy] = field(default_factory=list)
    attached_cards: list['Card'] = field(default_factory=list)  # Base evolution cards, Tools, etc.

    # Publisher-Subscriber patterns
    _death_subscribers: list = field(default_factory=list)

    def __post_init__(self):
        self.max_hp = self.card_data.hp
        self.current_hp = self.card_data.hp

    # --- Property Forwarding ---
    @property
    def id(self) -> int:
        return self.card_data.id

    @property
    def name(self) -> str:
        return self.card_data.name

    @property
    def supertype(self):
        return self.card_data.supertype

    @property
    def energy_type(self):
        return self.card_data.energy_type

    @property
    def evolve_from(self):
        return self.card_data.evolve_from

    @property
    def text(self) -> str:
        return self.card_data.text

    @property
    def stage(self) -> str:
        return self.card_data.stage

    @property
    def weakness(self):
        return self.card_data.weakness

    @property
    def retreat_cost(self):
        return self.card_data.retreat_cost

    @property
    def subtype(self):
        return self.card_data.subtype

    @property
    def rule(self):
        return self.card_data.rule

    @property
    def abilities(self):
        return self.card_data.abilities

    @property
    def attacks(self):
        return self.card_data.attacks

    def __str__(self):
        lines = [
            "",
            f"({self.stage}) {self.name} - HP: {self.current_hp}/{self.max_hp} ({self.energy_type})",
            f"Attached Energy: [{', '.join(e.code for e in self.attached_energy) if self.attached_energy else ''}]"
        ]

        if self.abilities:
            lines.append(f"Ability: {self.abilities[0]}")

        if self.attacks:
            lines.append("ATK:")
            for attack in self.attacks:
                lines.append(str(attack))

        lines.append(f"Weakness: {self.weakness if self.weakness else ''}  |  Retreat: "
                     + f"{self.retreat_cost if self.retreat_cost else ''}")
        return "\n        ".join(lines)

    def subscribe_to_death(self, callback):
        """
        Subscribe a callback to be called when the card is defeated.
        The callback should accept one argument: the defeated card.
        """
        self._death_subscribers.append(callback)

    def unsubscribe_from_death(self, callback):
        """
        Unsubscribe a callback from the death event.
        """
        if callback in self._death_subscribers:
            self._death_subscribers.remove(callback)

    def _invoke_death_event(self):
        """
        Invoke all subscribed callbacks when the card is defeated.
        """
        for callback in self._death_subscribers:
            callback(self)

    def take_damage(self, amount: int):
        """
        Apply damage to the card. If the card's HP drops to 0 or below, invoke death event.
        """
        self.current_hp = max(0, self.current_hp - amount)
        print(f"[CARD] {self.name} takes {amount} damage. Max HP: {self.max_hp}. Current HP: {self.current_hp}")
        if not self.is_alive():
            self._invoke_death_event()

    def is_alive(self):
        return self.current_hp > 0

    def get_available_attacks(self):
        available_attacks = []
        for attack in self.attacks:
            colorless_count = 0
            attack_costs = attack.costs
            attached_energy = self.attached_energy

            for energy in attack_costs:
                if energy in attached_energy:
                    attached_energy.remove(energy)
                elif energy == "Colorless":
                    colorless_count = colorless_count + 1
                else:
                    # Attack requires energy that the card does not have
                    break

            if colorless_count <= len(attached_energy):
                available_attacks.append(attack)

        return available_attacks

    def attach_energy(self, energy_type):
        self.attached_energy.append(energy_type)
