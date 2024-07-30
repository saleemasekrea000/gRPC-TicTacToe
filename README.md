# Remote Procedure Calls

> Distributed and Networking Programming

## Overview

this code is to write a multiplayer Tic-Tac-Toe game with gRPC.
## Client Implementation 

Client accepts an address of the server as an argument and prompts a user to play Tic-Tac-Toe.

Client communicates with the server using the gRPC stub files generated by the `protoc` from the `tic_tac_toe.proto` proto file (see ["Working with gRPC" section](#working-with-grpc)).

To play the game you have two options:

1. create a new game, or
2. connect to an existing game.

When creating a new game, client:

- prompts the user to ask for a mark he wants to play (cross or nought);
- sends a request to the server to create a new game;
- prints the ID of a created game and mark the user plays;
- then prompts the user to make moves until the game is finished.

When connecting to an existing game, client:

- prompts the user to enter an ID of the game to join;
- prompts the user to ask for a mark he wants to play (cross or nought);
- connects to a game (i.e. just fetches the actual game state from the server);
- prints the ID of a created game and mark the user plays;
- then prompts the user to make moves until the game is finished.

When waiting for the opponent's move, client just repeatedly calls the `GetGame` method once a second until its the user's turn or until the game is over.

## Server Implementation

Server should accept a port as an argument and run an implemented `TicTacToe` gRPC servicer that listens on all interfaces on the specified port (i.e. `0.0.0.0:port`).

Server should store all created games in order to be able to retrieve them by their IDs and update them with new moves.
It's OK to store games in memory (e.g. in any Python structure), but you need to make sure that the server can handle multiple games at once and avoid race conditions when using threading.

### Methods

Server should implement the `TicTacToe` gRPC service defined by you in the `tic_tac_toe.proto`.
It should have 3 RPCs:

1. `CreateGame` — accepts an empty message and returns a message with a new `Game`.
2. `GetGame` — accepts a message with a single `game_id` field and returns a `Game` with the specified ID.
3. `MakeMove` - accepts a message with two fields: `game_id` and `move`, validates the move, updates the state of a `Game` (according to the rules of Tic-Tac-Toe game) and returns the updated `Game`.


### Messages

All three RPCs return `Game` message that represents the state of the Tic-Tac-Toe game.
It has the following fields:

- `id` — unique identifier of the game.
- `is_finished` — whether the game is finished or not.
- `winner` — mark of the winner, if the game is finished. Not present if the game is not finished or it's a draw.
- `turn` — mark of the player who should make a move. Not present if the game is finished.
- `moves` — sequence of moves made in the game.

`Move` message represents a single move in the game:

- `mark` — mark of the player who made the move.
- `cell` — cell number where the player placed the mark (1-9).

`Mark` is an enumeration with two values: `MARK_NOUGHT` and `MARK_CROSS`.

### Error handling

When processing requests, server should handle the following errors:

- `CreateGame` should not have any errors.
- `GetGame` should return an error with status code `NOT_FOUND` if the game with the specified ID does not exist.
- `MakeMove` should validate the request and return error with the following status codes:
  - `NOT_FOUND` — if the game with the specified ID does not exist.
  - `INVALID_ARGUMENT` — if the move's cell is invalid.
  - `FAILED_PRECONDITION` — if the game is already finished.
  - `FAILED_PRECONDITION` — if it's not the player's turn.
  - `FAILED_PRECONDITION` — if the move's cell is already occupied.

## Example Run

Here is an example of playing a game by running the server and two clients:

Server output:

```bash
$ python server.py 8080
Server listening on 0.0.0.0:8080...
CreateGame()
MakeMove(game_id=1, move=Move(mark=X, cell=5))
GetGame(game_id=1)
GetGame(game_id=1)
GetGame(game_id=1)
GetGame(game_id=1)
MakeMove(game_id=1, move=Move(mark=O, cell=1))
GetGame(game_id=1)
GetGame(game_id=1)
GetGame(game_id=1)
MakeMove(game_id=1, move=Move(mark=X, cell=3))
GetGame(game_id=1)
GetGame(game_id=1)
MakeMove(game_id=1, move=Move(mark=O, cell=2))
GetGame(game_id=1)
GetGame(game_id=1)
GetGame(game_id=1)
MakeMove(game_id=1, move=Move(mark=X, cell=7))
GetGame(game_id=1)
^CExiting...
```

1st client output:

```bash
$ python client.py localhost:8080
Welcome to Tic-Tac-Toe! 👋

Please, choose an option:
 (1) create a new game
 (2) connect to a game
> 1
Choose a player (X/O): x
Creating a new game...
Playing a game (ID=1) as player X.

┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ 5 │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 9 │
└───┴───┴───┘
Your move (X): 5

┌───┬───┬───┐
│   │   │   │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘
Waiting for the opponent's move...

┌───┬───┬───┐
│ O │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ X │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 9 │
└───┴───┴───┘
Your move (X): 3

┌───┬───┬───┐
│ O │   │ X │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘
Waiting for the opponent's move...

┌───┬───┬───┐
│ O │ O │ X │
├───┼───┼───┤
│ 4 │ X │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 9 │
└───┴───┴───┘
Your move (X): 7

[ Game over ]
┌───┬───┬───┐
│ O │ O │ X │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│ X │   │   │
└───┴───┴───┘
🎉 You won! 🎉
```

2nd client output:

```bash
python client.py localhost:8080
Welcome to Tic-Tac-Toe! 👋

Please, choose an option:
 (1) create a new game
 (2) connect to a game
> 2
Enter game ID to connect: 1
Choose a player (X/O): o
Retrieving a game (ID=1)...
Playing a game (ID=1) as player O.

┌───┬───┬───┐
│ 1 │ 2 │ 3 │
├───┼───┼───┤
│ 4 │ X │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 9 │
└───┴───┴───┘
Your move (O): 1

┌───┬───┬───┐
│ O │   │   │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘
Waiting for the opponent's move...

┌───┬───┬───┐
│ O │ 2 │ X │
├───┼───┼───┤
│ 4 │ X │ 6 │
├───┼───┼───┤
│ 7 │ 8 │ 9 │
└───┴───┴───┘
Your move (O): 2

┌───┬───┬───┐
│ O │ O │ X │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│   │   │   │
└───┴───┴───┘
Waiting for the opponent's move...

[ Game over ]
┌───┬───┬───┐
│ O │ O │ X │
├───┼───┼───┤
│   │ X │   │
├───┼───┼───┤
│ X │   │   │
└───┴───┴───┘
You lose.
```

## Working with gRPC

To work with gRPC you need to install `grpcio` package and also `grpcio-tools` package to generate code from `.proto` schema:

```bash
pip install grpcio grpcio-tools
```

you can create a [proto file](https://grpc.io/docs/what-is-grpc/introduction/#working-with-protocol-buffers) `tic_tac_toe.proto` that defines structure of the data and interface of the server.

use the following command to generate gRPC code for the server and client from the `tic_tac_toe.proto`:

```bash
python3 -m grpc_tools.protoc \
  --proto_path=. \
  --python_out=. \
  --pyi_out=. \
  --grpc_python_out=. \
  ./tic_tac_toe.proto
```

This should generate 3 files to be imported in the server and client:

```plain
├── tic_tac_toe_pb2.py      - classes corresponding to Protobuf messages and descriptors
├── tic_tac_toe_pb2.pyi     - type hint file that provides typings
└── tic_tac_toe_pb2_grpc.py - gRPC-specific code with classes for server and client
```

> Please, read the official short ["Introduction to gRPC" guide](https://grpc.io/docs/what-is-grpc/introduction/#working-with-protocol-buffers) to get better understanding of what gRPC is.
