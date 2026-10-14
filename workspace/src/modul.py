"""src/multiplayer.py
Minimaler, deterministischer Mehrspieler‑Modus für das RPG‑Projekt.

Dieses Modul enthält:
* `MessageProtocol` – Serialisierung/Deserialisierung von JSON‑Nachrichten.
* `Lobby` – Verwaltung einer Spiel‑Lobby (Hinzufügen/Entfernen von Spielern).
* `ChatSession` – Einfaches Chat‑System innerhalb einer Lobby.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Die Kern‑Klassen des Spiels (Player, Item, …) liegen in src.core.
# Wir importieren nur das, was wir benötigen, um Zyklen zu vermeiden.
from src.core import Player


# --------------------------------------------------------------------------- #
# MessageProtocol
# --------------------------------------------------------------------------- #
class MessageProtocol:
    """Kodiert und dekodiert Nachrichten als JSON‑Strings (eine Zeile pro Nachricht).

    Die Implementierung ist vollständig deterministisch und damit leicht
    testbar.  Ein Zeilen‑Break wird beim Kodieren angehängt, damit ein
    Netzwerk‑Stream einfach zeilenweise gelesen werden kann.
    """

    def encode(self, data: Dict[str, Any]) -> str:
        """Serialisiert ``data`` nach JSON und hängt einen Zeilen‑Break an.

        Parameters
        ----------
        data: dict
            Das zu übertragende Payload.

        Returns
        -------
        str
            JSON‑String + ``"\\n"``.
        """
        return json.dumps(data) + "\n"

    def decode(self, data_str: str) -> Dict[str, Any]:
        """Deserialisiert einen zuvor mit :meth:`encode` erzeugten String.

        Whitespace (z. B. das abschließende ``\\n``) wird entfernt, bevor
        ``json.loads`` aufgerufen.

        Parameters
        ----------
        data_str: str
            Der empfangene JSON‑String.

        Returns
        -------
        dict
            Das ursprüngliche Payload.
        """
        return json.loads(data_str.strip())


# --------------------------------------------------------------------------- #
# Lobby
# --------------------------------------------------------------------------- #
@dataclass
class Lobby:
    """Verwaltet eine Gruppe von Spielern.

    Attributes
    ----------
    name: str
        Anzeigename der Lobby.
    players: List[Player]
        Aktuell verbundene Spieler.  Intern als Liste, weil die Reihenfolge
        für die Tests nicht relevant ist, aber ein ``list`` lässt sich leicht
        serialisieren, falls das später nötig wird.
    """

    name: str
    players: List[Player] = field(default_factory=list)

    # ------------------------------------------------------------------- #
    # Spieler‑Management
    # ------------------------------------------------------------------- #
    def add_player(self, player: Player) -> None:
        """Fügt ``player`` zur Lobby hinzu, falls er noch nicht enthalten ist."""
        if player not in self.players:
            self.players.append(player)

    def remove_player(self, player: Player) -> None:
        """Entfernt ``player`` aus der Lobby, falls er vorhanden ist."""
        if player in self.players:
            self.players.remove(player)

    # ------------------------------------------------------------------- #
    # Hilfsfunktion – Broadcast (wird von den Tests nicht direkt genutzt,
    #                     ist aber nützlich für ein späteres Netzwerk‑Design)
    # ------------------------------------------------------------------- #
    def broadcast(self, message: Dict[str, Any], protocol: MessageProtocol) -> List[str]:
        """Serialisiert ``message`` und gibt die kodierten Strings für alle Spieler zurück."""
        encoded = protocol.encode(message)
        return [encoded for _ in self.players]


# --------------------------------------------------------------------------- #
# ChatSession
# --------------------------------------------------------------------------- #
class ChatSession:
    """Ein einfacher Chat‑Dienst innerhalb einer Lobby.

    Der Chat speichert jede gesendete Nachricht in ``self.history``.
    Jede Nachricht ist ein Dictionary mit den Schlüsseln ``type``, ``sender``
    und ``message`` – exakt das Format, das :class:`MessageProtocol` erwartet.
    """

    def __init__(self, lobby: Lobby):
        self.lobby: Lobby = lobby
        self.history: List[Dict[str, Any]] = []

    def send_message(self, sender: Player, content: str) -> Dict[str, Any]:
        """Erzeugt eine Chat‑Nachricht und fügt sie dem Verlauf hinzu.

        Parameters
        ----------
        sender: Player
            Der Spieler, der die Nachricht sendet.
        content: str
            Der eigentliche Text.

        Returns
        -------
        dict
            Das erzeugte Nachrichten‑Objekt.
        """
        msg = {"type": "chat", "sender": sender.name, "message": content}
        self.history.append(msg)
        return msg

    def get_history(self) -> List[Dict[str, Any]]:
        """Gibt eine Kopie des bisherigen Chat‑Verlaufs zurück."""
        return list(self.history)


# Export für ``from src.multiplayer import *``
__all__ = ["MessageProtocol", "Lobby", "ChatSession"]