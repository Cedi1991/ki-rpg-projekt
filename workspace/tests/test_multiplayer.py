import pytest
from src.multiplayer import MessageProtocol, Lobby, ChatSession


def test_message_protocol_encode_decode():
    protocol = MessageProtocol()
    data = {"type": "chat", "sender": "Alice", "message": "Hallo"}
    encoded = protocol.encode(data)
    decoded = protocol.decode(encoded)
    assert decoded == data


def test_lobby_add_and_remove_player():
    lobby = Lobby(name="TestLobby")
    player_data = {"name": "Alice", "hp": 100}
    lobby.add_player("Alice", player_data)
    assert "Alice" in lobby.list_players()
    assert lobby.get_player("Alice") == player_data

    lobby.remove_player("Alice")
    assert "Alice" not in lobby.list_players()
    assert lobby.get_player("Alice") is None


def test_chat_session_send_and_get_messages():
    chat = ChatSession()
    chat.send_message("Alice", "Hallo")
    chat.send_message("Bob", "Hi")
    messages = chat.get_messages()
    assert len(messages) == 2
    assert messages[0] == {"sender": "Alice", "message": "Hallo"}
    assert messages[1] == {"sender": "Bob", "message": "Hi"}


def test_chat_session_clear_messages():
    chat = ChatSession()
    chat.send_message("Alice", "Hallo")
    chat.clear_messages()
    assert chat.get_messages() == []
