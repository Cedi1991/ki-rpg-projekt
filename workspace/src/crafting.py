from dataclasses import dataclass
from typing import Dict

from src.core import Item, Player


@dataclass(frozen=True)
class Recipe:
    """Ein Rezept zum Herstellen eines neuen Items.

    Attributes
    ----------
    name: str
        Name des herzustellenden Gegenstands (für Lesbarkeit, wird nicht
        programmgesteuert verwendet).
    ingredients: Dict[str, int]
        Mapping von Item-Namen zu benötigter Menge im Inventar des Spielers.
    result: Item
        Das Item, das nach erfolgreichem Craften dem Spieler hinzugefügt
        wird. ``quantity`` gibt an, wie viele Stück des Resultats entstehen.
    """

    name: str
    ingredients: Dict[str, int]
    result: Item


def craft_item(player: Player, recipe: Recipe) -> bool:
    """Versucht, das gegebene Rezept mit dem Inventar des Spielers zu craften.

    - Prüft, ob der Spieler alle benötigten Zutaten in ausreichender Menge besitzt.
    - Entfernt die Zutaten aus dem Inventar.
    - Fügt das Ergebnis‑Item dem Inventar hinzu.
    - Gibt ``True`` zurück, wenn das Craften erfolgreich war, sonst ``False``.
    """
    # 1. Verfügbarkeit prüfen
    for ingredient_name, qty_needed in recipe.ingredients.items():
        if not player.has_item(ingredient_name, min_quantity=qty_needed):
            return False

    # 2. Zutaten entfernen
    for ingredient_name, qty_needed in recipe.ingredients.items():
        # ``remove_item`` gibt ``True`` zurück, weil wir vorher geprüft haben
        player.remove_item(ingredient_name, qty_needed)

    # 3. Ergebnis hinzufügen
    player.add_item(recipe.result)
    return True