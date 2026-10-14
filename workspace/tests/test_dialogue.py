import pytest
from src.dialogue import DialogueNode, DialogueOption, DialogueManager

def test_dialogue_progression_and_finish():
    nodes = [
        DialogueNode(
            node_id="start",
            text="Willkommen, Abenteurer!",
            options=[
                DialogueOption(text="Hallo", next_node="greet"),
                DialogueOption(text="Tschüss", next_node=None),
            ],
        ),
        DialogueNode(
            node_id="greet",
            text="Wie kann ich dir helfen?",
            options=[
                DialogueOption(text="Quest", next_node=None),
            ],
        ),
    ]
    dm = DialogueManager(nodes=nodes, start_node="start")
    assert dm.get_current_text() == "Willkommen, Abenteurer!"
    assert len(dm.get_options()) == 2
    # Choose first option – should move to "greet"
    assert dm.choose(0) is True
    assert dm.get_current_text() == "Wie kann ich dir helfen?"
    assert dm.is_finished() is False
    # Choose the only option – dialogue ends
    assert dm.choose(0) is True
    assert dm.is_finished() is True

def test_invalid_choice_returns_false():
    nodes = [
        DialogueNode(
            node_id="only",
            text="Ende",
            options=[],
        )
    ]
    dm = DialogueManager(nodes=nodes, start_node="only")
    # No options – any choice is invalid
    assert dm.choose(0) is False
    # Dialogue should still be considered finished because there are no options
    assert dm.is_finished() is False
