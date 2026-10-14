from src.core import Player, Item

def use_item(player: Player, item_name: str, quantity: int = 1) -> bool:
    """Verbraucht ein Item aus dem Inventar des Spielers.

    Das Item muss im Inventar vorhanden sein und die Kategorie ``consumable`` besitzen.
    Der Heilungswert wird aus ``item.base_value`` abgeleitet und mit der
    Menge multipliziert. Der Spieler wird anschließend geheilt (maximal bis
    ``max_hp``) und das Item wird aus dem Inventar entfernt.

    Returns
    -------
    bool
        ``True`` wenn das Item erfolgreich verwendet wurde, sonst ``False``.
    """
    if quantity < 1:
        raise ValueError("Menge muss mindestens 1 sein.")
    # Prüfen, ob das Item im Inventar vorhanden ist
    if not player.has_item(item_name, min_quantity=quantity):
        return False
    item: Item = player.inventory[item_name]
    if item.category != "consumable":
        return False
    # Heilungsbetrag berechnen und anwenden
    total_heal = item.base_value * quantity
    player.heal(total_heal)
    # Item aus dem Inventar entfernen
    player.remove_item(item_name, quantity)
    return True