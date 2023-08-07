import time
import os
import pickle
from collections import Counter
from copy import deepcopy
import threading
import json
from ScrabbleBoard import ScrabbleBoard
from brute import Brute
from  Trie import Trie


def load_words_into_trie(file_name):
    """
    Reads words from a text file and inserts each word into the Trie.

    Args:
        file_name (str): The name of the file to read the words from.

    Returns:
        Trie: The Trie loaded with words.
    """
    trie = Trie()
    with open(file_name, 'r') as file:
        for line in file:
            word = line.strip()  # remove newline character
            trie.insert(word)
    return trie

def saveExample(state, lock):
    lock.acquire()
    # with open('examples.json', 'r') as f:
    #     config = json.load(f)
    # if len(config["examples"]) == 0:
    #     config["examples"] = [state]
    # else:
    #     config["examples"].append(state)
    # with open('examples.json','w') as f:
    #     json.dump(config, f)
    lock.release()

def thread_func(move, move_num, game, players, player, depth, lock):
    print("thread " + str(move_num) + " open")
    for shuffle_num in range(10):
        n = len(players)
        # make a copy of the game to play out a couple turns
        start = time.time()
        temp_game = deepcopy(game)
        end = time.time()
        print("time to copy game: " + str(end-start))
        # get the state from the root player to store for later
        state = deepcopy(players[player].get_state())
        # play the input move
        # make temp players list
        temp_players = []
        initial_diff = 0
        for ind in range(n):
            p = players[ind]
            if ind == player:
                initial_diff += temp_game.player_scores[ind]
            else:
                initial_diff -= temp_game.player_scores[ind]
            start = time.time()
            temp_players.append(deepcopy(p))
            end = time.time()
            print("time to copy player #" + str(ind) + " state: " + str(end-start))
            temp_players[-1].update_game(temp_game)
            temp_players[-1].recycle_hand()
        start = time.time()
        for i in range(depth):
            for tp in range(n):
                tp = (tp + player)%n
                if i == 0 and tp == player:
                    temp_players[tp].do_turn(move[1], move[2], move[3], move[4])
                else:
                    play = temp_players[tp].get_play(1)
                    temp_players[tp].do_turn(play[0], play[1], play[2], play[3])
        end = time.time()
        print("time to do full turn cycle of " + str(depth) + " turns: " + str(end-start))
        final_diff = temp_game.player_scores[player] - sum(score for p, score in temp_game.player_scores.items() if p != player)
        net_diff = initial_diff - final_diff
        print(move_num, shuffle_num, net_diff)
        state['reward'] = net_diff
        saveExample(state, lock)

def simulate(game, players, player, depth=2):
    lock = threading.Lock()
    moves = players[player].get_play(2)
    if len(moves) > 10:
        moves = moves[0:1]
    threads = []
    move_num = 0
    for move in moves:
        threads.append(threading.Thread(target=thread_func, args=(move, move_num, game, players, player, depth, lock,)))
        move_num += 1
    for th in threads:
        th.start()
    for th in threads:
        th.join()


def main(loaded_trie, seed, methods):
    n = len(methods)
    start = time.time()
    Game = ScrabbleBoard(n, loaded_trie, seed)
    end = time.time()
    print("time to initialize game: " + str(end-start))
    players = []
    for i in range(n):
        players.append(Brute(Game, i))
        
    player = 0
    while Game.winner < 0:
        if methods[player] == 2:
            simulate(Game, players, player)
        else:
            play = players[player].get_play(methods[player])[0]
            players[player].do_turn(play[0], play[1], play[2], play[3])
        player = (player + 1) % n

# load the words from the dictionary file into trie
start = time.time()
if os.path.isfile('trie.pkl'):
    # Load trie_instance from a file
    with open('trie.pkl', 'rb') as file:
        loaded_trie = pickle.load(file)
else:
    loaded_trie = load_words_into_trie('Collins Scrabble Words (2019).txt')
end = time.time()
print("time to load trie: " + str(end-start))

# initialize the board
times_per_move = []
times = []
winners = []
for seed in range(11,12):
    b1 = 1
    b2 = 2
    main(loaded_trie, seed, [b1, b2])
    Game = ScrabbleBoard(2, loaded_trie, seed)
    brute_1 = Brute(Game, 0)
    brute_2 = Brute(Game, 1)
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