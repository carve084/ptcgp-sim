from dataclasses import dataclass


@dataclass
class Energy:
    id: int
    name: str
    code: str

    def __str__(self) -> str:
        return f"{self.name}"
