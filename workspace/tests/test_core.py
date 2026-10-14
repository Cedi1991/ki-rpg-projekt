import pytest
from src.core import Item, Player


def test_player_initialization():
    player = Player(name="Arthas")
    assert player.name == "Arthas"
    assert player.hp == 100
    assert player.gold == 50
    assert player.is_alive is True


def test_combat_damage_and_healing():
    player = Player(name="Hero", hp=100, max_hp=100)
    player.take_damage(40)
    assert player.hp == 60

    # Heilung darf max_hp nicht überschreiten
    player.heal(50)
    assert player.hp == 100

    # Tödlicher Schaden setzt is_alive auf False und verhindert Heilung
    player.take_damage(150)
    assert player.hp == 0
    assert player.is_alive is False
    assert player.heal(20) == 0


def test_gold_transactions():
    player = Player(name="Trader", gold=50)
    player.add_gold(30)
    assert player.gold == 80

    assert player.spend_gold(60) is True
    assert player.gold == 20

    # Nicht genug Gold vorhanden
    assert player.spend_gold(50) is False
    assert player.gold == 20


def test_inventory_stacking_and_removal():
    player = Player(name="Crafter", gold=10)
    iron = Item(name="Eisenerz", category="material", base_value=5, quantity=2)
    more_iron = Item(name="Eisenerz", category="material", base_value=5, quantity=3)

    player.add_item(iron)
    player.add_item(more_iron)

    assert player.has_item("Eisenerz", min_quantity=5) is True
    assert player.net_worth() == 10 + (5 * 5)  # 10 Gold + 25 Materialwert = 35

    # Teilmenge entfernen
    assert player.remove_item("Eisenerz", quantity=2) is True
    assert player.inventory["Eisenerz"].quantity == 3

    # Rest komplett entfernen -> Schlüssel verschwindet aus dem Dict
    assert player.remove_item("Eisenerz", quantity=3) is True
    assert player.has_item("Eisenerz") is False


def test_invalid_inputs_raise_errors():
    with pytest.raises(ValueError):
        Item(name="Bugged", category="misc", base_value=-10)

    player = Player(name="Tester")
    with pytest.raises(ValueError):
        player.take_damage(-5)
