# src/core.py
"""Kern-Datenmodelle für die RPG- und Wirtschaftssimulation."""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import sys
import os

# Wir müssen vorsichtig sein mit Import-Zyklen. 
# Da quests.py von core.py abhängt (Item, Player), können wir hier nicht direkt Quest importieren.
# Stattdessen speichern wir in Player eine Liste von Objekten, die als "Quest" interpretiert werden können,
# oder wir nutzen eine schwache Referenz / Lazy Loading in der Persistenz.
# Für die Persistenz ist es am einfachsten, wenn Player eine Liste von Dicts oder Dataclasses speichert,
# die in persistence.py konvertiert werden.

# Um die Abhängigkeit zu lösen, definieren wir hier eine minimale Struktur oder nutzen Any.
# Besser: Player speichert Quests als Liste von Objekten, die ein `to_dict()` und `from_dict()` haben.
# Da Quest in quests.py ist, und core.py nicht von quests.py importieren darf (Zyklus),
# speichern wir in Player eine Liste von "QuestState"-Objekten oder einfach Dicts?
# Nein, die Anforderung sagt: "Bestehende Klassen in src/core.py dürfen um neue Attribute/Methoden erweitert werden".
# Wenn Player bereits Quests speichert, ist es gut. Wenn nicht, fügen wir es hinzu.
# Da Quest eine Dataclass ist, können wir sie in Player speichern, wenn wir den Import vermeiden.
# Trick: Wir importieren Quest nicht in core.py, sondern Player hat ein Attribut `quests` vom Typ List[Any].
# In persistence.py casten wir dann.

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

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "base_value": self.base_value,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        return cls(
            name=data["name"],
            category=data["category"],
            base_value=data["base_value"],
            quantity=data.get("quantity", 1)
        )


@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    gold: int = 50
    inventory: Dict[str, Item] = field(default_factory=dict)
    # Neues Attribut für Quests. Typ ist Any, um Import-Zyklus zu vermeiden.
    # In der Praxis sollte dies eine Liste von Quest-Objekten sein.
    quests: List[Any] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.hp < 0:
            self.hp = 0
        if self.max_hp < 0:
            self.max_hp = 0
        if self.gold < 0:
            self.gold = 0

    @property
    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> None:
        self.hp = max(0, self.hp - amount)

    def heal(self, amount: int) -> None:
        self.hp = min(self.max_hp, self.hp + amount)

    def add_item(self, item: Item) -> None:
        if item.name in self.inventory:
            self.inventory[item.name].quantity += item.quantity
        else:
            self.inventory[item.name] = item

    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        if item_name in self.inventory:
            item = self.inventory[item_name]
            if item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity == 0:
                    del self.inventory[item_name]
                return True
        return False

    def get_item(self, item_name: str) -> Optional[Item]:
        return self.inventory.get(item_name)

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert den Spieler zu einem Dictionary.
        
        Hinweis: Quests werden hier als Liste von Dicts serialisiert,
        falls sie ein to_dict() haben, sonst als repr.
        In der Persistenz-Logik wird dies genauer behandelt.
        """
        inventory_dict = {name: item.to_dict() for name, item in self.inventory.items()}
        
        # Quests serialisieren: Wenn Quest-Objekte sind, nutzen wir to_dict, sonst repr
        quests_data = []
        for q in self.quests:
            if hasattr(q, 'to_dict'):
                quests_data.append(q.to_dict())
            else:
                quests_data.append(str(q)) # Fallback

        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "gold": self.gold,
            "inventory": inventory_dict,
            "quests": quests_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Erstellt einen Player aus einem Dictionary.
        
        Hinweis: Quests werden hier als Platzhalter (Dicts) geladen.
        Die eigentliche Rekonstruktion der Quest-Objekte erfolgt in persistence.py,
        da dort der Import von Quest möglich ist.
        """
        inventory = {}
        for name, item_data in data.get("inventory", {}).items():
            inventory[name] = Item.from_dict(item_data)
        
        # Quests werden vorerst als Liste von Dicts gespeichert, 
        # die in load_player_from_json in Quest-Objekte konvertiert werden.
        quests_data = data.get("quests", [])
        
        player = cls(
            name=data["name"],
            hp=data.get("hp", 100),
            max_hp=data.get("max_hp", 100),
            gold=data.get("gold", 50),
            inventory=inventory,
            quests=quests_data # Vorläufige Speicherung als Dicts
        )
        return player