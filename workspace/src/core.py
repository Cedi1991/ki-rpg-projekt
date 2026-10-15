"""Kern-Datenmodelle für die RPG- und Wirtschaftssimulation."""

from dataclasses import dataclass, field


@dataclass
class Item:
    name: str
    category: str  # z.B. "weapon", "potion", "material", "quest"
    base_value: int
    quantity: int = 1

    def __post_init__(self) -> None:
        if self.base_value < 0:
            raise ValueError("base_value darf nicht negativ sein.")
        if self.quantity < 1:
            raise ValueError("quantity muss mindestens 1 sein.")


@dataclass
class Player:
    name: str
    hp: int = 100
    max_hp: int = 100
    gold: int = 50
    inventory: dict[str, Item] = field(default_factory=dict)

    @property
    def is_alive(self) -> bool:
        """Prüft, ob der Spieler noch Lebenspunkte hat."""
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        """Fügt dem Spieler Schaden zu (HP fallen nicht unter 0)."""
        if amount < 0:
            raise ValueError("Schaden darf nicht negativ sein.")
        self.hp = max(0, self.hp - amount)
        return self.hp

    def heal(self, amount: int) -> int:
        """Heilt den Spieler bis maximal max_hp (nur wenn er lebt)."""
        if amount < 0:
            raise ValueError("Heilung darf nicht negativ sein.")
        if not self.is_alive:
            return 0
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp

    def add_gold(self, amount: int) -> int:
        """Fügt Gold hinzu."""
        if amount < 0:
            raise ValueError("Betrag muss positiv sein.")
        self.gold += amount
        return self.gold

    def spend_gold(self, amount: int) -> bool:
        """Gibt Gold aus, falls genug vorhanden ist. Gibt True bei Erfolg zurück."""
        if amount < 0:
            raise ValueError("Betrag muss positiv sein.")
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def add_item(self, item: Item) -> None:
        """Fügt ein Item zum Inventar hinzu oder erhöht die Anzahl bei gleichem Namen."""
        if item.name in self.inventory:
            existing = self.inventory[item.name]
            existing.quantity += item.quantity
        else:
            self.inventory[item.name] = Item(
                name=item.name,
                category=item.category,
                base_value=item.base_value,
                quantity=item.quantity,
            )

    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """Entfernt eine bestimmte Menge eines Items aus dem Inventar."""
        if quantity < 1:
            raise ValueError("Menge muss mindestens 1 sein.")
        if item_name not in self.inventory:
            return False

        existing = self.inventory[item_name]
        if existing.quantity < quantity:
            return False

        existing.quantity -= quantity
        if existing.quantity == 0:
            del self.inventory[item_name]
        return True

    def has_item(self, item_name: str, min_quantity: int = 1) -> bool:
        """Prüft, ob der Spieler mindestens `min_quantity` Exemplare eines Items besitzt."""
        item = self.inventory.get(item_name)
        return item is not None and item.quantity >= min_quantity

    def net_worth(self) -> int:
        """Berechnet das Gesamtvermögen (Gold + Basiswert aller Inventar-Items)."""
        inventory_value = sum(
            item.base_value * item.quantity for item in self.inventory.values()
        )
        return self.gold + inventory_value
