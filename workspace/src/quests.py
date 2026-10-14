from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from src.core import Item, Player


@dataclass
class Quest:
    """Ein Quest‑Objekt mit Zielen, Fortschritt und Belohnungen.

    Attributes
    ----------
    id: str
        Eindeutige Kennung des Quests.
    name: str
        Anzeigename.
    description: str
        Kurzbeschreibung für den Spieler.
    objectives: Dict[str, int]
        Mapping von Ziel‑Item‑Namen zu benötigter Menge.
    reward_gold: int = 0
        Gold, das nach Abschluss verliehen wird.
    reward_items: List[Item] = field(default_factory=list)
        Liste von Items, die als Belohnung vergeben werden.
    """

    id: str
    name: str
    description: str
    objectives: Dict[str, int]
    reward_gold: int = 0
    reward_items: List[Item] = field(default_factory=list)
    progress: Dict[str, int] = field(default_factory=dict)
    completed: bool = False

    def __post_init__(self) -> None:
        # Initialise progress counters for each objective
        for obj in self.objectives:
            self.progress.setdefault(obj, 0)

    def is_completed(self) -> bool:
        """Return True if all objectives have reached their required amount."""
        if self.completed:
            return True
        for name, required in self.objectives.items():
            if self.progress.get(name, 0) < required:
                return False
        self.completed = True
        return True

    def add_progress(self, objective_name: str, amount: int = 1) -> None:
        """Increase progress for a given objective.

        Raises
        ------
        KeyError
            If the objective is not part of the quest.
        ValueError
            If ``amount`` is not positive.
        """
        if amount < 1:
            raise ValueError("Progress amount must be positive.")
        if objective_name not in self.objectives:
            raise KeyError(f"Objective '{objective_name}' not defined for quest '{self.id}'.")
        self.progress[objective_name] = self.progress.get(objective_name, 0) + amount
        # Cap at required amount to avoid overflow
        required = self.objectives[objective_name]
        if self.progress[objective_name] > required:
            self.progress[objective_name] = required


# ---------------------------------------------------------------------------
# Helper functions operating on a Player instance
# ---------------------------------------------------------------------------

def assign_quest(player: Player, quest: Quest) -> None:
    """Add a quest to the player's active quest log.

    The player object is extended with two new attributes if they do not yet exist:
    ``quest_log`` (active quests) and ``completed_quests`` (finished quests).
    """
    if not hasattr(player, "quest_log"):
        player.quest_log = {}  # type: ignore[attr-defined]
    if not hasattr(player, "completed_quests"):
        player.completed_quests = {}  # type: ignore[attr-defined]
    player.quest_log[quest.id] = quest  # type: ignore[attr-defined]


def progress_quest(player: Player, quest_id: str, objective_name: str, amount: int = 1) -> bool:
    """Increase the progress of a specific quest objective.

    Returns ``True`` if the quest and objective exist and progress was updated,
    otherwise ``False``.
    """
    if not hasattr(player, "quest_log"):
        return False
    quest: Quest | None = player.quest_log.get(quest_id)  # type: ignore[attr-defined]
    if quest is None or quest.completed:
        return False
    try:
        quest.add_progress(objective_name, amount)
    except (KeyError, ValueError):
        return False
    return True


def complete_quest(player: Player, quest_id: str) -> bool:
    """Finalize a quest, grant rewards and move it to the completed list.

    Returns ``True`` if the quest was successfully completed, ``False`` otherwise.
    """
    if not hasattr(player, "quest_log"):
        return False
    quest: Quest | None = player.quest_log.get(quest_id)  # type: ignore[attr-defined]
    if quest is None:
        return False
    if not quest.is_completed():
        return False
    # Grant rewards
    if quest.reward_gold:
        player.add_gold(quest.reward_gold)
    for item in quest.reward_items:
        player.add_item(item)
    # Move quest to completed list
    if not hasattr(player, "completed_quests"):
        player.completed_quests = {}  # type: ignore[attr-defined]
    player.completed_quests[quest.id] = quest  # type: ignore[attr-defined]
    del player.quest_log[quest.id]  # type: ignore[attr-defined]
    return True


def get_active_quests(player: Player) -> List[Quest]:
    """Return a list of currently active (not yet completed) quests for the player."""
    if not hasattr(player, "quest_log"):
        return []
    return list(player.quest_log.values())  # type: ignore[attr-defined]


def get_completed_quests(player: Player) -> List[Quest]:
    """Return a list of quests the player has finished."""
    if not hasattr(player, "completed_quests"):
        return []
    return list(player.completed_quests.values())  # type: ignore[attr-defined]
