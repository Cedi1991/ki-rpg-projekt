from dataclasses import dataclass
from src.core import Player


@dataclass
class Monster:
    """Ein einfacher Gegner.

    Attributes
    ----------
    name: str
        Name des Monsters.
    hp: int
        Lebenspunkte des Monsters.
    attack: int
        Schaden, den das Monster pro Runde dem Spieler zufügt.
    gold_drop: int
        Goldbetrag, den das Monster beim Tod an den Spieler gibt.
    """
    name: str
    hp: int
    attack: int
    gold_drop: int

    def is_alive(self) -> bool:
        """Return True if the monster still has HP left."""
        return self.hp > 0


def resolve_combat_round(player: Player, monster: Monster, player_damage: int = 10) -> None:
    """Simuliere eine einzelne Kampfrunde.

    1. Der Spieler greift das Monster an und reduziert dessen HP um ``player_damage``.
    2. Wenn das Monster nach dem Angriff noch lebt, schlägt es zurück und fügt dem Spieler ``monster.attack`` Schaden zu.
    3. Stirbt das Monster (HP <= 0), erhält der Spieler den im Monster definierten ``gold_drop``.

    Die Funktion ist deterministisch – sie verwendet keine Zufallszahlen und gibt keinen Rückgabewert zurück.
    Sie mutiert die übergebenen ``player``- und ``monster``-Objekte.
    """
    if player_damage < 0:
        raise ValueError("player_damage darf nicht negativ sein.")
    if not player.is_alive:
        # Ein toter Spieler kann nicht kämpfen.
        return

    # Spieler greift an
    monster.hp = max(0, monster.hp - player_damage)

    # Monster greift nur an, wenn es noch lebt
    if monster.is_alive():
        player.take_damage(monster.attack)
    else:
        # Monster ist tot – Gold wird ausbezahlt
        player.add_gold(monster.gold_drop)
