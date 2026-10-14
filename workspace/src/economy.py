from dataclasses import dataclass, field
from typing import Dict

from src.core import Item, Player


@dataclass
class Merchant:
    """Ein Händler mit eigenem Inventar und Goldbestand.

    - ``buy_markup``: Faktor, mit dem der Händler den Basiswert eines Items
      reduziert, wenn er vom Spieler kauft (also der Preis, den der Spieler
      erhält). Standard: 0.5 (50% des Basiswerts).
    - ``sell_markup``: Faktor, mit dem der Händler den Basiswert erhöht,
      wenn er dem Spieler etwas verkauft. Standard: 1.5 (150% des Basiswerts).
    """
    gold: int = 100
    inventory: Dict[str, Item] = field(default_factory=dict)
    buy_markup: float = 0.5
    sell_markup: float = 1.5

    def _price(self, item: Item, for_player_buying: bool) -> int:
        """Berechnet den Preis eines Items.

        Wenn ``for_player_buying`` True ist, kauft der Spieler vom Händler
        (Verkaufspreis des Händlers). Ansonsten verkauft der Spieler dem
        Händler (Kaufpreis des Händlers).
        """
        factor = self.sell_markup if for_player_buying else self.buy_markup
        # Preis immer mindestens 1 Gold
        return max(1, int(item.base_value * factor))

    def buy_from_player(self, player: Player, item_name: str, quantity: int = 1) -> bool:
        """Der Händler kauft ein Item vom Spieler.

        - Prüft, ob der Spieler das Item in ausreichender Menge besitzt.
        - Berechnet den Gesamtpreis (Preis pro Stück * Menge).
        - Transferiert Gold vom Händler zum Spieler und das Item vom
          Spieler zum Händler.
        - Gibt ``True`` zurück, wenn die Transaktion erfolgreich war.
        """
        if quantity < 1:
            raise ValueError("Menge muss mindestens 1 sein.")
        if not player.has_item(item_name, min_quantity=quantity):
            return False
        item = player.inventory[item_name]
        total_price = self._price(item, for_player_buying=False) * quantity
        if self.gold < total_price:
            return False
        # Gold transfer
        self.gold -= total_price
        player.add_gold(total_price)
        # Item transfer
        player.remove_item(item_name, quantity)
        self.add_item(Item(name=item.name, category=item.category, base_value=item.base_value, quantity=quantity))
        return True

    def sell_to_player(self, player: Player, item_name: str, quantity: int = 1) -> bool:
        """Der Händler verkauft ein Item an den Spieler.

        - Prüft, ob der Händler das Item in ausreichender Menge besitzt.
        - Berechnet den Gesamtpreis (Preis pro Stück * Menge).
        - Transferiert Gold vom Spieler zum Händler und das Item vom
          Händler zum Spieler.
        - Gibt ``True`` zurück, wenn die Transaktion erfolgreich war.
        """
        if quantity < 1:
            raise ValueError("Menge muss mindestens 1 sein.")
        if item_name not in self.inventory:
            return False
        merchant_item = self.inventory[item_name]
        if merchant_item.quantity < quantity:
            return False
        total_price = self._price(merchant_item, for_player_buying=True) * quantity
        if not player.spend_gold(total_price):
            return False
        # Gold transfer
        self.gold += total_price
        # Item transfer
        self.remove_item(item_name, quantity)
        player.add_item(Item(name=merchant_item.name, category=merchant_item.category, base_value=merchant_item.base_value, quantity=quantity))
        return True

    # Helper methods mirroring Player's inventory handling for the merchant
    def add_item(self, item: Item) -> None:
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
