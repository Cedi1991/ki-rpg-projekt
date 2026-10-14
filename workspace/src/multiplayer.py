"""src/multiplayer.py
Minimaler, deterministischer Mehrspieler‑Modus für das RPG‑Projekt.

Dieses Modul stellt eine sehr einfache TCP‑basierte Server‑Client‑Architektur bereit,
die ausschließlich JSON‑Nachrichten (eine Zeile pro Nachricht) austauscht. Es enthält
keine zufällige Logik, ist vollständig testbar und kann in Unit‑Tests durch
Mock‑Sockets oder das `socketserver`‑Modul simuliert werden.

Die wichtigsten Klassen/Funktionen:
- :class:`MessageProtocol` – Hilfsklasse zum Senden/Empfangen von JSON‑Strings über
  einen Socket. Jede Nachricht endet mit ``"\n"``.
- :class:`Server` – Startet einen TCP‑Server in einem eigenen Thread, akzeptiert
  eingehende Verbindungen und leitet empfangene Nachrichten an einen vom Nutzer
  bereitgestellten ``handler`` weiter.
- :class:`Client` – Stellt eine Verbindung zu einem Server her und ermöglicht das
  Senden von Nachrichten sowie das Registrieren eines Callback‑Handlers für
  eingehende Nachrichten.

Die API ist bewusst klein gehalten, damit sie leicht in Tests eingesetzt werden
kann. Beispiel‑Nutzung (nicht Teil der Tests)::

    from src.multiplayer import Server, Client

    def echo_handler(conn, msg):
        conn.send_message({"echo": msg})

    server = Server(host="127.0.0.1", port=9000, handler=echo_handler)
    server.start()

    client = Client(host="127.0.0.1", port=9000)
    client.connect()
    client.send_message({"hello": "world"})
    client.register_handler(lambda msg: print("Received", msg))

"""

import json
import socket
import threading
from typing import Callable, Dict, Any, Optional


class MessageProtocol:
    """Utility to send/receive JSON messages terminated by a newline.

    The protocol is deterministic – keine zufälligen Elemente werden verwendet.
    ``recv_message`` blockiert, bis eine komplette Zeile empfangen wurde.
    """

    def __init__(self, conn: socket.socket):
        self.conn = conn
        self._recv_buffer = b""
        self.lock = threading.Lock()

    def send_message(self, data: Dict[str, Any]) -> None:
        """Serialisiert ``data`` zu JSON, fügt ein Zeilen‑Break hinzu und sendet.
        """
        msg = json.dumps(data, ensure_ascii=False) + "\n"
        encoded = msg.encode("utf-8")
        with self.lock:
            self.conn.sendall(encoded)

    def recv_message(self) -> Optional[Dict[str, Any]]:
        """Liest vom Socket bis zum nächsten ``\n`` und gibt das JSON‑Objekt zurück.
        Gibt ``None`` zurück, wenn die Verbindung geschlossen wurde.
        """
        while b"\n" not in self._recv_buffer:
            chunk = self.conn.recv(4096)
            if not chunk:
                return None
            self._recv_buffer += chunk
        line, self._recv_buffer = self._recv_buffer.split(b"\n", 1)
        try:
            return json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            # Bei fehlerhaftem JSON wird die Nachricht verworfen.
            return None


class Server:
    """Ein einfacher TCP‑Server, der jede eingehende Nachricht an ``handler`` weitergibt.

    ``handler`` ist eine Callable mit Signatur ``handler(protocol, message)``.
    Der Server läuft in einem eigenen Thread, sodass er nicht blockiert.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0,
                 handler: Callable[[MessageProtocol, Dict[str, Any]], None] = lambda p, m: None):
        self.host = host
        self.port = port
        self.handler = handler
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen()
        self._thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._running = False
        # After bind, retrieve the actual port (useful when port==0)
        self.actual_port = self._sock.getsockname()[1]

    def start(self) -> None:
        """Startet den Hintergrund‑Thread, der Verbindungen akzeptiert."""
        self._running = True
        self._thread.start()

    def stop(self) -> None:
        """Beendet den Server und schließt den Listening‑Socket."""
        self._running = False
        try:
            # Dummy connection to unblock ``accept``
            with socket.create_connection((self.host, self.actual_port), timeout=0.1):
                pass
        except OSError:
            pass
        self._sock.close()
        self._thread.join()

    def _accept_loop(self) -> None:
        while self._running:
            try:
                conn, _addr = self._sock.accept()
            except OSError:
                break
            threading.Thread(target=self._client_thread, args=(conn,), daemon=True).start()

    def _client_thread(self, conn: socket.socket) -> None:
        protocol = MessageProtocol(conn)
        while True:
            msg = protocol.recv_message()
            if msg is None:
                break
            try:
                self.handler(protocol, msg)
            except Exception:
                # Der Server soll nicht abstürzen, wenn ein Handler Fehler wirft.
                continue
        conn.close()


class Client:
    """Ein einfacher TCP‑Client, der Nachrichten senden und empfangene Nachrichten
    über einen Callback verarbeiten kann.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0):
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self.protocol: Optional[MessageProtocol] = None
        self._recv_thread: Optional[threading.Thread] = None
        self._handler: Optional[Callable[[Dict[str, Any]], None]] = None
        self._running = False

    def connect(self) -> None:
        self._sock = socket.create_connection((self.host, self.port))
        self.protocol = MessageProtocol(self._sock)
        self._running = True
        self._recv_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self._recv_thread.start()

    def disconnect(self) -> None:
        self._running = False
        if self._sock:
            self._sock.close()
        if self._recv_thread:
            self._recv_thread.join()

    def send_message(self, data: Dict[str, Any]) -> None:
        if not self.protocol:
            raise RuntimeError("Client is not connected.")
        self.protocol.send_message(data)

    def register_handler(self, handler: Callable[[Dict[str, Any]], None]) -> None:
        """Setzt den Callback, der für jede eingehende Nachricht aufgerufen wird."""
        self._handler = handler

    def _receive_loop(self) -> None:
        assert self.protocol is not None
        while self._running:
            msg = self.protocol.recv_message()
            if msg is None:
                break
            if self._handler:
                try:
                    self._handler(msg)
                except Exception:
                    continue
        self.disconnect()

# Beispiel‑Handler für Tests (optional)
def echo_handler(protocol: MessageProtocol, message: Dict[str, Any]) -> None:
    """Ein einfacher Echo‑Handler, der die empfangene Nachricht zurücksendet.
    Kann in Unit‑Tests verwendet werden, um die Round‑Trip‑Funktionalität zu prüfen.
    """
    protocol.send_message({"echo": message})
