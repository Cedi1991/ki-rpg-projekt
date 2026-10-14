"""src/multiplayer.py
Minimaler, deterministischer Mehrspieler-Modus für das RPG-Projekt.

Dieses Modul stellt eine sehr einfache TCP-basierte Server-Client-Architektur bereit,
die ausschließlich JSON-Nachrichten (eine Zeile pro Nachricht) austauscht. Es enthält
keine zufällige Logik, ist vollständig testbar und kann in Unit-Tests durch
Mock-Sockets oder das `socketserver`-Modul simuliert werden.

Die wichtigsten Klassen/Funktionen:
- :class:`MessageProtocol` – Hilfsklasse zum Senden/Empfangen von Nachrichten.
- :class:`Lobby` – Verwaltung von Spielern in einer Lobby.
- :class:`ChatSession` – Verwaltung von Chat-Nachrichten.
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MessageProtocol:
    """Hilfsklasse zum Senden/Empfangen von Nachrichten."""

    def encode(self, data: dict) -> str:
        """Kodiert ein Dictionary als JSON-String."""
        return json.dumps(data)

    def decode(self, data: str) -> dict:
        """Dekodiert einen JSON-String zu einem Dictionary."""
        return json.loads(data)


@dataclass
class Lobby:
    """Verwaltung von Spielern in einer Lobby.

    Attributes
    ----------
    name: str
        Name der Lobby.
    players: Dict[str, dict]
        Mapping von Spielernamen zu Spielerdaten.
    """

    name: str
    players: Dict[str, dict] = field(default_factory=dict)

    def add_player(self, player_name: str, player_data: dict) -> None:
        """Fügt einen Spieler zur Lobby hinzu."""
        self.players[player_name] = player_data

    def remove_player(self, player_name: str) -> None:
        """Entfernt einen Spieler aus der Lobby."""
        if player_name in self.players:
            del self.players[player_name]

    def get_player(self, player_name: str) -> Optional[dict]:
        """Ruft die Daten eines Spielers ab."""
        return self.players.get(player_name)

    def list_players(self) -> List[str]:
        """Listet alle Spieler in der Lobby auf."""
        return list(self.players.keys())


@dataclass
class ChatSession:
    """Verwaltung von Chat-Nachrichten.

    Attributes
    ----------
    messages: List[dict]
        Liste aller Chat-Nachrichten.
    """

    messages: List[dict] = field(default_factory=list)

    def send_message(self, sender: str, message: str) -> None:
        """Sendet eine Chat-Nachricht."""
        self.messages.append({"sender": sender, "message": message})

    def get_messages(self) -> List[dict]:
        """Ruft alle Chat-Nachrichten ab."""
        return self.messages

    def clear_messages(self) -> None:
        """Löscht alle Chat-Nachrichten."""
        self.messages.clear()
