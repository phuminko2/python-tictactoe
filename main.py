"""Tkinter client for the multiplayer Tic Tac Toe server."""

import json
import queue
import socket
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog

PORT = 5000


class TicTacToeClient:
    def __init__(self, root, host, name):
        self.root = root
        self.root.title("Tic Tac Toe Online")
        self.root.resizable(False, False)
        self.host = host
        self.name = name
        self.sock = None
        self.player = None
        self.symbol = None
        self.state = None
        self.incoming = queue.Queue()

        tk.Label(root, text="Tic Tac Toe", font=("Arial", 24, "bold")).pack(pady=15)
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(padx=20, pady=10)
        self.buttons = []
        for position in range(9):
            button = tk.Button(
                self.board_frame, text=" ", font=("Arial", 24, "bold"),
                width=5, height=2, command=lambda p=position: self.play(p),
            )
            button.grid(row=position // 3, column=position % 3, padx=3, pady=3)
            self.buttons.append(button)

        self.status = tk.Label(root, text="Connecting...", font=("Arial", 14))
        self.status.pack(pady=10)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.connect()
        self.root.after(100, self.process_messages)

    def connect(self):
        try:
            self.sock = socket.create_connection((self.host, PORT), timeout=8)
            self.sock.settimeout(None)
            self.send({"type": "join", "name": self.name})
            threading.Thread(target=self.receive, daemon=True).start()
        except OSError as error:
            messagebox.showerror("Connection failed", f"Could not connect to {self.host}:{PORT}\n{error}")
            self.root.destroy()

    def send(self, message):
        self.sock.sendall((json.dumps(message) + "\n").encode("utf-8"))

    def receive(self):
        try:
            stream = self.sock.makefile("r", encoding="utf-8")
            for line in stream:
                self.incoming.put(json.loads(line))
        except (OSError, json.JSONDecodeError):
            pass
        self.incoming.put({"type": "disconnected"})

    def process_messages(self):
        while True:
            try:
                message = self.incoming.get_nowait()
            except queue.Empty:
                break
            if message["type"] == "welcome":
                self.player = message["player"]
                self.symbol = message["symbol"]
            elif message["type"] == "state":
                self.state = message
                self.update_ui()
            elif message["type"] == "error":
                self.status.config(text=message["message"])
            elif message["type"] == "disconnected":
                if self.root.winfo_exists():
                    self.status.config(text="Disconnected from server")
                    for button in self.buttons:
                        button.config(state="disabled")
        if self.root.winfo_exists():
            self.root.after(100, self.process_messages)

    def play(self, position):
        if self.state and not self.state["game_over"] and self.state["turn"] == self.player:
            try:
                self.send({"type": "move", "position": position})
            except OSError:
                self.status.config(text="Could not send move")

    def update_ui(self):
        state = self.state
        for position, button in enumerate(self.buttons):
            cell = state["board"][position]
            color = {"X": "blue", "O": "red", " ": "black"}[cell]
            can_play = (not state["game_over"] and state["turn"] == self.player
                        and cell == " ")
            button.config(text=cell, fg=color, disabledforeground=color,
                          state="normal" if can_play else "disabled")

        if state["winner"] is not None:
            winner_name = state["names"][state["winner"]]
            text = f"{winner_name} ({'XO'[state['winner']]}) wins!"
        elif state["game_over"]:
            text = "It's a draw!"
        else:
            turn_name = state["names"][state["turn"]]
            text = ("Your turn" if state["turn"] == self.player else f"{turn_name}'s turn")
            text += f" ({'XO'[state['turn']]})"
        self.status.config(text=text)

    def close(self):
        if self.sock:
            self.sock.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    root.withdraw()
    host = simpledialog.askstring("Join game", "Server address:", initialvalue="127.0.0.1", parent=root)
    if not host:
        root.destroy()
        return
    name = simpledialog.askstring("Join game", "Your name:", initialvalue="Player", parent=root)
    if not name:
        root.destroy()
        return
    root.deiconify()
    TicTacToeClient(root, host.strip(), name.strip())
    root.mainloop()


if __name__ == "__main__":
    main()
