from __future__ import annotations
from typing import TYPE_CHECKING
from datetime import datetime
import abc

if TYPE_CHECKING:
    from ptcgp_sim.game.logic.events import GameEvent


class BaseLogEntry(abc.ABC):
    """Abstract base class for any item that can be logged."""
    def __init__(self):
        self.timestamp = datetime.now()

    @abc.abstractmethod
    def get_display_message(self) -> str:
        """Returns the formatted string for this log entry."""
        pass

    def __lt__(self, other):
        """Allows sorting by timestamp."""
        return self.timestamp < other.timestamp


class TextEntry(BaseLogEntry):
    """An entry that represents a simple text message."""
    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def get_display_message(self) -> str:
        return self.message


class EventEntry(BaseLogEntry):
    """An entry that represents a game event."""
    def __init__(self, event: GameEvent):
        super().__init__()
        self.event = event

    def get_display_message(self) -> str:
        return str(self.event)  # Relies on the event's __repr__


class GameLog:
    """
    Records a chronological history of events that have occurred in a game.
    Also allows for simple text entries to be logged.
    """
    def __init__(self):
        self.entries: list[BaseLogEntry] = []

    def log_message(self, message: str):
        """Adds a simple text message to the log."""
        entry = TextEntry(message=message)
        self.entries.append(entry)

    def log_event(self, event: GameEvent):
        """Wraps a GameEvent and adds it to the log."""
        entry = EventEntry(event)
        self.entries.append(entry)

    def display(self):
        """Prints the log entries in chronological order."""
        print("\n--- Game Log ---")
        # The list is already chronological.
        # If there is any doubt, we can do sorted(self.entries)
        for i, entry in enumerate(self.entries):
            timestamp = entry.timestamp.strftime('%H:%M:%S')
            message = entry.get_display_message()
            print(f"{i + 1}: [{timestamp}] {message}")
        print("\n----------------\n")

    def __str__(self):
        return "\n".join(f"[{e.timestamp.strftime('%H:%M:%S')}] {e.get_display_message()}" for e in self.entries)
