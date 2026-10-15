```python
# src/dungeon.py
"""
Dungeon module with integrated faction reputation mechanics.

The implementation is self‑contained and does not require modifications to
other source files.  It provides:
* A ``Faction`` enumeration.
* ``ReputationManager`` – a simple per‑player reputation store.
* Helper functions that can be called from economy, combat or quest code
  to update reputations.
* ``Dungeon`` – determines accessible levels, exclusive equipment,
  price discounts and hostility based on a player's reputation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Tuple


# --------------------------------------------------------------------------- #
# Faction definition
# --------------------------------------------------------------------------- #
class Faction(Enum):
    MERCHANTS = auto()   # Händlergilde
    GUARDIANS = auto()   # Wächter
    ROGUES = auto