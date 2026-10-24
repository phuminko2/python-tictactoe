import random


class Board:
    def __init__(self):
        self._cells = [" "] * 9

    def available_position(self):
        return [i for i, cell in enumerate(self._cells) if cell == " "]

    def display(self):
        for i in range(0, 9, 3):
            print(" | ".join(self._cells[i : i + 3]))
            if i < 6:
                print("--+---+--")

    def place(self, position, symbol):
        if position < 0 or position > 8:
            return False
        if self._cells[position] != " ":
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
        return " " not in self._cells


class Player:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol

    def choose_position(self, board):
        return None


class HumanPlayer(Player):
    def choose_position(self, board):
        position = int(input("Position 1-9: "))
        return position - 1


class AIPlayer(Player):
    def choose_position(self, board):
        available = board.available_position()
        return random.choice(available)


class TicTacToeGame:
    def __init__(self, player1, player2):
        self.board = Board()
        self.players = [
            player1,
            player2,
        ]
        self.current_player = 0

    def switch_player(self):
        self.current_player = 1 - self.current_player

    def play(self):
        while True:
            self.board.display()
            player = self.players[self.current_player]
            print(f"\n{player.name}'s turn ({player.symbol})")
            try:
                position = player.choose_position(self.board)
            except ValueError:
                print("Please enter a valid number!")
                continue
            if not self.board.place(position, player.symbol):
                print("Invalid position!")
                continue
            winner = self.board.check_winner()
            if winner:
                self.board.display()
                print(f"\n{player.name} wins!")
                break
            if self.board.is_full():
                self.board.display()
                print("\nIt's a draw!")
                break
            self.switch_player()


game = TicTacToeGame(HumanPlayer("Alice", "X"), AIPlayer("Bob", "O"))
game.play()