from dataclasses import dataclass


@dataclass
class Rule:
    id: int = 0
    name: str = "Unknown Rule"
    description: str = "No rule description provided"
