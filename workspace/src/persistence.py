import json
from src.core import Player, Item

def _item_to_dict(item: Item) -> dict:
    """Konvertiert ein Item in ein serialisierbares Dict."""
    return {
        "name": item.name,
        "category": item.category,
        "base_value": item.base_value,
        "quantity": item.quantity,
    }

def _dict_to_item(data: dict) -> Item:
    """Erstellt ein Item aus einem Dict, das mit ``_item_to_dict`` erzeugt wurde."""
    return Item(
        name=data["name"],
        category=data["category"],
        base_value=data["base_value"],
        quantity=data.get("quantity", 1),
    )

def save_player_to_json(player: Player) -> str:
    """Serialisiert einen ``Player`` inklusive Inventar zu einem JSON‑String.

    Der Rückgabewert ist ein ``str`` und kann direkt in Dateien geschrieben
    oder über das Netzwerk gesendet werden.
    """
    player_dict = {
        "name": player.name,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "gold": player.gold,
        "inventory": [_item_to_dict(item) for item in player.inventory.values()],
    }
    return json.dumps(player_dict, ensure_ascii=False)

def load_player_from_json(json_str: str) -> Player:
    """Deserialisiert einen JSON‑String, der von ``save_player_to_json`` erzeugt wurde,
    und gibt ein neues ``Player``‑Objekt zurück.
    """
    data = json.loads(json_str)
    player = Player(
        name=data["name"],
        hp=data.get("hp", 100),
        max_hp=data.get("max_hp", 100),
        gold=data.get("gold", 0),
    )
    for item_data in data.get("inventory", []):
        player.add_item(_dict_to_item(item_data))
    return player
