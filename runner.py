import time
from collections import Counter
from ScrabbleBoard import ScrabbleBoard
from brute import Brute

# initialize the board
times_per_move = []
times = []
winners = []
for seed in range(0,2):
    Game = ScrabbleBoard(2, seed=seed)
    brute_1 = Brute(Game, 0, method=0)
    brute_2 = Brute(Game, 1, method=0)
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
        # THREE = brute_3.do_turn()
        # FOUR = brute_4.do_turn()
    end = time.time()
    moves = Game.get_num_moves()
    winners.append(Game.get_winner())
    times_per_move.append((end-start)/moves)
    times.append(end-start)
print(Counter(winners))
print(sum(times)/len(times))
print(sum(times_per_move)/len(times_per_move))