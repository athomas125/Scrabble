import re
from itertools import combinations
from Trie import Trie
from ScrabbleBoard import ScrabbleBoard
import time
from copy import deepcopy
import numpy as np
import string
from enum import Enum

class Brute:
    """
    game player that uses a brute force method
    """
    def __init__(self, game, number):
        # load the words from the dictionary file into the brute's brain
        self.brain = self.load_words_into_trie('Collins Scrabble Words (2019).txt')
        self.Game = game
        self.hand = self.Game.draw_letters(7)
        self.number = number
        
        
    def load_words_into_trie(self, file_name):
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


    def get_words(self, letters, prefix='', words=None, fixed_letters=None):
        if words is None:
            words = set()
        if fixed_letters is None:
            fixed_letters = {}

        if len(prefix) in fixed_letters:
            prefix += fixed_letters[len(prefix)]

        if prefix:
            valid_word, valid_prefix = self.brain.search(prefix)
            if valid_word:
                words.add(prefix)
            if not valid_prefix:
                return words

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_words(new_letters, prefix + wildcard, words)
            else:
                self.get_words(new_letters, prefix + letter, words)
        return words
    
    def get_prefixes(self, letters, prefix='', prefixes = None):
        if prefixes is None:
            prefixes = set()
            
        if prefix:
            valid_word, valid_prefix = self.brain.search(prefix)
            if not valid_prefix:
                return prefixes

        for i, letter in enumerate(letters):
            new_letters = list(letters)
            new_letters.pop(i)
            if letter == ' ':
                for wildcard in string.ascii_uppercase:
                    self.get_words(new_letters, prefix + wildcard, prefixes)
            else:
                self.get_words(new_letters, prefix + letter, prefixes)
        return prefixes
    
    
    def find_best_play(self):
        """
        Finds the best place to play a word from the given list of words.

        Returns:
            tuple: A tuple containing the best word to play, its score, starting position (row, col), and direction.
        """
        best_word = None
        best_score = 0
        best_position = None
        best_direction = None
        best_letters_from_hand = None

        if self.Game.get_is_first_turn():
            # just want to calculate the highest score word in our hand
            valid_words = self.get_words(self.hand)
            valid_words = sorted(valid_words, key=len)[::-1]
            for word in valid_words:
                # simplifying by placing the first word horizontally always
                row = 7
                letters_from_hand = word
                for col in range(7 - (len(word)-1), 8):
                    letter_multipliers, word_multipliers = self.Game.get_multipliers(row, col, word, 'across')
                    score = self.Game.calculate_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
                    if score > best_score:
                        best_word = word
                        best_letters_from_hand = best_word
                        best_score = score
                        best_position = (row, col)
                        best_direction = 'across'
        else:
            # TODO: Implement this
            # compute all words that are made out of our letters so that 
            # we have a set of prefixes to use to check for more words
            # prefixes = self.get_prefixes(self.hand)
            # sorted_dict = {}
            # for prefix in prefixes:
            #     length = len(prefix)
            #     if length not in sorted_dict:
            #         sorted_dict[length] = []
            #     sorted_dict[length].append(prefix)

            # here you want to check both directions and all possible play locations
            # TODO: update full board search to just search to play off where there are letters
            for i, item in enumerate(self.Game.letter_locations):
                row = item[0]
                col = item[1]
                letter = self.Game.board[item[0]][item[1]]
                for direction in ['across', 'down']:
                    # TODO: update this so that it accounts for other words on the board
                    fl = {}
                    for i in range(8):
                        fl[i] = letter
                        # Check if word can be played in this position
                        words = self.get_words(self.hand, fixed_letters=fl)
                        for word in words:
                            if self.Game.can_play_word(row, col, word, direction):
                                letter_multipliers, word_multipliers = self.Game.get_multipliers(row, col, word, direction)
                                # Calculate score
                                letters_from_hand = word.replace(letter, "", 1)
                                score = self.Game.calculate_score(word, letter_multipliers, word_multipliers, len(letters_from_hand))
                                if score > best_score:
                                    best_word = word
                                    best_letters_from_hand = letters_from_hand
                                    best_score = score
                                    best_position = (row, col)
                                    best_direction = direction
        
        return best_word, best_position, best_direction, best_letters_from_hand

    def do_turn(self):
        """turn execution
        """
        word, position, direction, letters_from_hand = self.find_best_play()
        self.Game.place_word(position[0], position[1], word, direction, self.number, len(letters_from_hand))
        temp_hand = deepcopy(self.hand)
        for letter in letters_from_hand:
            if letter not in self.hand:
                letter = ' '
            index = self.hand.index(letter)
            self.hand = self.hand[0:index] + self.hand[index + 1:]
        self.Game.display_board()
        print("hand was: " + str(temp_hand) + "\nword: "+ word + "\nnumber of points: " + str(self.Game.get_scores()[self.number]))
        self.hand += self.Game.draw_letters(len(letters_from_hand))
        print("new hand" + str(self.hand))

# initialize the board
Game = ScrabbleBoard(1)
brute_1 = Brute(Game, 1)
go_again = 'yep'
while go_again != 'stop':
    brute_1.do_turn()
    go_again = input("type stop to stop, otherwise it will do another turn: ")
