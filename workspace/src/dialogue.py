from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class DialogueOption:
    """Option presented to the player in a dialogue node.

    Attributes
    ----------
    text: str
        The text displayed for this option.
    next_node: Optional[str]
        Identifier of the next node. ``None`` signals the end of the dialogue.
    """

    text: str
    next_node: Optional[str] = None


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
        # Normalise ``options`` to an empty list if ``None`` was supplied.
        if self.options is None:
            self.options = []


class DialogueManager:
    """Manages progression through a static dialogue tree.

    The manager is deterministic and fully testable – no random elements are used.
    It tracks the current node, provides the current text and options, and
    records whether the dialogue has finished (i.e., a successful choice led to a
    ``next_node`` of ``None``).
    """

    def __init__(self, nodes: List[DialogueNode], start_node: str) -> None:
        # Build a fast lookup table ``node_id -> DialogueNode``.
        self._node_map: Dict[str, DialogueNode] = {node.node_id: node for node in nodes}
        if start_node not in self._node_map:
            raise ValueError(f"Start node '{start_node}' not found in provided nodes.")
        self._current_node: Optional[DialogueNode] = self._node_map[start_node]
        self._finished: bool = False

    def get_current_text(self) -> str:
        """Return the text of the active node.

        If the dialogue has finished, an empty string is returned.
        """
        return self._current_node.text if self._current_node else ""

    def get_options(self) -> List[DialogueOption]:
        """Return the list of options for the active node.

        Returns an empty list when the dialogue is finished or the current node
        has no options.
        """
        return list(self._current_node.options) if self._current_node else []

    def choose(self, index: int) -> bool:
        """Select an option by its index.

        Parameters
        ----------
        index: int
            Zero‑based index into the list returned by :meth:`get_options`.

        Returns
        -------
        bool
            ``True`` if the choice was valid and the dialogue progressed,
            ``False`` otherwise (invalid index or dialogue already finished).
        """
        if self._finished or self._current_node is None:
            return False
        options = self._current_node.options
        if not options or index < 0 or index >= len(options):
            return False
        chosen = options[index]
        # If ``next_node`` is ``None`` the dialogue ends.
        if chosen.next_node is None:
            self._finished = True
            self._current_node = None
        else:
            # Move to the referenced node; raise if the node does not exist.
            if chosen.next_node not in self._node_map:
                raise ValueError(f"Dialogue node '{chosen.next_node}' does not exist.")
            self._current_node = self._node_map[chosen.next_node]
        return True

    def is_finished(self) -> bool:
        """Return ``True`` if the dialogue has reached an end state.

        The dialogue is considered finished only after a *successful* choice
        that leads to a ``next_node`` of ``None``. Invalid choices or attempts to
        choose when no options are available do **not** set the finished flag.
        """
        return self._finished
