import pytest
from src.core import Item, Player
from src.economy import Merchant


def test_merchant_initialization():
    m = Merchant()
    assert m.gold == 100
    assert m.inventory == {}
    assert m.buy_markup == 0.5
    assert m.sell_markup == 1.5


def test_buy_from_player_success():
    player = Player(name="Bob", gold=20)
    iron = Item(name="Eisenerz", category="material", base_value=10, quantity=2)
    player.add_item(iron)
    merchant = Merchant(gold=50)

    # Spieler verkauft 1 Eisenerz (Preis = 10 * 0.5 = 5)
    result = merchant.buy_from_player(player, "Eisenerz", quantity=1)
    assert result is True
    assert player.gold == 25  # 20 + 5
    assert merchant.gold == 45
    assert not player.has_item("Eisenerz", min_quantity=2)
    assert player.has_item("Eisenerz", min_quantity=1)
    assert merchant.inventory["Eisenerz"].quantity == 1


def test_sell_to_player_success():
    merchant = Merchant(gold=30)
    potion = Item(name="Heiltrank", category="consumable", base_value=8, quantity=3)
    merchant.add_item(potion)
    player = Player(name="Alice", gold=50)

    # Spieler kauft 2 Heiltränke (Preis = 8 * 1.5 = 12 pro Stück)
    result = merchant.sell_to_player(player, "Heiltrank", quantity=2)
    assert result is True
    assert player.gold == 26  # 50 - 24
    assert merchant.gold == 54
    assert player.inventory["Heiltrank"].quantity == 2
    assert merchant.inventory["Heiltrank"].quantity == 1


def test_insufficient_funds_player_cannot_buy():
    merchant = Merchant(gold=100)
    sword = Item(name="Schwert", category="weapon", base_value=40, quantity=1)
    merchant.add_item(sword)
    player = Player(name="PoorGuy", gold=10)

    result = merchant.sell_to_player(player, "Schwert")
    assert result is False
    assert player.gold == 10
    assert merchant.gold == 100
    assert "Schwert" in merchant.inventory
    assert "Schwert" not in player.inventory


def test_insufficient_item_merchant_cannot_sell():
    merchant = Merchant(gold=100)
    player = Player(name="RichGuy", gold=200)
    result = merchant.sell_to_player(player, "NichtExistiert")
    assert result is False


def test_price_calculation_factors():
    merchant = Merchant(buy_markup=0.4, sell_markup=2.0)
    ore = Item(name="Erz", category="material", base_value=25, quantity=5)
    merchant.add_item(ore)
    player = Player(name="Trader", gold=100)
    # Player buys 1 Erz: price = 25 * 2.0 = 50
    assert merchant.sell_to_player(player, "Erz", quantity=1) is True
    assert player.gold == 50
    assert merchant.gold == 150
    # Player now sells the same Erz back: price = 25 * 0.4 = 10
    assert merchant.buy_from_player(player, "Erz", quantity=1) is True
    assert player.gold == 60
    assert merchant.gold == 140
