from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class DialogueOption:
    """Option presented to the player in a dialogue node."""
    text: str
    next_node: Optional[str] = None  # None signals the end of the dialogue

@dataclass
class DialogueNode:
    """A single node in a deterministic dialogue tree.

    Attributes
    ----------
    node_id: str
        Unique identifier used to reference the node.
    text: str
        The text displayed to the player when this node is active.
    options: List[DialogueOption]
        List of possible player choices. An empty list means the dialogue ends.
    """
    node_id: str
    text: str
    options: List[DialogueOption] | None = None

    def __post_init__(self) -> None:
        if self.options is None:
            self.options = []

class DialogueManager:
    """Manages progression through a deterministic dialogue tree.

    The manager is completely deterministic – no random elements are used –
    making it straightforward to unit‑test.
    """
    def __init__(self, nodes: List[DialogueNode], start_node: str) -> None:
        self._nodes: Dict[str, DialogueNode] = {n.node_id: n for n in nodes}
        if start_node not in self._nodes:
            raise ValueError(f"Start node '{start_node}' not found in provided nodes.")
        self.current_node_id: Optional[str] = start_node

    def get_current_text(self) -> str:
        """Return the text of the currently active node.
        """
        if self.current_node_id is None:
            raise RuntimeError("Dialogue has already finished.")
        return self._nodes[self.current_node_id].text

    def get_options(self) -> List[DialogueOption]:
        """Return the list of options for the current node.
        """
        if self.current_node_id is None:
            return []
        return self._nodes[self.current_node_id].options

    def choose(self, index: int) -> bool:
        """Select an option by its list index.

        Returns
        -------
        bool
            ``True`` if the choice was valid and the internal state was updated,
            ``False`` if the index is out of range or the dialogue is already
            finished.
        """
        if self.current_node_id is None:
            return False
        options = self.get_options()
        if not options or index < 0 or index >= len(options):
            return False
        next_id = options[index].next_node
        if next_id is None:
            # Dialogue ends
            self.current_node_id = None
            return True
        if next_id not in self._nodes:
            raise ValueError(f"Next node '{next_id}' is not defined in the dialogue tree.")
        self.current_node_id = next_id
        return True

    def is_finished(self) -> bool:
        """Return ``True`` when the dialogue has reached an end state.
        """
        return self.current_node_id is None
