import random
import tkinter as tk

# ======================================
# 1. Board
# ======================================


class Board:
    def __init__(self):
        self._cells = [" "] * 9

    def get_cells(self):
        return self._cells.copy()

    def available_positions(self):
        return [i for i, cell in enumerate(self._cells) if cell == " "]

    def place(self, position, symbol):
        if position not in self.available_positions():
            return False

        self._cells[position] = symbol
        return True

    def check_winner(self):
        patterns = [
            (0, 1, 2),
            (3, 4, 5),
            (6, 7, 8),
            (0, 3, 6),
            (1, 4, 7),
            (2, 5, 8),
            (0, 4, 8),
            (2, 4, 6),
        ]

        for a, b, c in patterns:
            if (
                self._cells[a] != " "
                and self._cells[a] == self._cells[b]
                and self._cells[b] == self._cells[c]
            ):
                return self._cells[a]

        return None

    def is_full(self):
        return len(self.available_positions()) == 0


# ======================================
# 2. Player (Parent Class)
# ======================================


class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def choose_position(self, board, position=None):
        return position


# ======================================
# 3. HumanPlayer
# ======================================


class HumanPlayer(Player):
    def choose_position(self, board, position=None):
        return position


# ======================================
# 4. AIPlayer
# ======================================


class AIPlayer(Player):
    def choose_position(self, board, position=None):
        available = board.available_positions()

        if not available:
            return None

        return random.choice(available)


# ======================================
# 5. TicTacToeGame
# ======================================


class TicTacToeGame:
    def __init__(self):
        self.board = Board()

        self.players = [HumanPlayer("You", "X"), AIPlayer("Computer", "O")]

        self.current_player = 0
        self.winner = None
        self.game_over = False

    def switch_player(self):
        self.current_player = 1 - self.current_player

    def play_turn(self, position=None):
        if self.game_over:
            return False

        player = self.players[self.current_player]

        chosen_position = player.choose_position(self.board, position)

        if not self.board.place(chosen_position, player.symbol):
            return False

        winner_symbol = self.board.check_winner()

        if winner_symbol:
            self.winner = player
            self.game_over = True

        elif self.board.is_full():
            self.game_over = True

        else:
            self.switch_player()

        return True


# ======================================
# 6. TicTacToeGUI
# ======================================


class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - OOP")
        self.root.resizable(False, False)

        self.game = TicTacToeGame()
        self.buttons = []
        self.ai_job = None

        # Title
        self.title_label = tk.Label(
            root, text="Tic Tac Toe", font=("Arial", 24, "bold")
        )
        self.title_label.pack(pady=15)

        # Board Frame
        self.board_frame = tk.Frame(root)
        self.board_frame.pack(padx=20, pady=10)

        # Create 3x3 Buttons
        for i in range(9):
            button = tk.Button(
                self.board_frame,
                text=" ",
                font=("Arial", 24, "bold"),
                width=5,
                height=2,
                command=lambda pos=i: self.on_click(pos),
            )

            button.grid(row=i // 3, column=i % 3, padx=3, pady=3)

            self.buttons.append(button)

        # Status Label
        self.status_label = tk.Label(root, text="Your turn (X)", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Restart Button
        self.restart_button = tk.Button(
            root, text="New Game", font=("Arial", 12), command=self.restart
        )
        self.restart_button.pack(pady=10)

        self.update_ui()

    # Handle Human Click
    def on_click(self, position):
        if self.game.game_over:
            return

        if self.game.current_player != 0:
            return

        success = self.game.play_turn(position)

        if not success:
            return

        self.update_ui()

        # AI Turn
        if not self.game.game_over:
            self.ai_job = self.root.after(500, self.ai_turn)

    # AI plays automatically
    def ai_turn(self):
        self.ai_job = None

        if self.game.game_over:
            return

        if self.game.current_player != 1:
            return

        self.game.play_turn()
        self.update_ui()

    # Update GUI
    def update_ui(self):
        cells = self.game.board.get_cells()

        for i, button in enumerate(self.buttons):
            symbol = cells[i]

            if symbol == "X":
                color = "blue"
            elif symbol == "O":
                color = "red"
            else:
                color = "black"

            can_click = (
                not self.game.game_over
                and self.game.current_player == 0
                and symbol == " "
            )

            button.config(
                text=symbol,
                fg=color,
                disabledforeground=color,
                state="normal" if can_click else "disabled",
            )

        if self.game.winner:
            message = f"{self.game.winner.name} wins!"

        elif self.game.game_over:
            message = "It's a draw!"

        else:
            player = self.game.players[self.game.current_player]
            message = f"{player.name}'s turn ({player.symbol})"

        self.status_label.config(text=message)

    # Restart Game
    def restart(self):
        if self.ai_job is not None:
            self.root.after_cancel(self.ai_job)
            self.ai_job = None

        self.game = TicTacToeGame()
        self.update_ui()


# ======================================
# 7. Main
# ======================================

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
