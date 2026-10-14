import pytest
from src.core import Item, Player
from src.crafting import Recipe, craft_item


def test_successful_crafting():
    player = Player(name="Alchemist", gold=0)
    # Ausgangsmaterialien
    iron_ore = Item(name="Eisenerz", category="material", base_value=5, quantity=3)
    wood = Item(name="Holz", category="material", base_value=2, quantity=2)
    player.add_item(iron_ore)
    player.add_item(wood)

    # Rezept: 2 Eisenerz + 1 Holz -> 1 Eisenbarren
    result_item = Item(name="Eisenbarren", category="material", base_value=15, quantity=1)
    recipe = Recipe(
        name="Eisenbarren herstellen",
        ingredients={"Eisenerz": 2, "Holz": 1},
        result=result_item,
    )

    assert craft_item(player, recipe) is True
    # Zutaten wurden reduziert/entfernt
    assert player.inventory["Eisenerz"].quantity == 1
    assert player.inventory["Holz"].quantity == 1
    # Ergebnis ist im Inventar
    assert player.inventory["Eisenbarren"].quantity == 1


def test_crafting_fails_due_to_missing_ingredients():
    player = Player(name="Novice", gold=0)
    iron_ore = Item(name="Eisenerz", category="material", base_value=5, quantity=1)
    player.add_item(iron_ore)

    result_item = Item(name="Eisenbarren", category="material", base_value=15, quantity=1)
    recipe = Recipe(
        name="Eisenbarren herstellen",
        ingredients={"Eisenerz": 2},
        result=result_item,
    )

    assert craft_item(player, recipe) is False
    # Inventar bleibt unverändert
    assert player.inventory["Eisenerz"].quantity == 1
    assert "Eisenbarren" not in player.inventory