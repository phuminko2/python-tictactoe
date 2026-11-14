# Network Tic Tac Toe

A two-player Tic Tac Toe game. `server.py` hosts the game and `main.py` is the
Tkinter client. The server assigns X to the first player and O to the second.

## Start a game

1. On the host computer, run `python server.py`.
2. Run `python main.py` on two computers (or twice on one computer).
3. Enter the server's address and a player name in each client. On the host
   computer, use `127.0.0.1`. On another computer on the same network, use the
   host computer's local IP address.

The server listens on TCP port `5000`. Allow that port through the host's
firewall if clients on other computers cannot connect. Stop the server with
Ctrl+C; start it again for a new game.
