import time
from collections import Counter
import threading
import json
from ScrabbleBoard import ScrabbleBoard
from brute import Brute

def saveExample(state, lock):
    lock.acquire()
    with open('examples.json', 'r') as f:
        config = json.load(f)
    if len(config["examples"]) == 0:
        config["examples"] = [state]
    else:
        config["examples"].append(state)
    with open('examples.json','w') as f:
        json.dump(config, f)
    lock.release()

def thread_func(move, game, ply, lock):
    lettersUsed = game.board.get_letters_used(move[2], move[0], move[3])
    lettersLeft = game.players[game.currentPlayer].rack[:]
    for letter in game.players[game.currentPlayer].rack:
        if letter.islower() and "?" in game.players[game.currentPlayer].rack:
            lettersLeft.remove("?")
        elif letter in lettersUsed:
            lettersLeft.remove(letter)
    print(lettersLeft, move[0])
    for _ in range(10):
        temp_board = copy.deepcopy(game.board)
        temp_players = copy.deepcopy(game.players)
        temp_game = copy.copy(game)
        temp_game.players = temp_players
        temp_game.board = temp_board
        temp_game.exchangeSeven(not temp_game.currentPlayer)
        temp_game.players[temp_game.currentPlayer].score += move[1]
        temp_game.play(move[2], move[0], move[3])
        state = mapBoardToState(temp_game, lettersLeft)
        temp_game.playBestMove()
        for __ in range(ply - 1):
            temp_game.playBestMove()
            temp_game.playBestMove()
        diff = temp_game.players[temp_game.currentPlayer].score - temp_game.players[not temp_game.currentPlayer].score
        state['scoreDifferentialAfterXPly'] = diff
        saveExample(state, lock)
    print(move[0])

def simulate(game, ply=2):
    lock = threading.Lock()
    moves = game.find_best_moves(game.players[game.currentPlayer].rack, 5)
    threads = []
    for move in moves:
        threads.append(threading.Thread(target=thread_func, args=(move, game, ply, lock,)))
    for th in threads:
        th.start()
    for th in threads:
        th.join()


def main(seed, b1, b2):
    Game = ScrabbleBoard(2, seed=seed)
    brute_1 = Brute(Game, 0, method=b1)
    brute_2 = Brute(Game, 1, method=b2)
    if b1 == 2:
        state, moves = brute_1.do_turn()
    TWO = brute_2.do_turn()
    while a.numMoves >= 0:
        simulate(a)
        a.playBestMove()

# initialize the board
times_per_move = []
times = []
winners = []
for seed in range(11,12):
    b1 = 2
    b2 = 2
    main(seed, b1, b2)
    Game = ScrabbleBoard(2, seed=seed)
    brute_1 = Brute(Game, 0, method=1)
    brute_2 = Brute(Game, 1, method=2)
    # brute_3 = Brute(Game, 2, method=0)
    # brute_4 = Brute(Game, 3, method=0)
    i = 0
    ONE = True
    TWO = True
    THREE = True
    FOUR = True
    start = time.time()
    while ONE and TWO and THREE and FOUR:
        ONE = brute_1.do_turn()
        TWO = brute_2.do_turn()
    # end = time.time()
    # moves = Game.get_num_moves()
    # winners.append(Game.get_winner())
    # times_per_move.append((end-start)/moves)
    # times.append(end-start)
# print(Counter(winners))
# print(sum(times)/len(times))
# print(sum(times_per_move)/len(times_per_move))