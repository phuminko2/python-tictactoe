"""Authoritative TCP server for a two-player Tic Tac Toe game."""

import json
import socket
import threading

HOST = "0.0.0.0"
PORT = 5000
WINNING_LINES = (
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
)


class GameServer:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.clients = []
        self.names = []
        self.board = [" "] * 9
        self.turn = 0
        self.winner = None
        self.game_over = False
        self.lock = threading.Lock()

    @staticmethod
    def send(client, message):
        client.sendall((json.dumps(message) + "\n").encode("utf-8"))

    def state(self, message=""):
        return {
            "type": "state", "board": self.board, "turn": self.turn,
            "names": self.names, "winner": self.winner,
            "game_over": self.game_over, "message": message,
        }

    def broadcast(self, message=""):
        payload = (json.dumps(self.state(message)) + "\n").encode("utf-8")
        for client in self.clients:
            try:
                client.sendall(payload)
            except OSError:
                pass

    def handle_move(self, player, message):
        position = message.get("position")
        if (self.game_over or player != self.turn or not isinstance(position, int)
                or isinstance(position, bool) or not 0 <= position < 9
                or self.board[position] != " "):
            self.send(self.clients[player], {"type": "error", "message": "That move is not valid."})
            return

        symbol = "XO"[player]
        self.board[position] = symbol
        line_won = any(all(self.board[i] == symbol for i in line) for line in WINNING_LINES)
        if line_won:
            self.winner = player
            self.game_over = True
        elif " " not in self.board:
            self.game_over = True
        else:
            self.turn = 1 - self.turn
        self.broadcast()

    def handle_client(self, player, client):
        try:
            stream = client.makefile("r", encoding="utf-8")
            for line in stream:
                try:
                    message = json.loads(line)
                except json.JSONDecodeError:
                    self.send(client, {"type": "error", "message": "Invalid message."})
                    continue
                if message.get("type") == "move":
                    with self.lock:
                        self.handle_move(player, message)
        except (OSError, ConnectionError):
            pass
        finally:
            try:
                client.close()
            except OSError:
                pass
            print(f"{self.names[player]} disconnected.")

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.port))
            server.listen(2)
            print(f"Waiting for two players on port {self.port}...")

            while len(self.clients) < 2:
                client, address = server.accept()
                stream = client.makefile("r", encoding="utf-8")
                try:
                    hello = json.loads(stream.readline())
                except (json.JSONDecodeError, TypeError):
                    client.close()
                    continue
                if hello.get("type") != "join":
                    client.close()
                    continue

                player = len(self.clients)
                name = str(hello.get("name", f"Player {player + 1}"))[:24].strip()
                self.clients.append(client)
                self.names.append(name or f"Player {player + 1}")
                self.send(client, {"type": "welcome", "player": player, "symbol": "XO"[player]})
                print(f"{self.names[player]} joined from {address[0]} as {'XO'[player]}.")

            self.broadcast("Both players connected. X goes first.")
            for player, client in enumerate(self.clients):
                threading.Thread(target=self.handle_client, args=(player, client), daemon=True).start()
            print("Game started. Press Ctrl+C to stop the server.")
            try:
                threading.Event().wait()
            except KeyboardInterrupt:
                print("\nServer stopped.")


if __name__ == "__main__":
    try:
        GameServer().run()
    except OSError as error:
        print(f"Could not start server: {error}")
