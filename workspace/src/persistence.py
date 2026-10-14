# src/core.py
"""Kern-Datenmodelle für die RPG- und Wirtschaftssimulation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import sys
import os

# Wir müssen vorsichtig sein mit Import-Zyklen. 
# Da quests.py von core.py abhängt (Item, Player), können wir hier nicht direkt Quest importieren.
# Stattdessen speichern wir in Player eine Liste von Objekten, die als "Quest" interpretiert werden können,
# oder wir verwenden eine schwache Referenz / Typ-Hinweis.
# Für die Persistenz ist es am einfachsten, wenn Player eine Liste von Quest-Objekten hält.
# Da wir core.py nicht stark an quests.py koppeln wollen (um Zyklen zu vermeiden),
# definieren wir hier nur das Attribut. Die konkrete Klasse wird in persistence.py gehandhabt.

@dataclass
class Item:
    name: str
    category: str  # z.B. "weapon", "potion", "material", "quest"
    base_value: int
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.base_value < 0:
            raise ValueError("base_value darf nicht negativ sein.")
        if self.quantity < 0:
            raise ValueError("quantity darf nicht negativ sein.")


@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    gold: int = 50
    inventory: Dict[str, Item] = field(default_factory=dict)
    # Neues Attribut für Quests
    quests: List[Any] = field(default_factory=list)  # List[Quest]

    def __post_init__(self) -> None:
        if self.hp > self.max_hp:
            self.hp = self.max_hp
        if self.hp < 0:
            self.hp = 0

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def heal(self, amount: int) -> None:
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def add_item(self, item: Item) -> None:
        if item.name in self.inventory:
            self.inventory[item.name].quantity += item.quantity
        else:
            self.inventory[item.name] = item

    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        if item_name in self.inventory:
            if self.inventory[item_name].quantity >= quantity:
                self.inventory[item_name].quantity -= quantity
                if self.inventory[item_name].quantity == 0:
                    del self.inventory[item_name]
                return True
        return False