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
    with lock:
        with open('examples.json', 'r') as f:
            config = json.load(f)
        if len(config["examples"]) == 0:
            config["examples"] = [state]
        else:
            config["examples"].append(state)
        with open('examples.json','w') as f:
            json.dump(config, f)

def thread_func(move, move_num, game, players, player, depth, results_list, lock):
    total_diff = 0
    for shuffle_num in range(10):
        n = len(players)
        # make a copy of the game to play out a couple turns
        temp_game = deepcopy(game)
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
            temp_players.append(deepcopy(p))
            temp_players[-1].update_game(temp_game)
            if ind != player:
                # if the player isn't the primary player, recycle hand to give random letters
                temp_players[-1].recycle_hand()
        for i in range(depth):
            for tp in range(n):
                if temp_game.winner < 0:
                    tp = (tp + player)%n
                    if i == 0 and tp == player:
                        temp_players[tp].do_turn(move[1], move[2], move[3], move[4])
                    else:
                        play = temp_players[tp].get_play(1)[0]
                        temp_players[tp].do_turn(play[0], play[1], play[2], play[3])
        final_diff = temp_game.player_scores[player] - sum(score for p, score in enumerate(temp_game.player_scores) if p != player)
        net_diff = final_diff - initial_diff
        total_diff += net_diff
        state['reward'] = net_diff
        state['action'] = move
        saveExample(state, lock)
    with lock:
        # save to total diff as a metric to determine what move to use
        results_list[move_num] = total_diff

def simulate(game, players, player, depth=2):
    lock = threading.Lock()
    moves = players[player].get_play(2)
    if len(moves) > 10:
        moves = moves[0:10]
    threads = []
    move_num = 0
    # Initialize the results list with None for each move
    results_list = [None] * len(moves)
    for move in moves:
        threads.append(threading.Thread(target=thread_func, args=(move, move_num, game, players, player, depth, results_list, lock,)))
        move_num += 1
    for th in threads:
        th.start()
    for th in threads:
        th.join()
        
    # After threads are done, analyze results_list to determine best move
    best_move_index = results_list.index(max(results_list))
    print(best_move_index)
    return moves[best_move_index]
    


def main(loaded_trie, seed, methods):
    n = len(methods)
    Game = ScrabbleBoard(n, loaded_trie, seed)
    players = []
    for i in range(n):
        players.append(Brute(Game, i))
        
    player = 0
    cnt = 0
    start = time.time()
    while Game.winner < 0:
        if methods[player] == 2:
            play = simulate(Game, players, player)[1:]
        else:
            play = players[player].get_play(methods[player])[0]
        players[player].do_turn(play[0], play[1], play[2], play[3])
        player = (player + 1) % n
        cnt += 1
    end = time.time()
    Game.display_board()
    print(Game.player_scores)
    print("time for one simulation: " + str(end-start))

# load the words from the dictionary file into trie
if os.path.isfile('trie.pkl'):
    # Load trie_instance from a file
    with open('trie.pkl', 'rb') as file:
        loaded_trie = pickle.load(file)
else:
    loaded_trie = load_words_into_trie('Collins Scrabble Words (2019).txt')

# initialize the board
times_per_move = []
times = []
winners = []
for seed in range(0,10):
    b1 = 1
    b2 = 2
    main(loaded_trie, seed, [b1, b2])
    # Game = ScrabbleBoard(2, loaded_trie, seed)
    # brute_1 = Brute(Game, 0)
    # brute_2 = Brute(Game, 1)
    # brute_3 = Brute(Game, 2, method=0)
    # brute_4 = Brute(Game, 3, method=0)
    # i = 0
    # ONE = True
    # TWO = True
    # THREE = True
    # FOUR = True
    # start = time.time()
    # while ONE and TWO and THREE and FOUR:
    #     ONE = brute_1.do_turn()
    #     TWO = brute_2.do_turn()
    # end = time.time()
    # moves = Game.get_num_moves()
    # winners.append(Game.get_winner())
    # times_per_move.append((end-start)/moves)
    # times.append(end-start)
# print(Counter(winners))
# print(sum(times)/len(times))
# print(sum(times_per_move)/len(times_per_move))