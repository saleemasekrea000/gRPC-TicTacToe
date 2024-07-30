from typing import Iterable, Optional
import tic_tac_toe_pb2_grpc as ttt_grpc
import tic_tac_toe_pb2 as ttt
import grpc
import threading
import argparse
from concurrent import futures


def get_winner(moves: Iterable[ttt.Move]):
    winning_combinations = (
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),  # Rows
        (1, 4, 7),
        (2, 5, 8),
        (3, 6, 9),  # Cols
        (1, 5, 9),
        (3, 5, 7),  # Diagonals
    )

    x_moves = []
    o_moves = []

    for move in moves:
        if move.mark == ttt.MARK_CROSS:
            x_moves.append(move.cell)
        elif move.mark == ttt.MARK_NOUGHT:
            o_moves.append(move.cell)

    for combination in winning_combinations:
        if all((cell in x_moves) for cell in combination):
            return ttt.MARK_CROSS
        if all((cell in o_moves) for cell in combination):
            return ttt.MARK_NOUGHT

    return None


class TicTacToeServicer(ttt_grpc.TicTacToeServicer):
    def __init__(self):
        self.games = {}
        self.lock = threading.Lock()

    def CreateGame(self, request, context):
        with self.lock:
            game_id = len(self.games) + 1
            game = ttt.Game(
                id=game_id,
                is_finished=False,
                winner=ttt.MARK_NOUGHT,
                turn=ttt.MARK_CROSS,
            )
            self.games[game_id] = game
            print("CreateGame()")
            return game

    def GetGame(self, request, context):
        with self.lock:
            game_id = request.game_id
            if game_id not in self.games:
                context.abort(grpc.StatusCode.NOT_FOUND, "Game not found")
            print(f"GetGame(game_id={game_id})")
            return self.games[game_id]

    def MakeMove(self, request, context):
        with self.lock:
            game_id = request.game_id
            move = request.move
            # print("the move is ",move)

            if game_id not in self.games:
                context.abort(grpc.StatusCode.NOT_FOUND, "Game not found")

            game = self.games[game_id]

            if game.is_finished:
                context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION, "Game is already finished"
                )

            if move.cell < 1 or move.cell > 9:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid cell number")

            if move.cell in [m.cell for m in game.moves]:
                context.abort(
                    grpc.StatusCode.FAILED_PRECONDITION, "Cell is already occupied"
                )

            if move.mark != game.turn:
                context.abort(grpc.StatusCode.FAILED_PRECONDITION, "It's not your turn")

            game.moves.append(move)
            # print("XXXXX")
            # print(game.moves)
            winner = get_winner(game.moves)
            # print("XXXXXX")
            if winner is not None:
                game.is_finished = True
                game.winner = get_winner(game.moves)
            elif len(game.moves) == 9:
                game.is_finished = True
                game.ClearField("winner")

            if not game.is_finished:
                game.turn = (
                    ttt.MARK_NOUGHT if game.turn == ttt.MARK_CROSS else ttt.MARK_CROSS
                )
            print(
                f"MakeMove(game_id={game_id}, move=Move(mark={mark_to_symbol(move.mark)}, cell={move.cell}))"
            )
            return game


def mark_to_symbol(mark):
    if mark == ttt.MARK_CROSS:
        return "X"
    elif mark == ttt.MARK_NOUGHT:
        return "O"


def serve(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ttt_grpc.add_TicTacToeServicer_to_server(TicTacToeServicer(), server)
    server.add_insecure_port("[::]:8080")
    server.add_insecure_port("[::]:" + str(port))
    server.start()
    print("Server listening on 0.0.0.0:" + str(port) + "...")
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Keyboard interrupt received. Stopping the server...")
        server.stop(None)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("port", type=int, help="Port number to run the server on")
    args = parser.parse_args()
    serve(args.port)
